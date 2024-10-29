import sys
import random
from random import randint
import sqlite3
import multiprocessing
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QComboBox, QTableWidget, QTabWidget, 
    QVBoxLayout, QWidget, QSplitter, QTableWidgetItem, QHeaderView, QMenu, QAction,
    QFileDialog, QInputDialog,QSizePolicy
)
from PyQt5.QtGui import QColor

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import concurrent.futures
import threading
from queue import Queue
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from functools import partial

class TaskMonitorWidget(QWidget):
    stop_task_signal = pyqtSignal(str)

    def __init__(self, task_name, total_accounts):
        super().__init__()
        self.task_name = task_name
        self.total_accounts = total_accounts
        self.valid_count = 0
        self.invalid_count = 0
        self.start_time = time.time()
        self.setup_ui()
        
        # Initialize and start a QTimer for updating time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

    def setup_ui(self):
        layout = QVBoxLayout()
        
        
        layout_style = """
        border: 5px solid #00796b;
        max-height: 250px;
        """
        
        
        label_style = """
        background: #F2FCFD;
        border: 1px solid #00796b;
        padding: 5px;
        color: #004d40;
        """

        button_style = """
        background: green;
        border: 1px solid;
        padding: 8px 16px;
        color: black;
        border-radius: 4px;
        """

        button_hover_style = """
        QPushButton:hover {
            background: red;
        }
        QPushButton:disabled {
            background: blue;
        }
        """

        container_widget = QWidget()
        container_widget.setLayout(layout)
        
        self.task_label = QLabel(f"Задача: {self.task_name}")
        self.status_label = QLabel("Статус: В процессе")
        self.accounts_label = QLabel(f"Всего аккаунтов: {self.total_accounts}")   
        self.valid_label = QLabel(f"Валидные: {self.valid_count}") 
        self.invalid_label = QLabel(f"Невалидные: {self.invalid_count}") 
        self.time_label = QLabel("Время: 0с")
        
        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_task)
        
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.close_task)
        self.close_button.setVisible(False)
        
        layout.addWidget(self.task_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.accounts_label)
        layout.addWidget(self.valid_label)
        layout.addWidget(self.invalid_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.close_button)
        
        
        #self.layout.setStyleSheet(layout_style)
        self.task_label.setStyleSheet(label_style)
        self.status_label.setStyleSheet(label_style)
        self.accounts_label.setStyleSheet(label_style)
        self.valid_label.setStyleSheet(label_style)
        self.invalid_label.setStyleSheet(label_style)
        self.time_label.setStyleSheet(label_style)
        self.stop_button.setStyleSheet(button_style)
        self.close_button.setStyleSheet(button_style)
        container_widget.setStyleSheet(layout_style) # Setting style for the container widget
        #layout.addStretch()  # Add stretch to prevent full height stretching
        main_layout = QVBoxLayout(self)
        container_widget.adjustSize()
        container_widget.setAlignment(Qt.AlignTop)

        container_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        #container_widget.setFixedSize(container_widget.sizeHint())

        main_layout.addWidget(container_widget)
        container_widget.adjustSize()
        #self.setLayout(layout)

    def update_time(self):
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Время: {elapsed_time}с")

    def update_status(self, valid_count, invalid_count, status):
        print(f"Before update: valid_count={self.valid_count}, invalid_count={self.invalid_count}")
        self.valid_count += valid_count  # Increment the count instead of setting it
        self.invalid_count += invalid_count  # Increment the count instead of setting it
        print(f"After update: valid_count={self.valid_count}, invalid_count={self.invalid_count}")
        self.valid_label.setText(f"Валидные: {self.valid_count}")
        self.invalid_label.setText(f"Невалидные: {self.invalid_count}")
        self.status_label.setText(f"Статус: {status}")

        if status in ["Завершен", "Остановлен"]:
            self.stop_button.setVisible(False)
            self.close_button.setVisible(True)
            self.timer.stop()

    def stop_task(self):
        self.stop_task_signal.emit(self.task_name)

    def close_task(self):
        self.close()   
        
