import sys
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt6 import uic


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle('Просмотр информации о сортах кофе')
        self.setFixedSize(750, 600)
        self.load_table()

    def load_table(self):
        with sqlite3.connect('coffee.sqlite') as con:
            cur = con.cursor()
            result = cur.execute('''SELECT coffee.id as ID,
                                        coffee.SortTitle as 'Сорт',
                                        roasting.title as 'Степень обжарки',
                                        types.title as 'Вид',
                                        price as 'Цена',
                                        coffee.PackingVolume as 'Обьем упаковки'
                                    FROM coffee
                                    LEFT JOIN types ON types.id=coffee.Type
                                    LEFT JOIN roasting ON roasting.id=coffee.RoastinпDegree
                                    ''').fetchall()
            title = [i[0] for i in cur.description]
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(list(result)):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    item = QTableWidgetItem(str(elem))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.tableWidget.setItem(
                        i, j, item)
            self.tableWidget.resizeColumnsToContents()

    def initUI(self):
        self.setFixedSize(750, 600)
        self.setWindowTitle('CoffeeMan v1.0')

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook  # Удалить при релизе
    ex = Example()
    ex.show()
    sys.exit(app.exec())
