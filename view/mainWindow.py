import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                             QFileDialog, QLabel, QVBoxLayout, QHBoxLayout,
                             QWidget, QGridLayout, QTableWidget, QTableWidgetItem)
from models.lexical_analyzer import LexicalAnalyzer

class PHPAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PHP Lexical Analyzer')
        self.setGeometry(100, 100, 800, 600)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        layout = QVBoxLayout()
        centralWidget.setLayout(layout)

        topLayout = QHBoxLayout()
        layout.addLayout(topLayout)

        self.codeEditor = QTextEdit()
        topLayout.addWidget(self.codeEditor)

        self.tokensEditor = QTextEdit()
        topLayout.addWidget(self.tokensEditor)

        bottomLayout = QGridLayout()
        layout.addLayout(bottomLayout)

        self.createLexemeFields(bottomLayout)
        self.createButtons(layout)

    def createLexemeFields(self, layout):
        lexemeTypes = ['Keywords', 'Identifiers', 'Operations', 'Delimiters',
                       'Numbers', 'Strings']
        self.lexemeFields = {}

        for i, lexemeType in enumerate(lexemeTypes):
            label = QLabel(lexemeType)
            layout.addWidget(label, i // 3, (i % 3) * 2)

            table = QTableWidget()
            layout.addWidget(table, i // 3, (i % 3) * 2 + 1)

            self.lexemeFields[lexemeType] = table

    def createButtons(self, layout):
        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)

        self.openButton = QPushButton('Open File')
        self.openButton.clicked.connect(self.openFile)
        buttonLayout.addWidget(self.openButton)

        self.runButton = QPushButton('Run')
        self.runButton.clicked.connect(self.runAnalysis)
        buttonLayout.addWidget(self.runButton)

        self.debugButton = QPushButton('Debug')
        self.debugButton.clicked.connect(self.debugAnalysis)
        buttonLayout.addWidget(self.debugButton)

        self.nextButton = QPushButton('Next')
        self.nextButton.clicked.connect(self.debugStep)
        self.nextButton.setEnabled(False)
        buttonLayout.addWidget(self.nextButton)

        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.stopDebug)
        self.stopButton.setEnabled(False)
        buttonLayout.addWidget(self.stopButton)

        self.clearButton = QPushButton('Clear')
        self.clearButton.clicked.connect(self.clearFields)
        buttonLayout.addWidget(self.clearButton)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File', '',
                                                  'PHP Files (*.php);;Text Files (*.txt)')
        if fileName:
            with open(fileName, 'r') as file:
                self.codeEditor.setPlainText(file.read())

    def runAnalysis(self):
        # 1. Получаем PHP код из поля ввода
        php_code = self.codeEditor.toPlainText()

        # 2. Выполняем лексический анализ
        analyzer = LexicalAnalyzer()
        output_sequence, tokens = analyzer.analyze_php(php_code)

        # 3. Выводим последовательность токенов
        self.tokensEditor.setPlainText(output_sequence)

        # 4. Выводим лексемы и их коды в таблицы
        for token_class, lexemes in tokens.items():
            if token_class == 'W':
                table = self.lexemeFields['Keywords']
            elif token_class == 'I':
                table = self.lexemeFields['Identifiers']
            elif token_class == 'O':
                table = self.lexemeFields['Operations']
            elif token_class == 'R':
                table = self.lexemeFields['Delimiters']
            elif token_class == 'N':
                table = self.lexemeFields['Numbers']
            elif token_class == 'C':
                table = self.lexemeFields['Strings']

            table.setRowCount(len(lexemes))
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(['Lexeme', 'Code'])

            for row, (lexeme, code) in enumerate(lexemes.items()):
                table.setItem(row, 0, QTableWidgetItem(lexeme))
                table.setItem(row, 1, QTableWidgetItem(code))

    def debugAnalysis(self):
        php_code = self.codeEditor.toPlainText()
        self.analyzer = LexicalAnalyzer()
        self.output_sequence, self.tokens, self.debug_generator = self.analyzer.analyze_php(php_code, debug=True)

        self.current_line = 1
        self.current_pos = 1

        self.debugButton.setEnabled(False)
        self.runButton.setEnabled(False)
        self.nextButton.setEnabled(True)
        self.stopButton.setEnabled(True)

    def debugStep(self):
        try:
            event = next(self.debug_generator)
            if event['type'] == 'transition':
                self.current_line = event['line']
                self.current_pos = event['pos']
            elif event['type'] == 'output':
                self.output_sequence += event['token'] + ' '
            elif event['type'] == 'lexeme':
                self.analyzer.check(self.tokens, event['token_class'], event['lexeme'])

            self.highlightCurrentPosition()
            self.updateDebugOutput()

        except StopIteration:
            self.stopDebug()
            print('Debug finished')

    def highlightCurrentPosition(self):
        # TODO: Подсветить текущую позицию в self.codeEditor
        pass

    def updateDebugOutput(self):
        self.tokensEditor.setPlainText(self.output_sequence)

        for token_class, table in self.lexemeFields.items():
            lexemes = self.tokens.get(token_class, {})
            table.setRowCount(len(lexemes))
            for row, (lexeme, code) in enumerate(lexemes.items()):
                table.setItem(row, 0, QTableWidgetItem(lexeme))
                table.setItem(row, 1, QTableWidgetItem(code))

    def stopDebug(self):
        self.debugButton.setEnabled(True)
        self.runButton.setEnabled(True)
        self.nextButton.setEnabled(False)
        self.stopButton.setEnabled(False)

    def clearFields(self):
        self.codeEditor.clear()
        self.tokensEditor.clear()
        for table in self.lexemeFields.values():
            table.clearContents()
            table.setRowCount(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = PHPAnalyzerGUI()
    gui.show()
    sys.exit(app.exec())