def check_validity_thread(account_queue, result_queue, status_queue):
    while not account_queue.empty():
        login, row = account_queue.get()
        try:
            # Симуляция проверки валидности
            time.sleep(random.uniform(1, 10))
            valid_status = random.choice(["Валид", "Невалид"])

            result_queue.put((login, valid_status, row))
            status_queue.put((row, valid_status))
        except Exception as e:
            print(f"Error in thread for login {login}: {e}")
        finally:
            account_queue.task_done()

def process_function(account_list, table_name, db_filename, result_queue, status_queue):
    account_queue = Queue()
    for account in account_list:
        account_queue.put(account)

    threads = []
    for _ in range(10):  # 100 потоков
        thread = threading.Thread(target=check_validity_thread, args=(account_queue, result_queue, status_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def audience_task(login_list, row_list, table_name, group_name, db_filename, result_queue, status_queue):
    def audience_thread(login, row):
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        user_ids = [f"user_{i}" for i in range(random.randint(10, 100))]  # Рандомное кол-во пользователей для каждого аккаунта
        for user_id in user_ids:
            query = "INSERT INTO audience_users (group_name, user_id, status) VALUES (?, ?, ?)"
            cursor.execute(query, (group_name, user_id, "не пройден"))
            conn.commit()
            time.sleep(0.1)  # Пауза между каждым пользователем
            result_queue.put((group_name, 1, row, table_name))  # Отправка результата в очередь
            print(f"User {user_id} added to group {group_name} by account {login}")
        cursor.close()
        conn.close()
        status_queue.put((row, "Завершен"))  # Отправка статуса завершения

    print(f"Process started for accounts: {login_list}")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(audience_thread, login_list, row_list)
    print(f"Process finished for accounts: {login_list}")



class MainWindow(QMainWindow):
    
    
    def __init__(self):
        super().__init__()
        self.tasks = {}
        self.setWindowTitle("Управление аккаунтами")  # Заголовок окна
        self.setGeometry(100, 100, 1200, 800)  # Размеры окна
        
        self.db_filename = 'total.db'  # Имя файла базы данных
        self.conn = sqlite3.connect(self.db_filename)  # Подключение к базе данных
        self.cursor = self.conn.cursor()  # Курсор для выполнения SQL-запросов

        self.initUI()  # Инициализация интерфейса
        self.create_audience_table()  # Создание таблицы аудитории
        self.load_tables()  # Загрузка всех существующих таблиц при старте приложения
        self.load_audience_data()  # Загрузка данных таблицы аудитории

    def initUI(self):
        self.main_layout = QVBoxLayout()  # Основной компоновщик

        # Кнопка "Создать таблицу"
        self.create_table_btn = QPushButton("Создать таблицу")
        self.create_table_btn.clicked.connect(self.create_table)
        self.main_layout.addWidget(self.create_table_btn)

        # Кнопка "Загрузить аккаунты"
        self.load_accounts_btn = QPushButton("Загрузить аккаунты")
        self.load_accounts_btn.clicked.connect(self.load_accounts)
        self.main_layout.addWidget(self.load_accounts_btn)

        # Кнопка "Запустить задачу"
        self.run_task_btn = QPushButton("Запустить задачу")
        self.run_task_btn.clicked.connect(self.run_task)
        self.main_layout.addWidget(self.run_task_btn)

        # Выпадающий список для выбора задачи
        self.task_combo = QComboBox()
        self.task_combo.addItems(["Проверка валидности", "Парсинг аудитории", "Рассылка сообщений"])
        self.main_layout.addWidget(self.task_combo)

        # Кнопка "Заполнить таблицу"
        self.fill_table_btn = QPushButton("Заполнить таблицу")
        self.fill_table_btn.clicked.connect(self.fill_table)
        self.main_layout.addWidget(self.fill_table_btn)

        # QTabWidget для отображения таблиц аккаунтов
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.delete_table)
        #self.main_layout.addWidget(self.tab_widget)

        # QTableWidget для отображения таблицы аудитории
        self.audience_table = QTableWidget()
        self.audience_table.setColumnCount(4)
        self.audience_table.setHorizontalHeaderLabels(["Название группы аудитории", "Кол-во пользователей", "Кол-во пройденных пользователей", "Дата создания группы"])
        self.audience_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.audience_table.setSelectionBehavior(QTableWidget.SelectRows)  # Выделение всей строки

        # QSplitter для разделения таблиц по горизонтали
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.audience_table)

        # Общий блок статистики
        self.stats_layout = QVBoxLayout()
        self.stats_container = QWidget()
        self.stats_container.setLayout(self.stats_layout)
        self.splitter.addWidget(self.stats_container)

        # Установка размеров для QSplitter
        self.splitter.setSizes([600, 200, 400])  # 60% - таблицы аккаунтов, 20% - таблица аудитории, 20% - блок статистики

        self.main_layout.addWidget(self.splitter)

        # Виджет для основного окна
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        self.audience_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.audience_table.customContextMenuRequested.connect(self.show_audience_context_menu)

    def show_audience_context_menu(self, position):
        context_menu = QMenu()
        delete_action = QAction("Удалить группу", self)
        delete_action.triggered.connect(self.delete_audience_group)
        context_menu.addAction(delete_action)
        context_menu.exec_(self.audience_table.viewport().mapToGlobal(position))

    def delete_audience_group(self):
        selected_rows = self.audience_table.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            group_name = self.audience_table.item(index.row(), 0).text()
            
            # Удалить группу из базы данных
            try:
                conn = sqlite3.connect(self.db_filename)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM audience_users WHERE group_name=?", (group_name,))
                conn.commit()
                cursor.close()
                conn.close()
            except sqlite3.Error as e:
                print(f"Ошибка при удалении группы из базы данных: {e}")
            
            # Удалить строку из таблицы
            self.audience_table.removeRow(index.row())
            
            
            
            
    def create_audience_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS audience (
            group_name TEXT,
            user_count INTEGER,
            passed_users INTEGER,
            creation_date TEXT
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

        query = """
        CREATE TABLE IF NOT EXISTS audience_users (
            id INTEGER PRIMARY KEY,
            group_name TEXT,
            user_id TEXT,
            status TEXT
        )
        """
        self.cursor.execute(query)
        self.conn.commit()
        print("Таблицы аудитории созданы")

    def create_table(self):
        table_name, ok = QInputDialog.getText(self, "Создать таблицу", "Введите имя таблицы:")
        if ok and table_name:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} (login TEXT, password TEXT, device TEXT, cookies TEXT, status TEXT, messages_sent INTEGER)"
            self.cursor.execute(query)
            self.conn.commit()
            self.add_table_tab(table_name)
            print(f"Создана таблица {table_name}")

    def add_table_tab(self, table_name):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Логин", "Пароль", "Device", "Cookies", "Статус", "Кол-во сообщений за запуск/всего"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(lambda pos, t=table: self.table_context_menu(pos, t))
        
        # Отключить редактирование ячеек
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Включить возможность изменения ширины столбцов
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        self.tab_widget.addTab(table, table_name)
        self.load_table_data(table_name, table)
        print(f"Добавлена вкладка для таблицы {table_name}")

    def load_table_data(self, table_name, table):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            for col_num, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                table.setItem(row_num, col_num, item)
            self.set_row_color(table, row_num)
        print(f"Данные загружены в таблицу {table_name}")

    def set_row_color(self, table, row, color=None):
        if color is None:
            status_item = table.item(row, 4)
            if status_item is not None:
                status_text = status_item.text()
                if status_text == "Валид":
                    color = QColor(130,250,130)
                elif status_text == "Невалид":
                    color = QColor(250,140,140)
                elif status_text == "В работе":
                    color = QColor(250,250,140)
                elif status_text == "Завершен":
                    color = QColor(220,220,250)
                else:
                    color = None  # Не менять цвет
        if color is not None:
            for col in range(table.columnCount()):
                table.item(row, col).setBackground(color)

    def load_audience_data(self):
        query = "SELECT group_name, COUNT(user_id), SUM(CASE WHEN status = 'пройден' THEN 1 ELSE 0 END) FROM audience_users GROUP BY group_name"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.audience_table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            group_name, user_count, passed_users = row_data
            self.audience_table.setItem(row_num, 0, QTableWidgetItem(group_name))
            self.audience_table.setItem(row_num, 1, QTableWidgetItem(str(user_count)))
            self.audience_table.setItem(row_num, 2, QTableWidgetItem(str(passed_users)))
            self.audience_table.setItem(row_num, 3, QTableWidgetItem("2024-10-28"))
        print("Данные загружены в таблицу аудитории")

    def delete_table(self, index):
        table_name = self.tab_widget.tabText(index)
        menu = QMenu()
        delete_action = QAction("Удалить вкладку?", self)
        delete_action.triggered.connect(lambda: self.confirm_delete_table(index, table_name))
        menu.addAction(delete_action)
        menu.exec_(self.tab_widget.mapToGlobal(self.tab_widget.tabBar().tabRect(index).center()))

    def confirm_delete_table(self, index, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.conn.commit()
        self.tab_widget.removeTab(index)
        print(f"Таблица {table_name} удалена")

    def load_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' AND name != 'audience_users'")
        tables = self.cursor.fetchall()
        for table_name in tables:
            if table_name[0] != "audience":
                self.add_table_tab(table_name[0])
        print("Все таблицы загружены при старте приложения")

    def load_accounts(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Загрузить аккаунты", "", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            current_table = self.tab_widget.currentWidget()
            if current_table:
                table_name = self.tab_widget.tabText(self.tab_widget.indexOf(current_table))
                data_list = []
                with open(filename, 'r') as file:
                    for line in file:
                        accLine = line.strip().split("|")
                        if len(accLine) < 4:
                            continue  # Пропустить некорректные строки
                        usernamepass = accLine[0].split(":")
                        if len(usernamepass) < 2:
                            continue  # Пропустить некорректные строки
                        login = usernamepass[0].lower()
                        password = usernamepass[1]
                        device = accLine[2]
                        cookies = accLine[3]
                        data_list.append((login, password, device, cookies, "status", 0))  # Замените "status" и "0" на нужные значения, если требуется

                query = f"INSERT INTO {table_name} (login, password, device, cookies, status, messages_sent) VALUES (?, ?, ?, ?, ?, ?)"
                self.cursor.executemany(query, data_list)
                self.conn.commit()

                for data in data_list:
                    row_pos = current_table.rowCount()
                    current_table.insertRow(row_pos)
                    for col_pos, value in enumerate(data):
                        current_table.setItem(row_pos, col_pos, QTableWidgetItem(str(value)))
                    self.set_row_color(current_table, row_pos)

                print(f"Аккаунты загружены в таблицу {table_name}")

    def fill_table(self):
        num_accounts = random.randint(1, 1000)
        current_table = self.tab_widget.currentWidget()
        if current_table:
            table_name = self.tab_widget.tabText(self.tab_widget.indexOf(current_table))
            data_list = []
            for _ in range(num_accounts):
                data = [f"login{random.randint(1, num_accounts)}", "password", "device", "cookies", "status", random.randint(0, 100)]
                data_list.append(data)
            
            query = f"INSERT INTO {table_name} (login, password, device, cookies, status, messages_sent) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.executemany(query, data_list)
            self.conn.commit()

            for data in data_list:
                row_pos = current_table.rowCount()
                current_table.insertRow(row_pos)
                for col_pos, value in enumerate(data):
                    current_table.setItem(row_pos, col_pos, QTableWidgetItem(str(value)))
                self.set_row_color(current_table, row_pos)

            print(f"{num_accounts} аккаунтов добавлены в таблицу {table_name}")

    def run_task(self):
        selected_task = self.task_combo.currentText()
        current_table = self.tab_widget.currentWidget()
        if current_table:
            selected_items = current_table.selectedItems()
            if selected_items:
                if selected_task == "Проверка валидности":
                    self.check_validity(current_table, selected_items)
                elif selected_task == "Парсинг аудитории":
                    self.parse_audience(current_table, selected_items)
                elif selected_task == "Рассылка сообщений":
                    self.send_messages(current_table, selected_items)






    def check_validity(self, table, items):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        status_queue = multiprocessing.Queue()

        if total_accounts == 0:
            return
        task_name = f"Validation Check ({table_name})"
        task_widget = TaskMonitorWidget(task_name, total_accounts)
        task_widget.stop_task_signal.connect(lambda: self.stop_task(task_name))
        self.stats_layout.addWidget(task_widget)
        self.tasks[task_name] = task_widget
        task_widget.rows = selected_rows  # Associate rows with the task

        process_count = min(10, (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")

        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [table.item(row, 0).text() for row in chunk]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
            p = multiprocessing.Process(target=process_function, args=(list(zip(login_list, row_list)), table_name, self.db_filename, result_queue, status_queue))
            processes.append(p)
            p.start()

        task_widget.processes = processes  # Associate processes with the task_widget
        self.monitor_validity_processes(processes, result_queue, status_queue, table_name, table, task_name)
        print("Проверка валидности аккаунтов запущена")
    
    def stop_task(self, task_name):
        task_widget = self.tasks.get(task_name)
        if task_widget:
            task_widget.update_status(0, 0, "Остановлен")
            self.terminate_validity_check(task_name)
    
    def terminate_validity_check(self, task_name):
        if task_name in self.tasks:
            task = self.tasks[task_name]
            if hasattr(task, 'processes') and task.processes:
                for process in task.processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()
                print(f"All processes for task {task_name} have been terminated.")
                
                # Update account status to 'Остановлен'
                for row in task.rows:
                    if self.tab_widget.currentWidget().item(row, 4).text() == "В работе":  # Assuming `tab_widget` is the correct reference
                        self.tab_widget.currentWidget().setItem(row, 4, QTableWidgetItem("Остановлен"))
                        self.set_row_color(self.tab_widget.currentWidget(), row, QColor(220,220,250))
                        print(f"Account {self.tab_widget.currentWidget().item(row, 0).text()} status set to 'Остановлен'")
            else:
                print(f"No processes found for task {task_name}.")
        else:
            print(f"Task {task_name} not found.")
    def monitor_validity_processes(self, processes, result_queue, status_queue, table_name, table, task_name):
        def check_results(task_name):
            conn = sqlite3.connect('total.db')
            cursor = conn.cursor()
            updates = []
            table_updates = []
            valid_count = 0
            invalid_count = 0
            processed_rows = set()  # Keep track of processed rows to avoid double counting

            while not result_queue.empty():
                login, valid_status, row = result_queue.get()
                print(f"Processing result: login={login}, valid_status={valid_status}, row={row}")

                if row in processed_rows:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updates.append((valid_status, login))
                table_updates.append((row, valid_status))
                processed_rows.add(row)  # Mark row as processed

                if valid_status == "Валид":
                    valid_count += 1
                if valid_status == "Невалид":
                    invalid_count += 1

                print(f"Valid count: {valid_count}, Invalid count: {invalid_count}")

            if updates:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET status = ? WHERE login = ?"
                    cursor.executemany(query, updates)
                    conn.commit()
                    print(f"Database updated with {len(updates)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()
            conn.close()

            for row, valid_status in table_updates:
                table.setItem(row, 4, QTableWidgetItem(valid_status))
                self.set_row_color(table, row)
                print(f"Updated table row {row} with status {valid_status}")

            while not status_queue.empty():
                row, status = status_queue.get()
                table.setItem(row, 4, QTableWidgetItem(status))
                self.set_row_color(table, row)
                print(f"Updated status queue row {row} with status {status}")

            task_widget = self.tasks[task_name]
            task_widget.update_status(valid_count, invalid_count, "В работе")
            print(f"Task widget updated: valid_count={valid_count}, invalid_count={invalid_count}, status='В работе'")

            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, partial(check_results, task_name))
                    return

            task_widget.update_status(valid_count, invalid_count, "Завершен")
            print(f"Task widget final update: valid_count={valid_count}, invalid_count={invalid_count}, status='Завершен'")
            print("Проверка валидности аккаунтов завершена")

        QTimer.singleShot(100, partial(check_results, task_name))    
    
    def parse_audience(self, table, items):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        
        # Проверка существования таблицы
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        if not self.cursor.fetchone():
            print(f"Error: Table {table_name} not found")
            return
        
        # Запрос выбора действия у пользователя
        choice, ok = QInputDialog.getItem(self, "Выбор действия", "Выберите действие:", ["Создать новую группу", "Использовать существующую группу"], 0, False)
        if not ok:
            return
        
        if choice == "Создать новую группу":
            group_name, ok = QInputDialog.getText(self, "Создать группу", "Введите название группы:")
            if not ok or not group_name:
                return
        else:
            # Получение списка существующих групп
            query = "SELECT DISTINCT group_name FROM audience_users"
            self.cursor.execute(query)
            existing_groups = [row[0] for row in self.cursor.fetchall()]
            if not existing_groups:
                print("No existing groups found. Please create a new group.")
                return

            group_name, ok = QInputDialog.getItem(self, "Выбор группы", "Выберите существующую группу:", existing_groups, 0, False)
            if not ok or not group_name:
                return

        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        status_queue = multiprocessing.Queue()
        
        if total_accounts == 0:
            return

        # Разделение на процессы
        process_count = min(100, (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")

        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [table.item(row, 0).text() for row in chunk]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
                print(f"Account {table.item(row, 0).text()} status set to 'В работе'")
            p = multiprocessing.Process(target=audience_task, args=(login_list, row_list, table_name, group_name, self.db_filename, result_queue, status_queue))
            processes.append(p)
            p.start()
        
        self.monitor_processes(processes, result_queue, status_queue, table, selected_rows)
        print("Парсинг аудитории запущен")
    
    def monitor_processes(self, processes, result_queue, status_queue, table, selected_rows):
        def check_results():
            while not result_queue.empty():
                result = result_queue.get()
                self.update_audience_table(result, result[0])
                row = result[2]
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
            
            while not status_queue.empty():
                row, status = status_queue.get()
                table.setItem(row, 4, QTableWidgetItem(status))
                self.set_row_color(table, row, QColor(220,220,250) if status == "Завершен" else QColor(250,250,140))
                print(f"Account {table.item(row, 0).text()} status set to '{status}'")
            
            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, check_results)
                    return
            
            # Обновить статус и цвет аккаунтов после завершения всех процессов
            for row in selected_rows:
                if table.item(row, 4).text() != "Завершен":
                    table.setItem(row, 4, QTableWidgetItem("Завершен"))
                    self.set_row_color(table, row, QColor(220,220,250))
                    print(f"Account {table.item(row, 0).text()} status set to 'Завершен'")
            print("Парсинг аудитории завершен")
        
        QTimer.singleShot(100, check_results)
    
    
    def update_audience_table(self, result, group_name):
        group_name, user_count, row, table_name = result
        # Проверить, существует ли группа уже в таблице
        rows = self.audience_table.rowCount()
        group_row = -1
        for row in range(rows):
            if self.audience_table.item(row, 0).text() == group_name:
                group_row = row
                break
        
        if group_row == -1:
            # Группа не существует, добавить новую строку
            self.audience_table.insertRow(self.audience_table.rowCount())
            group_row = self.audience_table.rowCount() - 1
            self.audience_table.setItem(group_row, 0, QTableWidgetItem(group_name))
            self.audience_table.setItem(group_row, 1, QTableWidgetItem(str(user_count)))
            self.audience_table.setItem(group_row, 2, QTableWidgetItem("0"))
            self.audience_table.setItem(group_row, 3, QTableWidgetItem("2024-10-28"))
        else:
            # Обновить существующую группу
            current_count = int(self.audience_table.item(group_row, 1).text())
            new_count = current_count + user_count
            self.audience_table.setItem(group_row, 1, QTableWidgetItem(str(new_count)))
        print(f"Updated group {group_name} with {user_count} new users")
    def send_messages(self, table, items):
        selected_rows = set(item.row() for item in items)
        processes = []
        for row in selected_rows:
            status_item = table.item(row, 4)
            if status_item and status_item.text() == "В работе":
                continue  # Пропустить аккаунты, которые уже в работе
            table.setItem(row, 4, QTableWidgetItem("В работе"))
            self.set_row_color(table, row)
            login = table.item(row, 0).text()
            p = multiprocessing.Process(target=self.message_task, args=(login, row, self.tab_widget.tabText(self.tab_widget.indexOf(table))))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
        print("Рассылка сообщений выполнена")

    def message_task(self, login, row, table_name):
        time.sleep(random.randint(30, 60))  # Симуляция рассылки сообщений
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        group_name = f"Group_{login}"
        query = "UPDATE audience_users SET status = 'пройден' WHERE group_name = ?"
        cursor.execute(query, (group_name,))
        conn.commit()
        cursor.close()
        conn.close()
        current_table = self.tab_widget.findChild(QTableWidget, table_name)
        current_table.setItem(row, 4, QTableWidgetItem("Готово"))
        self.set_row_color(current_table, row)
    
    def table_context_menu(self, pos, table):
        menu = QMenu()
        delete_action = QAction("Удалить выбранные строки", self)
        delete_action.triggered.connect(lambda: self.delete_selected_rows(table))
        menu.addAction(delete_action)
        menu.exec_(table.viewport().mapToGlobal(pos))

    def delete_selected_rows(self, table):
        selected_rows = set(item.row() for item in table.selectedItems())
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table))
        
        if not selected_rows:
            return
        
        print("Собрано выделенных строк:", len(selected_rows))
        
        logins = [table.item(row, 0).text() for row in selected_rows]
        
        if not logins:
            return
        
        print("Собрано логинов:", len(logins))

        # Пакетное удаление из базы данных в одной транзакции с использованием оператора IN
        placeholders = ','.join('?' * len(logins))
        query = f"DELETE FROM {table_name} WHERE login IN ({placeholders})"
        try:
            self.conn.execute("BEGIN TRANSACTION")
            self.cursor.execute(query, logins)
            self.conn.commit()
            print("Удаление из базы данных завершено")
        except sqlite3.Error as e:
            print(f"Ошибка при удалении строк из базы данных: {e}")
            self.conn.rollback()
            return

        # Отключение сигналов обновления таблицы
        table.blockSignals(True)
        
        # Удаление строк из таблицы
        for index, row in enumerate(sorted(selected_rows, reverse=True)):
            table.removeRow(row)
            print(f"Удалена строка {index + 1} из {len(selected_rows)}")
        
        # Включение сигналов обновления таблицы
        table.blockSignals(False)
        
        print("Выбранные строки удалены")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
