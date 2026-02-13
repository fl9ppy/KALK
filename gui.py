from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QListWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QMessageBox, QInputDialog, QPlainTextEdit,
    QTextEdit
)

from PySide6.QtGui import (
    QFont, QSyntaxHighlighter,
    QTextCharFormat, QColor,
    QTextFormat, QPainter,
    QTextCursor
)

from PySide6.QtCore import Qt, QRect, QSize

from .lexer import Lexer
from .parser import Parser
from .engine import Engine
from .ast_nodes import Context

import sys
import os
import re


STD_DIR = "kalk/programs"
USR_DIR = "kalk/user_programs"


# =========================================================
# LINE NUMBER AREA
# =========================================================

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_width(), 0)

    def mousePressEvent(self, event):
        block = self.editor.firstVisibleBlock()
        top = int(self.editor.blockBoundingGeometry(block)
                  .translated(self.editor.contentOffset()).top())

        while block.isValid():
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            if top <= event.pos().y() <= bottom:
                line = block.blockNumber()
                self.editor.toggle_breakpoint(line)
                break
            block = block.next()
            top = bottom

    def paintEvent(self, event):
        self.editor.line_number_area_paint(event)


# =========================================================
# CODE EDITOR
# =========================================================

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.breakpoints = set()
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_width(0)
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    # ---------- LINE NUMBERS ----------

    def line_number_width(self):
        digits = max(2, len(str(self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space + 10

    def update_line_number_width(self, _):
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(),
                                       self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(),
                  self.line_number_width(), cr.height())
        )

    def line_number_area_paint(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#252526"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block)
                  .translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)

                # breakpoint
                if blockNumber in self.breakpoints:
                    painter.setBrush(QColor("red"))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(2, top + 4, 8, 8)

                painter.setPen(QColor("#858585"))
                painter.drawText(
                    0, top,
                    self.lineNumberArea.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def toggle_breakpoint(self, line):
        if line in self.breakpoints:
            self.breakpoints.remove(line)
        else:
            self.breakpoints.add(line)
        self.lineNumberArea.update()

    # ---------- CURRENT LINE HIGHLIGHT ----------

    def highlight_current_line(self):
        if self.isReadOnly():
            return

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#2a2d2e"))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()

        self.setExtraSelections([selection])

    # ---------- AUTO INDENT + TAB ----------

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Tab:
            self.insertPlainText("    ")
            return

        if event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            cursor.select(QTextCursor.LineUnderCursor)
            line = cursor.selectedText()

            indent = ""
            for ch in line:
                if ch == " ":
                    indent += " "
                else:
                    break

            stripped = line.strip().upper()

            if stripped.endswith("ATUNCI") or stripped.endswith("EXECUTA") or stripped == "ALTFEL":
                indent += "    "

            if stripped == "SFARSIT":
                indent = indent[:-4] if len(indent) >= 4 else ""

            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        super().keyPressEvent(event)


# =========================================================
# SYNTAX HIGHLIGHTER
# =========================================================

class KalkHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "CITESTE", "DECLAR", "VALOARE",
            "DACA", "ATUNCI", "ALTFEL",
            "CATTIMP", "EXECUTA", "SFARSIT",
            "SCRIE", "SI", "SAU"
        ]

        for word in keywords:
            self.rules.append((r"\b" + word + r"\b", keyword_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.rules.append((r"\b[0-9]+\b", number_format))

        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4"))
        operators = ["<-", "+", "-", "*", "/", "%", "==", "!=", "<=", ">=", "<", ">"]

        for op in operators:
            self.rules.append((re.escape(op), operator_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


# =========================================================
# MAIN WINDOW
# =========================================================

class KalkWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KALK IDE")
        self.resize(1200, 700)

        self.editor = CodeEditor()
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        font = QFont("Consolas")
        font.setPointSize(11)
        self.editor.setFont(font)
        self.output.setFont(font)

        self.highlighter = KalkHighlighter(self.editor.document())

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

        self.std_list.itemDoubleClicked.connect(lambda: self.load_selected(self.std_list, STD_DIR))
        self.usr_list.itemDoubleClicked.connect(lambda: self.load_selected(self.usr_list, USR_DIR))

        left = QVBoxLayout()
        left.addWidget(QLabel("Editor"))
        left.addWidget(self.editor)
        left.addWidget(run_btn)
        left.addWidget(save_btn)

        right = QVBoxLayout()
        right.addWidget(QLabel("Standard Library"))
        right.addWidget(self.std_list)
        right.addWidget(load_std_btn)

        right.addWidget(QLabel("Personal Library"))
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

        self.apply_dark_theme()

    # ---------- UI ----------

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QMainWindow { background-color: #1e1e1e; }
        QPlainTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; }
        QListWidget { background-color: #252526; color: #ccc; border: 1px solid #333; }
        QPushButton { background-color: #3c3c3c; color: white; padding: 6px; }
        QPushButton:hover { background-color: #505050; }
        QLabel { color: #ccc; }
        """)

    # ---------- FILE MANAGEMENT ----------

    def load_program_lists(self):
        os.makedirs(STD_DIR, exist_ok=True)
        os.makedirs(USR_DIR, exist_ok=True)

        self.std_list.clear()
        self.usr_list.clear()

        for f in os.listdir(STD_DIR):
            if f.endswith(".kalk"):
                self.std_list.addItem(f)

        for f in os.listdir(USR_DIR):
            if f.endswith(".kalk"):
                self.usr_list.addItem(f)

    def load_selected(self, widget, directory):
        item = widget.currentItem()
        if not item:
            return
        path = os.path.join(directory, item.text())
        with open(path, "r") as file:
            self.editor.setPlainText(file.read())

    def save_program(self):
        name, ok = QInputDialog.getText(self, "Save", "Program name:")
        if ok and name:
            if not name.endswith(".kalk"):
                name += ".kalk"
            with open(os.path.join(USR_DIR, name), "w") as f:
                f.write(self.editor.toPlainText())
            self.load_program_lists()

    # ---------- EXECUTION ----------

    def run_program(self):
        self.output.clear()
        text = self.editor.toPlainText()

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

            ctx = Context()
            engine = Engine()
            engine.run(program, ctx)

            self.output.setPlainText("\n".join(ctx.output))

        except Exception as e:
            self.output.setPlainText(str(e))


# =========================================================
# START
# =========================================================

def start_gui():
    app = QApplication(sys.argv)
    win = KalkWindow()
    win.show()
    sys.exit(app.exec())
