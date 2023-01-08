import sys
import threading

import PyQt5
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRunnable, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import QWidget, QLabel, QStackedWidget, QScrollArea, QVBoxLayout, QFrame, QSizePolicy, QComboBox, \
    QLineEdit, QPushButton, QDateEdit, QApplication
from playsound import playsound
import resources

pg.setConfigOptions(antialias=True)

from config import Sounds, Colors
from speech import speech_to_text, text_to_speech

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class SoundWorker(QRunnable):
    def __init__(self, sound_path):
        super().__init__()
        self.sound_path = sound_path

    @pyqtSlot()
    def run(self):
        playsound(self.sound_path)


class TransactionWidget(QFrame):
    def __init__(self, arrow, date, description, amount):
        super().__init__()
        self.amount_value = 0
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(0, 40))
        self.setStyleSheet(f"background-color:{Colors.TRANSACTION_WIDGET_BACKGROUND};")

        self.description = QLabel(description, self)
        self.description.setGeometry(QtCore.QRect(185, 10, 130, 20))
        self.description.setStyleSheet(f"font-size:12px;color: {Colors.TRANSACTION_WIDGET_LABELS};")
        self.description.setAlignment(QtCore.Qt.AlignCenter)

        self.amount = QLabel(amount + '$', self)
        self.amount.setGeometry(QtCore.QRect(330, 10, 50, 20))
        self.amount.setStyleSheet(f"font-size:12px;color: {Colors.TRANSACTION_WIDGET_LABELS};")
        self.amount.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.date = QLabel(date, self)
        self.date.setGeometry(QtCore.QRect(60, 10, 100, 20))
        self.date.setStyleSheet(f"font-size:12px;color: {Colors.TRANSACTION_WIDGET_LABELS};")
        self.date.setAlignment(QtCore.Qt.AlignCenter)

        self.arrow = QLabel(arrow, self)
        self.arrow.setGeometry(QtCore.QRect(10, 10, 30, 20))
        if arrow == "▲":
            self.amount_value = int(amount)
            self.arrow.setStyleSheet(f"font-size:20px;color:{Colors.TRANSACTION_WIDGET_INCOME};")
        else:
            self.amount_value = -int(amount)
            self.arrow.setStyleSheet(f"font-size:20px;color:{Colors.TRANSACTION_WIDGET_EXPENSE};")

        self.arrow.setAlignment(QtCore.Qt.AlignCenter)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.transaction_amounts = []
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)
        self.mainLabel = QLabel(self)
        self.mainLabel.setGeometry(0, 0, 600, 400)
        self.mainLabel.setPixmap(QtGui.QPixmap(":/icons/background.png"))
        self.mainLabel.setScaledContents(True)
        self.operationsWidget = QWidget(self)
        self.operationsWidget.setGeometry(30, 60, 450, 310)
        self.operationsWidget.setStyleSheet(f"background-color:{Colors.OPERATIONS_WIDGET_COLOR} ;")
        self.stackedWidget = QStackedWidget(self.operationsWidget)

        self.stackedWidget.setGeometry(0, 0, 450, 310)

        self.overviewPage = QWidget()
        self.budgetOverviewTitle = QLabel("Budget Overview", self.overviewPage)
        self.budgetOverviewTitle.setGeometry(180, 10, 130, 20)
        self.budgetOverviewTitle.setStyleSheet(f"font-size:16px;color: {Colors.TITLE_COLOR};")
        self.graphWidget = QWidget(self.overviewPage)
        self.graphVerticalLayout = QVBoxLayout(self.graphWidget)
        self.graphWidget.setGeometry(10, 40, 430, 260)
        self.graph = pg.PlotWidget(self.graphWidget)
        self.graph.setBackground('#000033')
        self.graphVerticalLayout.addWidget(self.graph)

        self.stackedWidget.addWidget(self.overviewPage)

        self.transactionsPage = QWidget()
        self.scrollArea = QScrollArea(self.transactionsPage)
        self.scrollArea.setGeometry(20, 50, 410, 250)
        self.scrollArea.setStyleSheet("QScrollBar:vertical\n"
                                      "    {\n"
                                      "       background-color: rgb(101, 116, 197);\n"
                                      "        width: 15px;\n"
                                      "        margin: 0px 0px 0px 3px;\n"
                                      "        \n"
                                      "    }\n"
                                      "\n"
                                      "    QScrollBar::handle:vertical\n"
                                      "    {\n"
                                      "        background-color: rgb(36, 52, 142); \n"
                                      "    }\n"
                                      "\n"
                                      "    QScrollBar::sub-line:vertical\n"
                                      "    {\n"
                                      "        margin: 3px 0px 3px 0px;\n"
                                      "        border-image: url(:/qss_icons/rc/up_arrow_disabled.png);\n"
                                      "        height: 10px;\n"
                                      "        width: 10px;\n"
                                      "        subcontrol-position: top;\n"
                                      "        subcontrol-origin: margin;\n"
                                      "    }\n"
                                      "QScrollBar::add-line:vertical\n"
                                      "    {\n"
                                      "        margin: 3px 0px 3px 0px;\n"
                                      "        border-image: url(:/qss_icons/rc/down_arrow_disabled.png);\n"
                                      "        height: 10px;\n"
                                      "        width: 10px;\n"
                                      "        subcontrol-position: bottom;\n"
                                      "        subcontrol-origin: margin;\n"
                                      "    }\n"
                                      "\n"
                                      "    QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on\n"
                                      "    {\n"
                                      "        border-image: url(:/qss_icons/rc/up_arrow.png);\n"
                                      "        height: 10px;\n"
                                      "        width: 10px;\n"
                                      "        subcontrol-position: top;\n"
                                      "        subcontrol-origin: margin;\n"
                                      "    }\n"
                                      "\n"
                                      "    QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on\n"
                                      "    {\n"
                                      "        border-image: url(:/qss_icons/rc/down_arrow.png);\n"
                                      "        height: 10px;\n"
                                      "        width: 10px;\n"
                                      "        subcontrol-position: bottom;\n"
                                      "        subcontrol-origin: margin;\n"
                                      "    }\n"
                                      "\n"
                                      "    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical\n"
                                      "    {\n"
                                      "        background: none;\n"
                                      "    }\n"
                                      "\n"
                                      "    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical\n"
                                      "    {\n"
                                      "        background: none;\n"
                                      "    }")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(0, 0, 410, 250)
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)

        transactions = [TransactionWidget("▲", "12/02/2019", "Salary", "4000"),
                        TransactionWidget("▼", "12/03/2019", "Home tax", "200"),
                        TransactionWidget("▼", "12/04/2019", "Shopping", "300"),
                        TransactionWidget("▲", "12/05/2019", "Bonus", "2000"),
                        TransactionWidget("▼", "12/06/2019", "Home tax", "500"),
                        TransactionWidget("▼", "12/07/2019", "Toys", "201"),
                        TransactionWidget("▼", "12/08/2019", "Food", "400"),
                        TransactionWidget("▼", "12/09/2019", "Film tickets", "50")]
        for transaction in transactions:
            self.transaction_amounts.append(transaction.amount_value)
            self.verticalLayout.addWidget(transaction)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.transactionTitle = QLabel("Transactions", self.transactionsPage)
        self.transactionTitle.setGeometry(QtCore.QRect(180, 10, 120, 20))
        self.transactionTitle.setStyleSheet(f"font-size:16px;color: {Colors.TITLE_COLOR};")
        self.stackedWidget.addWidget(self.transactionsPage)

        self.addPage = QWidget()
        self.newTransactionTitle = QLabel("New Transaction", self.addPage)
        self.newTransactionTitle.setGeometry(QtCore.QRect(170, 10, 130, 20))
        self.newTransactionTitle.setStyleSheet(f"font-size:16px;color: {Colors.TITLE_COLOR};")

        self.typeLabel = QLabel("Transaction Type:", self.addPage)
        self.typeLabel.setGeometry(QtCore.QRect(90, 70, 100, 20))
        self.typeLabel.setStyleSheet(f"font-size:12px;color: {Colors.TITLE_COLOR};")
        self.typeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.typeComboBox = QComboBox(self.addPage)
        self.typeComboBox.setGeometry(QtCore.QRect(230, 70, 100, 20))
        self.typeComboBox.setStyleSheet("font-size:12px;\n"
                                        f"border: 1px solid {Colors.SPECIAL_COLOR};\n"
                                        f"color: {Colors.SPECIAL_COLOR};\n"
                                        "")
        self.typeComboBox.addItems(["Income", "Expense"])

        self.amountEdit = QLineEdit(self.addPage)
        self.amountEdit.setGeometry(QtCore.QRect(230, 190, 60, 20))
        self.amountEdit.setStyleSheet(f"border: 1px solid {Colors.SPECIAL_COLOR};\n"
                                      f"color: {Colors.SPECIAL_COLOR};\n"
                                      "font-size:12px;\n"
                                      "")

        self.listenBtn = QPushButton(self.addPage)
        self.listenBtn.setGeometry(QtCore.QRect(180, 240, 40, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/listen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.listenBtn.setIcon(icon)
        self.listenBtn.setIconSize(QtCore.QSize(40, 30))

        self.descriptionEdit = QLineEdit(self.addPage)
        self.descriptionEdit.setGeometry(QtCore.QRect(230, 150, 180, 20))
        self.descriptionEdit.setStyleSheet(f"border: 1px solid {Colors.SPECIAL_COLOR};\n"
                                           f"color: {Colors.SPECIAL_COLOR};\n"
                                           "font-size:12px;")

        self.dateEdit = QDateEdit(self.addPage)
        self.dateEdit.setGeometry(QtCore.QRect(230, 110, 100, 20))
        self.dateEdit.setStyleSheet("font-size:12px;\n"
                                    f"border: 1px solid {Colors.SPECIAL_COLOR};\n"
                                    f"color: {Colors.SPECIAL_COLOR}")

        self.descriptionLabel = QLabel("Description:", self.addPage)
        self.descriptionLabel.setGeometry(QtCore.QRect(90, 150, 100, 20))
        self.descriptionLabel.setStyleSheet("font-size:12px;\n"
                                            f"color: {Colors.TITLE_COLOR};")
        self.descriptionLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.addTransactionBtn = QPushButton(self.addPage)
        self.addTransactionBtn.setGeometry(QtCore.QRect(230, 240, 40, 40))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/add_btn.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addTransactionBtn.setIcon(icon1)
        self.addTransactionBtn.setIconSize(QtCore.QSize(30, 35))

        self.dateLabel = QLabel("Date:", self.addPage)
        self.dateLabel.setGeometry(QtCore.QRect(90, 110, 100, 20))
        self.dateLabel.setStyleSheet("font-size:12px;\n"
                                     f"color: {Colors.TITLE_COLOR};")
        self.dateLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.amountLabel2 = QLabel("Amount:", self.addPage)
        self.amountLabel2.setGeometry(QtCore.QRect(90, 190, 100, 20))
        self.amountLabel2.setStyleSheet("font-size:12px;\n"
                                        f"color: {Colors.TITLE_COLOR};")
        self.amountLabel2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.stackedWidget.addWidget(self.addPage)

        self.menu = QWidget(self)
        self.menu.setGeometry(QtCore.QRect(510, 60, 60, 310))
        self.menu.setStyleSheet(f"background-color:{Colors.MENU_COLOR};\n")
        self.overviewBtn = QPushButton(self.menu)
        self.overviewBtn.setGeometry(QtCore.QRect(10, 20, 40, 40))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/overview.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.overviewBtn.setIcon(icon2)
        self.overviewBtn.setIconSize(QtCore.QSize(35, 35))

        self.transactionsBtn = QPushButton(self.menu)
        self.transactionsBtn.setGeometry(QtCore.QRect(10, 75, 40, 40))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/transaction.webp"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.transactionsBtn.setIcon(icon3)
        self.transactionsBtn.setIconSize(QtCore.QSize(35, 35))

        self.addBtn = QPushButton(self.menu)
        self.addBtn.setGeometry(QtCore.QRect(10, 130, 40, 40))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addBtn.setIcon(icon4)
        self.addBtn.setIconSize(QtCore.QSize(35, 35))

        self.speakBtn = QPushButton(self.menu)
        self.speakBtn.setGeometry(QtCore.QRect(10, 190, 40, 40))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/speak.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.speakBtn.setIcon(icon5)
        self.speakBtn.setIconSize(QtCore.QSize(35, 35))

        self.exitBtn = QPushButton(self.menu)
        self.exitBtn.setGeometry(QtCore.QRect(10, 250, 40, 40))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.exitBtn.setIcon(icon6)
        self.exitBtn.setIconSize(QtCore.QSize(35, 35))

        self.currentBalanceLabel = QLabel(self)
        self.currentBalanceLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.currentBalanceLabel.setGeometry(QtCore.QRect(250, 20, 230, 30))
        self.currentBalanceLabel.setStyleSheet(f"color:{Colors.INFO_COLOR};\n"
                                               "font-size:16px;")

        self.welcomeLabel = QLabel("Welcome back!", self)
        self.welcomeLabel.setGeometry(QtCore.QRect(30, 20, 220, 30))
        self.welcomeLabel.setStyleSheet(f"color:{Colors.INFO_COLOR};\n"
                                        "font-size:16px;")

        self.stackedWidget.setCurrentIndex(0)
        self.handle_btns()
        self.plot()
        self.calculate_and_display_total_amount()
        self.threadpool = QThreadPool()
        worker = SoundWorker(Sounds.START_SOUND)
        self.threadpool.start(worker)

    def calculate_and_display_total_amount(self):
        total_amount = sum(self.transaction_amounts)
        self.currentBalanceLabel.setText(f"Current balance: {total_amount}$")

    def handle_btns(self):
        self.overviewBtn.clicked.connect(self.overview_btn_clicked)
        self.transactionsBtn.clicked.connect(self.transactions_btn_clicked)
        self.addBtn.clicked.connect(self.add_btn_clicked)
        self.exitBtn.clicked.connect(self.exit_btn_clicked)
        self.listenBtn.clicked.connect(self.listen_btn_clicked)
        self.addTransactionBtn.clicked.connect(self.add_new_transaction)
        self.speakBtn.clicked.connect(self.speak_btn_clicked)

    def overview_btn_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
        worker = SoundWorker(Sounds.SELECT_OPTION_SOUND)
        self.threadpool.start(worker)

    def transactions_btn_clicked(self):
        self.stackedWidget.setCurrentIndex(1)
        worker = SoundWorker(Sounds.SELECT_OPTION_SOUND)
        self.threadpool.start(worker)

    def add_btn_clicked(self):
        self.stackedWidget.setCurrentIndex(2)
        worker = SoundWorker(Sounds.SELECT_OPTION_SOUND)
        self.threadpool.start(worker)

    def exit_btn_clicked(self):
        worker = SoundWorker(Sounds.EXIT_SOUND)
        self.threadpool.start(worker)
        sys.exit()

    def speak_btn_clicked(self):
        response = speech_to_text().lower()
        if response == 'exit':
            sys.exit()
        elif response == 'overview' or response == "0":
            self.stackedWidget.setCurrentIndex(0)
        elif response == 'transaction' or response == "1":
            self.stackedWidget.setCurrentIndex(1)
        elif response == "add page" or response == "2":
            self.stackedWidget.setCurrentIndex(2)

    def add_new_transaction(self):
        arrow = "▲" if self.typeComboBox.currentText() == 'Income' else "▼"
        date = self.dateEdit.text()
        description = self.descriptionEdit.text()
        amount = self.amountEdit.text()
        if description != '' and amount != '' and amount.isdigit():
            transaction = TransactionWidget(arrow, date, description, amount)
            self.verticalLayout.addWidget(transaction)
            self.transaction_amounts.append(transaction.amount_value)
            self.calculate_and_display_total_amount()
            self.plot()
            worker = SoundWorker(Sounds.ADD_TRANSFER_SOUND)
            self.threadpool.start(worker)
        elif not amount.isdigit():
            text_to_speech("Please enter a valid amount!")
        else:
            text_to_speech("Please complete all required fields!")
        self.amountEdit.setText('')
        self.descriptionEdit.setText('')

    def listen_btn_clicked(self):
        type = self.typeComboBox.currentText()
        date = self.dateEdit.text()
        description = self.descriptionEdit.text()
        amount = self.amountEdit.text()
        text_to_speech(
            f"Transaction type: {type}\nDate: {date} \nDescription: {'No desription yet' if description == '' else description}\n Amount:{'No amount yet' if amount == '' else amount}")

    def plot(self):
        pen = pg.mkPen(color=(204, 217, 255), width=3)
        budgets = list(np.cumsum(self.transaction_amounts))
        self.graph.plot(range(len(budgets)), budgets, pen=pen, symbol='o', symbolSize=10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
