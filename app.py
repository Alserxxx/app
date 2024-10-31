import sys
import random
from random import randint
import sqlite3
import multiprocessing
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QComboBox, QTableWidget, QTabWidget, 
    QVBoxLayout, QWidget, QSplitter, QTableWidgetItem, QHeaderView, QMenu, QAction,
    QFileDialog, QInputDialog,QSizePolicy,QGroupBox,QScrollArea,QMessageBox,QDialog,QLineEdit,QSpinBox,QTextEdit
)
from PyQt5.QtGui import QColor,QStandardItemModel

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import concurrent.futures
import threading
from queue import Queue
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from functools import partial
import json
class TaskMonitorWidget(QWidget):
    stop_task_signal = pyqtSignal(str)

    def __init__(self, task_name, total_accounts, task_id, table, group_name):
        super().__init__()
        self.group_name = group_name
        self.task_name = task_name
        self.total_accounts = total_accounts
        self.task_id = task_id
        self.table = table
        self.valid_count = 0
        self.invalid_count = 0
        self.processed_count = 0
        self.start_time = time.time()
        self.setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def stop_task(self):
        self.stop_task_signal.emit(self.task_id)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        label_style = """
        background: #F2FCFD;
        border: 1px solid #00796b;
        padding: 5px;
        color: #004d40;
        """
        if 'Validation Check' in self.task_name:

            self.task_label = QLabel(f"Задача: {self.task_name}")
            self.valid_label = QLabel(f"Валидные: {self.valid_count}")
            self.invalid_label = QLabel(f"Невалидные: {self.invalid_count}")
        if 'Audience' in self.task_name:
            self.task_label = QLabel(f"Задача: {self.task_name} Запись в [ {self.group_name} ]")
            self.processed_label = QLabel(f"Обработано: {self.processed_count}")

        self.status_label = QLabel("Статус: В процессе")
        self.accounts_label = QLabel(f"Всего аккаунтов: {self.total_accounts}")

        self.time_label = QLabel("Время: 0с")

        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_task)

        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.close_task)
        self.close_button.setVisible(False)

        layout.addWidget(self.task_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.accounts_label)
        
        if 'Validation Check' in self.task_name:
            layout.addWidget(self.valid_label)
            layout.addWidget(self.invalid_label)      
            self.valid_label.setStyleSheet(label_style)
            self.invalid_label.setStyleSheet(label_style)
            
        if 'Audience' in self.task_name:
            layout.addWidget(self.processed_label)
            self.processed_label.setStyleSheet(label_style)

        layout.addWidget(self.time_label)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.close_button)

        self.task_label.setStyleSheet(label_style)
        self.status_label.setStyleSheet(label_style)
        self.accounts_label.setStyleSheet(label_style)

        
        self.time_label.setStyleSheet(label_style)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        container_widget.setStyleSheet("border: 5px solid #00796b; max-height: 250px;")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container_widget)
        self.setLayout(main_layout)

    def update_time(self):
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Время: {elapsed_time}с")

    def update_status(self, valid_count, invalid_count, processed_count, status):

        
        print(self.task_name)
        if 'Validation Check' in self.task_name:
            self.valid_count += valid_count
            self.invalid_count += invalid_count
            self.valid_label.setText(f"Валидные: {self.valid_count}")
            self.invalid_label.setText(f"Невалидные: {self.invalid_count}")
        elif 'Audience Parsing' in self.task_name:
            self.processed_count += processed_count
            self.processed_label.setText(f"Обработано: {self.processed_count}")

        self.status_label.setText(f"Статус: {status}")

        if status in ["Завершен", "Остановлен"]:
            self.stop_button.setVisible(False)
            self.close_button.setVisible(True)
            self.timer.stop()

    def close_task(self):
        self.close()
        
        
        
        
def check_validity_thread(account_queue, result_queue, status_queue, proxy_group):
    while not account_queue.empty():
        login, row = account_queue.get()
        try:
            # Симуляция проверки валидности
            time.sleep(random.uniform(10, 60))
            valid_status = random.choice(["Валид", "Невалид"])

            result_queue.put((login, valid_status, row))
            status_queue.put((row, valid_status))
        except Exception as e:
            print(f"Error in thread for login {login}: {e}")
        finally:
            account_queue.task_done()

