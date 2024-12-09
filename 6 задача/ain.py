import sys
import sqlite3
from PyQt5 import QtWidgets, uic


class CoffeeDatabase:
    def __init__(self, db_file='inventory.db'):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Coffee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            year INTEGER NOT NULL
        )
        ''')
        self.conn.commit()

    def add_coffee(self, name, coffee_type, year):
        self.cursor.execute('INSERT INTO Coffee (name, type, year) VALUES (?, ?, ?)', (name, coffee_type, year))
        self.conn.commit()

    def update_coffee(self, coffee_id, name, coffee_type, year):
        self.cursor.execute('UPDATE Coffee SET name = ?, type = ?, year = ? WHERE id = ?', (name, coffee_type, year, coffee_id))
        self.conn.commit()

    def get_all_coffee(self):
        self.cursor.execute('SELECT * FROM Coffee')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


class AddEditCoffeeForm(QtWidgets.QDialog):
    def __init__(self, db, coffee_id=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.db = db
        self.coffee_id = coffee_id

        if coffee_id:
            self.load_coffee(coffee_id)

        self.saveButton.clicked.connect(self.save)

    def load_coffee(self, coffee_id):
        cursor = self.db.cursor
        cursor.execute('SELECT name, type, year FROM Coffee WHERE id = ?', (coffee_id,))
        coffee = cursor.fetchone()
        if coffee:
            self.nameLineEdit.setText(coffee[1])
            self.typeLineEdit.setText(coffee[2])
            self.yearSpinBox.setValue(coffee[3])

    def save(self):
        name = self.nameLineEdit.text()
        coffee_type = self.typeLineEdit.text()
        year = self.yearSpinBox.value()

        if self.coffee_id:
            self.db.update_coffee(self.coffee_id, name, coffee_type, year)
        else:
            self.db.add_coffee(name, coffee_type, year)

        self.accept()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mainWindow.ui', self)

        self.db = CoffeeDatabase()
        self.load_coffee_list()

        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)

    def load_coffee_list(self):
        self.coffeeTable.setRowCount(0)  # Очистка таблицы
        for coffee in self.db.get_all_coffee():
            row_position = self.coffeeTable.rowCount()
            self.coffeeTable.insertRow(row_position)
            for column, value in enumerate(coffee[1:]):  # Пропускаем ID
                self.coffeeTable.setItem(row_position, column, QtWidgets.QTableWidgetItem(str(value)))

    def add_coffee(self):
        form = AddEditCoffeeForm(self.db)
        if form.exec_() == QtWidgets.QDialog.Accepted:
            self.load_coffee_list()

    def edit_coffee(self):
        selected_row = self.coffeeTable.currentRow()
        if selected_row >= 0:
            coffee_id = self.db.get_all_coffee()[selected_row][0]  # Получаем ID выбранного кофе
            form = AddEditCoffeeForm(self.db, coffee_id)
            if form.exec_() == QtWidgets.QDialog.Accepted:
                self.load_coffee_list()

        def main():
            app = QtWidgets.QApplication(sys.argv)
            window = MainWindow()
            window.show()
            sys.exit(app.exec_())

        if __name__ == '__main__':
            main()
