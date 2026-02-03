from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QTextEdit, QPushButton, QListWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QInputDialog
)

from .lexer import Lexer
from .parser import Parser
from .engine import Engine
from .ast_nodes import Context

import sys
import os


STD_DIR = "kalk/programs"
USR_DIR = "kalk/user_programs"


class KalkWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KALK Interpreter")
        self.resize(1000, 600)

        self.editor = QTextEdit()
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.std_list = QListWidget()
        self.usr_list = QListWidget()

        self.load_program_lists()

        run_btn = QPushButton("Run")
        save_btn = QPushButton("Save to My Library")
        load_std_btn = QPushButton("Load Standard")
        load_usr_btn = QPushButton("Load Personal")

        run_btn.clicked.connect(self.run_program)
        save_btn.clicked.connect(self.save_program)
        load_std_btn.clicked.connect(lambda: self.load_selected(self.std_list, STD_DIR))
        load_usr_btn.clicked.connect(lambda: self.load_selected(self.usr_list, USR_DIR))

        left = QVBoxLayout()
        left.addWidget(QLabel("Editor"))
        left.addWidget(self.editor)
        left.addWidget(run_btn)
        left.addWidget(save_btn)

        right = QVBoxLayout()
        right.addWidget(QLabel("Biblioteca standard"))
        right.addWidget(self.std_list)
        right.addWidget(load_std_btn)

        right.addWidget(QLabel("Biblioteca personală"))
        right.addWidget(self.usr_list)
        right.addWidget(load_usr_btn)

        right.addWidget(QLabel("Output"))
        right.addWidget(self.output)

        root = QHBoxLayout()
        root.addLayout(left, 2)
        root.addLayout(right, 1)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

    # ---------- FILE MANAGEMENT ----------

    def load_program_lists(self):
        self.std_list.clear()
        self.usr_list.clear()

        for f in os.listdir(STD_DIR):
            if f.endswith(".kalk"):
                self.std_list.addItem(f)

        if not os.path.exists(USR_DIR):
            os.mkdir(USR_DIR)

        for f in os.listdir(USR_DIR):
            if f.endswith(".kalk"):
                self.usr_list.addItem(f)

    def load_selected(self, widget, directory):
        item = widget.currentItem()
        if not item:
            return
        path = os.path.join(directory, item.text())
        self.editor.setText(open(path).read())

    def save_program(self):
        name, ok = QInputDialog.getText(self, "Save", "Nume algoritm:")
        if not ok or not name:
            return

        if not name.endswith(".kalk"):
            name += ".kalk"

        path = os.path.join(USR_DIR, name)
        open(path, "w").write(self.editor.toPlainText())
        self.load_program_lists()

    # ---------- EXECUTION ----------

    def run_program(self):
        self.output.clear()
        text = self.editor.toPlainText()

        def gui_input(var):
            val, ok = QInputDialog.getInt(self, "Input", f"{var} =")
            if not ok:
                raise Exception("Input anulat")
            return val

        try:
            lexer = Lexer(text)
            tokens = []
            while True:
                t = lexer.next_token()
                tokens.append(t)
                if t.type == "EOF":
                    break

            parser = Parser(tokens)
            program = parser.parse_program()

            ctx = Context(input_provider=gui_input)
            engine = Engine()
            engine.run(program, ctx)

            self.output.setText("\n".join(ctx.output))

        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))


def start_gui():
    app = QApplication(sys.argv)
    win = KalkWindow()
    win.show()
    sys.exit(app.exec())