def process_function(account_list, table_name, result_queue, status_queue, proxy_group, threadsx):
    account_queue = Queue()
    for account in account_list:
        account_queue.put(account)

    threads = []
    for _ in range(threadsx):  # 100 потоков
        thread = threading.Thread(target=check_validity_thread, args=(account_queue, result_queue, status_queue, proxy_group))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def audience_thread(account_queue, result_queue, status_queue, group_name, proxy_group, listUsername_queue,limit_input):
    while not account_queue.empty():
        login, row = account_queue.get()
        
        print('limit_input: '+str(limit_input))

        
        
        if listUsername_queue.empty():
            print('Закончились Username  в списке для парсинга')
            result_queue.put((login, 'Закончил парсинг', 'Закончил парсинг', row))
            continue
            
        else:
            usernameParsing = listUsername_queue.get()
            print('usernameParsing: '+usernameParsing)
            
            
        try:
            for _ in range(5):
                time.sleep(random.uniform(1, 10))

                user_ids = [f"user_{i}" for i in range(random.randint(10, 100))]  # Рандомное кол-во пользователей для каждого аккаунта
                result_queue.put((login, group_name, user_ids, row))
                
                
            result_queue.put((login, 'Закончил парсинг', 'Закончил парсинг', row))

            
        except Exception as e:
            print(f"Error in thread for login {login}: {e}")
        finally:
            account_queue.task_done()

