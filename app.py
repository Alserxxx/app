import sys
import random
from random import randint
import sqlite3
import multiprocessing
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QComboBox, QTableWidget, QTabWidget, 
    QVBoxLayout, QWidget, QSplitter, QTableWidgetItem, QHeaderView, QMenu, QAction,
    QFileDialog, QInputDialog
)
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import concurrent.futures
def check_validity_task(login_list, row_list, table_name, db_filename, result_queue, status_queue):
    def check_validity_thread(login, row):
        # Симуляция проверки валидности
        time.sleep(random.uniform(1, 5))
        valid_status = random.choice(["Валид", "Невалид"])

        # Обновление базы данных
        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()
        query = f"UPDATE {table_name} SET status = ? WHERE login = ?"
        cursor.execute(query, (valid_status, login))
        conn.commit()
        cursor.close()
        conn.close()

        result_queue.put((login, valid_status, row))
        status_queue.put((row, valid_status))
        print(f"Account {login} status updated to {valid_status}")

    print(f"Process started for checking validity of accounts: {login_list}")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(check_validity_thread, login_list, row_list)
    print(f"Process finished for checking validity of accounts: {login_list}")
    
    
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
        self.splitter.setSizes([800, 200])  # 80% ширины - таблица аккаунтов, 20% ширины - таблица аудитории
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
                    color = Qt.green
                elif status_text == "Невалид":
                    color = Qt.red
                elif status_text == "В работе":
                    color = Qt.yellow
                elif status_text == "Завершен":
                    color = Qt.lightGray
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

        # Разделение на процессы
        process_count = min(10, (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")

        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [table.item(row, 0).text() for row in chunk]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, Qt.yellow)
                print(f"Account {table.item(row, 0).text()} status set to 'В работе'")
            p = multiprocessing.Process(target=check_validity_task, args=(login_list, row_list, table_name, self.db_filename, result_queue, status_queue))
            processes.append(p)
            p.start()

        self.monitor_validity_processes(processes, result_queue, status_queue, table, selected_rows)
        print("Проверка валидности аккаунтов запущена")

    def monitor_validity_processes(self, processes, result_queue, status_queue, table, selected_rows):
        def check_results():
            while not result_queue.empty():
                login, valid_status, row = result_queue.get()
                table.setItem(row, 4, QTableWidgetItem(valid_status))
                self.set_row_color(table, row)
            
            while not status_queue.empty():
                row, status = status_queue.get()
                table.setItem(row, 4, QTableWidgetItem(status))
                self.set_row_color(table, row, Qt.lightGray if status == "Завершен" else Qt.yellow)
                print(f"Account {table.item(row, 0).text()} status set to '{status}'")
            
            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, check_results)
                    return
            
            # Обновить статус и цвет аккаунтов после завершения всех процессов
            for row in selected_rows:
                if table.item(row, 4).text() != "Завершен":
                    table.setItem(row, 4, QTableWidgetItem("Завершен"))
                    self.set_row_color(table, row, Qt.lightGray)
                    print(f"Account {table.item(row, 0).text()} status set to 'Завершен'")
            print("Проверка валидности аккаунтов завершена")
        
        QTimer.singleShot(100, check_results) 
    
    
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
        process_count = min(10, (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")

        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [table.item(row, 0).text() for row in chunk]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, Qt.yellow)
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
                self.set_row_color(table, row, Qt.yellow)
            
            while not status_queue.empty():
                row, status = status_queue.get()
                table.setItem(row, 4, QTableWidgetItem(status))
                self.set_row_color(table, row, Qt.lightGray if status == "Завершен" else Qt.yellow)
                print(f"Account {table.item(row, 0).text()} status set to '{status}'")
            
            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, check_results)
                    return
            
            # Обновить статус и цвет аккаунтов после завершения всех процессов
            for row in selected_rows:
                if table.item(row, 4).text() != "Завершен":
                    table.setItem(row, 4, QTableWidgetItem("Завершен"))
                    self.set_row_color(table, row, Qt.lightGray)
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