import sqlite3
import threading
import multiprocessing
import requests
import logging
import csv
import random
import time
from collections import defaultdict

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QMessageBox, QInputDialog, QFileDialog, QMainWindow, QAction,
    QComboBox, QSpinBox, QTabWidget, QTextEdit, QMenu, QTableView, QSplitter,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QModelIndex, QTimer
from PyQt5.QtGui import QColor, QKeySequence


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление аккаунтами")
        self.db_file = 'accounts.db'  # Имя файла базы данных
        self.conn = None  # Соединение с базой данных
        self.settings = defaultdict(lambda: None)  # Настройки
        self.current_table = None  # Текущая таблица
        self.available_tables = []  # Список доступных таблиц

        # UI элементы
        self.create_table_button = QPushButton("Создать таблицу")
        self.load_accounts_button = QPushButton("Загрузить аккаунты")
        self.start_task_button = QPushButton("Запустить задачу")
        self.task_select = QComboBox()
        self.task_select.addItems(["Проверка валидности", "Парсинг аудитории", "Рассылка сообщений"])
        self.fill_table_button = QPushButton("Заполнить таблицу")
        self.fill_table_button.clicked.connect(self.fill_table_with_data)

        # Create Splitter
        self.splitter = QSplitter()

        # Create tabs for account tables
        self.tab_widget = QTabWidget()
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_table_context_menu)

        # Placeholder for audience table
        self.audience_table = QTableWidget()
        self.setup_parsed_audience_table(self.audience_table)

        # Add widgets to splitter
        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.audience_table)

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_table_button)
        button_layout.addWidget(self.load_accounts_button)
        button_layout.addWidget(self.task_select)
        button_layout.addWidget(self.start_task_button)
        button_layout.addWidget(self.fill_table_button)
        main_layout.addWidget(self.splitter)
        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Подключения
        self.show()
        self.create_table_button.clicked.connect(self.show_create_table_dialog)
        self.load_accounts_button.clicked.connect(self.load_accounts)
        self.start_task_button.clicked.connect(self.start_task_with_group_name)
        self.fill_table_button.clicked.connect(self.fill_table_with_data)
        self.load_tables_from_database()
        self.load_settings()

        # Инициализация account_table (важно!)
        #self.account_table = QTableWidget()
        #self.setup_account_table(self.account_table)

    def start_task_with_group_name(self):
        audience_name, ok = QInputDialog.getText(self, "Название группы", "Введите название группы:")
        if ok and audience_name:
            if not audience_name.isalnum():
                QMessageBox.warning(self, "Ошибка", "Название группы должно состоять из букв и цифр.")
                return
            task_type = self.task_select.currentText()
            self.run_task(task_type, audience_name)
        else:
            QMessageBox.warning(self, "Ошибка", "Введите название группы.")

    def send_selected_to_task_thread(self, accounts, task_type, table_name):
        """
        Отправляет выделенные аккаунты в задачу в отдельном потоке.
        """
        thread = threading.Thread(target=self.run_task, args=(accounts, task_type, table_name))
        thread.start()

    def run_task(self, task_type, audience_name):
        """
        Обработка задачи (в отдельном потоке).
        """
        self.connect_to_db()
        accounts = self.get_accounts(self.current_table)
        if task_type == "Проверка валидности":
            self.update_account_status(accounts, self.current_table)
        elif task_type == "Парсинг аудитории":
            self.parse_audience(accounts, audience_name)
        elif task_type == "Рассылка сообщений":
            self.send_messages(accounts, audience_name)
        self.update_account_table(self.current_table)

    def show_create_table_dialog(self):
        """
        Отображает диалоговое окно для создания новой таблицы.
        """
        table_name, ok = QInputDialog.getText(self, "Создание таблицы", "Введите имя таблицы:")
        if ok:
            if table_name:
                if not table_name.isalnum():
                    QMessageBox.warning(self, "Ошибка", "Имя таблицы должно состоять из букв и цифр.")
                    return
                self.create_table(table_name)
                self.create_audience_table(table_name)
                self.available_tables.append(table_name)
                self.current_table = table_name
                # self.account_table = self.create_account_table(table_name)  # Убрали создание новой таблицы
                self.tab_widget.addTab(self.account_table, table_name)
                self.tab_widget.setCurrentWidget(self.account_table)
                print(f"Таблица '{table_name}' создана.")
            else:
                QMessageBox.warning(self, "Ошибка", "Введите имя таблицы.")
        else:
            print("Создание таблицы отменено.")
    def load_accounts(self):
        """
        Загружает аккаунты из файла.
        """
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Текущая таблица не задана.")
            return

        file_path, ok = QFileDialog.getOpenFileName(self, "Загрузить аккаунты", "", "All Files (*)")
        if ok:
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            self.add_account(self.current_table, row)
                            self.update_account_table(self.current_table)
                except Exception as e:
                    print(f"Ошибка при загрузке аккаунтов: {e}")
                    QMessageBox.warning(self, "Ошибка", f"Ошибка при загрузке аккаунтов: {e}")
            else:
                print("Загрузка аккаунтов отменена.")
        else:
            print("Загрузка аккаунтов отменена.")


    def show_settings(self):
        """
        Отображает окно настроек.
        """
        self.settings_window = SettingsWindow(self.settings)
        self.settings_window.show()

    def fill_table_with_data(self):
        """
        Заполняет таблицу сгенерированными данными.
        """
        print("Кнопка 'Заполнить таблицу' нажата")
        
        current_widget = self.tab_widget.currentWidget()
        if not hasattr(current_widget, 'table_name'):
            QMessageBox.warning(self, "Ошибка", "Текущий виджет не содержит таблицы.")
            return

        self.current_table = current_widget.table_name

        if current_widget.rowCount() > 0:
            reply = QMessageBox.question(self, "Предупреждение", "Таблица уже содержит данные. Вы уверены, что хотите заполнить ее заново?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        row_count = random.randint(50, 500)
        for _ in range(row_count):
            self.add_account(self.current_table, {
                'username': f'user_{random.randint(1, 1000)}',
                'password': f'pass_{random.randint(1, 1000)}',
                'ua': f'UA_{random.randint(1, 1000)}',
                'cookie': f'cookie_{random.randint(1, 1000)}',
                'device': f'device_{random.randint(1, 1000)}'
            })
        self.update_account_table(self.current_table)


    def load_tables_from_database(self):
        """
        Загружает таблицы из базы данных.
        """
        print("Загрузка таблиц из базы данных")
        try:
            self.connect_to_db()
            c = self.conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in c.fetchall() if row[0] != 'sqlite_sequence']
            for table_name in tables:
                if table_name not in self.available_tables:
                    if 'audience' in table_name:
                        self.available_tables.append(table_name)
                        self.update_parsed_audience_table(table_name)
                    else:
                        self.available_tables.append(table_name)
                        # Initialize account_table if not already done
                        if not hasattr(self, 'account_table'):
                            self.account_table = QTableWidget()
                            self.setup_account_table(self.account_table)
                        self.update_account_table(table_name)
        except Exception as e:
            print(f"Ошибка при загрузке таблиц из базы данных: {e}")

    def show_table_context_menu(self, point):
        """
        Отображает контекстное меню для таблицы.
        """
        menu = QMenu(self)
        delete_action = QAction("Удалить таблицу", self)
        delete_action.triggered.connect(self.delete_table)
        menu.addAction(delete_action)
        menu.exec_(self.tab_widget.mapToGlobal(point))

    def delete_table(self):
        """
        Удаляет таблицу из базы данных и интерфейса.
        """
        current_index = self.tab_widget.currentIndex()
        table_name = self.tab_widget.tabText(current_index)

        reply = QMessageBox.question(self, "Удаление таблицы", f"Вы уверены, что хотите удалить таблицу '{table_name}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_table_from_db(table_name)
            self.tab_widget.removeTab(current_index)
            self.available_tables.remove(table_name)
            self.current_table = None
            print(f"Таблица '{table_name}' удалена.")
        else:
            print(f"Удаление таблицы '{table_name}' отменено.")

    def load_settings(self):
        """
        Загружает настройки из файла (реализуйте свою логику загрузки).
        """
        try:
            with open('settings.txt', 'r') as f:
                for line in f:
                    key, value = line.strip().split("=", 1)
                    self.settings[key] = value
            print("Настройки загружены.")
        except FileNotFoundError:
            print("Файл настроек не найден. Используются стандартные настройки.")

    def save_settings(self):
        """
        Сохраняет настройки в файл (реализуйте свою логику сохранения).
        """
        try:
            with open('settings.txt', 'w') as f:
                for key, value in self.settings.items():
                    f.write(f"{key}={value}\n")
            print("Настройки сохранены.")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")

    # Database functions

    def connect_to_db(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            print("Database connection successful.")
        except sqlite3.Error as e:
            self.conn = None
            print(f"Database connection error: {e}")
    def create_table(self, table_name: str):
        """
        Создает таблицу в базе данных.
        """
        try:
            c = self.conn.cursor()
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    ua TEXT,
                    cookie TEXT,
                    device TEXT,
                    status_account TEXT,
                    messages_total INTEGER,
                    messages_day INTEGER,
                    messages_run INTEGER,
                    color TEXT
                )
            """)
            self.conn.commit()
            print(f"Таблица '{table_name}' создана.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы: {e}")

    def create_audience_table(self, table_name: str) -> None:

        try:
            c = self.conn.cursor()
            table_name = f"audience_{table_name}"
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audience_name TEXT NOT NULL,
                    total_audience_count INTEGER NOT NULL,
                    processed_audience_count INTEGER NOT NULL,
                    audience_date TEXT NOT NULL
                )
            """)
            self.conn.commit()
            print(f"Table '{table_name}' created.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_account(self, table_name: str, account: dict):
        try:
            c = self.conn.cursor()
            c.execute(f"""
                INSERT INTO '{table_name}' (username, password, ua, cookie, device, status_account, messages_total, messages_day, messages_run, color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (account['username'], account['password'], account.get('ua', ''), account.get('cookie', ''), account.get('device', ''), 'Не проверено', 0, 0, 0, ''))
            self.conn.commit()
            print(f"Аккаунт '{account['username']}' добавлен в таблицу '{table_name}'.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении аккаунта: {e}")

    def get_accounts(self, table_name: str):
        try:
            c = self.conn.cursor()
            c.execute(f"SELECT * FROM '{table_name}'")
            rows = c.fetchall()
            accounts = [dict(zip([column[0] for column in c.description], row)) for row in rows]
            print(f"Список аккаунтов из таблицы '{table_name}' получен.")
            return accounts
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка аккаунтов: {e}")
            return []

    def update_account_status(self, accounts: list, table_name: str):
        try:
            for account in accounts:
                c = self.conn.cursor()
                # Проверка занятости аккаунта
                if account['status_account'] == 'В процессе':
                    print(f"Аккаунт '{account['username']}' уже выполняет задачу.")
                    continue

                status = 'Валидный' if random.randint(1, 2) == 1 else 'Невалидный'
                color = 'lightgreen' if status == 'Валидный' else 'lightcoral'

                c.execute(f"UPDATE '{table_name}' SET status_account = ?, color = ? WHERE id = ?", (status, color, account['id']))
                self.conn.commit()
                print(f"Статус аккаунта '{account['username']}' обновлен в таблице '{table_name}'.")
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении статуса аккаунта: {e}")

    def delete_table_from_db(self, table_name: str):
        """
        Удаляет таблицу из базы данных.
        """
        try:
            c = self.conn.cursor()
            c.execute(f"DROP TABLE '{table_name}'")
            self.conn.commit()
            print(f"Таблица '{table_name}' удалена.")
        except sqlite3.Error as e:
            print(f"Ошибка при удалении таблицы: {e}")

    def add_audience_id(self, audience_id):
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO parsed_audience (audience_id) VALUES (?)", (audience_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding audience ID: {e}")

    def get_unused_audience_ids(self):
        try:
            c = self.conn.cursor()
            c.execute("SELECT audience_id FROM parsed_audience WHERE used = 0")
            return [row[0] for row in c.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving audience IDs: {e}")
            return []

    def mark_audience_id_as_used(self, audience_id):
        try:
            c = self.conn.cursor()
            c.execute("UPDATE parsed_audience SET used = 1 WHERE audience_id = ?", (audience_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error marking audience ID as used: {e}")

    # UI functions

    def setup_parsed_audience_table(self, table):
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Название аудитории", "Кол-во аудитории всего", "Кол-во пройденной аудитории", "Дата аудитории"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

    def setup_account_table(self, table):
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels(["Имя пользователя", "Пароль", "UA", "Cookie", "Device", "Статус", "Сообщ. всего", "Сообщ. день", "Сообщ. запуск", " "])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

    def update_account_messages(self, table_name, account_id, messages_run):
        try:
            c = self.conn.cursor()
            c.execute(f"""
                UPDATE '{table_name}'
                SET messages_run = messages_run + ?,
                    messages_total = messages_total + ?
                WHERE id = ?
            """, (messages_run, messages_run, account_id))
            self.conn.commit()
            print(f"Счетчик сообщений для аккаунта '{account_id}' обновлен.")
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении счетчика сообщений: {e}")


    def update_account_table(self, table_name):
        try:
            accounts = self.get_accounts(table_name)
            self.account_table.setRowCount(0)  # Очистка таблицы
            for account in accounts:
                row_position = self.account_table.rowCount()
                self.account_table.insertRow(row_position)
                self.account_table.setItem(row_position, 0, QTableWidgetItem(account['username']))
                self.account_table.setItem(row_position, 1, QTableWidgetItem(account['password']))
                self.account_table.setItem(row_position, 2, QTableWidgetItem(account['ua']))
                self.account_table.setItem(row_position, 3, QTableWidgetItem(account['cookie']))
                self.account_table.setItem(row_position, 4, QTableWidgetItem(account['device']))
                self.account_table.setItem(row_position, 5, QTableWidgetItem(account['status_account']))
                self.account_table.setItem(row_position, 6, QTableWidgetItem(str(account['messages_total'])))
                self.account_table.setItem(row_position, 7, QTableWidgetItem(str(account['messages_day'])))
                self.account_table.setItem(row_position, 8, QTableWidgetItem(str(account['messages_run'])))
                self.account_table.setItem(row_position, 9, QTableWidgetItem(account['color']))
            self.account_table.repaint()
        except Exception as e:
            print(f"Ошибка при обновлении таблицы аккаунтов: {e}")

    def update_parsed_audience_table(self, table_name):
        try:
            # Получить данные аудитории из базы данных
            c = self.conn.cursor()
            c.execute(f"SELECT * FROM '{table_name}'")
            rows = c.fetchall()
            
            self.audience_table.setRowCount(0)  # Очистка таблицы
            for row in rows:
                row_position = self.audience_table.rowCount()
                self.audience_table.insertRow(row_position)
                self.audience_table.setItem(row_position, 0, QTableWidgetItem(row['audience_name']))
                self.audience_table.setItem(row_position, 1, QTableWidgetItem(str(row['total_audience_count'])))
                self.audience_table.setItem(row_position, 2, QTableWidgetItem(str(row['processed_audience_count'])))
                self.audience_table.setItem(row_position, 3, QTableWidgetItem(row['audience_date']))
            self.audience_table.repaint()
        except Exception as e:
            print(f"Ошибка при обновлении таблицы аудитории: {e}")



    # Task functions

    def parse_audience(self, accounts, audience_name):
        for _ in range(len(accounts)):
            audience_id = random.randint(10000, 100000)
            self.add_audience_id(audience_id)
            time.sleep(0.01)

    def send_messages(self, accounts, audience_name):
        for account in accounts:
            unused_audience_ids = self.get_unused_audience_ids()
            if unused_audience_ids:
                audience_id = random.choice(unused_audience_ids)
                self.mark_audience_id_as_used(audience_id)
                self.update_account_messages(self.current_table, account['id'], 1)
                time.sleep(0.01)


def ensure_parsed_audience_table_exists(db_file: str):
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        # Check if table exists
        c.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name='parsed_audience';
        """)

        if c.fetchone() is None:
            # Create table if it does not exist
            c.execute("""
                CREATE TABLE parsed_audience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audience_id INTEGER NOT NULL,
                    used INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            print("Table 'parsed_audience' created.")
        else:
            print("Table 'parsed_audience' already exists.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    ensure_parsed_audience_table_exists('accounts.db')
    app = QApplication([])
    main_window = MainWindow()
    app.exec_()