def process_audience_function(account_list, table_name, group_name,  result_queue, status_queue, proxy_group, threadsx, listUsername_queue, limit_input):
    account_queue = Queue()
    for account in account_list:
        account_queue.put(account)

    threads = []
    for _ in range(threadsx):  # 100 потоков
        thread = threading.Thread(target=audience_thread, args=(account_queue, result_queue, status_queue, group_name, proxy_group, listUsername_queue, limit_input))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


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
        
        self.create_proxy_group_btn = QPushButton("Создать группу прокси")
        self.create_proxy_group_btn.clicked.connect(self.open_create_proxy_group_dialog)
        self.main_layout.addWidget(self.create_proxy_group_btn)
        
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
        self.task_combo.addItems(["Рассылка сообщений"])
        self.main_layout.addWidget(self.task_combo)

        # New Button "Проверка валидности"
        self.check_validity_btn = QPushButton("Проверка валидности")
        self.check_validity_btn.clicked.connect(self.open_check_validity_dialog)
        self.main_layout.addWidget(self.check_validity_btn)

        # New Button "Парсинг аудитории"
        self.parsing_btn = QPushButton("Парсинг аудитории")
        self.parsing_btn.clicked.connect(self.open_check_parsing_dialog)
        self.main_layout.addWidget(self.parsing_btn)
        
        # Кнопка "Заполнить таблицу"
        self.fill_table_btn = QPushButton("Заполнить таблицу")
        self.fill_table_btn.clicked.connect(self.fill_table)
        self.main_layout.addWidget(self.fill_table_btn)

        # QTabWidget для отображения таблиц аккаунтов
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.delete_table)

        # QTableWidget для отображения таблицы аудитории
        self.audience_table = QTableWidget()
        self.audience_table.setColumnCount(4)
        self.audience_table.setHorizontalHeaderLabels(["Название группы аудитории", "Кол-во пользователей", "Кол-во пройденных пользователей", "Дата создания группы"])
        self.audience_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.audience_table.setSelectionBehavior(QTableWidget.SelectRows)  # Выделение всей строки
        
        
        # QTableWidget для отображения прокси
        self.proxy_table = QTableWidget()
        self.proxy_table.setColumnCount(3)
        self.proxy_table.setHorizontalHeaderLabels(["Группа прокси" ,"Кол-во прокси", "Ссылка для обновления прокси"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proxy_table.setSelectionBehavior(QTableWidget.SelectRows)  # Выделение всей строки
        self.proxy_table.setEditTriggers(QTableWidget.NoEditTriggers)


        # QSplitter для разделения таблиц по горизонтали
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.proxy_table)
        self.splitter.addWidget(self.audience_table)

        # Общий блок статистики

        self.stats_layout = QVBoxLayout()
        self.stats_layout.setAlignment(Qt.AlignTop)  # Установка выравнивания по верхнему краю

        self.stats_container = QWidget()
        self.stats_container = QGroupBox("Статистика")  # Using QGroupBox to add a title and border

        self.stats_container.setLayout(self.stats_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.stats_container)

        self.splitter.addWidget(self.scroll_area)

        # Установка размеров для QSplitter
        self.splitter.setSizes([600, 200, 200, 200])  # 60% - таблицы аккаунтов, 20% - таблица аудитории, 20% - блок статистики

        self.main_layout.addWidget(self.splitter)

        # Виджет для основного окна
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        self.audience_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.audience_table.customContextMenuRequested.connect(self.show_audience_context_menu)
        self.load_proxy_groups()
        
    def load_proxy_groups_into_dropdown(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'proxygroup_%'"
        self.cursor.execute(query)
        groups = self.cursor.fetchall()
        self.proxy_group_dropdown.addItems([group[0].replace("proxygroup_", "") for group in groups])   
        
    if True: #VALIDITY   
        
        def open_check_validity_dialog(self):
            dialog = QDialog(self)
            dialog.setWindowTitle("Проверка валидности")
            layout = QVBoxLayout()

            # Proxy group dropdown
            self.status_label = QLabel("Выберите прокси для этой задачи")
            self.proxy_group_dropdown = QComboBox(dialog)
            self.load_proxy_groups_into_dropdown()
            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_group_dropdown)

            # Number of processes input
            self.status_label = QLabel("Кол-во процессов")
            self.processes_input = QSpinBox(dialog)
            self.processes_input.setRange(1, 100)
            self.processes_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.processes_input)

            # Number of threads input
            self.status_label = QLabel("Кол-во потоков")
            self.threads_input = QSpinBox(dialog)
            self.threads_input.setRange(1, 100)
            self.threads_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.threads_input)

            # Config name input
            self.status_label = QLabel("Сохранить конфиг?")
            self.config_name_input = QLineEdit(dialog)
            self.config_name_input.setPlaceholderText("Название конфига")
            layout.addWidget(self.status_label)
            layout.addWidget(self.config_name_input)
            # Load config button
            save_config_button = QPushButton("Сохранить конфиг", dialog)
            save_config_button.clicked.connect(self.saveConfigButton)
            layout.addWidget(save_config_button)

            # Config dropdown
            self.status_label = QLabel("Выберите конфиг для его загрузки")

            self.config_dropdown = QComboBox(dialog)
            self.load_configs_into_dropdown()
            layout.addWidget(self.status_label)

            layout.addWidget(self.config_dropdown)

            # Load config button
            load_config_button = QPushButton("Загрузить конфиг", dialog)
            load_config_button.clicked.connect(self.load_config)
            layout.addWidget(load_config_button)

            # OK button
            ok_button = QPushButton("OK", dialog)
            ok_button.clicked.connect(self.save_and_start_validation)
            layout.addWidget(ok_button)
            
            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get('DEFAULT', {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
            except:
                none = ''
                
            dialog.setLayout(layout)
            dialog.exec_()



        def load_configs_into_dropdown(self):
            # Load saved configs from a file or database
            # For simplicity, using a file here
            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
                    self.config_dropdown.addItems(configs.keys())
            except:
                none = ''

        def load_config(self):
            config_name = self.config_dropdown.currentText()
            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get(config_name, {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
            except FileNotFoundError:
                pass
        def saveConfigButton(self):
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            processes = self.processes_input.value()
            threads = self.threads_input.value()

            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs[config_name] = {
                'proxy_group': proxy_group,
                'processes': processes,
                'threads': threads
            }

            with open('configsValidity.json', 'w') as f:
                json.dump(configs, f)
        def save_and_start_validation(self):
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            processes = self.processes_input.value()
            threads = self.threads_input.value()

            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs['DEFAULT'] = {
                'proxy_group': proxy_group,
                'processes': processes,
                'threads': threads
            }

            with open('configsValidity.json', 'w') as f:
                json.dump(configs, f)
            selected_task = self.task_combo.currentText()
            current_table = self.tab_widget.currentWidget()
            if current_table:
                selected_items = current_table.selectedItems()
                if selected_items:
                    # Check if any selected account is already "In Progress"
                    selected_rows = list(set(item.row() for item in selected_items))
                    for row in selected_rows:
                        if current_table.item(row, 4) and current_table.item(row, 4).text() == "В работе":
                            QMessageBox.warning(self, "Задача не запустилась", "Выделенные аккаунты уже в работе.")
                            return
                    print(str(processes))
                    print(str(threads))
                    print(str(proxy_group))
                    self.check_validity(current_table, selected_items, proxy_group, processes, threads)

        
    if True: #PARSING    
        def open_check_parsing_dialog(self):
            dialog = QDialog(self)
            dialog.setWindowTitle("Парсинг")
            layout = QVBoxLayout()

            # Proxy group dropdown
            self.status_label = QLabel("Выберите прокси для этой задачи")
            self.proxy_group_dropdown = QComboBox(dialog)
            self.load_proxy_groups_into_dropdown()
            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_group_dropdown)
            
            self.status_label = QLabel("Введите список Username")
            self.list_username_for_parsing = QTextEdit()
            layout.addWidget(self.status_label)
            layout.addWidget(self.list_username_for_parsing)
            
            self.status_label = QLabel("Лимит сбора с каждого Username")
            self.limit_input = QSpinBox(dialog)
            self.limit_input.setRange(1, 99999999)
            self.limit_input.setValue(1000)
            layout.addWidget(self.status_label)
            layout.addWidget(self.limit_input)
            
            
            
            self.status_label = QLabel("Выберите группу для сохранения аудитории")

            self.combo_box = QComboBox()
            self.combo_box.addItems(["Создать новую группу", "Использовать существующую группу"])
            self.combo_box.currentIndexChanged.connect(self.on_combobox_changed)

            self.new_group_input = QLineEdit()
            self.new_group_input.setPlaceholderText("Введите название новой группы")
            self.new_group_input.setVisible(True)

            self.existing_group_combo = QComboBox()
            self.existing_group_combo.setVisible(False)
            
            layout.addWidget(self.status_label)
            layout.addWidget(self.combo_box)
            layout.addWidget(self.new_group_input)
            layout.addWidget(self.existing_group_combo)



                    
                    
            # Number of processes input
            self.status_label = QLabel("Кол-во процессов")
            self.processes_input = QSpinBox(dialog)
            self.processes_input.setRange(1, 100)
            self.processes_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.processes_input)

            # Number of threads input
            self.status_label = QLabel("Кол-во потоков")
            self.threads_input = QSpinBox(dialog)
            self.threads_input.setRange(1, 100)
            self.threads_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.threads_input)

            # Config name input
            self.status_label = QLabel("Сохранить конфиг?")
            self.config_name_input = QLineEdit(dialog)
            self.config_name_input.setPlaceholderText("Название конфига")
            layout.addWidget(self.status_label)
            layout.addWidget(self.config_name_input)
            # Load config button
            save_config_button = QPushButton("Сохранить конфиг", dialog)
            save_config_button.clicked.connect(self.saveConfigButton_parsing)
            layout.addWidget(save_config_button)

            # Config dropdown
            self.status_label = QLabel("Выберите конфиг для его загрузки")

            self.config_dropdown = QComboBox(dialog)
            self.load_configs_into_dropdown_parsing()
            layout.addWidget(self.status_label)

            layout.addWidget(self.config_dropdown)

            # Load config button
            load_config_button = QPushButton("Загрузить конфиг", dialog)
            load_config_button.clicked.connect(self.load_config_parsing)
            layout.addWidget(load_config_button)

            # OK button
            ok_button = QPushButton("OK", dialog)
            ok_button.clicked.connect(self.save_and_start_parsing)
            layout.addWidget(ok_button)
            
            try:
                with open('configsParsing.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get('DEFAULT', {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
                    self.limit_input.setValue(config.get('limit_input', 10))         
                    self.existing_group_combo.setCurrentText(config.get('existing_group_combo', ''))
                    self.combo_box.setCurrentText(config.get('combo_box', ''))
                    self.new_group_input.setText(config.get('new_group_input', ''))
                    self.list_username_for_parsing.setPlainText(config.get('listUsername', ''))

            except:
                none = ''
                
            dialog.setLayout(layout)
            dialog.exec_()

        def on_combobox_changed(self, index):
            if index == 0:  # Создать новую группу
                self.new_group_input.setVisible(True)
                self.existing_group_combo.setVisible(False)
            elif index == 1:  # Использовать существующую группу
                self.new_group_input.setVisible(False)
                self.populate_existing_groups()

        def populate_existing_groups(self):
            self.existing_group_combo.clear()
            query = "SELECT DISTINCT group_name FROM audience_users"
            self.cursor.execute(query)
            existing_groups = [row[0] for row in self.cursor.fetchall()]
          
            if existing_groups:
                self.existing_group_combo.addItems(existing_groups)
                self.existing_group_combo.setVisible(True)
            else:
                QMessageBox.warning(self, "Ошибка", "Нет существующих групп.")
                self.combo_box.setCurrentIndex(0)
                self.existing_group_combo.setVisible(False)
                
                
        def load_configs_into_dropdown_parsing(self):
            # Load saved configs from a file or database
            # For simplicity, using a file here
            try:
                with open('configsParsing.json', 'r') as f:
                    configs = json.load(f)
                    self.config_dropdown.addItems(configs.keys())
            except:
                none = ''

        def load_config_parsing(self):
            config_name = self.config_dropdown.currentText()
            try:
                with open('configsParsing.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get(config_name, {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
                    self.limit_input.setValue(config.get('limit_input', 10))
                    self.existing_group_combo.setCurrentText(config.get('existing_group_combo', ''))
                    self.combo_box.setCurrentText(config.get('combo_box', ''))
                    self.new_group_input.setText(config.get('new_group_input', ''))    
                    self.list_username_for_parsing.setPlainText(config.get('listUsername', ''))
            except FileNotFoundError:
                pass
        def saveConfigButton_parsing(self):
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            processes = self.processes_input.value()
            threads = self.threads_input.value()
            limit_input = self.limit_input.value()
            existing_group_combo = self.existing_group_combo.currentText()
            combo_box = self.combo_box.currentText()
            new_group_input = self.new_group_input.text()         
            listUsername = self.list_username_for_parsing.toPlainText()

            try:
                with open('configsParsing.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs[config_name] = {
                'proxy_group': proxy_group,
                'processes': processes,
                'threads': threads,
                'limit_input': limit_input,
                'existing_group_combo': existing_group_combo,
                'combo_box': combo_box,
                'new_group_input': new_group_input,     
                'listUsername': listUsername
            }

            with open('configsParsing.json', 'w') as f:
                json.dump(configs, f)
        def save_and_start_parsing(self,dialog):
            
            if self.combo_box.currentIndex() == 0:  # Создать новую группу
                group_name = self.new_group_input.text()
            else:  # Использовать существующую группу
                group_name = self.existing_group_combo.currentText()
                
            if not group_name:
                QMessageBox.warning(self, "Ошибка", "Название группы не задано.")
                return
                
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            processes = self.processes_input.value()
            threads = self.threads_input.value()
            limit_input = self.limit_input.value()
            existing_group_combo = self.existing_group_combo.currentText()
            combo_box = self.combo_box.currentText()
            new_group_input = self.new_group_input.text()  
            listUsername = self.list_username_for_parsing.toPlainText()

            try:
                with open('configsParsing.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs['DEFAULT'] = {
                'proxy_group': proxy_group,
                'processes': processes,
                'threads': threads,
                'limit_input': limit_input,
                'existing_group_combo': existing_group_combo,
                'combo_box': combo_box,
                'new_group_input': new_group_input,   
                'listUsername': listUsername

            }

            with open('configsParsing.json', 'w') as f:
                json.dump(configs, f)
                
            selected_task = self.task_combo.currentText()
            current_table = self.tab_widget.currentWidget()
            if current_table:
                selected_items = current_table.selectedItems()
                if selected_items:
                    # Check if any selected account is already "In Progress"
                    selected_rows = list(set(item.row() for item in selected_items))
                    for row in selected_rows:
                        if current_table.item(row, 4) and current_table.item(row, 4).text() == "В работе":
                            QMessageBox.warning(self, "Задача не запустилась", "Выделенные аккаунты уже в работе.")
                            return
        
                    self.parse_audience(current_table, selected_items, proxy_group, processes, threads, listUsername, limit_input,group_name)


    def load_proxy_groups(self):
        self.proxy_table.setRowCount(0)
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'proxygroup_%'"
        self.cursor.execute(query)
        groups = self.cursor.fetchall()
        for group in groups:
            group_name = group[0].replace("proxygroup_", "")
            query = f"SELECT COUNT(*) FROM {group[0]}"
            self.cursor.execute(query)
            try:
                count = self.cursor.fetchone()[0]
                query = f"SELECT url_update FROM {group[0]} LIMIT 1"
                self.cursor.execute(query)
                url_update = self.cursor.fetchone()[0]
                self.update_proxy_table(group_name, count, url_update)
            except:
                none = ''
    
    
    def open_create_proxy_group_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Создать группу прокси")
        layout = QVBoxLayout()

        # Field for group name
        self.group_name_input = QLineEdit(dialog)
        self.group_name_input.setPlaceholderText("Название группы")
        layout.addWidget(self.group_name_input)

        # Field for proxy file upload
        self.proxy_file_input = QLineEdit(dialog)
        self.proxy_file_input.setPlaceholderText("Файл прокси")
        self.proxy_file_button = QPushButton("Обзор")
        self.proxy_file_button.clicked.connect(self.select_proxy_file)
        layout.addWidget(self.proxy_file_input)
        layout.addWidget(self.proxy_file_button)

        # Field for proxy type
        self.proxy_type_input = QComboBox(dialog)
        self.proxy_type_input.addItems(["socks5", "http"])
        layout.addWidget(self.proxy_type_input)

        # Field for update URL
        self.update_url_input = QLineEdit(dialog)
        self.update_url_input.setPlaceholderText("Ссылка для обновления прокси")
        layout.addWidget(self.update_url_input)

        # OK button
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(self.create_proxy_group)
        layout.addWidget(ok_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def select_proxy_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать файл прокси", "", "All Files (*);;Text Files (*.txt)")
        if file_name:
            self.proxy_file_input.setText(file_name)

    def create_proxy_group(self):
        group_name = self.group_name_input.text()
        proxy_file = self.proxy_file_input.text()
        proxy_type = self.proxy_type_input.currentText()
        update_url = self.update_url_input.text()

        if not group_name or not proxy_file or not proxy_type:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        # Read proxies from file
        try:
            with open(proxy_file, 'r') as f:
                proxies = f.readlines()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл прокси: {e}")
            return

        # Insert proxies into the database
        table_name = f"proxygroup_{group_name}"
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (ip TEXT, port TEXT, login TEXT, password TEXT, type TEXT, url_update TEXT)"
        self.cursor.execute(query)
        for proxy in proxies:
            if '@' in proxy:
                ip, port = proxy.strip().split('@')[1].split(':')
                login, password = proxy.strip().split('@')[0].split(':')
            else:
                ip, port = proxy.strip().split(':')
                login = ''
                password = ''
                
            query = f"INSERT INTO {table_name} (ip, port, login, password, type, url_update) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.execute(query, (ip, port, login, password, proxy_type, update_url))
        self.conn.commit()

        # Update proxy table in the UI
        self.update_proxy_table(group_name, len(proxies), update_url)
        QMessageBox.information(self, "Успех", "Группа прокси создана успешно")
        self.load_proxy_groups()

    def update_proxy_table(self, group_name, proxy_count, update_url):
        row_position = self.proxy_table.rowCount()
        self.proxy_table.insertRow(row_position)
        self.proxy_table.setItem(row_position, 0, QTableWidgetItem(group_name))
        self.proxy_table.setItem(row_position, 1, QTableWidgetItem(str(proxy_count)))
        self.proxy_table.setItem(row_position, 2, QTableWidgetItem(update_url))
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
                elif status_text == "Закончил парсинг":
                    color = QColor(220,220,250)
                else:
                    color = QColor(250,250,140) #
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
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' AND name != 'audience_users' AND name NOT LIKE 'proxygroup_%'")
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
                # Check if any selected account is already "In Progress"
                selected_rows = list(set(item.row() for item in selected_items))
                for row in selected_rows:
                    if current_table.item(row, 4) and current_table.item(row, 4).text() == "В работе":
                        QMessageBox.warning(self, "Задача не запустилась", "Выделенные аккаунты уже в работе.")
                        return


                if selected_task == "Рассылка сообщений":
                    self.send_messages(current_table, selected_items)





    def check_validity(self, table, items, proxy_group, processesx, threads):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        status_queue = multiprocessing.Queue()

        if total_accounts == 0:
            return
        task_id = f"{table_name}_{time.time()}"  # Generate a unique task_id
        task_name = f"Validation Check ({table_name})"
        task_widget = TaskMonitorWidget(task_name, total_accounts, task_id, table, '')  # Pass table here
        task_widget.stop_task_signal.connect(lambda: self.stop_task(task_id))
        self.stats_layout.addWidget(task_widget)
        self.tasks[task_id] = task_widget
        task_widget.rows = selected_rows  # Associate rows with the task
        process_count = min(int(processesx), (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")

        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [table.item(row, 0).text() for row in chunk]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
            p = multiprocessing.Process(target=process_function, args=(list(zip(login_list, row_list)), table_name, result_queue, status_queue, proxy_group, threads))
            processes.append(p)
            p.start()

        task_widget.processes = processes  # Associate processes with the task_widget
        self.monitor_validity_processes(processes, result_queue, status_queue, table_name, table, task_id)
        print("Проверка валидности аккаунтов запущена")
    

    def stop_task(self, task_id):
        task_widget = self.tasks.get(task_id)
        if task_widget:
            task_widget.update_status(0,0,0, "Остановлен")
            self.terminate_audience_task(task_id)

    def terminate_audience_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if hasattr(task, 'processes') and task.processes:
                for process in task.processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()
                print(f"All processes for task {task.task_name} have been terminated.")
                
                # Update account status to 'Остановлен'
                for row in task.rows:
                    if task.table.item(row, 4).text() == "В работе":
                        task.table.setItem(row, 4, QTableWidgetItem("Остановлен"))
                        self.set_row_color(task.table, row, QColor(220,220,250))
                        print(f"Group {task.table.item(row, 0).text()} status set to 'Остановлен'")
            else:
                print(f"No processes found for task {task.task_name}.")
        else:
            print(f"Task {task_id} not found.")
            
            
            
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
            task_widget.update_status(valid_count, invalid_count, '', "В работе")  # Example usage
            print(f"Task widget updated: valid_count={valid_count}, invalid_count={invalid_count}, status='В работе'")

            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, partial(check_results, task_name))
                    return

            task_widget.update_status(valid_count, invalid_count, '', "Завершен")
            print(f"Task widget final update: valid_count={valid_count}, invalid_count={invalid_count}, status='Завершен'")
            print("Проверка валидности аккаунтов завершена")

        QTimer.singleShot(100, partial(check_results, task_name))    
    
    def parse_audience(self, table, items, proxy_group, processesx, threads, listUsername, limit_input,group_name):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        status_queue = multiprocessing.Queue()


        task_id = f"{table_name}_{time.time()}"  # Generate a unique task_id
        task_name = f"Audience Parsing ({table_name})"
        task_widget = TaskMonitorWidget(task_name, total_accounts, task_id, table, group_name)  # Pass table and group_name here

        task_widget.stop_task_signal.connect(lambda: self.stop_task(task_id))
        self.stats_layout.addWidget(task_widget)
        self.tasks[task_id] = task_widget
        task_widget.rows = selected_rows  # Associate rows with the task

        process_count = min(processesx, (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")



        listUsername_queue = multiprocessing.Queue()
        for usernameParsing in listUsername.split('\n'):
            print('usernameParsing')
            print(usernameParsing)
            listUsername_queue.put(usernameParsing)
            
            
            
            
            
        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [table.item(row, 0).text() for row in chunk]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 4, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
            p = multiprocessing.Process(target=process_audience_function, args=(list(zip(login_list, row_list)), table_name, group_name, result_queue, status_queue, proxy_group, threads, listUsername_queue, limit_input))

            processes.append(p)
            p.start()

        task_widget.processes = processes  # Associate processes with the task_widget
        self.monitor_audience_processes(processes, result_queue, status_queue, table_name, table, task_id,group_name)
        print("Парсинг аудитории запущен")
    
    


    def monitor_audience_processes(self, processes, result_queue, status_queue, table_name, table, task_name,group_name):
        def check_results(task_name):
            conn = sqlite3.connect('total.db')
            cursor = conn.cursor()
            table_updates = []
            collected_users = 0
            user_count = 0
            processed_rows = set()  # Keep track of processed rows to avoid double counting

            while not result_queue.empty():
                login, status_acc, user_ids, row = result_queue.get()
                print(status_acc)

  
                if row in processed_rows:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                user_count = len(user_ids)  # Подсчет количества пользователей
                table_updates.append((row, user_count))
                processed_rows.add(row)  # Mark row as processed

                collected_users += user_count

                print(f"User count: {collected_users}")

                # Сохранение пользователей пакетно
                user_data = [(group_name, user_id, "Новый") for user_id in user_ids]
                cursor.executemany("INSERT INTO audience_users (group_name, user_id, status) VALUES (?, ?, ?)", user_data)
                self.update_audience_table((group_name, user_count, row, table_name))

            conn.commit()
            conn.close()

            for row, user_count in table_updates:
                print(table_updates)
                if 'Закончил парсинг' in status_acc:
                    table.setItem(row, 4, QTableWidgetItem('Закончил парсинг'))
                    self.set_row_color(table, row)  
                else:
                    table.setItem(row, 4, QTableWidgetItem('Собрал: '+str(user_count)+' ...'))
                    self.set_row_color(table, row)

            task_widget = self.tasks[task_name]
            task_widget.update_status(0, 0, collected_users, "В работе")  # Обновление статуса с учетом количества пользователей

            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, partial(check_results, task_name))
                    return
            task_widget.update_status(0, 0, collected_users, "Завершен")
            #for row, user_count in table_updates:
            #    table.setItem(row, 4, QTableWidgetItem('Парсинг завершен'))
            #    self.set_row_color(table, row)
            print("Парсинг аудитории завершена")

        QTimer.singleShot(100, partial(check_results, task_name))

    
    
    def stop_task(self, task_id):
        task_widget = self.tasks.get(task_id)
        if task_widget:
            task_widget.update_status(0,0,0, "Остановлен")
            self.terminate_audience_task(task_id)

    def terminate_audience_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if hasattr(task, 'processes') and task.processes:
                for process in task.processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()
                print(f"All processes for task {task.task_name} have been terminated.")
                
                # Update account status to 'Остановлен'
                for row in task.rows:
                    if task.table.item(row, 4).text() == "В работе" or "Собрал" in task.table.item(row, 4).text():  # Use task.table instead of self.tab_widget.currentWidget()
                        task.table.setItem(row, 4, QTableWidgetItem("Остановлен"))
                        self.set_row_color(task.table, row, QColor(220,220,250))
                        print(f"Group {task.table.item(row, 0).text()} status set to 'Остановлен'")
            else:
                print(f"No processes found for task {task.task_name}.")
        else:
            print(f"Task {task_id} not found.")
    
    
    
    
    
    
    
    
    def update_audience_table(self, result):
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

        # Вызов функции обновления пользовательского интерфейса после добавления группы
        self.audience_table.viewport().update()
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
