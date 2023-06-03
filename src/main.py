import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.Qsci import *


import sys
from pathlib import Path

import keyword 
import pkgutil 



class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        # Add before init
        self.side_bar_clr = "#282c34"
        self.init_ui()

        self.current_file = None

    def init_ui(self):
        self.setWindowTitle("Emerald")
        self.resize(1300, 900)

        self.setStyleSheet(open("./src/css/style.qss", "r").read())

        # Alternative Console font
        self.window_font = QFont("Fire Code")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)

        self.set_up_menu()
        self.set_up_body()
        self.statusBar().showMessage("hello")
        

        self.show()

    def set_up_menu(self):
        menu_bar = self.menuBar()

        # File Menu 
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+K")
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        # Edit Menu 
        edit_menu = menu_bar.addMenu("Edit")

        copy_action = edit_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)

    
    def get_editor(self) -> QsciScintilla:
        
        # Instance
        editor = QsciScintilla() 
        # Encoding
        editor.setUtf8(True)
        # Font
        editor.setFont(self.window_font)

        # Brace matching 
        editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Indentation
        editor.setIndentationGuides(True)
        editor.setTabWidth(4)
        editor.setIndentationsUseTabs(False)
        editor.setAutoIndent(True)

        # Autocomplete 
        editor.setAutoCompletionSource(QsciScintilla.AcsAll)
        editor.setAutoCompletionThreshold(1)
        editor.setAutoCompletionCaseSensitivity(False)
        editor.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # Caret
        #editor.setCaretForegroundColor(QColor("#dedcdc"))
        editor.setCaretLineVisible(True)
        editor.setCaretWidth(2)
        #editor.setCaretLineBackgroundColor(QColor("#2c313c"))

        # EOL
        editor.setEolMode(QsciScintilla.EolWindows)
        editor.setEolVisibility(False)

        # Lexer for syntax highlighting
        self.pylexer = QsciLexerPython()
        self.pylexer.setDefaultFont(self.window_font)

        # Api
        self.api = QsciAPIs(self.pylexer)
        for key in keyword.kwlist + dir(__builtins__):
            self.api.add(key)

        for _, name, _ in pkgutil.iter_modules():
            self.api.add(name)

        self.api.prepare()

        editor.setLexer(self.pylexer)

        # Line numbers 
        editor.setMarginType(0, QsciScintilla.NumberMargin)
        editor.setMarginWidth(0, "000")
        editor.setMarginsForegroundColor(QColor("#ff888888"))
        editor.setMarginsBackgroundColor(QColor("#282c34"))
        editor.setMarginsFont(self.window_font)

        # Key Press 
        editor.keyPressEvent = self.handle_editor_press

        return editor

    def handle_editor_press(self, e: QKeyEvent):
        editor: QsciScintilla = self.tab_view.currentWidget()
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Space:
            editor.autoCompleteFromAll()
        else: 
            QsciScintilla.keyPressEvent(editor, e)
    
    def is_binary(self, path):
        '''
        Check if file is binary 
        ''' 
        with open(path, 'rb') as f: 
            return b'\0' in f.read(1024)

    def set_new_tab(self, path: Path, is_new_file=False):
        editor = self.get_editor()

        if is_new_file: 
            self.tab_view.addTab(editor, "untitled")
            self.setWindowTitle("untitled")
            self.statusBar().showMessage("Opened Untitled")
            self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
            self.current_file = None 
            return

        if not path.is_file():
            return
        if self.is_binary(path):
            self.statusBar().showMessage("Cannot Open Binary File", 2000)
            return 
        
        # Check if file already open 
        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == path.name:
                self.tab_view.setCurrentIndex(i)
                self.current_file = path
                return 


        # Create new tab
        self.tab_view.addTab(editor, path.name)
        editor.setText(path.read_text())
        self.setWindowTitle(path.name)
        self.current_file = path 
        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
        self.statusBar().showMessage(f"Opened {path.name}", 2000)

    def set_up_body(self):
        
        # Body
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)

        # side_bar 
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Plain)
        self.side_bar.setStyleSheet(f'''
            background-color: {self.side_bar_clr};
        ''')
        side_bar_layout = QHBoxLayout()
        side_bar_layout.setContentsMargins(5, 10, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # Setup labels 
        folder_label = QLabel()
        folder_label.setPixmap(QPixmap("./src/icons/folder-icon-blue.svg").scaled(QSize(25, 25)))
        folder_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        folder_label.setFont(self.window_font)
        folder_label.mousePressEvent = self.show_hide_tab
        side_bar_layout.addWidget(folder_label)
        self.side_bar.setLayout(side_bar_layout)

        body.addWidget(self.side_bar)

        # Split View 
        self.hsplit = QSplitter(Qt.Horizontal)

        # Frame & Layout to hold tree view
        self.tree_frame = QFrame()
        self.tree_frame.setLineWidth(1)
        self.tree_frame.setMaximumWidth(400)
        self.tree_frame.setMinimumWidth(200)
        self.tree_frame.setBaseSize(100, 0)
        self.tree_frame.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)
        self.tree_frame.setStyleSheet('''
            QFrame {
                background-color: #21252b;
                border-radius: 5px;
                border: none; 
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame:hover {
                color: white;
            }
        ''')

        # File system model to show in tree view
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())
        #File system filters 
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

        # Tree View 
        self.tree_view = QTreeView()
        self.tree_view.setFont(QFont("FireCode", 13))
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.getcwd()))
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        # Custom context menu 
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.tree_view_context_menu)
        # Handling click 
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.setIndentation(10)
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Hide header & hide other colums xcept for name 
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        # Setup layout 
        tree_frame_layout.addWidget(self.tree_view)
        self.tree_frame.setLayout(tree_frame_layout)

        # Tab widget to add either to
        self.tab_view = QTabWidget()
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.setTabsClosable(True)
        self.tab_view.setMovable(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.tabCloseRequested.connect(self.close_tab)

        # Tree view & Tab View 
        self.hsplit.addWidget(self.tree_frame)
        self.hsplit.addWidget(self.tab_view)

        body.addWidget(self.hsplit)
        body_frame.setLayout(body)

        self.setCentralWidget(body_frame)

    def close_tab(self, index):
        self.tab_view.removeTab(index)

    def show_hide_tab(self):
        ...


    def tree_view_context_menu(self, pos):
        ...

    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        self.set_new_tab(p)

    def new_file(self):
        self.set_new_tab(None, is_new_file=True) 
    
    def save_file(self):
        if self.current_file is None and self.tab_view.count() > 0:
            self.save_as()
        
        editor = self.tab_view.currentWidget()
        self.current_file.write_text(editor.text())
        self.statusBar().showMessage(f"Saved {self.current_file.name}", 2000)

    def save_as(self):
        # Save as 
        editor = self.tab_view.currentWidget()
        if editor is None: 
            return 
        file_path = QFileDialog.getSaveFileName(self, "Save as", os.getcwd())[0]
        if file_path == '':
            self.statusBar().showMessage("Cancelled", 2000)
            return
        path = Path(file_path)
        path.write_text(editor.text())
        self.tab_view.setTabText(self.tab_view.currentIndex(), path.name)
        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.current_file = path

    def open_file(self):
        # Open File 
        ops = QFileDialog.Options() # This is optional 
        ops |= QFileDialog.DontUseNativeDialog
        new_file, _ = QFileDialog.getOpenFileName(self,
                    "Pick A File", "", "All Files (*);;Python Files (*.py)",
                    options=ops)
        if new_file == '':
            self.statusBar().showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)

    def open_folder(self):
        # Open Folder 
        ops = QFileDialog.Options() # This is optional 
        ops |= QFileDialog.DontUseNativeDialog

        new_folder = QFileDialog.getExistingDirectory(self, "Pick A Folder", "", options=ops)
        if new_folder:
            self.model.setRootPath(new_folder)
            self.tree_view.setRootIndex(self.model.index(new_folder))
            self.statusBar().showMessage(f"Opened {new_folder}", 2000)
    
    def copy(self):
        editor = self.tab_view.currentWidget()
        if editor is not None: 
            editor.copy()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())