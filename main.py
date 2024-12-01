import sys
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QDialog, QMessageBox
from PyQt6 import uic


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle('Просмотр информации о сортах кофе')
        self.setFixedSize(750, 600)
        self.item_active = list()
        self.loadtable()
        self.button_create.clicked.connect(self.create_data_coffee)
        self.button_edit.clicked.connect(self.edit_data_coffee)

    def loadtable(self, mode=None):
        if mode == '+disconnect':
            self.tableWidget.disconnect()
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
                                    LEFT JOIN roasting ON roasting.id=coffee.RoastingDegree
                                    ''').fetchall()
            title = [i[0] for i in cur.description]
            self.tableWidget.setColumnCount(len(title) + 1)
            self.tableWidget.setHorizontalHeaderLabels([''] + title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(list(result)):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                item = QTableWidgetItem('')
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.tableWidget.setItem(i, 0, item)
                self.tableWidget.setItem(i, 1, QTableWidgetItem(row[0]))
                if str(row[0]) in self.item_active:
                    item.setCheckState(Qt.CheckState.Checked)
                for j, elem in enumerate(row, 1):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.cellChanged.connect(self.slot_active_inactive)

    def slot_active_inactive(self, row):
        if self.tableWidget.item(row, 0).checkState() != Qt.CheckState.Checked:
            self.item_active.remove(self.tableWidget.item(row, 1).text())
        else:
            self.item_active.append(self.tableWidget.item(row, 1).text())

    def edit_data_coffee(self):
        if not self.item_active:
            QMessageBox.warning(self, 'Ошибка', 'Сорт кофе для редактирования не выбран.')
        elif len(self.item_active) > 1:
            QMessageBox.warning(self, 'Ошибка', 'Выберите один сорт кофе для редактирования.')
        else:
            self.add_edit_form = AddEditForm(self, 'edit')
            self.add_edit_form.show()

    def create_data_coffee(self):
        self.add_edit_form = AddEditForm(self)
        self.add_edit_form.show()

    def initUI(self):
        self.setFixedSize(750, 600)
        self.setWindowTitle('CoffeeMan v1.0')


class AddEditForm(QDialog):
    def __init__(self, parent=None, mode=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.parent_link = parent
        self.mode = mode

        with sqlite3.connect('coffee.sqlite') as con:
            cur = con.cursor()
            roasting = cur.execute('''SELECT * FROM roasting ORDER BY id''').fetchall()
            self.rstg = dict()
            for i in roasting:
                self.rstg[i[1]] = i[0]
                self.combo_roasting.addItem(i[1])
            self.tps = dict()
            types = cur.execute('''SELECT * FROM types ORDER BY id''').fetchall()
            for type in types:
                self.tps[type[1]] = type[0]
                self.combo_types.addItem(type[1])
            self.spin_price.setMaximum(100000)
            self.spin_volume.setMaximum(100000)
            if self.mode == 'edit':
                result = cur.execute('''SELECT coffee.id as ID,
                                                            coffee.SortTitle as 'Сорт',
                                                            roasting.title as 'Степень обжарки',
                                                            types.title as 'Вид',
                                                            price as 'Цена',
                                                            coffee.PackingVolume as 'Обьем упаковки'
                                                        FROM coffee
                                                        LEFT JOIN types ON types.id=coffee.Type
                                                        LEFT JOIN roasting ON roasting.id=coffee.RoastingDegree
                                                        WHERE coffee.id=?
                                                        ''', tuple(self.parent_link.item_active)).fetchone()
                self.line_sort.setText(result[1])
                self.combo_roasting.setCurrentText(result[2])
                self.combo_types.setCurrentText(result[3])
                self.spin_price.setValue(result[4])
                self.spin_volume.setValue(result[5])

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

    def accept(self):
        if self.line_sort.text():
            data = (self.line_sort.text(), self.rstg[self.combo_roasting.currentText()],
                    self.tps[self.combo_types.currentText()],
                    self.spin_price.value(), self.spin_volume.value())
            with sqlite3.connect('coffee.sqlite') as con:
                cur = con.cursor()
                if self.mode is None:
                    cur.execute('''INSERT INTO coffee(sorttitle, roastingdegree, type, price, packingvolume) 
                    VALUES(?, ?, ?, ?, ?)''', data)
                elif self.mode == 'edit':
                    cur.execute('''UPDATE coffee
                                    SET sorttitle=?, roastingdegree=?, type=?, price=?, packingvolume=?
                                    WHERE id=?''', data + (self.parent_link.item_active[0],))
            self.parent_link.loadtable('+disconnect')
            super().accept()
        else:
            self.label_error.setText('Данные некорректны')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook  # Удалить при релизе
    ex = Example()
    ex.show()
    sys.exit(app.exec())
