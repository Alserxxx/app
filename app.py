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
from PyQt5.QtGui import QColor,QStandardItemModel,QCursor

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
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import pytz
import uuid
import re
import base64
from lxml import etree
import datetime
import spintax
import secrets
import urllib.parse

import csv
import requests
import json
import os
import subprocess
import hashlib
import ssl
import time

SERVER_URL = "http://serveridm/"
LICENSE_FILE = "license.json"





SERVER_URL = 'http://37.230.116.31/admin_panel'
LICENSE_FILE = 'license.json'

def read_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as file:
            return json.load(file)
    return None

def write_license(license_data):
    with open(LICENSE_FILE, 'w') as file:
        json.dump(license_data, file)

def validate_license(license_key):
    response = requests.post(SERVER_URL, data={'license_key': license_key})
    print(response.text)
    return response.json()

def prompt_license():
    app = QApplication([])
    license_key, ok = QInputDialog.getText(None, 'License Key', 'Enter your license key:')
    if ok and license_key:
        result = validate_license(license_key)
        print(result)
        if result['valid']:
            write_license(result)
            return result
        else:
            QMessageBox.critical(None, 'Error', 'Invalid license key.')
            sys.exit(1)
    else:
        sys.exit(1)









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
        QLabel { 
            color: black;
        }        
        """

        if 'Validation Check' in self.task_name:

            self.task_label = QLabel(f"Задача: {self.task_name}")
            self.valid_label = QLabel(f"Валидные: {self.valid_count}")
            self.invalid_label = QLabel(f"Невалидные: {self.invalid_count}")
            
        if 'Audience' in self.task_name:
            self.task_label = QLabel(f"Задача: {self.task_name} Запись в [ {self.group_name} ]")
            self.processed_label = QLabel(f"Обработано: {self.processed_count}")
            
        if 'Direct' in self.task_name:
            self.task_label = QLabel(f"Задача: {self.task_name} [ {self.group_name} ]")
            self.processed_label = QLabel(f"Кол-во доставленных сообщений: {self.processed_count}")

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
            
        if 'Direct' in self.task_name:
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
        container_widget.setObjectName('div1')

        container_widget.setLayout(layout)
        container_widgetStyle = """
        #div1 { 
            border: 2px solid black;
            border-radius: 5px;
            max-height: 250px;
            background: white;
        }        
        """
        container_widget.setStyleSheet(container_widgetStyle)
        #container_widget.setStyleSheet("border: 5px solid #00796b; max-height: 250px;")

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container_widget)
        self.setLayout(main_layout)

    def update_time(self):
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Время: {elapsed_time}с")

    def update_status(self, valid_count, invalid_count, processed_count, status):

        try:
            #print(self.task_name)
            if 'Validation Check' in self.task_name:
                self.valid_count += valid_count
                self.invalid_count += invalid_count
                self.valid_label.setText(f"Валидные: {self.valid_count}")
                self.invalid_label.setText(f"Невалидные: {self.invalid_count}")
            elif 'Audience Parsing' in self.task_name:
                self.processed_count += processed_count
                self.processed_label.setText(f"Обработано: {self.processed_count}")
            elif 'Direct' in self.task_name:
                self.processed_count += processed_count
                self.processed_label.setText(f"Доставленных сообщений: {self.processed_count}")
            self.status_label.setText(f"Статус: {status}")

            if status in ["Завершен", "Остановлен"]:
                self.stop_button.setVisible(False)
                self.close_button.setVisible(True)
                self.timer.stop()
        except Exception as e:
            print(e)
            print('ERROR BLA')
    def close_task(self):
        self.close()
  




def getCookies(response, mid, csrftoken, sessionid, rur, ds_user_id, authorization, claim):

    cookiesnew = response.cookies
    headsnew = response.headers
   
        
    if 'csrftoken' in str(cookiesnew):
        csrftoken = cookiesnew['csrftoken']

    if 'mid' in str(cookiesnew):
        mid = cookiesnew['mid']

    if 'ds_user_id' in str(cookiesnew):
        ds_user_id = cookiesnew['ds_user_id']

    if 'sessionid' in str(cookiesnew):
        sessionid = cookiesnew['sessionid']
        #printMessage('COOK sessionid: '+sessionid)

    if 'rur' in str(cookiesnew):
        rur = cookiesnew['rur']

    if 'ig_did' in str(cookiesnew):
        ig_did = cookiesnew['ig_did']

    if 'ig-set-ig-u-ig-direct-region-hint' in str(headsnew):
        igdirectregion = headsnew['ig-set-ig-u-ig-direct-region-hint']

    if 'ig-set-x-mid' in str(headsnew):
        mid8 = headsnew['ig-set-x-mid']
        if mid8 != '':
            mid = mid8
            
            
            
    if 'ig-set-ig-u-ig-direct-region-hint' in str(headsnew):
        igdirectregion8 = headsnew['ig-set-ig-u-ig-direct-region-hint']
        if igdirectregion8 != '':
            igdirectregion = igdirectregion8
            
            
    if 'ig-set-ig-u-rur' in str(headsnew):
        rur8 = headsnew['ig-set-ig-u-rur']
        if rur8 != '':
            rur = rur8
    if 'ig-set-ig-u-ds-user-id' in str(headsnew):
        ds_user_id8 = headsnew['ig-set-ig-u-ds-user-id']
        if ds_user_id8 != '':
            ds_user_id = ds_user_id8
            
    if 'ig-set-authorization' in str(headsnew):
        authorization8 = headsnew['ig-set-authorization']
        if authorization8 != '' and authorization8 != 'Bearer IGT:2:':
            authorization = authorization8
            #printMessage('COOK 1: '+authorization)
            
            
    if 'x-ig-set-www-claim' in str(headsnew):
        claim8 = headsnew['x-ig-set-www-claim']
        if claim8 != '':
            claim = claim8
            
            
            
    if 'ig-set-ig-u-shbid' in str(headsnew):
        shbid8 = headsnew['ig-set-ig-u-shbid']
        #printMessage('shbid: '+shbid8)

        if shbid8 != '':
            shbid = shbid8
            
    if 'ig-set-ig-u-shbts' in str(headsnew):
        shbts8 = headsnew['ig-set-ig-u-shbts']
        #printMessage('shbts8: '+shbts8)

        if shbts8 != '':
            shbts = shbts8
            
    if 'Ig-Set-Ig-U-Shbid' in str(headsnew):
        shbid8 = headsnew['ig-set-ig-u-shbid']
        #printMessage('shbid: '+shbid8)
        if shbid8 != '':
            shbid = shbid8
            
    if 'Ig-Set-Ig-U-Shbts' in str(headsnew):
        shbts8 = headsnew['ig-set-ig-u-shbts']
        #printMessage('shbts8: '+shbts8)

        if shbts8 != '':
            shbts = shbts8              
            
            
    if 'ig-set-password-encryption-key-id' in str(headsnew):
        keyid = headsnew['ig-set-password-encryption-key-id']
        keyid = int(keyid)
        print(str(keyid))

    if 'ig-set-password-encryption-pub-key' in str(headsnew):
        pubkey = headsnew['ig-set-password-encryption-pub-key']

    if 'ig-set-password-encryption-web-key-id' in str(headsnew):
        webkeyid = headsnew['ig-set-password-encryption-web-key-id']

    if 'ig-set-password-encryption-web-key-version' in str(headsnew):
        webversion = headsnew['ig-set-password-encryption-web-key-version']

    if 'ig-set-password-encryption-web-pub-key' in str(headsnew):
        webpubkey = headsnew['ig-set-password-encryption-web-pub-key']
        
        
        
    textrespa = response.text
    textrespa = textrespa.replace('\\\\\\', '')
    textrespa = textrespa.replace('\\\\', '')
    textrespa = textrespa.replace('\\', '')
    textrespa = textrespa.replace('\u005C', '')
    textrespa = textrespa.replace('\\u005C', '')
    #printMessage('TEXTCOOKIE :'+textrespa)
    try:
        authorization8 = re.findall('"IG-Set-Authorization": "(.*?)"', textrespa)
        authorization = authorization8[0]
        #printMessage('COOK 2: '+authorization)

    except:
        #printMessage('error1 authorization')
        none = ''
        
    try:
        authorization8 = re.findall('"IG-Set-Authorization\\\\\\\\\\\\\\":\ \\\\\\\\\\\\\\"(.*?)\\\\\\\\\\\\\\" ', textrespa)
        authorization = authorization8[0]
       # printMessage('COOK 3: '+authorization)

    except:
        #printMessage('error2 authorization')
        none = ''   
        

    try:
        ds_user_id8 = re.findall('"ig-set-ig-u-ds-user-id": (.*?),', textrespa)
        ds_user_id = ds_user_id8[0]
        #printMessage('DS ID 1: '+str(ds_user_id))

    except:
        #printMessage('error ds_user_id')
        none = ''
        




    try:
        rur8 = re.findall('"ig-set-ig-u-rur": "(.*?)",', textrespa)
        rur = rur8[0]
        #printMessage(str(rur))

    except:
        #printMessage('error rur')
        none = ''  
        
        
    try:
        rur8 = re.findall('"ig\-set\-ig\-u\-rur\\\\\\\\\\\\\\":\ \\\\\\\\\\\\\\"(.*?)\\\\\\\\\\\\\\"', textrespa)
        rur = rur8[0]
        #printMessage(str(rur))

    except:
        #printMessage('error rur')
        none = ''            
        
        
    try:
        csrftoken8 = re.findall('csrftoken=(.*?);', textrespa)
        csrftoken = csrftoken8[0]
        #printMessage(str(csrftoken))

    except:
        #printMessage('error csrftoken')
        none = ''

    try:
        mid8 = re.findall('mid=(.*?);', textrespa)
        mid = mid8[0]
        #printMessage(str(mid))

    except:
       #printMessage('error mid')
        none = ''
        

    return mid, csrftoken, sessionid, rur, ds_user_id, authorization, claim

def generate_random_string(length):
    abc = "abcdef0123456789"
    return ''.join(random.choice(abc) for _ in range(length))




def gettimereal(timezonename):
    dtime = datetime.datetime.now()
    timezone = pytz.timezone(timezonename) #/
    dtzone = timezone.localize(dtime)
    tstamp = dtzone.timestamp()
    timereal = time.time()
    timereal = str(timereal)[:-4]
    return(str(int(round(tstamp)))+"."+str(randint(000,999)))
      
def changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown):
    savehtmlcountry = '<tbody> <tr><td><a href="https://country-codes.org/Afghanistan"><b>Afghanistan</b></a></td><td><b>AFG</b></td><td><b>af</b></td><td><a href="93"><b>93</b></a></td><td><b>Kabul</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/af.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/South-Africa"><b>South Africa</b></a></td><td><b>ZAF</b></td><td><b>za</b></td><td><a href="27"><b>27</b></a></td><td><b>Pretoria</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/za.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Albania"><b>Albania</b></a></td><td><b>ALB</b></td><td><b>al</b></td><td><a href="355"><b>355</b></a></td><td><b>Tirana</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/al.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Algeria"><b>Algeria</b></a></td><td><b>DZA</b></td><td><b>dz</b></td><td><a href="213"><b>213</b></a></td><td><b>Algiers</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/dz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Germany"><b>Germany</b></a></td><td><b>DEU</b></td><td><b>de</b></td><td><a href="49"><b>49</b></a></td><td><b>Berlin</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/de.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Andorra"><b>Andorra</b></a></td><td><b>AND</b></td><td><b>ad</b></td><td><a href="376"><b>376</b></a></td><td><b>Andorra la Vella</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ad.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/England"><b>England</b></a></td><td><b>GBE</b></td><td><b>gb</b></td><td><a href="44"><b>44</b></a></td><td><b>London</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Angola"><b>Angola</b></a></td><td><b>AGO</b></td><td><b>ao</b></td><td><a href="244"><b>244</b></a></td><td><b>Luanda</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ao.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Anguilla"><b>Anguilla</b></a></td><td><b>AIA</b></td><td><b>ai</b></td><td><a href="1264"><b>1264</b></a></td><td><b>The Valley</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ai.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Antigua-Barbuda"><b>Antigua and Barbuda</b></a></td><td><b>ATG</b></td><td><b>ag</b></td><td><a href="1268"><b>1268</b></a></td><td><b>St. Johns</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ag.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Netherlands-Antilles"><b>Netherlands Antilles</b></a></td><td><b>ANT</b></td><td><b>an</b></td><td><a href="599"><b>599</b></a></td><td><b>Willemstad</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/an.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Saudi-Arabia"><b>Saudi Arabia</b></a></td><td><b>SAU</b></td><td><b>sa</b></td><td><a href="966"><b>966</b></a></td><td><b>Riyadh</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sa.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Argentina"><b>Argentina</b></a></td><td><b>ARG</b></td><td><b>ar</b></td><td><a href="54"><b>54</b></a></td><td><b>Buenos Aires</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ar.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Armenia"><b>Armenia</b></a></td><td><b>ARM</b></td><td><b>am</b></td><td><a href="374"><b>374</b></a></td><td><b>Yerevan</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/am.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Aruba"><b>Aruba</b></a></td><td><b>ABW</b></td><td><b>aw</b></td><td><a href="297"><b>297</b></a></td><td><b>Oranjestad</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/aw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Australia"><b>Australia</b></a></td><td><b>AUS</b></td><td><b>au</b></td><td><a href="61"><b>61</b></a></td><td><b>Canberra</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/au.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Austria"><b>Austria</b></a></td><td><b>AUT</b></td><td><b>at</b></td><td><a href="43"><b>43</b></a></td><td><b>Vienna</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/at.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Azerbaijan"><b>Azerbaijan</b></a></td><td><b>AZE</b></td><td><b>az</b></td><td><a href="994"><b>994</b></a></td><td><b>Baku</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/az.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bahamas"><b>Bahamas</b></a></td><td><b>BHS</b></td><td><b>bs</b></td><td><a href="1242"><b>1242</b></a></td><td><b>Nassau</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bs.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bahrain"><b>Bahrain</b></a></td><td><b>BHR</b></td><td><b>bh</b></td><td><a href="973"><b>973</b></a></td><td><b>Manama</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bh.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bangladesh"><b>Bangladesh</b></a></td><td><b>BGD</b></td><td><b>bd</b></td><td><a href="880"><b>880</b></a></td><td><b>Dhaka</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bd.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Barbados"><b>Barbados</b></a></td><td><b>BRB</b></td><td><b>bb</b></td><td><a href="1246"><b>1246</b></a></td><td><b>Bridgetown</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Belgium"><b>Belgium</b></a></td><td><b>BEL</b></td><td><b>be</b></td><td><a href="32"><b>32</b></a></td><td><b>Brussels</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/be.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Belize"><b>Belize</b></a></td><td><b>BLZ</b></td><td><b>bz</b></td><td><a href="501"><b>501</b></a></td><td><b>Belmopan</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Benin"><b>Benin</b></a></td><td><b>BEN</b></td><td><b>bj</b></td><td><a href="229"><b>229</b></a></td><td><b>Porto-Novo</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bj.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bermuda"><b>Bermuda</b></a></td><td><b>BMU</b></td><td><b>bm</b></td><td><a href="1441"><b>1441</b></a></td><td><b>Hamilton</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bhutan"><b>Bhutan</b></a></td><td><b>BTN</b></td><td><b>bt</b></td><td><a href="975"><b>975</b></a></td><td><b>Thimphu</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bt.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Belarus"><b>Belarus</b></a></td><td><b>BLR</b></td><td><b>by</b></td><td><a href="375"><b>375</b></a></td><td><b>Minsk</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/by.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bolivia"><b>Bolivia</b></a></td><td><b>BOL</b></td><td><b>bo</b></td><td><a href="591"><b>591</b></a></td><td><b>Sucre</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bo.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bosnia-Herzegovina"><b>Bosnia and Herzegovina</b></a></td><td><b>BIH</b></td><td><b>ba</b></td><td><a href="387"><b>387</b></a></td><td><b>Sarajevo</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ba.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Botswana"><b>Botswana</b></a></td><td><b>BWA</b></td><td><b>bw</b></td><td><a href="267"><b>267</b></a></td><td><b>Gaborone</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Brazil"><b>Brazil</b></a></td><td><b>BRA</b></td><td><b>br</b></td><td><a href="55"><b>55</b></a></td><td><b>Brasilia</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/br.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Brunei"><b>Brunei</b></a></td><td><b>BRN</b></td><td><b>bn</b></td><td><a href="673"><b>673</b></a></td><td><b>Bandar Seri Begawan</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Bulgaria"><b>Bulgaria</b></a></td><td><b>BGR</b></td><td><b>bg</b></td><td><a href="359"><b>359</b></a></td><td><b>Sofia</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Burkina-Faso"><b>Burkina Faso</b></a></td><td><b>BFA</b></td><td><b>bf</b></td><td><a href="226"><b>226</b></a></td><td><b>Ouagadougou</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bf.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Burundi"><b>Burundi</b></a></td><td><b>BDI</b></td><td><b>bi</b></td><td><a href="257"><b>257</b></a></td><td><b>Bujumbura</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/bi.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Cambodia"><b>Cambodia</b></a></td><td><b>KHM</b></td><td><b>kh</b></td><td><a href="855"><b>855</b></a></td><td><b>Phnom Penh</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kh.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Cameroon"><b>Cameroon</b></a></td><td><b>CMR</b></td><td><b>cm</b></td><td><a href="237"><b>237</b></a></td><td><b>Yaounde</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Canada"><b>Canada</b></a></td><td><b>CAN</b></td><td><b>ca</b></td><td><a href="1"><b>1</b></a></td><td><b>Ottawa</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ca.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Cape-Verde"><b>Cape Verde</b></a></td><td><b>CPV</b></td><td><b>cv</b></td><td><a href="238"><b>238</b></a></td><td><b>Praia</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cv.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Chile"><b>Chile</b></a></td><td><b>CHL</b></td><td><b>cl</b></td><td><a href="56"><b>56</b></a></td><td><b>Santiago</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cl.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/China"><b>Republic of China</b></a></td><td><b>CHN</b></td><td><b>cn</b></td><td><a href="86"><b>86</b></a></td><td><b>Beijing</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Cyprus"><b>Cyprus</b></a></td><td><b>CYP</b></td><td><b>cy</b></td><td><a href="357"><b>357</b></a></td><td><b>Nicosia</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cy.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Colombia"><b>Colombia</b></a></td><td><b>COL</b></td><td><b>co</b></td><td><a href="57"><b>57</b></a></td><td><b>Bogota</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/co.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Comoros"><b>Comoros</b></a></td><td><b>COM</b></td><td><b>km</b></td><td><a href="269"><b>269</b></a></td><td><b>Moroni</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/km.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Congo"><b>Republic of the Congo</b></a></td><td><b>COG</b></td><td><b>cg</b></td><td><a href="242"><b>242</b></a></td><td><b>Brazzaville</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/South-Korea"><b>South Korea</b></a></td><td><b>KOR</b></td><td><b>kr</b></td><td><a href="82"><b>82</b></a></td><td><b>Seoul</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Costa-Rica"><b>Costa Rica</b></a></td><td><b>CRC</b></td><td><b>cr</b></td><td><a href="506"><b>506</b></a></td><td><b>San Jose</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Ivory-Coast"><b>Ivory Coast</b></a></td><td><b>CIV</b></td><td><b>ci</b></td><td><a href="225"><b>225</b></a></td><td><b>Yamoussoukro</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ci.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Croatia"><b>Croatia</b></a></td><td><b>HRV</b></td><td><b>hr</b></td><td><a href="385"><b>385</b></a></td><td><b>Zagreb</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/hr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Cuba"><b>Cuba</b></a></td><td><b>CUB</b></td><td><b>cu</b></td><td><a href="53"><b>53</b></a></td><td><b>Havana</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cu.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Denmark"><b>Denmark</b></a></td><td><b>DNK</b></td><td><b>dk</b></td><td><a href="45"><b>45</b></a></td><td><b>Copenhagen</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/dk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Djibouti"><b>Djibouti</b></a></td><td><b>DJI</b></td><td><b>dj</b></td><td><a href="253"><b>253</b></a></td><td><b>Djibouti</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/dj.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Dominica"><b>Dominica</b></a></td><td><b>DMA</b></td><td><b>dm</b></td><td><a href="1767"><b>1767</b></a></td><td><b>Roseau</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/dm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Scotland"><b>Scotland</b></a></td><td><b>GBS</b></td><td><b>gb</b></td><td><a href="44"><b>44</b></a></td><td><b>London</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Egypt"><b>Egypt</b></a></td><td><b>EGY</b></td><td><b>eg</b></td><td><a href="20"><b>20</b></a></td><td><b>Cairo</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/eg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/United-Arab-Emirates"><b>United Arab Emirates</b></a></td><td><b>ARE</b></td><td><b>ae</b></td><td><a href="971"><b>971</b></a></td><td><b>Abu Dhabi</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ae.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Ecuador"><b>Ecuador</b></a></td><td><b>ECU</b></td><td><b>ec</b></td><td><a href="593"><b>593</b></a></td><td><b>Quito</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ec.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Eritrea"><b>Eritrea</b></a></td><td><b>ERI</b></td><td><b>er</b></td><td><a href="291"><b>291</b></a></td><td><b>Asmara</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/er.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Spain"><b>Spain</b></a></td><td><b>ESP</b></td><td><b>es</b></td><td><a href="34"><b>34</b></a></td><td><b>Madrid</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/es.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Estonia"><b>Estonia</b></a></td><td><b>EST</b></td><td><b>ee</b></td><td><a href="372"><b>372</b></a></td><td><b>Tallinn</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ee.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/United-States-of-America"><b>United States</b></a></td><td><b>USA</b></td><td><b>us</b></td><td><a href="1"><b>1</b></a></td><td><b>Washington</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/us.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Ethiopia"><b>Ethiopia</b></a></td><td><b>ETH</b></td><td><b>et</b></td><td><a href="251"><b>251</b></a></td><td><b>Addis Ababa</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/et.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Finland"><b>Finland</b></a></td><td><b>FIN</b></td><td><b>fi</b></td><td><a href="358"><b>358</b></a></td><td><b>Helsinki</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fi.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/France"><b>France</b></a></td><td><b>FRA</b></td><td><b>fr</b></td><td><a href="33"><b>33</b></a></td><td><b>Paris</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Gabon"><b>Gabon</b></a></td><td><b>GAB</b></td><td><b>ga</b></td><td><a href="241"><b>241</b></a></td><td><b>Libreville</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ga.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Gambia"><b>Gambia</b></a></td><td><b>GMB</b></td><td><b>gm</b></td><td><a href="220"><b>220</b></a></td><td><b>Banjul</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Georgia"><b>Georgia</b></a></td><td><b>GEO</b></td><td><b>ge</b></td><td><a href="995"><b>995</b></a></td><td><b>Tbilisi</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ge.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Ghana"><b>Ghana</b></a></td><td><b>GHA</b></td><td><b>gh</b></td><td><a href="233"><b>233</b></a></td><td><b>Accra</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gh.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Gibraltar"><b>Gibraltar</b></a></td><td><b>GIB</b></td><td><b>gi</b></td><td><a href="350"><b>350</b></a></td><td><b>Gibraltar</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gi.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Greece"><b>Greece</b></a></td><td><b>GRC</b></td><td><b>gr</b></td><td><a href="30"><b>30</b></a></td><td><b>Athens</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Grenada"><b>Grenada</b></a></td><td><b>GRD</b></td><td><b>gd</b></td><td><a href="1473"><b>1473</b></a></td><td><b>St. Georges</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gd.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Groenland"><b>Greenland</b></a></td><td><b>GRL</b></td><td><b>gl</b></td><td><a href="299"><b>299</b></a></td><td><b>Nuuk</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gl.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Guadalupe"><b>Guadeloupe</b></a></td><td><b>GP</b></td><td><b>fr</b></td><td><a href="590"><b>590</b></a></td><td><b> </b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Guatemala"><b>Guatemala</b></a></td><td><b>GTM</b></td><td><b>gt</b></td><td><a href="502"><b>502</b></a></td><td><b>Guatemala City</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gt.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Guinea"><b>Guinea</b></a></td><td><b>GIN</b></td><td><b>gn</b></td><td><a href="224"><b>224</b></a></td><td><b>Conakry</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Equatorial-Guinea"><b>Equatorial Guinea</b></a></td><td><b>GNQ</b></td><td><b>gq</b></td><td><a href="240"><b>240</b></a></td><td><b>Malabo</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gq.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Guinea-Bissau"><b>Guinea-Bissau</b></a></td><td><b>GNB</b></td><td><b>gw</b></td><td><a href="245"><b>245</b></a></td><td><b>Bissau</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Guyana"><b>Guyana</b></a></td><td><b>GUY</b></td><td><b>gy</b></td><td><a href="592"><b>592</b></a></td><td><b>Georgetown</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gy.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Haiti"><b>Haiti</b></a></td><td><b>HTI</b></td><td><b>ht</b></td><td><a href="509"><b>509</b></a></td><td><b>Port-au-Prince</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ht.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Honduras"><b>Honduras</b></a></td><td><b>HND</b></td><td><b>hn</b></td><td><a href="504"><b>504</b></a></td><td><b>Tegucigalpa</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/hn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Hong-Kong"><b>Hong Kong</b></a></td><td><b>HKG</b></td><td><b>hk</b></td><td><a href="852"><b>852</b></a></td><td><b>Hong Kong</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/hk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Hungary"><b>Hungary</b></a></td><td><b>HUN</b></td><td><b>hu</b></td><td><a href="36"><b>36</b></a></td><td><b>Budapest</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/hu.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Iles-Ascension"><b>Ascension Island</b></a></td><td><b>SHN</b></td><td><b>sh</b></td><td><a href="247"><b>247</b></a></td><td><b>Jamestown</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sh.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Isla-Christmas"><b>Christmas Island</b></a></td><td><b>CXR</b></td><td><b>cx</b></td><td><a href="61"><b>61</b></a></td><td><b>Flying Fish Cove</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cx.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Marshall-Islands"><b>Marshall Islands</b></a></td><td><b>MHL</b></td><td><b>mh</b></td><td><a href="692"><b>692</b></a></td><td><b>Majuro</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mh.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mauritius"><b>Mauritius</b></a></td><td><b>MUS</b></td><td><b>mu</b></td><td><a href="230"><b>230</b></a></td><td><b>Port Louis</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mu.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Solomon-Islands"><b>Solomon Islands</b></a></td><td><b>SLB</b></td><td><b>sb</b></td><td><a href="677"><b>677</b></a></td><td><b>Honiara</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Cayman-Islands"><b>Cayman Islands</b></a></td><td><b>CYM</b></td><td><b>ky</b></td><td><a href="1345"><b>1345</b></a></td><td><b>George Town</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ky.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/CookIslands"><b>Cook Islands</b></a></td><td><b>COK</b></td><td><b>ck</b></td><td><a href="682"><b>682</b></a></td><td><b>Avarua</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ck.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Falklands-Islands"><b>Falkland Islands</b></a></td><td><b>FLK</b></td><td><b>fk</b></td><td><a href="500"><b>500</b></a></td><td><b>Stanley</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Faroe-Islands"><b>Faroe Islands</b></a></td><td><b>FRO</b></td><td><b>fo</b></td><td><a href="298"><b>298</b></a></td><td><b>Torshavn</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fo.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Fiji"><b>Fiji</b></a></td><td><b>FJI</b></td><td><b>fj</b></td><td><a href="679"><b>679</b></a></td><td><b>Suva</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fj.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Iles-Mariannes"><b>Mariana Island</b></a></td><td><b>MNP</b></td><td><b>mp</b></td><td><a href="1670"><b>1670</b></a></td><td><b>Saipan</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mp.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Turksand-Caicos-Islands"><b>Turks and Caicos Islands</b></a></td><td><b>TCA</b></td><td><b>tc</b></td><td><a href="1649"><b>1649</b></a></td><td><b>Cockburn Town</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tc.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Virgin-Iles-UK"><b>British Virgin Islands</b></a></td><td><b>VGB</b></td><td><b>vg</b></td><td><a href="1284"><b>1284</b></a></td><td><b>Road Town</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/vg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Virgin-Iles-US"><b>Virgin Islands</b></a></td><td><b>VIR</b></td><td><b>vi</b></td><td><a href="1340"><b>1340</b></a></td><td><b>Charlotte Amalie</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/vi.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/India"><b>India</b></a></td><td><b>IND</b></td><td><b>in</b></td><td><a href="91"><b>91</b></a></td><td><b>New Delhi</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/in.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Indonezia"><b>Indonesia</b></a></td><td><b>IDN</b></td><td><b>id</b></td><td><a href="62"><b>62</b></a></td><td><b>Jakarta</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/id.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Iraq"><b>Iraq</b></a></td><td><b>IRQ</b></td><td><b>iq</b></td><td><a href="964"><b>964</b></a></td><td><b>Baghdad</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/iq.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Ireland"><b>Ireland</b></a></td><td><b>IRL</b></td><td><b>ie</b></td><td><a href="353"><b>353</b></a></td><td><b>Dublin</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ie.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/NorthIrland"><b>Northern Ireland</b></a></td><td><b>GBN</b></td><td><b>gb</b></td><td><a href="44"><b>44</b></a></td><td><b>London</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Israel"><b>Israel</b></a></td><td><b>ISR</b></td><td><b>il</b></td><td><a href="972"><b>972</b></a></td><td><b>Jerusalem</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/il.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Italy"><b>Italy</b></a></td><td><b>ITA</b></td><td><b>it</b></td><td><a href="39"><b>39</b></a></td><td><b>Rome</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/it.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Jamaica"><b>Jamaica</b></a></td><td><b>JAM</b></td><td><b>jm</b></td><td><a href="1876"><b>1876</b></a></td><td><b>Kingston</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/jm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Japan"><b>Japan</b></a></td><td><b>JPN</b></td><td><b>jp</b></td><td><a href="81"><b>81</b></a></td><td><b>Tokyo</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/jp.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Jordan"><b>Jordan</b></a></td><td><b>JOR</b></td><td><b>jo</b></td><td><a href="962"><b>962</b></a></td><td><b>Amman</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/jo.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Kazakhstan"><b>Kazakhstan</b></a></td><td><b>KAZ</b></td><td><b>kz</b></td><td><a href="7"><b>7</b></a></td><td><b>Astana</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Kenya"><b>Kenya</b></a></td><td><b>KEN</b></td><td><b>ke</b></td><td><a href="254"><b>254</b></a></td><td><b>Nairobi</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ke.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Kyrgyzstan"><b>Kyrgyzstan</b></a></td><td><b>KGZ</b></td><td><b>kg</b></td><td><a href="996"><b>996</b></a></td><td><b>Bishkek</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Kiribati"><b>Kiribati</b></a></td><td><b>KIR</b></td><td><b>ki</b></td><td><a href="686"><b>686</b></a></td><td><b>Tarawa</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ki.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Kosovo"><b>Kosovo</b></a></td><td><b>XKX</b></td><td><b>xk</b></td><td><a href="381"><b>381</b></a></td><td><b>Pristina</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/xk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Kuwait"><b>Kuwait</b></a></td><td><b>KWT</b></td><td><b>kw</b></td><td><a href="965"><b>965</b></a></td><td><b>Kuwait City</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Lesotho"><b>Lesotho</b></a></td><td><b>LSO</b></td><td><b>ls</b></td><td><a href="266"><b>266</b></a></td><td><b>Maseru</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ls.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Latvia"><b>Latvia</b></a></td><td><b>LVA</b></td><td><b>lv</b></td><td><a href="371"><b>371</b></a></td><td><b>Riga</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lv.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Lebanon"><b>Lebanon</b></a></td><td><b>LBN</b></td><td><b>lb</b></td><td><a href="961"><b>961</b></a></td><td><b>Beirut</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Liberia"><b>Liberia</b></a></td><td><b>LBR</b></td><td><b>lr</b></td><td><a href="231"><b>231</b></a></td><td><b>Monrovia</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Libya"><b>Libya</b></a></td><td><b>LBY</b></td><td><b>ly</b></td><td><a href="218"><b>218</b></a></td><td><b>Tripolis</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ly.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Liechtenshein"><b>Liechtenstein</b></a></td><td><b>LIE</b></td><td><b>li</b></td><td><a href="423"><b>423</b></a></td><td><b>Vaduz</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/li.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Lithuania"><b>Lithuania</b></a></td><td><b>LTU</b></td><td><b>lt</b></td><td><a href="370"><b>370</b></a></td><td><b>Vilnius</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lt.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Luxembourg"><b>Luxembourg</b></a></td><td><b>LUX</b></td><td><b>lu</b></td><td><a href="352"><b>352</b></a></td><td><b>Luxembourg</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lu.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Macau"><b>Macau</b></a></td><td><b>MAC</b></td><td><b>mo</b></td><td><a href="853"><b>853</b></a></td><td><b>Macao</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mo.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Macedonia"><b>Macedonia</b></a></td><td><b>MKD</b></td><td><b>mk</b></td><td><a href="389"><b>389</b></a></td><td><b>Skopje</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Madagascar"><b>Madagascar</b></a></td><td><b>MDG</b></td><td><b>mg</b></td><td><a href="261"><b>261</b></a></td><td><b>Antananarivo</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Malaysia"><b>Malaysia</b></a></td><td><b>MYS</b></td><td><b>my</b></td><td><a href="60"><b>60</b></a></td><td><b>Kuala Lumpur</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/my.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Malawi"><b>Malawi</b></a></td><td><b>MWI</b></td><td><b>mw</b></td><td><a href="265"><b>265</b></a></td><td><b>Lilongwe</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Maldives"><b>Maldives</b></a></td><td><b>MDV</b></td><td><b>mv</b></td><td><a href="960"><b>960</b></a></td><td><b>Male</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mv.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mali"><b>Mali</b></a></td><td><b>MLI</b></td><td><b>ml</b></td><td><a href="223"><b>223</b></a></td><td><b>Bamako</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ml.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Malta"><b>Malta</b></a></td><td><b>MLT</b></td><td><b>mt</b></td><td><a href="356"><b>356</b></a></td><td><b>Valletta</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mt.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Morocco"><b>Morocco</b></a></td><td><b>MAR</b></td><td><b>ma</b></td><td><a href="212"><b>212</b></a></td><td><b>Rabat</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ma.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Martinique"><b>Martinique</b></a></td><td><b>MTQ</b></td><td><b>fr</b></td><td><a href="596"><b>596</b></a></td><td><b>Fort-de-France</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mauritania"><b>Mauritania</b></a></td><td><b>MRT</b></td><td><b>mr</b></td><td><a href="222"><b>222</b></a></td><td><b>Nouakchott</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mayotte"><b>Mayotte</b></a></td><td><b>MYT</b></td><td><b>fr</b></td><td><a href="262"><b>262</b></a></td><td><b>Mamoudzou</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mexico"><b>Mexico</b></a></td><td><b>MEX</b></td><td><b>mx</b></td><td><a href="52"><b>52</b></a></td><td><b>Mexico City</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mx.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Micronesia"><b>Micronesia</b></a></td><td><b>FSM</b></td><td><b>fm</b></td><td><a href="691"><b>691</b></a></td><td><b>Palikir</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Monaco"><b>Monaco</b></a></td><td><b>MCO</b></td><td><b>mc</b></td><td><a href="377"><b>377</b></a></td><td><b>Monaco</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mc.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mongolia"><b>Mongolia</b></a></td><td><b>MNG</b></td><td><b>mn</b></td><td><a href="976"><b>976</b></a></td><td><b>Ulan Bator</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Montenegro"><b>Montenegro</b></a></td><td><b>MNE</b></td><td><b>me</b></td><td><a href="382"><b>382</b></a></td><td><b>Podgorica</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/me.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Montserrat"><b>Montserrat</b></a></td><td><b>MSR</b></td><td><b>ms</b></td><td><a href="1664"><b>1664</b></a></td><td><b>Plymouth</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ms.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Mozambique"><b>Mozambique</b></a></td><td><b>MOZ</b></td><td><b>mz</b></td><td><a href="258"><b>258</b></a></td><td><b>Maputo</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Burma"><b>Burma</b></a></td><td><b>MMR</b></td><td><b>mm</b></td><td><a href="95"><b>95</b></a></td><td><b>Nay Pyi Taw</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/mm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Namibia"><b>Namibia</b></a></td><td><b>NAM</b></td><td><b>na</b></td><td><a href="264"><b>264</b></a></td><td><b>Windhoek</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/na.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Nauru"><b>Nauru</b></a></td><td><b>NRU</b></td><td><b>nr</b></td><td><a href="674"><b>674</b></a></td><td><b>Yaren</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/nr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Nepal"><b>Nepal</b></a></td><td><b>NPL</b></td><td><b>np</b></td><td><a href="977"><b>977</b></a></td><td><b>Kathmandu</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/np.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Nicaragua"><b>Nicaragua</b></a></td><td><b>NIC</b></td><td><b>ni</b></td><td><a href="505"><b>505</b></a></td><td><b>Managua</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ni.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Niger"><b>Niger</b></a></td><td><b>NER</b></td><td><b>ne</b></td><td><a href="227"><b>227</b></a></td><td><b>Niamey</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ne.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Nigeria"><b>Nigeria</b></a></td><td><b>NGA</b></td><td><b>ng</b></td><td><a href="234"><b>234</b></a></td><td><b>Abuja</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ng.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Niue"><b>Niue</b></a></td><td><b>NUI</b></td><td><b>nu</b></td><td><a href="683"><b>683</b></a></td><td><b>Alofi</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/nu.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Norway"><b>Norway</b></a></td><td><b>NOR</b></td><td><b>no</b></td><td><a href="47"><b>47</b></a></td><td><b>Oslo</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/no.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/New-Caledony"><b>New Caledonia</b></a></td><td><b>NCL</b></td><td><b>nc</b></td><td><a href="687"><b>687</b></a></td><td><b>Noumea</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/nc.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/New-Zealand"><b>New Zealand</b></a></td><td><b>NZL</b></td><td><b>nz</b></td><td><a href="64"><b>64</b></a></td><td><b>Wellington</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/nz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Oman"><b>Oman</b></a></td><td><b>OMN</b></td><td><b>om</b></td><td><a href="968"><b>968</b></a></td><td><b>Muscat</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/om.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Uganda"><b>Uganda</b></a></td><td><b>UGA</b></td><td><b>ug</b></td><td><a href="256"><b>256</b></a></td><td><b>Kampala</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ug.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Uzbekistan"><b>Uzbekistan</b></a></td><td><b>UZB</b></td><td><b>uz</b></td><td><a href="998"><b>998</b></a></td><td><b>Tashkent</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/uz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Pakistan"><b>Pakistan</b></a></td><td><b>PAK</b></td><td><b>pk</b></td><td><a href="92"><b>92</b></a></td><td><b>Islamabad</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Palau"><b>Palau</b></a></td><td><b>PLW</b></td><td><b>pw</b></td><td><a href="680"><b>680</b></a></td><td><b>Melekeok</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Palestine"><b>Palestine</b></a></td><td><b>PSE</b></td><td><b>ps</b></td><td><a href="970"><b>970</b></a></td><td><b>East Jerusalem</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ps.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Panama"><b>Panama</b></a></td><td><b>PAN</b></td><td><b>pa</b></td><td><a href="507"><b>507</b></a></td><td><b>Panama City</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pa.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Paraguay"><b>Paraguay</b></a></td><td><b>PRY</b></td><td><b>py</b></td><td><a href="595"><b>595</b></a></td><td><b>Asuncion</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/py.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Wales"><b>Wales</b></a></td><td><b>GBW</b></td><td><b>gb</b></td><td><a href="44"><b>44</b></a></td><td><b>London</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Netherlands"><b>Netherlands</b></a></td><td><b>NLD</b></td><td><b>nl</b></td><td><a href="31"><b>31</b></a></td><td><b>Amsterdam</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/nl.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Peru"><b>Peru</b></a></td><td><b>PER</b></td><td><b>pe</b></td><td><a href="51"><b>51</b></a></td><td><b>Lima</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pe.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Philippines"><b>Philippines</b></a></td><td><b>PHL</b></td><td><b>ph</b></td><td><a href="63"><b>63</b></a></td><td><b>Manila</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ph.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Poland"><b>Poland</b></a></td><td><b>POL</b></td><td><b>pl</b></td><td><a href="48"><b>48</b></a></td><td><b>Warsaw</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pl.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/polynesie"><b>French Polynesia</b></a></td><td><b>PYF</b></td><td><b>fr</b></td><td><a href="689"><b>689</b></a></td><td><b>Papeete</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Puerto-Rico"><b>Puerto Rico</b></a></td><td><b>PRI</b></td><td><b>pr</b></td><td><a href="1"><b>1</b></a></td><td><b>San Juan</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Portugal"><b>Portugal</b></a></td><td><b>PRT</b></td><td><b>pt</b></td><td><a href="351"><b>351</b></a></td><td><b>Lisbon</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pt.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Qatar"><b>Qatar</b></a></td><td><b>QAT</b></td><td><b>qa</b></td><td><a href="974"><b>974</b></a></td><td><b>Doha</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/qa.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Central-African-Republic"><b>Central African Republic</b></a></td><td><b>CAF</b></td><td><b>cf</b></td><td><a href="236"><b>236</b></a></td><td><b>Bangui</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cf.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Moldova"><b>Moldova</b></a></td><td><b>MDA</b></td><td><b>md</b></td><td><a href="373"><b>373</b></a></td><td><b>Chisinau</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/md.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Congo-RDC"><b>Democratic Republic of the Congo</b></a></td><td><b>COD</b></td><td><b>cd</b></td><td><a href="243"><b>243</b></a></td><td><b>Kinshasa</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cd.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Dominican-Republic"><b>Dominican Republic</b></a></td><td><b>DOM</b></td><td><b>do</b></td><td><a href="1809"><b>1809</b></a></td><td><b>Santo Domingo</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/do.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Iran"><b>Iran</b></a></td><td><b>IRN</b></td><td><b>ir</b></td><td><a href="98"><b>98</b></a></td><td><b>Tehran</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ir.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/North-Korea"><b>North Korea</b></a></td><td><b>PRK</b></td><td><b>kp</b></td><td><a href="850"><b>850</b></a></td><td><b>Pyongyang</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kp.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Laos"><b>Laos</b></a></td><td><b>LAO</b></td><td><b>la</b></td><td><a href="856"><b>856</b></a></td><td><b>Vientiane</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/la.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Czech-Republic"><b>Czech Republic</b></a></td><td><b>CZE</b></td><td><b>cz</b></td><td><a href="420"><b>420</b></a></td><td><b>Prague</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/cz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/La-Reunion"><b>Réunion</b></a></td><td><b>REU</b></td><td><b>fr</b></td><td><a href="262"><b>262</b></a></td><td><b>Saint-Denis</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/fr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Romania"><b>Romania</b></a></td><td><b>ROU</b></td><td><b>ro</b></td><td><a href="40"><b>40</b></a></td><td><b>Bucharest</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ro.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/United-Kingdom"><b>United Kingdom</b></a></td><td><b>GBR</b></td><td><b>gb</b></td><td><a href="44"><b>44</b></a></td><td><b>London</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/gb.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Russia"><b>Russia</b></a></td><td><b>RUS</b></td><td><b>ru</b></td><td><a href="7"><b>7</b></a></td><td><b>Moscow</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ru.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Rwanda"><b>Rwanda</b></a></td><td><b>RWA</b></td><td><b>rw</b></td><td><a href="250"><b>250</b></a></td><td><b>Kigali</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/rw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/St-Kitts-Nevis"><b>St. Kitts and Nevis</b></a></td><td><b>KNA</b></td><td><b>kn</b></td><td><a href="1869"><b>1869</b></a></td><td><b>Basseterre</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/kn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Saint-Pierre-and-Miquelon"><b>Saint-Pierre and Miquelon</b></a></td><td><b>SPM</b></td><td><b>pm</b></td><td><a href="508"><b>508</b></a></td><td><b>Saint-Pierre</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/pm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/St-Vincent-the-Grenadines"><b>St. Vincent and the Grenadines</b></a></td><td><b>VCT</b></td><td><b>vc</b></td><td><a href="1784"><b>1784</b></a></td><td><b>Kingstown</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/vc.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Saint-Helene"><b>St. Helena</b></a></td><td><b>SH</b></td><td><b>sh</b></td><td><a href="290"><b>290</b></a></td><td><b>Jamestown</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sh.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Saint-Lucia"><b>St. Lucia</b></a></td><td><b>LCA</b></td><td><b>lc</b></td><td><a href="1758"><b>1758</b></a></td><td><b>Castries</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lc.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/San-Marino"><b>San Marino</b></a></td><td><b>SMR</b></td><td><b>sm</b></td><td><a href="378"><b>378</b></a></td><td><b>San Marino</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/El-Salvador"><b>El Salvador</b></a></td><td><b>SLV</b></td><td><b>sv</b></td><td><a href="503"><b>503</b></a></td><td><b>San Salvador</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sv.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Samoa"><b>Samoa</b></a></td><td><b>WSM</b></td><td><b>ws</b></td><td><a href="685"><b>685</b></a></td><td><b>Apia</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ws.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Sao-Tome-Principe"><b>São Tomé and Príncipe</b></a></td><td><b>STP</b></td><td><b>st</b></td><td><a href="239"><b>239</b></a></td><td><b>Sao Tome</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/st.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Senegal"><b>Senegal</b></a></td><td><b>SEN</b></td><td><b>sn</b></td><td><a href="221"><b>221</b></a></td><td><b>Dakar</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Serbia"><b>Serbia</b></a></td><td><b>SRB</b></td><td><b>rs</b></td><td><a href="381"><b>381</b></a></td><td><b>Belgrade</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/rs.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Seychelles"><b>Seychelles</b></a></td><td><b>SYC</b></td><td><b>sc</b></td><td><a href="248"><b>248</b></a></td><td><b>Victoria</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sc.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/SierraLeone"><b>Sierra Leone</b></a></td><td><b>SLE</b></td><td><b>sl</b></td><td><a href="232"><b>232</b></a></td><td><b>Freetown</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sl.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Singapore"><b>Singapore</b></a></td><td><b>SGP</b></td><td><b>sg</b></td><td><a href="65"><b>65</b></a></td><td><b>Singapur</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Slovakia"><b>Slovakia</b></a></td><td><b>SVK</b></td><td><b>sk</b></td><td><a href="421"><b>421</b></a></td><td><b>Bratislava</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Slovenia"><b>Slovenia</b></a></td><td><b>SVN</b></td><td><b>si</b></td><td><a href="386"><b>386</b></a></td><td><b>Ljubljana</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/si.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Somalia"><b>Somalia</b></a></td><td><b>SOM</b></td><td><b>so</b></td><td><a href="252"><b>252</b></a></td><td><b>Mogadishu</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/so.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Sudan"><b>Sudan</b></a></td><td><b>SDN</b></td><td><b>sd</b></td><td><a href="249"><b>249</b></a></td><td><b>Khartoum</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sd.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Sri-Lanka"><b>Sri Lanka</b></a></td><td><b>LKA</b></td><td><b>lk</b></td><td><a href="94"><b>94</b></a></td><td><b>Colombo</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/lk.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Sweden"><b>Sweden</b></a></td><td><b>SWE</b></td><td><b>se</b></td><td><a href="46"><b>46</b></a></td><td><b>Stockholm</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/se.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Switzerland"><b>Switzerland</b></a></td><td><b>CHE</b></td><td><b>ch</b></td><td><a href="41"><b>41</b></a></td><td><b>Berne</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ch.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Suriname"><b>Surinam</b></a></td><td><b>SUR</b></td><td><b>sr</b></td><td><a href="597"><b>597</b></a></td><td><b>Paramaribo</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Swaziland"><b>Swaziland</b></a></td><td><b>SWZ</b></td><td><b>sz</b></td><td><a href="268"><b>268</b></a></td><td><b>Mbabane</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Syria"><b>Syria</b></a></td><td><b>SYR</b></td><td><b>sy</b></td><td><a href="963"><b>963</b></a></td><td><b>Damascus</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/sy.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Tajikistan"><b>Tajikistan</b></a></td><td><b>TJK</b></td><td><b>tj</b></td><td><a href="992"><b>992</b></a></td><td><b>Dushanbe</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tj.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Taiwan"><b>Taiwan</b></a></td><td><b>TWN</b></td><td><b>tw</b></td><td><a href="886"><b>886</b></a></td><td><b>Taipei</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Tanzania"><b>Tanzania</b></a></td><td><b>TZA</b></td><td><b>tz</b></td><td><a href="255"><b>255</b></a></td><td><b>Dodoma</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tz.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Chad"><b>Chad</b></a></td><td><b>TCD</b></td><td><b>td</b></td><td><a href="235"><b>235</b></a></td><td><b>NDjamena</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/td.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Diego-Garcia"><b>Diego Garcia</b></a></td><td><b>IOT</b></td><td><b>io</b></td><td><a href="246"><b>246</b></a></td><td><b>Diego Garcia</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/io.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Thailand"><b>Thailand</b></a></td><td><b>THA</b></td><td><b>th</b></td><td><a href="66"><b>66</b></a></td><td><b>Bangkok</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/th.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Timororiental"><b>East Timor</b></a></td><td><b>TLS</b></td><td><b>tl</b></td><td><a href="670"><b>670</b></a></td><td><b>Dili</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tl.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Togo"><b>Togo</b></a></td><td><b>TGO</b></td><td><b>tg</b></td><td><a href="228"><b>228</b></a></td><td><b>Lome</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tg.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Tonga"><b>Tonga</b></a></td><td><b>TON</b></td><td><b>to</b></td><td><a href="676"><b>676</b></a></td><td><b>Nukualofa</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/to.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Trinidad-Tobago"><b>Trinidad and Tobago</b></a></td><td><b>TTO</b></td><td><b>tt</b></td><td><a href="1868"><b>1868</b></a></td><td><b>Port of Spain</b></td><td><b>North America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tt.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Tunisia"><b>Tunisia</b></a></td><td><b>TUN</b></td><td><b>tn</b></td><td><a href="216"><b>216</b></a></td><td><b>Tunis</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Turkmenistan"><b>Turkmenistan</b></a></td><td><b>TKM</b></td><td><b>tm</b></td><td><a href="993"><b>993</b></a></td><td><b>Ashgabat</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Turkey"><b>Turkey</b></a></td><td><b>TUR</b></td><td><b>tr</b></td><td><a href="90"><b>90</b></a></td><td><b>Ankara</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tr.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Tuvalu"><b>Tuvalu</b></a></td><td><b>TUV</b></td><td><b>tv</b></td><td><a href="688"><b>688</b></a></td><td><b>Funafuti</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/tv.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Ukraine"><b>Ukraine</b></a></td><td><b>UKR</b></td><td><b>ua</b></td><td><a href="380"><b>380</b></a></td><td><b>Kiev</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ua.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Uruguay"><b>Uruguay</b></a></td><td><b>URY</b></td><td><b>uy</b></td><td><a href="598"><b>598</b></a></td><td><b>Montevideo</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/uy.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Vanutau"><b>Vanuatu</b></a></td><td><b>VUT</b></td><td><b>vu</b></td><td><a href="678"><b>678</b></a></td><td><b>Port Vila</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/vu.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Vatican-City"><b>Vatican City</b></a></td><td><b>VAT</b></td><td><b>va</b></td><td><a href="39"><b>39</b></a></td><td><b>Vatican City</b></td><td><b>Europe</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/va.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Venezuela"><b>Venezuela</b></a></td><td><b>VEN</b></td><td><b>ve</b></td><td><a href="58"><b>58</b></a></td><td><b>Caracas</b></td><td><b>South America</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ve.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Vietnam"><b>Vietnam</b></a></td><td><b>VNM</b></td><td><b>vn</b></td><td><a href="84"><b>84</b></a></td><td><b>Hanoi</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/vn.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Wallis-and-Futuna"><b>Wallis and Futuna</b></a></td><td><b>WLF</b></td><td><b>wf</b></td><td><a href="681"><b>681</b></a></td><td><b>Mata Utu</b></td><td><b>Oceania</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/wf.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Yemen"><b>Yemen</b></a></td><td><b>YEM</b></td><td><b>ye</b></td><td><a href="967"><b>967</b></a></td><td><b>Sanaa</b></td><td><b>Asia</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/ye.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Zambia"><b>Zambia</b></a></td><td><b>ZMB</b></td><td><b>zm</b></td><td><a href="260"><b>260</b></a></td><td><b>Lusaka</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/zm.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr></tr><tr><td><a href="https://country-codes.org/Zimbabwe"><b>Zimbabwe</b></a></td><td><b>ZWE</b></td><td><b>zw</b></td><td><a href="263"><b>263</b></a></td><td><b>Harare</b></td><td><b>Africa</b></td><td width="100px" heigt="80px"><b><img src="images/flags_thumbs/zw.gif" width="30px" heigt="15px" <="" b=""></b></td> </tr><tr> </tr></tbody>'
    savehtmltimezone = "*Africa/Abidjan:-968 *Africa/Accra:-968 *Africa/Addis_Ababa:10800 *Atlantic/Reykjavik:0 *Pacific/Guam:36000 *Europe/Jersey:3600 *America/Lower_Princes:14400 *Europe/Isle_of_Man:3600 *Pacific/Port_Moresby:36000 *Africa/Algiers:3600 *Africa/Asmara:10800 *Africa/Asmera:10800 *Africa/Bamako:-968 *Africa/Bangui:3600 *Africa/Banjul:-968 *Africa/Bissau:-3740 *Africa/Blantyre:7200 *Africa/Brazzaville:3600 *Africa/Bujumbura:7200 *Africa/Cairo:7200 *Africa/Casablanca:-1820 *Africa/Ceuta:-1276 *Africa/Conakry:-968 *Africa/Dakar:-968 *Africa/Dar_es_Salaam:10800 *Africa/Djibouti:10800 *Africa/Douala:3600 *Africa/El_Aaiun:-3168 *Africa/Freetown:-968 *Africa/Gaborone:7200 *Africa/Harare:7200 *Africa/Johannesburg:6720 *Africa/Juba:10800 *Africa/Kampala:10800 *Africa/Khartoum:10800 *Africa/Kigali:7200 *Africa/Kinshasa:3600 *Africa/Lagos:3600 *Africa/Libreville:3600 *Africa/Lome:-968 *Africa/Luanda:3600 *Africa/Lubumbashi:7200 *Africa/Lusaka:7200 *Africa/Malabo:3600 *Africa/Maputo:7200 *Africa/Maseru:6720 *Africa/Mbabane:6720 *Africa/Mogadishu:10800 *Africa/Monrovia:-2588 *Africa/Nairobi:10800 *Africa/Ndjamena:3600 *Africa/Niamey:3600 *Africa/Nouakchott:-968 *Africa/Ouagadougou:-968 *Africa/Porto-Novo:3600 *Africa/Sao_Tome:0 *Africa/Timbuktu:0 *Africa/Tripoli:3164 *Africa/Tunis:2444 *Africa/Windhoek:3600 *America/Adak:-36000 *America/Anchorage:-32400 *America/Anguilla:-14400 *America/Antigua:-14400 *America/Araguaina:-10800 *America/Argentina/Buenos_Aires:-10800 *America/Argentina/Catamarca:-10800 *America/Argentina/ComodRivadavia:-10800 *America/Argentina/Cordoba:-10800 *America/Argentina/Jujuy:-10800 *America/Argentina/La_Rioja:-10800 *America/Argentina/Mendoza:-10800 *America/Argentina/Rio_Gallegos:-10800 *America/Argentina/Salta:-10800 *America/Argentina/San_Juan:-10800 *America/Argentina/San_Luis:-10800 *America/Argentina/Tucuman:-10800 *America/Argentina/Ushuaia:-10800 *America/Aruba:-14400 *America/Asuncion:-10800 *America/Atikokan:-18000 *America/Atka:-36000 *America/Bahia:-10800 *America/Bahia_Banderas:-21600 *America/Barbados:-14309 *America/Belem:-10800 *America/Belize:-21168 *America/Blanc-Sablon:-14400 *America/Boa_Vista:-14400 *America/Bogota:-17776 *America/Boise:-25200 *America/Buenos_Aires:-10800 *America/Cambridge_Bay:-25200 *America/Campo_Grande:-13108 *America/Cancun:-18000 *America/Caracas:-14400 *America/Catamarca:-10800 *America/Cayenne:-10800 *America/Cayman:-18000 *America/Chicago:-21036 *America/Chihuahua:-25200 *America/Ciudad_Juarez:-25556 *America/Coral_Harbour:-18000 *America/Cordoba:-10800 *America/Costa_Rica:-20173 *America/Creston:-25200 *America/Cuiaba:-13460 *America/Curacao:-14400 *America/Danmarkshavn:-4480 *America/Dawson:-25200 *America/Dawson_Creek:-25200 *America/Denver:-25196 *America/Detroit:-18000 *America/Dominica:-14400 *America/Edmonton:-25200 *America/Eirunepe:-16768 *America/El_Salvador:-21408 *America/Ensenada:-28800 *America/Fort_Nelson:-25200 *America/Fort_Wayne:-18000 *America/Fortaleza:-10800 *America/Glace_Bay:-14388 *America/Godthab:-10800 *America/Goose_Bay:-14400 *America/Grand_Turk:-14400 *America/Grenada:-14400 *America/Guadeloupe:-14400 *America/Guatemala:-21600 *America/Guayaquil:-18000 *America/Guyana:-13959 *America/Halifax:-14400 *America/Havana:-18000 *America/Hermosillo:-25200 *America/Indiana/Indianapolis:-18000 *America/Indiana/Knox:-20790 *America/Indiana/Marengo:-18000 *America/Indiana/Petersburg:-18000 *America/Indiana/Tell_City:-20823 *America/Indiana/Vevay:-18000 *America/Indiana/Vincennes:-18000 *America/Indiana/Winamac:-18000 *America/Indianapolis:-18000 *America/Inuvik:-25200 *America/Iqaluit:-18000 *America/Jamaica:-18000 *America/Jujuy:-10800 *America/Juneau:-32400 *America/Kentucky/Louisville:-18000 *America/Kentucky/Monticello:-18000 *America/Knox_IN:-21600 *America/Kralendijk:-14400 *America/La_Paz:-14400 *America/Lima:-18000 *America/Los_Angeles:-28378 *America/Louisville:-18000 *America/Lower_Princes:-14400 *America/Maceio:-10800 *America/Managua:-20708 *America/Manaus:-14400 *America/Marigot:-14400 *America/Martinique:-14400 *America/Matamoros:-21600 *America/Mazatlan:-25200 *America/Mendoza:-10800 *America/Menominee:-21027 *America/Merida:-21508 *America/Metlakatla:-28800 *America/Mexico_City:-21600 *America/Miquelon:-10800 *America/Moncton:-14400 *America/Monterrey:-21600 *America/Montevideo:-10800 *America/Montreal:-18000 *America/Montserrat:-14400 *America/Nassau:-18000 *America/New_York:-17762 *America/Nipigon:-18000 *America/Nome:-32400 *America/Noronha:-7200 *America/North_Dakota/Beulah:-21600 *America/North_Dakota/Center:-21600 *America/North_Dakota/New_Salem:-21600 *America/Nuuk:-10800 *America/Ojinaga:-25060 *America/Panama:-18000 *America/Pangnirtung:-18000 *America/Paramaribo:-10800 *America/Phoenix:-25200 *America/Port-au-Prince:-17360 *America/Port_of_Spain:-14400 *America/Porto_Acre:-18000 *America/Porto_Velho:-14400 *America/Puerto_Rico:-14400 *America/Punta_Arenas:-10800 *America/Rainy_River:-21600 *America/Rankin_Inlet:-21600 *America/Recife:-10800 *America/Regina:-21600 *America/Resolute:-21600 *America/Rio_Branco:-16272 *America/Rosario:-10800 *America/Santa_Isabel:-28800 *America/Santarem:-10800 *America/Santiago:-10800 *America/Santo_Domingo:-14400 *America/Sao_Paulo:-10800 *America/Scoresbysund:-3600 *America/Shiprock:-25200 *America/Sitka:-32400 *America/St_Barthelemy:-14400 *America/St_Johns:-12600 *America/St_Kitts:-14400 *America/St_Lucia:-14400 *America/St_Thomas:-14400 *America/St_Vincent:-14400 *America/Swift_Current:-21600 *America/Tegucigalpa:-20932 *America/Thule:-14400 *America/Thunder_Bay:-18000 *America/Tijuana:-28084 *America/Toronto:-18000 *America/Tortola:-14400 *America/Vancouver:-28800 *America/Virgin:-14400 *America/Whitehorse:-25200 *America/Winnipeg:-21600 *America/Yakutat:-32400 *America/Yellowknife:-25200 *Antarctica/Casey:0 *Antarctica/Davis:0 *Antarctica/DumontDUrville:35320 *Antarctica/Macquarie:0 *Antarctica/Mawson:0 *Antarctica/McMurdo:41944 *Antarctica/Palmer:-10800 *Antarctica/Rothera:-10800 *Antarctica/South_Pole:43200 *Antarctica/Syowa:10800 *Antarctica/Troll:0 *Antarctica/Vostok:21020 *Arctic/Longyearbyen:3208 *Asia/Aden:10800 *Asia/Almaty:18468 *Asia/Amman:7200 *Asia/Anadyr:42596 *Asia/Aqtau:12064 *Asia/Aqtobe:13720 *Asia/Ashgabat:14012 *Asia/Ashkhabad:18000 *Asia/Atyrau:12464 *Asia/Baghdad:10660 *Asia/Bahrain:10800 *Asia/Baku:11964 *Asia/Bangkok:24124 *Asia/Barnaul:20100 *Asia/Beirut:7200 *Asia/Bishkek:17904 *Asia/Brunei:26480 *Asia/Calcutta:19800 *Asia/Chita:27232 *Asia/Choibalsan:27480 *Asia/Chongqing:28800 *Asia/Chungking:28800 *Asia/Colombo:19164 *Asia/Dacca:21600 *Asia/Damascus:7200 *Asia/Dhaka:21600 *Asia/Dili:30140 *Asia/Dubai:13272 *Asia/Dushanbe:16512 *Asia/Famagusta:7200 *Asia/Gaza:7200 *Asia/Harbin:28800 *Asia/Hebron:7200 *Asia/Ho_Chi_Minh:25200 *Asia/Hong_Kong:27402 *Asia/Hovd:21996 *Asia/Irkutsk:25025 *Asia/Istanbul:7200 *Asia/Jakarta:25200 *Asia/Jayapura:32400 *Asia/Jerusalem:7200 *Asia/Kabul:16200 *Asia/Kamchatka:38076 *Asia/Karachi:16092 *Asia/Kashgar:21600 *Asia/Kathmandu:20476 *Asia/Katmandu:20700 *Asia/Khandyga:32400 *Asia/Kolkata:19800 *Asia/Krasnoyarsk:22286 *Asia/Kuala_Lumpur:24925 *Asia/Kuching:26480 *Asia/Kuwait:10800 *Asia/Macao:28800 *Asia/Macau:27250 *Asia/Magadan:36000 *Asia/Makassar:28656 *Asia/Manila:-57360 *Asia/Muscat:13272 *Asia/Nicosia:7200 *Asia/Novokuznetsk:20928 *Asia/Novosibirsk:19900 *Asia/Omsk:17610 *Asia/Oral:12324 *Asia/Phnom_Penh:24124 *Asia/Pontianak:25200 *Asia/Pyongyang:30180 *Asia/Qatar:10800 *Asia/Qostanay:15268 *Asia/Qyzylorda:15712 *Asia/Rangoon:23400 *Asia/Riyadh:10800 *Asia/Riyadh87:10800 *Asia/Riyadh88:10800 *Asia/Riyadh89:10800 *Asia/Saigon:25200 *Asia/Sakhalin:34248 *Asia/Samarkand:16073 *Asia/Seoul:30472 *Asia/Shanghai:28800 *Asia/Singapore:24925 *Asia/Srednekolymsk:36892 *Asia/Taipei:28800 *Asia/Tashkent:16631 *Asia/Tbilisi:10751 *Asia/Tehran:12344 *Asia/Tel_Aviv:7200 *Asia/Thimbu:21600 *Asia/Thimphu:21516 *Asia/Tokyo:32400 *Asia/Tomsk:20391 *Asia/Ujung_Pandang:28800 *Asia/Ulaanbaatar:25652 *Asia/Ulan_Bator:28800 *Asia/Urumqi:21020 *Asia/Ust-Nera:34374 *Asia/Vientiane:24124 *Asia/Vladivostok:31651 *Asia/Yakutsk:31138 *Asia/Yangon:23087 *Asia/Yekaterinburg:14553 *Asia/Yerevan:10680 *Atlantic/Azores:-3600 *Atlantic/Bermuda:-14400 *Atlantic/Canary:-3696 *Atlantic/Cape_Verde:-3600 *Atlantic/Faeroe:0 *Atlantic/Faroe:-1624 *Atlantic/Jan_Mayen:3600 *Atlantic/Madeira:-4056 *Atlantic/Reykjavik:-968 *Atlantic/South_Georgia:-7200 *Atlantic/St_Helena:-968 *Atlantic/Stanley:-10800 *Australia/ACT:36000 *Australia/Adelaide:33260 *Australia/Brisbane:36000 *Australia/Broken_Hill:33948 *Australia/Canberra:36000 *Australia/Currie:36000 *Australia/Darwin:31400 *Australia/Eucla:30928 *Australia/Hobart:35356 *Australia/LHI:37800 *Australia/Lindeman:35756 *Australia/Lord_Howe:37800 *Australia/Melbourne:34792 *Australia/NSW:36000 *Australia/North:34200 *Australia/Perth:27804 *Australia/Queensland:36000 *Australia/South:34200 *Australia/Sydney:36000 *Australia/Tasmania:36000 *Australia/Victoria:36000 *Australia/West:28800 *Australia/Yancowinna:34200 *Brazil/Acre:-18000 *Brazil/DeNoronha:-7200 *Brazil/East:-10800 *Brazil/West:-14400 *CET:3600 *CST6CDT:-21600 *Canada/Atlantic:-14400 *Canada/Central:-21600 *Canada/East-Saskatchewan:-21600 *Canada/Eastern:-18000 *Canada/Mountain:-25200 *Canada/Newfoundland:-12600 *Canada/Pacific:-28800 *Canada/Saskatchewan:-21600 *Canada/Yukon:-28800 *Chile/Continental:-10800 *Chile/EasterIsland:-18000 *Cuba:-18000 *EET:7200 *EST:-18000 *EST5EDT:-18000 *Egypt:7200 *Eire:0 *Etc/GMT:0 *Etc/GMT+0:0 *Etc/GMT+1:-3600 *Etc/GMT+10:-36000 *Etc/GMT+11:-39600 *Etc/GMT+12:-43200 *Etc/GMT+2:-7200 *Etc/GMT+3:-10800 *Etc/GMT+4:-14400 *Etc/GMT+5:-18000 *Etc/GMT+6:-21600 *Etc/GMT+7:-25200 *Etc/GMT+8:-28800 *Etc/GMT+9:-32400 *Etc/GMT-0:0 *Etc/GMT-1:3600 *Etc/GMT-10:36000 *Etc/GMT-11:39600 *Etc/GMT-12:43200 *Etc/GMT-13:46800 *Etc/GMT-14:50400 *Etc/GMT-2:7200 *Etc/GMT-3:10800 *Etc/GMT-4:14400 *Etc/GMT-5:18000 *Etc/GMT-6:21600 *Etc/GMT-7:25200 *Etc/GMT-8:28800 *Etc/GMT-9:32400 *Etc/GMT0:0 *Etc/Greenwich:0 *Etc/UCT:0 *Etc/UTC:0 *Etc/Universal:0 *Etc/Zulu:0 *Europe/Amsterdam:1050 *Europe/Andorra:3600 *Europe/Astrakhan:11532 *Europe/Athens:5692 *Europe/Belfast:0 *Europe/Belgrade:3600 *Europe/Berlin:3208 *Europe/Bratislava:3464 *Europe/Brussels:1050 *Europe/Bucharest:6264 *Europe/Budapest:3600 *Europe/Busingen:2048 *Europe/Chisinau:6920 *Europe/Copenhagen:3208 *Europe/Dublin:-1521 *Europe/Gibraltar:-1284 *Europe/Guernsey:-75 *Europe/Helsinki:5989 *Europe/Isle_of_Man:-75 *Europe/Istanbul:10800 *Europe/Jersey:-75 *Europe/Kaliningrad:4920 *Europe/Kiev:7200 *Europe/Kirov:10800 *Europe/Kyiv:7324 *Europe/Lisbon:-2205 *Europe/Ljubljana:3600 *Europe/London:-75 *Europe/Luxembourg:1050 *Europe/Madrid:-884 *Europe/Malta:3484 *Europe/Mariehamn:5989 *Europe/Minsk:10800 *Europe/Monaco:3600 *Europe/Moscow:10800 *Europe/Nicosia:7200 *Europe/Oslo:3208 *Europe/Paris:3600 *Europe/Podgorica:3600 *Europe/Prague:3464 *Europe/Riga:5794 *Europe/Rome:2996 *Europe/Samara:12020 *Europe/San_Marino:2996 *Europe/Sarajevo:3600 *Europe/Saratov:11058 *Europe/Simferopol:10800 *Europe/Skopje:3600 *Europe/Sofia:5596 *Europe/Stockholm:3208 *Europe/Tallinn:5940 *Europe/Tirane:3600 *Europe/Tiraspol:7200 *Europe/Ulyanovsk:11616 *Europe/Uzhgorod:7200 *Europe/Vaduz:2048 *Europe/Vatican:2996 *Europe/Vienna:3600 *Europe/Vilnius:6076 *Europe/Volgograd:10660 *Europe/Warsaw:3600 *Europe/Zagreb:3600 *Europe/Zaporozhye:7200 *Europe/Zurich:2048 *Factory:0 *GB:0 *GB-Eire:0 *GMT:0 *GMT+0:0 *GMT-0:0 *GMT0:0 *Greenwich:0 *HST:-36000 *Hongkong:28800 *Iceland:0 *Indian/Antananarivo:10800 *Indian/Chagos:17380 *Indian/Christmas:24124 *Indian/Cocos:23087 *Indian/Comoro:10800 *Indian/Kerguelen:17640 *Indian/Mahe:13272 *Indian/Maldives:17640 *Indian/Mauritius:13800 *Indian/Mayotte:10800 *Indian/Reunion:13272 *Iran:12600 *Israel:7200 *Jamaica:-18000 *Japan:32400 *Kwajalein:43200 *Libya:7200 *MET:3600 *MST:-25200 *MST7MDT:-25200 *Mexico/BajaNorte:-28800 *Mexico/BajaSur:-25200 *Mexico/General:-21600 *Mideast/Riyadh87:0 *Mideast/Riyadh88:0 *Mideast/Riyadh89:0 *NZ:43200 *NZ-CHAT:45900 *Navajo:0 *PRC:0 *PST8PDT:0 *Pacific/Apia:45184 *Pacific/Auckland:41944 *Pacific/Bougainville:37336 *Pacific/Chatham:44028 *Pacific/Chuuk:35320 *Pacific/Easter:-18000 *Pacific/Efate:39600 *Pacific/Enderbury:46800 *Pacific/Fakaofo:-41096 *Pacific/Fiji:42944 *Pacific/Funafuti:41524 *Pacific/Galapagos:-21504 *Pacific/Gambier:-32388 *Pacific/Guadalcanal:38388 *Pacific/Guam:-51660 *Pacific/Honolulu:-36000 *Pacific/Johnston:-36000 *Pacific/Kanton:0 *Pacific/Kiritimati:-37760 *Pacific/Kosrae:-47284 *Pacific/Kwajalein:40160 *Pacific/Majuro:41524 *Pacific/Marquesas:-33480 *Pacific/Midway:-39600 *Pacific/Nauru:40060 *Pacific/Niue:-39600 *Pacific/Norfolk:39600 *Pacific/Noumea:39600 *Pacific/Pago_Pago:-39600 *Pacific/Palau:-54124 *Pacific/Pitcairn:-28800 *Pacific/Pohnpei:38388 *Pacific/Ponape:39600 *Pacific/Port_Moresby:35320 *Pacific/Rarotonga:-36000 *Pacific/Saipan:-51660 *Pacific/Samoa:-39600 *Pacific/Tahiti:-35896 *Pacific/Tarawa:41524 *Pacific/Tongatapu:44352 *Pacific/Truk:36000 *Pacific/Wake:41524 *Pacific/Wallis:41524 *Pacific/Yap:36000 *Poland:3600 *Portugal:0 *ROC:28800 *ROK:32400 *Singapore:28800 *Turkey:7200 *UCT:0 *US/Alaska:-32400 *US/Aleutian:-36000 *US/Arizona:-25200 *US/Central:-21600 *US/East-Indiana:-18000 *US/Eastern:-18000 *US/Hawaii:-36000 *US/Indiana-Starke:-21600 *US/Michigan:-18000 *US/Mountain:-25200 *US/Pacific:-28800 *US/Pacific-New:-28800 *US/Samoa:-39600 *UTC:0 *Universal:0 *W-SU:10800 *WET:0 *Zulu:0 "
    geolist = [     "Australia|en-AU",     "Austria|de-AT",     "Azerbaijan|az-Latn-AZ",     "Albania|sq-AL",     "Algeria|ar-DZ",     "Argentina|es-AR",     "Armenia|hy-AM",     "Afghanistan|ps-AF",     "Bangladesh|bn-BD",     "Bahrain|ar-BH",     "Belarus|be-BY",     "Belize|en-BZ",     "Belgium|fr-BE",     "Belgium|nl-BE",     "Bulgaria|bg-BG",     "Bolivia|es-BO",     "Bolivia|quz-BO",     "Bosnia and Herzegovina|bs-Cyrl-BA",     "Bosnia and Herzegovina|bs-Latn-BA",     "Bosnia and Herzegovina|hr-BA",     "Bosnia and Herzegovina|sr-Cyrl-BA",     "Brazil|pt-BR",     "Brunei Darussalam|ms-BN",     "Former Yugoslav Republic of Macedonia|mk-MK",     "United Kingdom|en-GB",     "Hungary|hu-HU",     "Venezuela|es-VE",     "Vietnam|vi-VN",     "Galicia|gl-ES",     "Guatemala|es-GT",     "Germany|de-DE",     "Honduras|es-HN",     "Hong Kong|zh-HK",     "Greece|el-GR",     "Georgia|ka-GE",     "Denmark|da-DK",     "Dominican Republic|es-DO",     "Egypt|ar-EG",     "Zimbabwe|en-ZW",     "Israel|he-IL",     "India|hi-IN",     "Indonesia|id-ID",     "Jordan|ar-JO",     "Iraq|ar-IQ",     "Iran|fa-IR",     "Ireland|en-IE",     "Ireland|ga-IE",     "The Islamic Republic of Pakistan|ur-PK",     "Iceland|is-IS",     "Spain|es-ES",     "Italy|it-IT",     "Yemen|ar-YE",     "China|zh-CN",     "Kazakhstan|kk-KZ",     "Cambodia|km-KH",     "Canada|en-CA",     "Canada|fr-CA",     "The Caribbean|en-029",     "Catalonia|ca-ES",     "Qatar|ar-QA",     "Kenya|sw-KE",     "Kyrgyzstan|ky-KG",     "Colombia|es-CO",     "Costa Rica|es-CR",     "Kuwait|ar-KW",     "Latvia|lv-LV",     "Lebanon|ar-LB",     "Libya|ar-LY",     "Lithuania|lt-LT",     "Liechtenstein|de-LI",     "Luxembourg|de-LU",     "Luxembourg|fr-LU",     "Luxembourg|lb-LU",     "Macau|zh-MO",     "Malaysia|ms-MY",     "The Maldives|dv-MV",     "Malta|mt-MT",     "Morocco|ar-MA",     "Mexico|es-MX",     "The Mohawk|moh-CA",     "Moldova|ru-MO",     "Monaco|fr-MC",     "Mongolia|mn-MN",     "Nepal|ne-NP",     "Nigeria|ig-NG",     "Nigeria|yo-NG",     "Netherlands|fy-NL",     "Netherlands|nl-NL",     "Nicaragua|es-NI",     "New Zealand|en-NZ",     "New Zealand|mi-NZ",     "Norway|nb-NO",     "Norway|nn-NO",     "Norway|se-NO",     "Norway|sma-NO",     "Norway|smj-NO",     "UAE|ar-AE",     "Oman|ar-OM",     "Panama|es-PA",     "Paraguay|es-PY",     "Peru|es-PE",     "Peru|quz-PE",     "Poland|pl-PL",     "portugal|pt-PT",     "puerto rico|es-PR",     "Republic of Korea|ko-KR",     "Republic of senegal|wo-SN",     "Republic of the philippines|en-PH",     "Czech republic|cs-CZ",     "Russia|ru-RU",     "Romania|ro-RO",     "US|en-US",     "El Salvador|es-SV",     "Saudi Arabia|ar-SA",     "Serbia|sr-Cyrl-CS",     "Serbia|sr-Latn-CS",     "Serbia|sr-SP-Cyrl",     "Singapore|zh-SG",     "Syria|ar-SY",     "Syria|syr-SY",     "Slovakia|sk-SK",     "Slovenia|sl-SI",     "United Kingdom|cy-GB",     "Basque Country|eu-ES",     "Tajikistan|tg-Cyrl-TJ",     "Thailand|th-TH",     "Taiwan|zh-TW",     "Trinidad and Tobago|en-TT",     "Tunisia|ar-TN",     "Turkey|tr-TR",     "Uzbekistan|uz-Latn-UZ",     "Ukraine|uk-UA",     "Uruguay|es-UY",     "Faroe Islands|fo-FO",     "Philippines|fil-PH",     "Finland|fi-FI",     "Finland|smn-FI",     "Finland|sms-FI",     "Finland|sv-FI",     "France|fr-FR",     "Croatia|hr-HR",     "Chile|arn-CL",     "Chile|es-CL",     "Switzerland|de-CH",     "Switzerland|fr-CH",     "Switzerland|it-CH",     "Switzerland|rm-CH",     "Sweden|se-SE",     "Sweden|sma-SE",     "Sweden|smj-SE",     "Sweden|sv-SE",     "Sri Lanka|si-LK",     "Ecuador|es-EC",     "Ecuador|quz-EC",     "Estonia|et-EE",     "Ethiopia|am-ET",     "South Africa|af-ZA",     "South Africa|en-ZA",     "South Africa|nso-ZA",     "South Africa|tn-ZA",     "South Africa|xh-ZA",     "South Africa|zu-ZA",     "Jamaica|en-JM",     "Japan|ja-JP"     ]

    while True:
       
        conn = sqlite3.connect('total.db')
        cursor = conn.cursor()
        while True:
            try:
                # Сначала получаем количество строк в таблице
                
                cursor.execute(f"SELECT COUNT(*) FROM proxygroup_{proxy_group}")
                count = cursor.fetchone()[0]
                
                # Затем вычисляем случайное смещение
                random_offset = random.randint(0, count - 1)
                
                # Выполняем запрос с использованием вычисленного смещения
                cursor.execute(f"SELECT * FROM proxygroup_{proxy_group} LIMIT 1 OFFSET {random_offset}")
                random_row = cursor.fetchone()
                break
            except:
                print('OK ERROR. WAIT PROXY REFRESH')
                continue
        conn.close()
        
        
        ip,port,log,pas,typeproxy,linkUpdate = random_row

        if log == '':
            proxystring = ip+":"+port
        else:
           proxystring = log+":"+pas+"@"+ip+":"+port
        print(proxystring)

        if typeproxy == 'socks5':
            proxies = {
                'http': 'socks5://'+proxystring+'',
                'https': 'socks5://'+proxystring+''
            }
        else:
            proxies = {
                'http': 'http://'+proxystring+'',
                'https': 'http://'+proxystring+''
            }
            
        if proxy_method_dropdown == "Manual":
            accept_ln = re.findall('.*\>(.*)', proxy_method_manual_dropdown)
            accept_ln = accept_ln[0]
            ig_locale = accept_ln.replace('-', '_')
            ig_locale_startup = accept_ln.split('-')[-1]
            ig_locale_startupmin =  ig_locale_startup.lower()
            
            timezonename = proxy_method_manual2_dropdown.split(':')[0]
            timezone = proxy_method_manual2_dropdown.split(':')[1]
            timezone = str(timezone)
            timezone = timezone.replace('+', '')
            timezone = timezone.replace('-', '')
            print('accept_ln: '+accept_ln)
            print('ig_locale: '+ig_locale)
            print('ig_locale_startup: '+ig_locale_startup)
            print('timezone: '+timezone)
            print('timezonename: '+timezonename)
            
        if proxy_method_dropdown == "IP-API":
            try:
                response = requests.get('https://pro.ip-api.com/json/?key=niMr70clVRi33Yx', proxies=proxies,  timeout=60, verify=False)
            except Exception as exc:
                print('[#0160] FAIL CONNECT '+str(exc))
                if 'HTTPConnectionPool' in str(exc):
                    time.sleep(randint(1, 10))   
                continue
            try:
                ipreal = json.loads(response.text)['query']
                ipreal = str(ipreal)
                timezonename = json.loads(response.text)['timezone']    
                timezone = re.findall('\*'+timezonename+':(.*?)\ ', savehtmltimezone)
                timezone = str(timezone[0])
                timezone = timezone.replace('+', '')
                timezone = timezone.replace('-', '')
                ig_locale_startup = json.loads(response.text)['countryCode']
                treehtml = etree.HTML(savehtmlcountry)

            except Exception as exc:

                print('[#0160IP-API] ERROR GET INFO PROXY ['+response.text+'] ['+proxystring+']')
                continue
     

                                
            for val in geolist:
                locale = re.findall('.*\|(.+\-'+ig_locale_startup+')', val)
                try:
                    accept_ln = locale[0]
                    web_locale = ''+accept_ln+','+ig_locale_startup.lower()+';q=0.9,en-US;q=0.8,en;q=0.7'

                    ig_locale = accept_ln.replace('-', '_')
                    break
                except:
                    continue    
            
        
        return proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename

def authorize_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename):


    print('accept_ln: '+accept_ln)
    print('ig_locale: '+ig_locale)
    print('ig_locale_startup: '+ig_locale_startup)
    print('timezone: '+timezone)
    print('timezonename: '+timezonename)
    timereal = gettimereal(timezonename)
    print('timereal: '+str(timereal))
    print('proxies: '+str(proxies))
    while True:
        try:
            headers = {
                "x-ig-mapped-locale": ig_locale,
                "x-pigeon-session-id": session_id,
                "x-pigeon-rawclienttime": timereal,
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-app-startup-country": ig_locale_startup,
                "x-bloks-version-id": xbloksversionid,
                "x-ig-www-claim": claim,
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-is-panorama-enabled": "true",
                "x-ig-device-id": device_id,
                "x-ig-family-device-id": phone_id,
                "x-ig-android-id": "android-"+android,
                "x-ig-timezone-offset": timezone,
                "x-ig-nav-chain": '8XD:self_profile:11,ProfileMediaTabFragment:self_profile:12,4DP:bottom_sheet_profile:13,6ki:settings_category_options:14,7T8:landing_facebook:15,7T8:landing_facebook:16',
                "x-ig-connection-type": 'WIFI',
                "x-ig-capabilities": xigcapabilities,
                "x-ig-app-id": '567067343352427',
                "priority": "u=3",
                "user-agent": api_ua,
                "accept-language": accept_ln,
                "authorization": authorization,
                "x-mid": mid,
                "ig-u-ds-user-id": ds_user_id,
                "ig-u-rur": rur,
                "ig-intended-user-id": ds_user_id,
                "accept-encoding": "gzip, deflate",
                "x-fb-http-engine": "Liger",
                "x-fb-client-ip": "True",
                "x-fb-server-cluster": "True",
                'Connection': 'close'
            }
            response = requests.get('https://i.instagram.com/api/v1/accounts/current_user/?edit=true', headers=headers, timeout=60, proxies=proxies, verify=False)
            print(response.text)
            if 'login_required' in response.text or 'user_has_logged_out' in response.text or 'not-logged-in' in response.text or '","require_login":true,"status":"fail"' in response.text:
                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = login_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)
                if statusDef == "GOOD":

                    return 'GOOD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename

                else:
                    return 'BAD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename
            if 'ip_block' in response.text or 'sentry_block' in response.text or 'an error occurred' in response.text or 'consent_data' in response.text or 'DOCTYPE html' in response.text:
                print('CURR #CURR IP_BLOCK')
                
                proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                continue
            if login in response.text:   
                mid, csrftoken, sessionid, rur, ds_user_id, authorization, claim = getCookies(response, mid, csrftoken, sessionid, rur, ds_user_id, authorization, claim)

                return 'GOOD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename
            else:
                return 'BAD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename
  
        except Exception as exc:
            print('[#01s63] fail connect login ['+str(exc)+']')
            proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
            continue
            
def login_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename):


    timereal = gettimereal(timezonename)
    password_crypto = '#PWD_INSTAGRAM:0:0:'+password
    symbols = phone_id
    amount = sum(ord(s) for s in symbols)
    jazoest = '2'+str(amount)
    timereal_password = time.time()
    timereal_password = str(timereal_password)[:-4]
    timereal_password = timereal_password.replace('.', '')
    randombytesstr = secrets.token_bytes(24)
    sn_nonce = base64.b64encode(bytes('|'+timereal_password+'|'+str(randombytesstr), 'utf-8'))
    sn_nonce = sn_nonce.decode("utf-8")
    countrymobilecode = '7'
    postdata = 'signed_body=SIGNATURE.{"jazoest":"'+jazoest+'","country_codes":"[{\\"country_code\\":\\"'+countrymobilecode+'\\",\\"source\\":[\\"default\\"]}]","phone_id":"'+phone_id+'","enc_password":"'+password_crypto+'","_csrftoken":"'+csrftoken+'","username":"'+login+'","adid":"'+adid_id+'","guid":"'+device_id+'","device_id":"'+device_id+'","google_tokens":"[]","login_attempt_count":"0"}'


    postdata = urllib.parse.quote(postdata)
    postdata = postdata.replace('signed_body%3D', 'signed_body=')
    postdata = postdata.replace('/', '%2F')
    while True:
        try:
            headers = {
            "x-ig-app-locale": ig_locale,
            "x-ig-device-locale": ig_locale,
            "x-ig-mapped-locale": ig_locale,
            "x-pigeon-session-id": session_id,
            "x-pigeon-rawclienttime": timereal,
            "x-ig-bandwidth-speed-kbps": "-1.000",
            "x-ig-bandwidth-totalbytes-b": "0",
            "x-ig-bandwidth-totaltime-ms": "0",
            "x-bloks-version-id": xbloksversionid,
            "x-ig-www-claim": "0",
            "x-bloks-is-layout-rtl": "false",
            "x-bloks-is-panorama-enabled": "true",
            "x-ig-device-id": device_id,
            "x-ig-family-device-id": phone_id,
            "x-ig-android-id": "android-"+android,
            "x-ig-timezone-offset": timezone,
            "x-ig-connection-type": 'WIFI',
            "x-ig-capabilities": xigcapabilities,
            "x-ig-app-id": '567067343352427',
            "priority": "u=3",
            "user-agent": api_ua,
            "accept-language": accept_ln,
            #"x-mid": mid,
            "ig-intended-user-id": "0",
            "accept-encoding": "gzip, deflate",
            "x-fb-http-engine": "Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True",
            "Content-Type": "application/x-www-form-urlencoded"
            }
            
            
            
            try:
                response = requests.post('https://i.instagram.com/api/v1/accounts/login/', headers=headers, timeout=30, data=postdata, proxies=proxies)
                print(response.text)
                if response.status_code == 429:
                    print('REG #429 LOGIN')
                    proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                    continue
                else:
                    if 'ip_block' in response.text or 'sentry_block' in response.text or 'an error occurred' in response.text or 'consent_data' in response.text or 'DOCTYPE html' in response.text:
                        print('REG #LOGIN IP_BLOCK')
                        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                        continue

            except:
                print('[#0163] fail connect login')
                proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                continue  
                  
            if "bad_password" in response.text:    
                return 'BAD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename  


            if login in response.text:    
                mid, csrftoken, sessionid, rur, ds_user_id, authorization, claim = getCookies(response, mid, csrftoken, sessionid, rur, ds_user_id, authorization, claim)
                return 'GOOD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename   
            else:
                return 'BAD',login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename  
  
        except Exception as exc:

            print('ERROR API CHECK VALIDITY ['+str(exc)+']')
         
def check_validity_thread(account_queue, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown):

    
    
    while not account_queue.empty():
        massiveAcc,row = account_queue.get()
        login,password,device,api_ua,cookie = massiveAcc
        print('login: '+str(login))
        print('password: '+str(password))
        print('device: '+str(device))
        print('cookie: '+str(cookie))
        print('api_ua: '+str(api_ua))
        
        if device == "":

            android = ''.join([random.choice('abcdef0123456789') for _ in range(16)])
            device_id = f"{generate_random_string(8)}-{generate_random_string(1)}663-4{generate_random_string(3)}-{generate_random_string(4)}-{generate_random_string(12)}"
            phone_id = f"{generate_random_string(8)}-{generate_random_string(4)}-4{generate_random_string(3)}-{generate_random_string(4)}-{generate_random_string(12)}"

            adid_id = str(uuid.uuid4())
            infoDevice_queue.put((login, 'android-'+android+';'+phone_id+';'+device_id+';'+adid_id+'', row))
        else:
            devicelist = device.split(";")
            android = devicelist[0]
            phone_id = devicelist[1]
            device_id = devicelist[2]
            adid_id = devicelist[3] 
        session_id = 'UFS-'+str(uuid.uuid4())+'-0'

        if api_ua == "":
            api_ua = spintax.spin('{2{5|6|7|8|9}/{1|2|3|4|5|6|7|8|9|0}.{1|2|3|4|5|6|7|8|9|0}}; {480dpi|320dpi|420dpi|380dpi|640dpi|240dpi}; {1080x1920|1080x2076|1080x1794|1440x2392|1440x2560|480x854|720x1280}; {{Nokia}; {600|600|3208 classic|3208 classic|X2-05|X2-05|C2-05|C2-05|C1-02|C1-02|C1-01|C1-01|E73 Mode|E73 Mode|8.3 5G|8.3 5G|5310 (2020)|5310 (2020)|2.3|2.3|800 Tough|800 Tough|4.2|4.2|1 Plus|1 Plus|2.2|2.2|6.2|6.2|7.2|7.2|3.2|3.2|9 PureView|9 PureView|8.1|8.1|6.1 Plus|6.1 Plus|3.1 Plus|3.1 Plus|7.1|7.1|5.1 Plus|5.1 Plus|5.1|5.1|2.1|2.1|3.1|3.1|8 Sirocco|8 Sirocco|8110 4G|8110 4G|7 Plus|7 Plus|1|1|6.1|6.1|7|7|2|2|8|8|3310 (2017)|3310 (2017)|5|5|3|3|6|6|Lumia 730 Dual Sim|Lumia 730 Dual Sim|Lumia 830|Lumia 830|Lumia 735|Lumia 735|Lumia 530|Lumia 530|X2|X2|Lumia 635|Lumia 635|Lumia 630|Lumia 630|Lumia 930|Lumia 930|X|X|XL|XL|Asha 503 DS|Asha 503 DS|Lumia 1320|Lumia 1320|Lumia 928|Lumia 928|Lumia 525|Lumia 525|Lumia 1520|Lumia 1520|Lumia 625|Lumia 625|Lumia 1020|Lumia 1020|Lumia 925|Lumia 925|Asha 205 Dual Sim|Asha 205 Dual Sim|Lumia 720|Lumia 720|Lumia 822|Lumia 822|Lumia 520|Lumia 520|Lumia 505|Lumia 505|Lumia 620|Lumia 620|Lumia 510|Lumia 510|Asha 302|Asha 302|Lumia 920|Lumia 920|Lumia 820|Lumia 820|Asha 305|Asha 305|Lumia 610|Lumia 610|808 PureView|808 PureView|Lumia 900|Lumia 900|Asha 303|Asha 303|Asha 200|Asha 200|C5-05|C5-05|101|101|Asha 300|Asha 300|Asha 201|Asha 201|Lumia 710|Lumia 710|Lumia 800|Lumia 800|603|603|C5-06|C5-06|N950|N950|701|701|500|500|700|700|C5-00 5MP|C5-00 5MP|C2-03|C2-03|C2-06|C2-06|N9|N9|Oro|Oro|X7-00|X7-00|E6-00|E6-00|C2-01|C2-01|C3-01|C3-01|E7-00|E7-00|X2-01|X2-01|C5-03|C5-03|C6-01|C6-01|C7-00|C7-00|5250|5250|X3-02|X3-02|5330 XpressMusic|5330 XpressMusic|5228|5228|C5-01|C5-01|C2-00|C2-00|X5-01|X5-01|X2-00|X2-00|N8|N8|E5-00|E5-00|C6-00|C6-00|C3-00|C3-00|C5-00|C5-00|6303i classic|6303i classic|5235 Comes With Music|5235 Comes With Music|6700 slide|6700 slide|7230|7230|5330 Mobile TV Edition|5330 Mobile TV Edition|2220 slide|2220 slide|2690|2690|3710 fold|3710 fold|1280|1280|6303 classic|6303 classic|2710 Navigation Edition|2710 Navigation Edition|6788|6788|6750 Mural|6750 Mural|7705 Twist|7705 Twist|N97 mini|N97 mini|X3-00|X3-00|X6-00|X6-00|5230|5230|6760 slide|6760 slide|6790 Surge|6790 Surge|3720 classic|3720 classic|5030 XpressRadio|5030 XpressRadio|E72|E72|5530 XpressMusic|5530 XpressMusic|6216 classic|6216 classic|7510 Supernova|7510 Supernova|5130 XpressMusic|5130 XpressMusic|8800 Gold Arte|8800 Gold Arte|2700 classic|2700 classic|6700 classic|6700 classic|2730 classic|2730 classic|2720 fold|2720 fold|7020|7020|6600i slide|6600i slide|6730 classic|6730 classic|N900|N900|5730 XpressMusic|5730 XpressMusic|6710 Navigator|6710 Navigator|6720 classic|6720 classic|E52|E52|E55|E55|E75|E75|N86 8MP|N86 8MP|N97|N97|5630 XpressMusic|5630 XpressMusic|3120 classic|3120 classic|3110 Evolve|3110 Evolve|5000|5000|2330 classic|2330 classic|6260 slide|6260 slide|7310 Supernova|7310 Supernova|8800 Sapphire Arte|8800 Sapphire Arte|8800 Carbon Arte|8800 Carbon Arte|3600 slide|3600 slide|6124 classic|6124 classic|6650 fold|6650 fold|N810 WiMAX Edition|N810 WiMAX Edition|N85|N85|E63|E63|6210 Navigator|6210 Navigator|N96|N96|N78|N78|6220 classic|6220 classic|5320 XpressMusic|5320 XpressMusic|E66|E66|N79|N79|5800 XpressMusic|5800 XpressMusic|E71|E71|3500 classic|3500 classic|3110 classic|3110 classic|6500 classic|6500 classic|8600 Luna|8600 Luna|7900 Prism|7900 Prism|6500 slide|6500 slide|5310 XpressMusic|5310 XpressMusic|8800 Arte|8800 Arte|6121 classic|6121 classic|6290|6290|N77|N77|N810|N810|N800|N800|5700 XpressMusic|5700 XpressMusic|E90 Communicator|E90 Communicator|N76|N76|N75|N75|N81 8GB|N81 8GB|N81|N81|N95 8GB|N95 8GB|N93i|N93i|6110 Navigator|6110 Navigator|E65|E65|E61i|E61i|6120 classic|6120 classic|N82|N82|E51|E51|N95|N95|6070|6070|5300 XpressMusic|5300 XpressMusic|6300|6300|8800 Sirocco Edition|8800 Sirocco Edition|E62|E62|9300i Communicator|9300i Communicator|N72|N72|N80|N80|E70|E70|E60|E60|3250|3250|E50|E50|N92|N92|N71|N71|N91 8GB|N91 8GB|N93|N93|N91|N91|5500 Sport|5500 Sport|E61|E61|N73|N73|6111|6111|6021|6021|6233|6233|770 Internet Tablet|770 Internet Tablet|6280|6280|N90|N90|6230i|6230i|8800|8800|6708|6708|3230|3230|6681|6681|6682|6682|6680|6680|9500 Communicator|9500 Communicator|9300 Communicator|9300 Communicator|N70|N70|7200|7200|6020|6020|6260|6260|6620|6620|6670|6670|N-Gage QD|N-Gage QD|7710|7710|6630|6630|7610|7610|7600|7600|3600|3600|3620|3620|3650|3650|3660|3660|N-Gage|N-Gage|6600|6600|8910i|8910i|7650|7650|3210|3210}|{HUAWEI/HONOR|Xiaomi/xiaomi|samsung|Vestel|HTC|LENOVO/Lenovo|Xiaomi|Meizu|Sony|Motorola|LeMobile/LeEco|OPPO}; {FRD-L09|Redmi Note 4|GT-I9301I|wifionly-gms|cp2dcg|Mi A1|Lenovo A2020a40|Redmi 4A|SM-N900|Redmi Note 3|MI 6|PRO 6|m3 note|MI 5|SM-G950F|SM-A310F|F3311|fleming|Le X527|SM-G920F|SM-A500F|SM-G900F|SM-G935F|R827}}; {HWFRD|mido|s3ve3g|VP74-Finlux|HTC One SC|tissot_sprout|angus3A4|rolex|ha3g|kenzo|sagit|PRO6|m3note|gemini|dreamlte|a3xelte|F3311|MZ608|le_s2_ww|zeroflte|a5lte|klte|hero2lte|R827}; {samsungexynos8895|hi3650|mt6755|h1|samsungexynos7580|samsungexynos7420|samsungexynos8890|qcom|hi3660|mt6797|universal5420}')
            infoUA_queue.put((login, api_ua, row))
        
        xigcapabilities = '3brTv10='
        xbloksversionid = '1376d33db0db05728f01e1c189d98e23eec07e6ba2479b29dfc0125f8920193e'
        id_box = '658190018'
        api_key = '355.1.0.44.103'
        api_ua = 'Instagram '+api_key+' Android ('+api_ua+'; {ig_locale}; '+id_box+')'
        proxies = ''
        csrftoken = ''.join([random.choice('tydwpQv6kWn3GKs4bYD82caFM0') for _ in range(32)])

        if cookie == "":
            mid = ''
            rur = ''
            ds_user_id = ''
            claim = ''
            authorization = ''
            sessionid = ''
        else:
            mid = re.findall('mid=(.*?);', cookie)[0]
            rur = re.findall('rur=(.*?);', cookie)[0]
            ds_user_id = re.findall('ds_user_id=(.*?);', cookie)[0]  
            claim = str(re.findall('X-IG-WWW-Claim=(.*?);', cookie)[0]).rstrip().strip() 
            authorization = re.findall('Authorization=(.*?);', cookie)[0]
            sessionid = json.loads(base64.b64decode(authorization.split(":")[2]))['sessionid'] 

        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
        api_ua = api_ua.replace('{ig_locale}', ig_locale)
        try:
            #authorize_account
            if cookie == "":
                print('NO COOKIE. GO LOGIN')
                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = login_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)

            else: 
                print('YES COOKIE. GO CHECK SESSION')

                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = authorize_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)
            if statusDef == "GOOD":
                infoCookie_queue.put((login, 'rur='+rur+'; mid='+mid+'; ds_user_id='+ds_user_id+'; Authorization='+authorization+'; X-IG-WWW-Claim='+claim+';', row))
                valid_status = random.choice(["Валид"])
            elif statusDef == "BAD":
                valid_status = random.choice(["Невалид"])

                
            result_queue.put((login, valid_status, row))
            status_queue.put((row, valid_status)) 
        except Exception as e:
            print(f"Error in thread for login {login}: {e}")
                
                
        finally:
            account_queue.task_done()

def process_function(account_list, table_name, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, threadsx):
    account_queue = Queue()
    for account in account_list:
        print('account '+str(account))
        account_queue.put(account)

    threads = []
    print('threadsx: '+str(threadsx))
    print('proxy_method_dropdown: '+str(proxy_method_dropdown))
    
    for _ in range(threadsx):  # 100 потоков
        thread = threading.Thread(target=check_validity_thread, args=(account_queue, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def audience_thread(account_queue, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, group_name, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, listUsername_queue,limit_input):
    print('START audience_thread')

    while not account_queue.empty():

            
        massiveAcc,row = account_queue.get()
        login,password,device,api_ua,cookie = massiveAcc
        if listUsername_queue.empty():
            print('2Закончились Username  в списке для парсинга')
            result_queue.put((login, 'Закончил парсинг', 'Закончил парсинг', row))
            continue
        print('login: '+str(login))
        print('password: '+str(password))
        print('device: '+str(device))
        print('cookie: '+str(cookie))
        print('api_ua: '+str(api_ua))
        
        if device == "":

            android = ''.join([random.choice('abcdef0123456789') for _ in range(16)])
            device_id = f"{generate_random_string(8)}-{generate_random_string(1)}663-4{generate_random_string(3)}-{generate_random_string(4)}-{generate_random_string(12)}"
            phone_id = f"{generate_random_string(8)}-{generate_random_string(4)}-4{generate_random_string(3)}-{generate_random_string(4)}-{generate_random_string(12)}"

            adid_id = str(uuid.uuid4())
            infoDevice_queue.put((login, 'android-'+android+';'+phone_id+';'+device_id+';'+adid_id+'', row))
        else:
            devicelist = device.split(";")
            android = devicelist[0]
            phone_id = devicelist[1]
            device_id = devicelist[2]
            adid_id = devicelist[3] 
        session_id = 'UFS-'+str(uuid.uuid4())+'-0'

        if api_ua == "":
            api_ua = spintax.spin('{2{5|6|7|8|9}/{1|2|3|4|5|6|7|8|9|0}.{1|2|3|4|5|6|7|8|9|0}}; {480dpi|320dpi|420dpi|380dpi|640dpi|240dpi}; {1080x1920|1080x2076|1080x1794|1440x2392|1440x2560|480x854|720x1280}; {{Nokia}; {600|600|3208 classic|3208 classic|X2-05|X2-05|C2-05|C2-05|C1-02|C1-02|C1-01|C1-01|E73 Mode|E73 Mode|8.3 5G|8.3 5G|5310 (2020)|5310 (2020)|2.3|2.3|800 Tough|800 Tough|4.2|4.2|1 Plus|1 Plus|2.2|2.2|6.2|6.2|7.2|7.2|3.2|3.2|9 PureView|9 PureView|8.1|8.1|6.1 Plus|6.1 Plus|3.1 Plus|3.1 Plus|7.1|7.1|5.1 Plus|5.1 Plus|5.1|5.1|2.1|2.1|3.1|3.1|8 Sirocco|8 Sirocco|8110 4G|8110 4G|7 Plus|7 Plus|1|1|6.1|6.1|7|7|2|2|8|8|3310 (2017)|3310 (2017)|5|5|3|3|6|6|Lumia 730 Dual Sim|Lumia 730 Dual Sim|Lumia 830|Lumia 830|Lumia 735|Lumia 735|Lumia 530|Lumia 530|X2|X2|Lumia 635|Lumia 635|Lumia 630|Lumia 630|Lumia 930|Lumia 930|X|X|XL|XL|Asha 503 DS|Asha 503 DS|Lumia 1320|Lumia 1320|Lumia 928|Lumia 928|Lumia 525|Lumia 525|Lumia 1520|Lumia 1520|Lumia 625|Lumia 625|Lumia 1020|Lumia 1020|Lumia 925|Lumia 925|Asha 205 Dual Sim|Asha 205 Dual Sim|Lumia 720|Lumia 720|Lumia 822|Lumia 822|Lumia 520|Lumia 520|Lumia 505|Lumia 505|Lumia 620|Lumia 620|Lumia 510|Lumia 510|Asha 302|Asha 302|Lumia 920|Lumia 920|Lumia 820|Lumia 820|Asha 305|Asha 305|Lumia 610|Lumia 610|808 PureView|808 PureView|Lumia 900|Lumia 900|Asha 303|Asha 303|Asha 200|Asha 200|C5-05|C5-05|101|101|Asha 300|Asha 300|Asha 201|Asha 201|Lumia 710|Lumia 710|Lumia 800|Lumia 800|603|603|C5-06|C5-06|N950|N950|701|701|500|500|700|700|C5-00 5MP|C5-00 5MP|C2-03|C2-03|C2-06|C2-06|N9|N9|Oro|Oro|X7-00|X7-00|E6-00|E6-00|C2-01|C2-01|C3-01|C3-01|E7-00|E7-00|X2-01|X2-01|C5-03|C5-03|C6-01|C6-01|C7-00|C7-00|5250|5250|X3-02|X3-02|5330 XpressMusic|5330 XpressMusic|5228|5228|C5-01|C5-01|C2-00|C2-00|X5-01|X5-01|X2-00|X2-00|N8|N8|E5-00|E5-00|C6-00|C6-00|C3-00|C3-00|C5-00|C5-00|6303i classic|6303i classic|5235 Comes With Music|5235 Comes With Music|6700 slide|6700 slide|7230|7230|5330 Mobile TV Edition|5330 Mobile TV Edition|2220 slide|2220 slide|2690|2690|3710 fold|3710 fold|1280|1280|6303 classic|6303 classic|2710 Navigation Edition|2710 Navigation Edition|6788|6788|6750 Mural|6750 Mural|7705 Twist|7705 Twist|N97 mini|N97 mini|X3-00|X3-00|X6-00|X6-00|5230|5230|6760 slide|6760 slide|6790 Surge|6790 Surge|3720 classic|3720 classic|5030 XpressRadio|5030 XpressRadio|E72|E72|5530 XpressMusic|5530 XpressMusic|6216 classic|6216 classic|7510 Supernova|7510 Supernova|5130 XpressMusic|5130 XpressMusic|8800 Gold Arte|8800 Gold Arte|2700 classic|2700 classic|6700 classic|6700 classic|2730 classic|2730 classic|2720 fold|2720 fold|7020|7020|6600i slide|6600i slide|6730 classic|6730 classic|N900|N900|5730 XpressMusic|5730 XpressMusic|6710 Navigator|6710 Navigator|6720 classic|6720 classic|E52|E52|E55|E55|E75|E75|N86 8MP|N86 8MP|N97|N97|5630 XpressMusic|5630 XpressMusic|3120 classic|3120 classic|3110 Evolve|3110 Evolve|5000|5000|2330 classic|2330 classic|6260 slide|6260 slide|7310 Supernova|7310 Supernova|8800 Sapphire Arte|8800 Sapphire Arte|8800 Carbon Arte|8800 Carbon Arte|3600 slide|3600 slide|6124 classic|6124 classic|6650 fold|6650 fold|N810 WiMAX Edition|N810 WiMAX Edition|N85|N85|E63|E63|6210 Navigator|6210 Navigator|N96|N96|N78|N78|6220 classic|6220 classic|5320 XpressMusic|5320 XpressMusic|E66|E66|N79|N79|5800 XpressMusic|5800 XpressMusic|E71|E71|3500 classic|3500 classic|3110 classic|3110 classic|6500 classic|6500 classic|8600 Luna|8600 Luna|7900 Prism|7900 Prism|6500 slide|6500 slide|5310 XpressMusic|5310 XpressMusic|8800 Arte|8800 Arte|6121 classic|6121 classic|6290|6290|N77|N77|N810|N810|N800|N800|5700 XpressMusic|5700 XpressMusic|E90 Communicator|E90 Communicator|N76|N76|N75|N75|N81 8GB|N81 8GB|N81|N81|N95 8GB|N95 8GB|N93i|N93i|6110 Navigator|6110 Navigator|E65|E65|E61i|E61i|6120 classic|6120 classic|N82|N82|E51|E51|N95|N95|6070|6070|5300 XpressMusic|5300 XpressMusic|6300|6300|8800 Sirocco Edition|8800 Sirocco Edition|E62|E62|9300i Communicator|9300i Communicator|N72|N72|N80|N80|E70|E70|E60|E60|3250|3250|E50|E50|N92|N92|N71|N71|N91 8GB|N91 8GB|N93|N93|N91|N91|5500 Sport|5500 Sport|E61|E61|N73|N73|6111|6111|6021|6021|6233|6233|770 Internet Tablet|770 Internet Tablet|6280|6280|N90|N90|6230i|6230i|8800|8800|6708|6708|3230|3230|6681|6681|6682|6682|6680|6680|9500 Communicator|9500 Communicator|9300 Communicator|9300 Communicator|N70|N70|7200|7200|6020|6020|6260|6260|6620|6620|6670|6670|N-Gage QD|N-Gage QD|7710|7710|6630|6630|7610|7610|7600|7600|3600|3600|3620|3620|3650|3650|3660|3660|N-Gage|N-Gage|6600|6600|8910i|8910i|7650|7650|3210|3210}|{HUAWEI/HONOR|Xiaomi/xiaomi|samsung|Vestel|HTC|LENOVO/Lenovo|Xiaomi|Meizu|Sony|Motorola|LeMobile/LeEco|OPPO}; {FRD-L09|Redmi Note 4|GT-I9301I|wifionly-gms|cp2dcg|Mi A1|Lenovo A2020a40|Redmi 4A|SM-N900|Redmi Note 3|MI 6|PRO 6|m3 note|MI 5|SM-G950F|SM-A310F|F3311|fleming|Le X527|SM-G920F|SM-A500F|SM-G900F|SM-G935F|R827}}; {HWFRD|mido|s3ve3g|VP74-Finlux|HTC One SC|tissot_sprout|angus3A4|rolex|ha3g|kenzo|sagit|PRO6|m3note|gemini|dreamlte|a3xelte|F3311|MZ608|le_s2_ww|zeroflte|a5lte|klte|hero2lte|R827}; {samsungexynos8895|hi3650|mt6755|h1|samsungexynos7580|samsungexynos7420|samsungexynos8890|qcom|hi3660|mt6797|universal5420}')
            infoUA_queue.put((login, api_ua, row))
        
        xigcapabilities = '3brTv10='
        xbloksversionid = '1376d33db0db05728f01e1c189d98e23eec07e6ba2479b29dfc0125f8920193e'
        id_box = '658190018'
        api_key = '355.1.0.44.103'
        api_ua = 'Instagram '+api_key+' Android ('+api_ua+'; {ig_locale}; '+id_box+')'
        proxies = ''
        csrftoken = ''.join([random.choice('tydwpQv6kWn3GKs4bYD82caFM0') for _ in range(32)])

        if cookie == "":
            mid = ''
            rur = ''
            ds_user_id = ''
            claim = ''
            authorization = ''
            sessionid = ''
        else:
            mid = re.findall('mid=(.*?);', cookie)[0]
            rur = re.findall('rur=(.*?);', cookie)[0]
            ds_user_id = re.findall('ds_user_id=(.*?);', cookie)[0]  
            claim = str(re.findall('X-IG-WWW-Claim=(.*?);', cookie)[0]).rstrip().strip() 
            authorization = re.findall('Authorization=(.*?);', cookie)[0]
            sessionid = json.loads(base64.b64decode(authorization.split(":")[2]))['sessionid'] 

        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
        api_ua = api_ua.replace('{ig_locale}', ig_locale)
        try:
            #authorize_account
            if cookie == "":
                print('NO COOKIE. GO LOGIN')
                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = login_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)

            else: 
                print('YES COOKIE. GO CHECK SESSION')

                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = authorize_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)
            if statusDef == "GOOD":
                print('ВАЛИДНЫЙ АКК, ИДЕМ ПАРСИТЬ')

                infoCookie_queue.put((login, 'rur='+rur+'; mid='+mid+'; ds_user_id='+ds_user_id+'; Authorization='+authorization+'; X-IG-WWW-Claim='+claim+';', row))
            elif statusDef == "BAD":
                print('ДОХЛЫЙ АКК НАДО ДРУГОЙ')
                result_queue.put((login, 'Невалид', 'Закончил парсинг', row))
                

        except Exception as e:
            print(f"Error in thread for login {login}: {e}")
        
        if statusDef == "GOOD":
            print('limit_input: '+str(limit_input))

            while True:
                if listUsername_queue.empty():
                    print('Закончились Username  в списке для парсинга')
                    result_queue.put((login, 'Закончил парсинг', 'Закончил парсинг', row))
                    #print('account_queue task_done')
                    #account_queue.task_done()
                    #continue

                    #result_queue.put((login, 'Закончил парсинг', 'Закончил парсинг', row))

                    break
                    
                    
                    
                else:
                    usernameParsing = listUsername_queue.get()
                    print('usernameParsing: '+usernameParsing)
                
                rank_id = str(uuid.uuid4())
                
                exchall = False
                while True: #GET ID USERNAME
                    timereal = gettimereal(timezonename)
                    try:
                        headers = {
                            "x-ig-mapped-locale": ig_locale,
                            "x-pigeon-session-id": session_id,
                            "x-pigeon-rawclienttime": timereal,
                            "x-ig-bandwidth-speed-kbps": "-1.000",
                            "x-ig-bandwidth-totalbytes-b": "0",
                            "x-ig-bandwidth-totaltime-ms": "0",
                            "x-ig-app-startup-country": ig_locale_startup,
                            "x-bloks-version-id": xbloksversionid,
                            "x-ig-www-claim": claim,
                            "x-bloks-is-layout-rtl": "false",
                            "x-bloks-is-panorama-enabled": "true",
                            "x-ig-device-id": device_id,
                            "x-ig-family-device-id": phone_id,
                            "x-ig-android-id": "android-"+android,
                            "x-ig-timezone-offset": timezone,
                            "x-ig-nav-chain": '8XD:self_profile:11,ProfileMediaTabFragment:self_profile:12,4DP:bottom_sheet_profile:13,6ki:settings_category_options:14,7T8:landing_facebook:15,7T8:landing_facebook:16',
                            "x-ig-connection-type": 'WIFI',
                            "x-ig-capabilities": xigcapabilities,
                            "x-ig-app-id": '567067343352427',
                            "priority": "u=3",
                            "user-agent": api_ua,
                            "accept-language": accept_ln,
                            "authorization": authorization,
                            "x-mid": mid,
                            "ig-u-ds-user-id": ds_user_id,
                            "ig-u-rur": rur,
                            "ig-intended-user-id": ds_user_id,
                            "accept-encoding": "gzip, deflate",
                            "x-fb-http-engine": "Liger",
                            "x-fb-client-ip": "True",
                            "x-fb-server-cluster": "True",
                            'Connection': 'close'
                        }
                        response = requests.get('https://i.instagram.com/api/v1/fbsearch/topsearch_flat/?search_surface=top_search_page&timezone_offset='+timezone+'&count=30&query='+usernameParsing+'&context=blended', headers=headers, timeout=60, proxies=proxies, verify=False)
                        #print(response.text)
                        if 'ip_block' in response.text or 'sentry_block' in response.text or 'an error occurred' in response.text or 'consent_data' in response.text or 'DOCTYPE html' in response.text:
                            print('выф IP_BLOCK')
                            proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                            continue
                            
                            
                        if 'challenge_required' in response.text:
                            exchall = True
                            break    
                            
                        if '"username":"'+usernameParsing+'"' in response.text:  
                            
                            idParsing = re.findall('"pk_id":"(\d+)","username":"'+usernameParsing+'"', response.text)
                            idParsing = str(idParsing[0])
                            print('idParsing: '+str(idParsing))
                            break
                        else:
                            print('не нашел айди юзера..')
                    except Exception as exc:
                        print('[#01s63] fail connect login ['+str(exc)+']')
                        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                        continue
                
                if exchall == True:
                    print('Вставляю обратно usernameParsing и беру новый акк для парсинга если есть')
                    listUsername_queue.put(usernameParsing)
                    result_queue.put((login, 'Невалид', 'Закончил парсинг', row))

                    break
                    
                next_max_idstring = '' 
                countAll = 0
                exchall = False
                while True:
                    try:
                        response = requests.get('https://i.instagram.com/api/v1/friendships/'+idParsing+'/followers/?search_surface=follow_list_page'+next_max_idstring+'&order=default&query=&enable_groups=true&rank_token='+rank_id, headers=headers, timeout=60, proxies=proxies, verify=False)
                        #print(response.text)
                        

                    except Exception as exc:
                        print('[#01ss63] fail connect ['+str(exc)+']')
                        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                        continue 
                        
                    if 'challenge_required' in response.text:
                        exchall = True
                        break    
                        
                    if 'ip_block' in response.text or 'sentry_block' in response.text or 'an error occurred' in response.text or 'consent_data' in response.text or 'DOCTYPE html' in response.text:
                        print('ммвыф IP_BLOCK')
                        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                        continue 
                        
                        

                    
                    
                    #user_ids = json.loads(response.text)['pk_id']
                    #user_ids = [value for key, value in data.items() if key == "pk_id"]
                    user_ids = re.findall(r'"pk_id":\s*"?(\d+)', response.text)

                    print(str(user_ids))
                    countAll += len(user_ids)
                    print('countAll: '+str(countAll))


        
                    result_queue.put((login, group_name, user_ids, row))  
                    
                    if countAll >= int(limit_input):
                        break
                        
                    if 'next_max_id' in response.text:
                        print('GET next_max_id')
                        next_max_id = re.findall('"next_max_id":"(.*?)"', response.text)[0]
                        next_max_idstring = '&max_id='+next_max_id
                        print(next_max_idstring)
                    else:
                        print('NOU next_max_id')

                        break     
                      
                if exchall == True:
                    print('Вставляю обратно usernameParsing и беру новый акк для парсинга если есть')
                    listUsername_queue.put(usernameParsing)
                    result_queue.put((login, 'Невалид', 'Закончил парсинг', row))

                    break   
                    
                if listUsername_queue.empty():    
                    print('listUsername_queue пустой. Заканчиваю работу')

                    result_queue.put((login, 'Закончил парсинг', 'Закончил парсинг', row))
                    break
                else:
                    print('БЕРУ НОВЫЙ ЛОГИН ДЛЯ ПАРСИНГА')
                    continue
                    
            account_queue.task_done()

def process_audience_function(account_list, table_name, group_name,  result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, threadsx, listUsername_queue, limit_input):
    account_queue = Queue()
    for account in account_list:
        account_queue.put(account)

    threads = []
    for _ in range(threadsx):  # 100 потоков
        print('START THREAD')
        thread = threading.Thread(target=audience_thread, args=(account_queue, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, group_name, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, listUsername_queue, limit_input))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def direct_thread(account_queue, result_queue,infoUA_queue,infoCookie_queue,infoDevice_queue,  group_name, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,direct_methodmessage_dropdown,direct_method_dropdown,limit_input_group,limit_input_group2, listUserIdQueue, message_for_direct,limit_input_sleep, limit_input):
    
    print('START audience_thread')

    while not account_queue.empty():

            
        massiveAcc,row = account_queue.get()
        login,password,device,api_ua,cookie = massiveAcc
        if listUserIdQueue.empty():
            print('2Закончились Username  в списке для рассылки')
            result_queue.put((login, 'Закончил рассылку', 'Закончил рассылку', row))
            continue
        print('login: '+str(login))
        print('password: '+str(password))
        print('device: '+str(device))
        print('cookie: '+str(cookie))
        print('api_ua: '+str(api_ua))
        
        if device == "":

            android = ''.join([random.choice('abcdef0123456789') for _ in range(16)])
            device_id = f"{generate_random_string(8)}-{generate_random_string(1)}663-4{generate_random_string(3)}-{generate_random_string(4)}-{generate_random_string(12)}"
            phone_id = f"{generate_random_string(8)}-{generate_random_string(4)}-4{generate_random_string(3)}-{generate_random_string(4)}-{generate_random_string(12)}"

            adid_id = str(uuid.uuid4())
            infoDevice_queue.put((login, 'android-'+android+';'+phone_id+';'+device_id+';'+adid_id+'', row))
        else:
            devicelist = device.split(";")
            android = devicelist[0]
            phone_id = devicelist[1]
            device_id = devicelist[2]
            adid_id = devicelist[3] 
        session_id = 'UFS-'+str(uuid.uuid4())+'-0'

        if api_ua == "":
            api_ua = spintax.spin('{2{5|6|7|8|9}/{1|2|3|4|5|6|7|8|9|0}.{1|2|3|4|5|6|7|8|9|0}}; {480dpi|320dpi|420dpi|380dpi|640dpi|240dpi}; {1080x1920|1080x2076|1080x1794|1440x2392|1440x2560|480x854|720x1280}; {{Nokia}; {600|600|3208 classic|3208 classic|X2-05|X2-05|C2-05|C2-05|C1-02|C1-02|C1-01|C1-01|E73 Mode|E73 Mode|8.3 5G|8.3 5G|5310 (2020)|5310 (2020)|2.3|2.3|800 Tough|800 Tough|4.2|4.2|1 Plus|1 Plus|2.2|2.2|6.2|6.2|7.2|7.2|3.2|3.2|9 PureView|9 PureView|8.1|8.1|6.1 Plus|6.1 Plus|3.1 Plus|3.1 Plus|7.1|7.1|5.1 Plus|5.1 Plus|5.1|5.1|2.1|2.1|3.1|3.1|8 Sirocco|8 Sirocco|8110 4G|8110 4G|7 Plus|7 Plus|1|1|6.1|6.1|7|7|2|2|8|8|3310 (2017)|3310 (2017)|5|5|3|3|6|6|Lumia 730 Dual Sim|Lumia 730 Dual Sim|Lumia 830|Lumia 830|Lumia 735|Lumia 735|Lumia 530|Lumia 530|X2|X2|Lumia 635|Lumia 635|Lumia 630|Lumia 630|Lumia 930|Lumia 930|X|X|XL|XL|Asha 503 DS|Asha 503 DS|Lumia 1320|Lumia 1320|Lumia 928|Lumia 928|Lumia 525|Lumia 525|Lumia 1520|Lumia 1520|Lumia 625|Lumia 625|Lumia 1020|Lumia 1020|Lumia 925|Lumia 925|Asha 205 Dual Sim|Asha 205 Dual Sim|Lumia 720|Lumia 720|Lumia 822|Lumia 822|Lumia 520|Lumia 520|Lumia 505|Lumia 505|Lumia 620|Lumia 620|Lumia 510|Lumia 510|Asha 302|Asha 302|Lumia 920|Lumia 920|Lumia 820|Lumia 820|Asha 305|Asha 305|Lumia 610|Lumia 610|808 PureView|808 PureView|Lumia 900|Lumia 900|Asha 303|Asha 303|Asha 200|Asha 200|C5-05|C5-05|101|101|Asha 300|Asha 300|Asha 201|Asha 201|Lumia 710|Lumia 710|Lumia 800|Lumia 800|603|603|C5-06|C5-06|N950|N950|701|701|500|500|700|700|C5-00 5MP|C5-00 5MP|C2-03|C2-03|C2-06|C2-06|N9|N9|Oro|Oro|X7-00|X7-00|E6-00|E6-00|C2-01|C2-01|C3-01|C3-01|E7-00|E7-00|X2-01|X2-01|C5-03|C5-03|C6-01|C6-01|C7-00|C7-00|5250|5250|X3-02|X3-02|5330 XpressMusic|5330 XpressMusic|5228|5228|C5-01|C5-01|C2-00|C2-00|X5-01|X5-01|X2-00|X2-00|N8|N8|E5-00|E5-00|C6-00|C6-00|C3-00|C3-00|C5-00|C5-00|6303i classic|6303i classic|5235 Comes With Music|5235 Comes With Music|6700 slide|6700 slide|7230|7230|5330 Mobile TV Edition|5330 Mobile TV Edition|2220 slide|2220 slide|2690|2690|3710 fold|3710 fold|1280|1280|6303 classic|6303 classic|2710 Navigation Edition|2710 Navigation Edition|6788|6788|6750 Mural|6750 Mural|7705 Twist|7705 Twist|N97 mini|N97 mini|X3-00|X3-00|X6-00|X6-00|5230|5230|6760 slide|6760 slide|6790 Surge|6790 Surge|3720 classic|3720 classic|5030 XpressRadio|5030 XpressRadio|E72|E72|5530 XpressMusic|5530 XpressMusic|6216 classic|6216 classic|7510 Supernova|7510 Supernova|5130 XpressMusic|5130 XpressMusic|8800 Gold Arte|8800 Gold Arte|2700 classic|2700 classic|6700 classic|6700 classic|2730 classic|2730 classic|2720 fold|2720 fold|7020|7020|6600i slide|6600i slide|6730 classic|6730 classic|N900|N900|5730 XpressMusic|5730 XpressMusic|6710 Navigator|6710 Navigator|6720 classic|6720 classic|E52|E52|E55|E55|E75|E75|N86 8MP|N86 8MP|N97|N97|5630 XpressMusic|5630 XpressMusic|3120 classic|3120 classic|3110 Evolve|3110 Evolve|5000|5000|2330 classic|2330 classic|6260 slide|6260 slide|7310 Supernova|7310 Supernova|8800 Sapphire Arte|8800 Sapphire Arte|8800 Carbon Arte|8800 Carbon Arte|3600 slide|3600 slide|6124 classic|6124 classic|6650 fold|6650 fold|N810 WiMAX Edition|N810 WiMAX Edition|N85|N85|E63|E63|6210 Navigator|6210 Navigator|N96|N96|N78|N78|6220 classic|6220 classic|5320 XpressMusic|5320 XpressMusic|E66|E66|N79|N79|5800 XpressMusic|5800 XpressMusic|E71|E71|3500 classic|3500 classic|3110 classic|3110 classic|6500 classic|6500 classic|8600 Luna|8600 Luna|7900 Prism|7900 Prism|6500 slide|6500 slide|5310 XpressMusic|5310 XpressMusic|8800 Arte|8800 Arte|6121 classic|6121 classic|6290|6290|N77|N77|N810|N810|N800|N800|5700 XpressMusic|5700 XpressMusic|E90 Communicator|E90 Communicator|N76|N76|N75|N75|N81 8GB|N81 8GB|N81|N81|N95 8GB|N95 8GB|N93i|N93i|6110 Navigator|6110 Navigator|E65|E65|E61i|E61i|6120 classic|6120 classic|N82|N82|E51|E51|N95|N95|6070|6070|5300 XpressMusic|5300 XpressMusic|6300|6300|8800 Sirocco Edition|8800 Sirocco Edition|E62|E62|9300i Communicator|9300i Communicator|N72|N72|N80|N80|E70|E70|E60|E60|3250|3250|E50|E50|N92|N92|N71|N71|N91 8GB|N91 8GB|N93|N93|N91|N91|5500 Sport|5500 Sport|E61|E61|N73|N73|6111|6111|6021|6021|6233|6233|770 Internet Tablet|770 Internet Tablet|6280|6280|N90|N90|6230i|6230i|8800|8800|6708|6708|3230|3230|6681|6681|6682|6682|6680|6680|9500 Communicator|9500 Communicator|9300 Communicator|9300 Communicator|N70|N70|7200|7200|6020|6020|6260|6260|6620|6620|6670|6670|N-Gage QD|N-Gage QD|7710|7710|6630|6630|7610|7610|7600|7600|3600|3600|3620|3620|3650|3650|3660|3660|N-Gage|N-Gage|6600|6600|8910i|8910i|7650|7650|3210|3210}|{HUAWEI/HONOR|Xiaomi/xiaomi|samsung|Vestel|HTC|LENOVO/Lenovo|Xiaomi|Meizu|Sony|Motorola|LeMobile/LeEco|OPPO}; {FRD-L09|Redmi Note 4|GT-I9301I|wifionly-gms|cp2dcg|Mi A1|Lenovo A2020a40|Redmi 4A|SM-N900|Redmi Note 3|MI 6|PRO 6|m3 note|MI 5|SM-G950F|SM-A310F|F3311|fleming|Le X527|SM-G920F|SM-A500F|SM-G900F|SM-G935F|R827}}; {HWFRD|mido|s3ve3g|VP74-Finlux|HTC One SC|tissot_sprout|angus3A4|rolex|ha3g|kenzo|sagit|PRO6|m3note|gemini|dreamlte|a3xelte|F3311|MZ608|le_s2_ww|zeroflte|a5lte|klte|hero2lte|R827}; {samsungexynos8895|hi3650|mt6755|h1|samsungexynos7580|samsungexynos7420|samsungexynos8890|qcom|hi3660|mt6797|universal5420}')
            infoUA_queue.put((login, api_ua, row))
        
        xigcapabilities = '3brTv10='
        xbloksversionid = '1376d33db0db05728f01e1c189d98e23eec07e6ba2479b29dfc0125f8920193e'
        id_box = '658190018'
        api_key = '355.1.0.44.103'
        api_ua = 'Instagram '+api_key+' Android ('+api_ua+'; {ig_locale}; '+id_box+')'
        proxies = ''
        csrftoken = ''.join([random.choice('tydwpQv6kWn3GKs4bYD82caFM0') for _ in range(32)])

        if cookie == "":
            mid = ''
            rur = ''
            ds_user_id = ''
            claim = ''
            authorization = ''
            sessionid = ''
        else:
            mid = re.findall('mid=(.*?);', cookie)[0]
            rur = re.findall('rur=(.*?);', cookie)[0]
            ds_user_id = re.findall('ds_user_id=(.*?);', cookie)[0]  
            claim = str(re.findall('X-IG-WWW-Claim=(.*?);', cookie)[0]).rstrip().strip() 
            authorization = re.findall('Authorization=(.*?);', cookie)[0]
            sessionid = json.loads(base64.b64decode(authorization.split(":")[2]))['sessionid'] 

        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
        api_ua = api_ua.replace('{ig_locale}', ig_locale)
        try:
            #authorize_account
            if cookie == "":
                print('NO COOKIE. GO LOGIN')
                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = login_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)

            else: 
                print('YES COOKIE. GO CHECK SESSION')

                statusDef,login,password,api_ua,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = authorize_account(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,login,password,api_ua,xbloksversionid,xigcapabilities,android,phone_id,device_id,adid_id,session_id,mid,rur,ds_user_id,claim,csrftoken,authorization,sessionid,proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename)
            if statusDef == "GOOD":
                print('ВАЛИДНЫЙ АКК, ИДЕМ ПАРСИТЬ')

                infoCookie_queue.put((login, 'rur='+rur+'; mid='+mid+'; ds_user_id='+ds_user_id+'; Authorization='+authorization+'; X-IG-WWW-Claim='+claim+';', row))
            elif statusDef == "BAD":
                print('ДОХЛЫЙ АКК НАДО ДРУГОЙ')
                result_queue.put((login, 'Невалид', 'Закончил рассылку', row))
                

        except Exception as e:
            print(f"Error in thread for login {login}: {e}")
        countAll = 0

        if statusDef == "GOOD":
            print('limit_input: '+str(limit_input))

            while True:
                if listUserIdQueue.empty():
                    print('Закончились Username  в списке для парсинга')
                    result_queue.put((login, 'Закончил рассылку', 'Закончил рассылку', row))
                    #print('account_queue task_done')
                    #account_queue.task_done()
                    #continue

                    #result_queue.put((login, 'Закончил рассылку', 'Закончил рассылку', row))

                    break
                    
                    
                    
                else:
                    idDirectList = []
                    if direct_method_dropdown == "Single":
                        idDirect = listUserIdQueue.get()
                        idDirectList.append(idDirect)
                        print('idDirect: '+idDirect)
                        idDirectSend = '['+idDirect+']'
                        idDirectSend = '[18303671817]'
                        print('idDirectSend: '+idDirectSend)

                        
                    if direct_method_dropdown == "Group":
                        cycGood = 0
                        
                        while True:
                            
                            print('cycGood:'+str(cycGood))
                            if cycGood >= limit_input_group:
                                print('cycGood limit_input_group')
                                break
                                
                            idDirect = listUserIdQueue.get()
                            exchall = False
                            
                            goodLi = False
                            while True: #get_by_participants
                                timereal = gettimereal(timezonename)
                                try:
                                    headers = {
                                        "x-ig-mapped-locale": ig_locale,
                                        "x-pigeon-session-id": session_id,
                                        "x-pigeon-rawclienttime": timereal,
                                        "x-ig-bandwidth-speed-kbps": "-1.000",
                                        "x-ig-bandwidth-totalbytes-b": "0",
                                        "x-ig-bandwidth-totaltime-ms": "0",
                                        "x-ig-app-startup-country": ig_locale_startup,
                                        "x-bloks-version-id": xbloksversionid,
                                        "x-ig-www-claim": claim,
                                        "x-bloks-is-layout-rtl": "false",
                                        "x-bloks-is-panorama-enabled": "true",
                                        "x-ig-device-id": device_id,
                                        "x-ig-family-device-id": phone_id,
                                        "x-ig-android-id": "android-"+android,
                                        "x-ig-timezone-offset": timezone,
                                        "x-ig-nav-chain": '8XD:self_profile:11,ProfileMediaTabFragment:self_profile:12,4DP:bottom_sheet_profile:13,6ki:settings_category_options:14,7T8:landing_facebook:15,7T8:landing_facebook:16',
                                        "x-ig-connection-type": 'WIFI',
                                        "x-ig-capabilities": xigcapabilities,
                                        "x-ig-app-id": '567067343352427',
                                        "priority": "u=3",
                                        "user-agent": api_ua,
                                        "accept-language": accept_ln,
                                        "authorization": authorization,
                                        "x-mid": mid,
                                        "ig-u-ds-user-id": ds_user_id,
                                        "ig-u-rur": rur,
                                        "ig-intended-user-id": ds_user_id,
                                        "accept-encoding": "gzip, deflate",
                                        "x-fb-http-engine": "Liger",
                                        "x-fb-client-ip": "True",
                                        "x-fb-server-cluster": "True",
                                        'Connection': 'close'
                                    }
                                    response = requests.get('https://i.instagram.com/api/v1/direct_v2/threads/get_by_participants/?recipient_users=['+idDirect+']&seq_id=18839&limit=20', headers=headers, timeout=60, proxies=proxies, verify=False)
                                    print(response.text)
                                    if 'ip_block' in response.text or 'sentry_block' in response.text or 'an error occurred' in response.text or 'consent_data' in response.text or 'DOCTYPE html' in response.text:
                                        print('вccыф IP_BLOCK')
                                        proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                                        continue
                                        
                                        
                                    if 'challenge_required' in response.text:
                                        exchall = True
                                        break    
                                        
                                    if response.status_code == 200:  
                                        print('goodLi true')
                                        goodLi = True
                                        break
                                    else:
                                        print('не нашел айди юзера..')
                                        break
                                except Exception as exc:
                                    print('[#01s63] fail connect login ['+str(exc)+']')
                                    proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                                    continue
                            
                            if goodLi == True:
                                cycGood += 1
                                idDirectList.append(idDirect) 
                                
                                
                            if exchall == True:
                                print('Вставляю обратно usernameParsing и беру новый акк для парсинга если есть')
                                listUsername_queue.put(usernameParsing)
                                result_queue.put((login, 'Невалид', 'Закончил парсинг', row))

                                break 
                            
                        if exchall == True:
                            print('Вставляю обратно usernameParsing и беру новый акк для парсинга если есть')
                            listUsername_queue.put(usernameParsing)
                            result_queue.put((login, 'Невалид', 'Закончил парсинг', row))

                            break 
                            
                            
                            
                            
                            
                            
                            
                            

                            
                            
                            
                        #idDirectList.append('70809640646')
                            
                        idDirectSend = ','.join(idDirectList)
                        
                        idDirectSend = '['+idDirectSend+']'
                        print('idDirectSend: '+idDirectSend)







                rank_id = str(uuid.uuid4())
                

                exchall = False
                exspam = False
                mutation_token = '7763347'+str(randint(127414653000,927414653000))              
                message = spintax.spin(message_for_direct)
                print(message)
                



                if True: #TEXT MESSAGE
                    while True:
                        try:
                            timereal = gettimereal(timezonename)

                            headers = {
                            
                        
                            
                                "x-ig-app-locale": ig_locale,
                                "x-ig-device-locale": ig_locale,
                                "x-ig-mapped-locale": ig_locale,
                                "x-pigeon-session-id": session_id,
                                "x-pigeon-rawclienttime": timereal,
                                "x-ig-bandwidth-speed-kbps": "-1.000",
                                "x-ig-bandwidth-totalbytes-b": "0",
                                "x-ig-bandwidth-totaltime-ms": "0",
                                "x-ig-app-startup-country": ig_locale_startup,
                                "x-bloks-version-id": xbloksversionid,
                                "x-ig-www-claim": claim,
                                "x-bloks-is-layout-rtl": "false",
                                "x-ig-device-id": device_id,
                                "x-ig-family-device-id": phone_id,
                                "x-ig-android-id": "android-"+android,
                                "x-ig-timezone-offset": timezone,
                                "x-ig-nav-chain": '8XD:self_profile:11,ProfileMediaTabFragment:self_profile:12,4DP:bottom_sheet_profile:13,6ki:settings_category_options:14,7T8:landing_facebook:15,7T8:landing_facebook:16',
                                "x-fb-connection-type": 'WIFI',
                                "x-ig-connection-type": 'WIFI',
                                "x-ig-capabilities": xigcapabilities,
                                "x-ig-app-id": '567067343352427',
                                "priority": "u=3",
                                "user-agent": api_ua,
                                "accept-language": accept_ln,
                                "authorization": authorization,
                                "x-mid": mid,
                                "ig-u-ds-user-id": ds_user_id,
                                "ig-u-rur": rur,
                                "ig-intended-user-id": ds_user_id,
                                "accept-encoding": "gzip, deflate",
                                "x-fb-http-engine": "Liger",
                                "x-fb-client-ip": "True",
                                "x-fb-server-cluster": "True",
                                "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
                                'Connection': 'close'
                                }
                                
                                
                                
                                
                            print('direct_methodmessage_dropdown: '+direct_methodmessage_dropdown)   
                            if direct_methodmessage_dropdown == "Text":
    
                                
                                postdata = {
                                "recipient_users":idDirectSend,
                                "action":"send_item",
                                "is_shh_mode":"0",
                                "send_attribution":"inbox_search",
                                "client_context":mutation_token,
                                "_csrftoken":csrftoken,
                                "text":message,
                                "device_id":"android-"+android,
                                "mutation_token":mutation_token,
                                "_uuid":device_id,
                                "offline_threading_id":mutation_token,
                                
                                
                                
                                }
                                response = requests.post('https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/', headers=headers, data=postdata,timeout=60, proxies=proxies, verify=False)
                                
                            if direct_methodmessage_dropdown == "Text+Link":

                                link_url = re.findall('\\b((?:https?://)?(?:(?:www\\.)?(?:[\\da-z\\.-]+)\\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\\w\\.-]*)*/?)\\b',message)
                                link_url = link_url[0]
                                #message = message.replace('\n', '\\n')
                                print('message: '+message)
                                postdata = {
                                "recipient_users":idDirectSend,
                                "link_text":message,
                                "link_urls":'["'+link_url+'"]',
                                "action":"send_item",
                                "is_shh_mode":"0",
                                "send_attribution":"inbox_search",
                                "client_context":mutation_token,
                                "_csrftoken":csrftoken,
                                "device_id":"android-"+android,
                                "mutation_token":mutation_token,
                                "_uuid":device_id,
                                "offline_threading_id":mutation_token,
                                
                                
                                
                                }
                                response = requests.post('https://i.instagram.com/api/v1/direct_v2/threads/broadcast/link/', headers=headers, data=postdata,timeout=60, proxies=proxies, verify=False)
                                
                            
                            
                            
                            print(postdata)
                            print(response.text)
                            

                        except Exception as exc:
                            print('[#01ss63] fail connect ['+str(exc)+']')
                            proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                            continue 
                            
                        if 'challenge_required' in response.text:
                            exchall = True
                            break   
                            
                            
                        if '"status_code":"403"' in response.text:
                            exspam = True
                            break   
                            
                            
                        if 'ip_block' in response.text or 'sentry_block' in response.text or 'an error occurred' in response.text or 'consent_data' in response.text or 'DOCTYPE html' in response.text:
                            print('ммвыф IP_BLOCK')
                            proxies,accept_ln,ig_locale,ig_locale_startup,timezone,timezonename = changeProxy(proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown)
                            continue 
                        if response.status_code == 200:    


                            countAll += 1
                            print('countAll: '+str(countAll))


                
                            result_queue.put((login, group_name, idDirectList, row))  
                            print('УСПЕШНО ОТПРАВИЛ СООБЩЕНИЕ')
                            time.sleep(int(limit_input_sleep))
                            break
                        else:
                            
                            print('ОШИБКА ЗАПРОСА РАССЫЛКА')
                    
                
                if direct_method_dropdown == "Group":
                    if countAll >= int(limit_input_group2):
                        print('ЛИМИТ ДОСТИГНУТ2')
                        result_queue.put((login, 'Лимит достигнут', 'Закончил рассылку', row))
                        break
                        
                        
                if direct_method_dropdown == "Single":

                    if countAll >= int(limit_input):
                        print('ЛИМИТ ДОСТИГНУТ2')
                        result_queue.put((login, 'Лимит достигнут', 'Закончил рассылку', row))

                        break        
                        
                if exspam == True:
                    print('Вставляю обратно username и беру новый акк для парсинга если есть')
                    
                    
                    for idDirect in idDirectList:
                        listUserIdQueue.put(idDirect)

                    result_queue.put((login, 'Спам-блок', 'Закончил парсинг', row))

                    break   
                    
                if exchall == True:
                    print('Вставляю обратно username и беру новый акк для парсинга если есть')
                    for idDirect in idDirectList:
                        listUserIdQueue.put(idDirect)
                        
                    result_queue.put((login, 'Невалид', 'Закончил парсинг', row))
                    break   
                    
                if listUserIdQueue.empty():    
                    print('listUserIdQueue пустой. Заканчиваю работу')
                    for idDirect in idDirectList:
                        listUserIdQueue.put(idDirect)
                    result_queue.put((login, 'Закончил рассылку', 'Закончил рассылку', row))
                    break
                else:
                    print('БЕРУ НОВЫЙ ЛОГИН ДЛЯ РАССЫЛКИ')
                    continue
                    
            account_queue.task_done()



def process_direct_function(account_list, table_name, group_name,  result_queue,infoUA_queue,infoCookie_queue,infoDevice_queue,  proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,direct_methodmessage_dropdown,direct_method_dropdown,limit_input_group,limit_input_group2, threadsx, listUserIdQueue,  message_for_direct,limit_input_sleep, limit_input):
    account_queue = Queue()
    for account in account_list:
        account_queue.put(account)

    threads = []
    for _ in range(threadsx):  # 100 потоков
        thread = threading.Thread(target=direct_thread, args=(account_queue, result_queue,infoUA_queue,infoCookie_queue,infoDevice_queue,  group_name, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,direct_methodmessage_dropdown,direct_method_dropdown,limit_input_group,limit_input_group2, listUserIdQueue, message_for_direct,limit_input_sleep, limit_input))
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
        self.auto_update_threads = {}
    def initUI(self):
        self.main_layout = QVBoxLayout()  # Основной компоновщик

        # Кнопка "Создать таблицу"
        self.create_table_btn = QPushButton("Создать таблицу")
        self.create_table_btn.clicked.connect(self.create_table)
        self.main_layout.addWidget(self.create_table_btn)
        
        
        # Кнопка "Создать группу прокси"
        self.create_proxy_group_btn = QPushButton("Создать группу прокси")
        self.create_proxy_group_btn.clicked.connect(self.open_create_proxy_group_dialog)
        self.main_layout.addWidget(self.create_proxy_group_btn)
        
        # Кнопка "Загрузить аккаунты"
        self.load_accounts_btn = QPushButton("Загрузить аккаунты")
        self.load_accounts_btn.clicked.connect(self.load_accounts)
        self.main_layout.addWidget(self.load_accounts_btn)



        # New Button "Проверка валидности"
        self.check_validity_btn = QPushButton("Проверка валидности")
        self.check_validity_btn.clicked.connect(self.open_check_validity_dialog)
        self.main_layout.addWidget(self.check_validity_btn)

        # New Button "Парсинг аудитории"
        self.parsing_btn = QPushButton("Парсинг аудитории")
        self.parsing_btn.clicked.connect(self.open_check_parsing_dialog)
        self.main_layout.addWidget(self.parsing_btn)
        
        
        # New Button "Рассылка"
        self.direct_btn = QPushButton("Рассылка")
        self.direct_btn.clicked.connect(self.open_check_direct_dialog)
        self.main_layout.addWidget(self.direct_btn)
        


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
        self.proxy_table.setColumnCount(5)
        self.proxy_table.setHorizontalHeaderLabels(["Группа прокси" ,"Кол-во прокси", "Тип прокси", "Ссылка для обновления прокси", "Статус"])
        self.proxy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.proxy_table.setSelectionBehavior(QTableWidget.SelectRows)  # Выделение всей строки
        self.proxy_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.proxy_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.proxy_table.customContextMenuRequested.connect(self.show_proxy_context_menu)

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
    def show_proxy_context_menu(self, position):
        menu = QMenu()

        delete_action = QAction("Удалить выбранные группы прокси", self)
        delete_action.triggered.connect(self.delete_selected_proxy_groups)
        menu.addAction(delete_action)

        enable_auto_update_action = QAction("Включить автообновление по ссылке", menu)
        enable_auto_update_action.triggered.connect(self.enable_auto_update)
        menu.addAction(enable_auto_update_action)

        stop_auto_update_action = QAction("Остановить обновление", menu)
        stop_auto_update_action.triggered.connect(self.stop_auto_update)
        menu.addAction(stop_auto_update_action)

        menu.exec_(self.proxy_table.viewport().mapToGlobal(position))

    def delete_selected_proxy_groups(self):
        selected_rows = self.proxy_table.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            group_name = self.proxy_table.item(index.row(), 0).text()
            table_name = f"proxygroup_{group_name}"

            # Удалить группу из базы данных
            query = f"DROP TABLE IF EXISTS {table_name}"
            self.cursor.execute(query)
            self.conn.commit()

            # Удалить строку из таблицы
            self.proxy_table.removeRow(index.row())
  

    def enable_auto_update(self):
        
        frequency, ok = QInputDialog.getInt(self, 'Частота обновления', 'Введите частоту обновления (в минутах):', value=5, min=1)
        if ok:
            selected_groups = self.get_selected_proxy_groups()
            for group_namex in selected_groups:
                group_name = group_namex.split('|')[0]
                url = group_namex.split('|')[1]
                if url == "":
                    print('skip group ['+group_name+'] no link')
                    continue
                typeProxy = group_namex.split('|')[2]
                thread = threading.Thread(target=self.auto_update_proxies, args=(url, frequency, group_name, typeProxy), daemon=True)
                self.auto_update_threads[group_name] = thread
                thread.start()
                self.highlight_group(group_name, True)

    def stop_auto_update(self):
        print('stop_auto_update')
        selected_groups = self.get_selected_proxy_groups()
        for group_name in selected_groups:
            print('stop_auto_update: '+str(group_name))
            group_name = group_name.split('|')[0]
            print('stop_auto_update2: '+str(self.auto_update_threads))
            if group_name in self.auto_update_threads:
                self.auto_update_threads[group_name].join(0)
                del self.auto_update_threads[group_name]
                print('STOP REFRESH:'+str(group_name))
                self.highlight_group(group_name, False)

    def get_selected_proxy_groups(self):
        groupList = []
        selected_rows = self.proxy_table.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            group_name = self.proxy_table.item(index.row(), 0).text()
            urlLink = self.proxy_table.item(index.row(), 3).text()
            typeProxy = self.proxy_table.item(index.row(), 2).text()
            print(group_name)
            print(urlLink)
            print(typeProxy)
            groupList.append(group_name+'|'+urlLink+'|'+typeProxy)
        return groupList

    def highlight_group(self, group_name, enable):
        print('enable: '+str(enable))
        for row in range(self.proxy_table.rowCount()):
            item = self.proxy_table.item(row, 0)  # Assuming group name is in the first column
            if item and item.text() == group_name:
                if enable:
                    self.proxy_table.item(row, 0).setBackground(QColor('yellow'))
                    self.proxy_table.item(row, 1).setBackground(QColor('yellow'))
                    self.proxy_table.item(row, 2).setBackground(QColor('yellow'))
                    self.proxy_table.item(row, 3).setBackground(QColor('yellow'))
                    self.proxy_table.item(row, 4).setBackground(QColor('yellow'))
                    self.proxy_table.setItem(row, 4, QTableWidgetItem('Автообновление запущено'))
                    self.proxy_table.item(row, 4).setBackground(QColor('yellow'))

                else:
                    self.proxy_table.item(row, 0).setBackground(QColor('white'))
                    self.proxy_table.item(row, 1).setBackground(QColor('white'))
                    self.proxy_table.item(row, 2).setBackground(QColor('white'))
                    self.proxy_table.item(row, 3).setBackground(QColor('white'))
                    self.proxy_table.setItem(row, 4, QTableWidgetItem('-'))
                    self.proxy_table.item(row, 4).setBackground(QColor('white'))

    def auto_update_proxies(self, url, frequency, group_name, typeProxy):
        while group_name in self.auto_update_threads:
            
            try:
                response = requests.get(url)
                #print(response.text)

                if response.status_code == 200:
                    proxies = response.text.splitlines()
                    self.update_proxy_group(group_name, proxies, url, typeProxy)
                    
            except:
                print('ERROR GET PROXY LINK')
                continue 
            time.sleep(frequency * 60)

    def update_proxy_group(self,group_name, proxies, url, typeProxy):
        print('START UPDATE PROXY ['+group_name+']')
        conn = sqlite3.connect('total.db')
        cursor = conn.cursor()

        # Clear the existing entries for the proxy group
        cursor.execute(f"DELETE FROM proxygroup_{group_name}")
        
        # Insert the new proxies into the proxy group
        for proxy in proxies:
            #print('proxy: '+proxy)
            if '@' in proxy:
                ip, port = proxy.strip().split('@')[1].split(':')
                log, pas = proxy.strip().split('@')[0].split(':')
            else:
                ip, port = proxy.strip().split(':')
                log = ''
                pas = ''
            cursor.execute(f"""
                INSERT INTO proxygroup_{group_name} (ip, port, login, password, type, url_update)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ip, port, log, pas, typeProxy, url))
            
            
        for row in range(self.proxy_table.rowCount()):
            item = self.proxy_table.item(row, 0)
            if item and item.text() == group_name:  
                self.proxy_table.setItem(row, 1, QTableWidgetItem(str(len(proxies))))
                self.proxy_table.item(row, 1).setBackground(QColor('yellow'))

                
        conn.commit()
        conn.close()
        
    def load_proxy_groups_into_dropdown(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'proxygroup_%'"
        self.cursor.execute(query)
        groups = self.cursor.fetchall()
        self.proxy_group_dropdown.addItems([group[0].replace("proxygroup_", "") for group in groups]) 
        
    def load_proxy_method_into_dropdown(self):
        self.proxy_method_dropdown.addItems(['Manual','IP-API']) 
        
        
    def load_proxy_method_manual_into_dropdown(self):
        self.proxy_method_manual_dropdown.addItems(["Australia>en-AU", "Austria>de-AT", "Azerbaijan>az-Latn-AZ", "Albania>sq-AL", "Algeria>ar-DZ", "Argentina>es-AR", "Armenia>hy-AM", "Afghanistan>ps-AF", "Bangladesh>bn-BD", "Bahrain>ar-BH", "Belarus>be-BY", "Belize>en-BZ", "Belgium>fr-BE", "Belgium>nl-BE", "Bulgaria>bg-BG", "Bolivia>es-BO", "Bolivia>quz-BO", "Bosnia and Herzegovina>bs-Cyrl-BA", "Bosnia and Herzegovina>bs-Latn-BA", "Bosnia and Herzegovina>hr-BA", "Bosnia and Herzegovina>sr-Cyrl-BA", "Brazil>pt-BR", "Brunei Darussalam>ms-BN", "The former Yugoslav Republic of Macedonia>mk-MK", "United Kingdom>en-GB", "Hungary>hu-HU", "Venezuela>es-VE", "Vietnam>vi-VN", "Galicia>gl-ES", "Guatemala>es-GT", "Germany>de-DE", "Honduras>es-HN", "Hong Kong>zh-HK", "Greece>el-GR", "Georgia>ka-GE", "Denmark>da-DK", "Dominican Republic>es-DO", "Egypt>ar-EG", "Zimbabwe>en-ZW", "Israel>he-IL", "India>bn-IN", "India>hi-IN", "India>kok-IN", "Indonesia>id-ID", "Jordan>ar-JO", "Iraq>ar-IQ", "Iran>fa-IR", "Ireland>en-IE", "Ireland>ga-IE", "Islamic Republic of Pakistan>ur-PK", "Iceland>is-IS", "Spain>es-ES", "Italy>it-IT", "Yemen>ar-YE", "CHINA>zh-CN", "Kazakhstan>kk-KZ", "Cambodia>km-KH", "Canada>en-CA", "Canada>fr-CA", "Caribbean>en-029", "Catalonia>ca-ES", "Qatar>ar-QA", "Kenya>sw-KE", "Kyrgyzstan>ky-KG", "Colombia>es-CO", "Costa Rica>es-CR", "Kuwait>ar-KW", "Latvia>lv-LV", "Lebanon>ar-LB", "Libya>ar-LY", "Lithuania>lt-LT", "Liechtenstein>de-LI", "Luxembourg>de-LU", "Luxembourg>fr-LU", "Luxembourg>lb-LU", "Macau>zh-MO", "Malaysia>ms-MY", "Maldives>dv-MV", "Malta>mt-MT", "Morocco>ar-MA", "Mexico>es-MX", "Mohawk>moh-CA", "Moldova>ru-MO", "Monaco>fr-MC", "Mongolia>mn-MN", "Nepal>ne-NP", "Nigeria>ig-NG", "Nigeria>yo-NG", "Netherlands>fy-NL", "Netherlands>nl-NL", "Nicaragua>es-NI", "New Zealand>en-NZ", "New Zealand>mi-NZ", "Norway>nb-NO", "Norway>nn-NO", "Norway>se-NO", "Norway>sma-NO", "Norway>smj-NO", "UAE>ar-AE", "Oman>ar-OM", "Panama>es-PA", "Paraguay>es-PY", "Peru>es-PE", "Peru>quz-PE", "Poland>pl-PL", "Portugal>pt-PT", "Puerto Rico>es-PR", "Republic of Korea>ko-KR", "Republic of Senegal>wo-SN", "Republic of the Philippines>en-PH", "Czech Republic>cs-CZ", "Russia>ru-RU", "Russia>tt-RU", "Rwanda>rw-RW", "Romania>ro-RO", "USA>en-US", "USA 2>es-US", "El Salvador>es-SV", "Saudi Arabia>ar-SA", "Serbia>sr-Cyrl-CS", "Serbia>sr-Latn-CS", "Serbia>sr-SP-Cyrl", "Singapore>zh-SG", "Syria>ar-SY", "Syria>syr-SY", "Slovakia>sk-SK", "Slovenia>sl-SI", "United Kingdom>cy-GB", "Basque Country>eu-ES", "Tajikistan>tg-Cyrl-TJ", "Thailand>th-TH", "Taiwan>zh-TW", "Trinidad and Tobago>en-TT", "Tunisia>ar-TN", "Turkey>tr-TR", "Uzbekistan>uz-Latn-UZ", "Ukraine>uk-UA", "Uruguay>es-UY", "Faroese Islands>fo-FO", "Philippines>fil-PH", "Finland>fi-FI", "Finland>smn-FI", "Finland>sms-FI", "Finland>sv-FI", "France>fr-FR", "Croatia>hr-HR", "Chile>arn-CL", "Chile>es-CL", "Switzerland>de-CH", "Switzerland>fr-CH", "Switzerland>it-CH", "Switzerland>rm-CH", "Sweden>se-SE", "Sweden>sma-SE", "Sweden>smj-SE", "Sweden>sv-SE", "Sri Lanka>si-LK", "Ecuador>es-EC", "Ecuador>quz-EC", "Estonia>et-EE", "Ethiopia>am-ET", "South Africa>af-ZA", "South Africa>en-ZA", "South Africa>nso-ZA", "South Africa>tn-ZA", "South Africa>xh-ZA", "South Africa>zu-ZA", "Jamaica>en-JM", "Japan>ja-JP"])
    def load_proxy_method_manual2_into_dropdown(self):
        self.proxy_method_manual2_dropdown.addItems(["Africa/Abidjan:-968", "Africa/Accra:-968", "Africa/Addis_Ababa:10800", "Africa/Algiers:3600", "Africa/Asmara:10800", "Africa/Asmera:10800", "Africa/Bamako:-968", "Africa/Bangui:3600", "Africa/Banjul:-968", "Africa/Bissau:-3740", "Africa/Blantyre:7200", "Africa/Brazzaville:3600", "Africa/Bujumbura:7200", "Africa/Cairo:7200", "Africa/Casablanca:-1820", "Africa/Ceuta:-1276", "Africa/Conakry:-968", "Africa/Dakar:-968", "Africa/Dar_es_Salaam:10800", "Africa/Djibouti:10800", "Africa/Douala:3600", "Africa/El_Aaiun:-3168", "Africa/Freetown:-968", "Africa/Gaborone:7200", "Africa/Harare:7200", "Africa/Johannesburg:6720", "Africa/Juba:10800", "Africa/Kampala:10800", "Africa/Khartoum:10800", "Africa/Kigali:7200", "Africa/Kinshasa:3600", "Africa/Lagos:3600", "Africa/Libreville:3600", "Africa/Lome:-968", "Africa/Luanda:3600", "Africa/Lubumbashi:7200", "Africa/Lusaka:7200", "Africa/Malabo:3600", "Africa/Maputo:7200", "Africa/Maseru:6720", "Africa/Mbabane:6720", "Africa/Mogadishu:10800", "Africa/Monrovia:-2588", "Africa/Nairobi:10800", "Africa/Ndjamena:3600", "Africa/Niamey:3600", "Africa/Nouakchott:-968", "Africa/Ouagadougou:-968", "Africa/Porto-Novo:3600", "Africa/Sao_Tome:0", "Africa/Timbuktu:0", "Africa/Tripoli:3164", "Africa/Tunis:2444", "Africa/Windhoek:3600", "America/Adak:-36000", "America/Anchorage:-32400", "America/Anguilla:-14400", "America/Antigua:-14400", "America/Araguaina:-10800", "America/Argentina/Buenos_Aires:-10800", "America/Argentina/Catamarca:-10800", "America/Argentina/ComodRivadavia:-10800", "America/Argentina/Cordoba:-10800", "America/Argentina/Jujuy:-10800", "America/Argentina/La_Rioja:-10800", "America/Argentina/Mendoza:-10800", "America/Argentina/Rio_Gallegos:-10800", "America/Argentina/Salta:-10800", "America/Argentina/San_Juan:-10800", "America/Argentina/San_Luis:-10800", "America/Argentina/Tucuman:-10800", "America/Argentina/Ushuaia:-10800", "America/Aruba:-14400", "America/Asuncion:-10800", "America/Atikokan:-18000", "America/Atka:-36000", "America/Bahia:-10800", "America/Bahia_Banderas:-21600", "America/Barbados:-14309", "America/Belem:-10800", "America/Belize:-21168", "America/Blanc-Sablon:-14400", "America/Boa_Vista:-14400", "America/Bogota:-17776", "America/Boise:-25200", "America/Buenos_Aires:-10800", "America/Cambridge_Bay:-25200", "America/Campo_Grande:-13108", "America/Cancun:-18000", "America/Caracas:-14400", "America/Catamarca:-10800", "America/Cayenne:-10800", "America/Cayman:-18000", "America/Chicago:-21036", "America/Chihuahua:-25200", "America/Ciudad_Juarez:-25556", "America/Coral_Harbour:-18000", "America/Cordoba:-10800", "America/Costa_Rica:-20173", "America/Creston:-25200", "America/Cuiaba:-13460", "America/Curacao:-14400", "America/Danmarkshavn:-4480", "America/Dawson:-25200", "America/Dawson_Creek:-25200", "America/Denver:-25196", "America/Detroit:-18000", "America/Dominica:-14400", "America/Edmonton:-25200", "America/Eirunepe:-16768", "America/El_Salvador:-21408", "America/Ensenada:-28800", "America/Fortaleza:-10800", "America/Fort_Nelson:-25200", "America/Fort_Wayne:-18000", "America/Glace_Bay:-14388", "America/Godthab:-10800", "America/Goose_Bay:-14400", "America/Grand_Turk:-14400", "America/Grenada:-14400", "America/Guadeloupe:-14400", "America/Guatemala:-21600", "America/Guayaquil:-18000", "America/Guyana:-13959", "America/Halifax:-14400", "America/Havana:-18000", "America/Hermosillo:-25200", "America/Indiana/Indianapolis:-18000", "America/Indiana/Knox:-20790", "America/Indiana/Marengo:-18000", "America/Indiana/Petersburg:-18000", "America/Indiana/Tell_City:-20823", "America/Indiana/Vevay:-18000", "America/Indiana/Vincennes:-18000", "America/Indiana/Winamac:-18000", "America/Indianapolis:-18000", "America/Inuvik:-25200", "America/Iqaluit:-18000", "America/Jamaica:-18000", "America/Jujuy:-10800", "America/Juneau:-32400", "America/Kentucky/Louisville:-18000", "America/Kentucky/Monticello:-18000", "America/Knox_IN:-21600", "America/Kralendijk:-14400", "America/La_Paz:-14400", "America/Lima:-18000", "America/Los_Angeles:-28378", "America/Louisville:-18000", "America/Lower_Princes:-14400", "America/Lower_Princes:14400", "America/Maceio:-10800", "America/Managua:-20708", "America/Manaus:-14400", "America/Marigot:-14400", "America/Martinique:-14400", "America/Matamoros:-21600", "America/Mazatlan:-25200", "America/Mendoza:-10800", "America/Menominee:-21027", "America/Merida:-21508", "America/Metlakatla:-28800", "America/Mexico_City:-21600", "America/Miquelon:-10800", "America/Moncton:-14400", "America/Monterrey:-21600", "America/Montevideo:-10800", "America/Montreal:-18000", "America/Montserrat:-14400", "America/Nassau:-18000", "America/New_York:-17762", "America/Nipigon:-18000", "America/Nome:-32400", "America/Noronha:-7200", "America/North_Dakota/Beulah:-21600", "America/North_Dakota/Center:-21600", "America/North_Dakota/New_Salem:-21600", "America/Nuuk:-10800", "America/Ojinaga:-25060", "America/Panama:-18000", "America/Pangnirtung:-18000", "America/Paramaribo:-10800", "America/Phoenix:-25200", "America/Port-au-Prince:-17360", "America/Porto_Acre:-18000", "America/Porto_Velho:-14400", "America/Port_of_Spain:-14400", "America/Puerto_Rico:-14400", "America/Punta_Arenas:-10800", "America/Rainy_River:-21600", "America/Rankin_Inlet:-21600", "America/Recife:-10800", "America/Regina:-21600", "America/Resolute:-21600", "America/Rio_Branco:-16272", "America/Rosario:-10800", "America/Santarem:-10800", "America/Santa_Isabel:-28800", "America/Santiago:-10800", "America/Santo_Domingo:-14400", "America/Sao_Paulo:-10800", "America/Scoresbysund:-3600", "America/Shiprock:-25200", "America/Sitka:-32400", "America/St_Barthelemy:-14400", "America/St_Johns:-12600", "America/St_Kitts:-14400", "America/St_Lucia:-14400", "America/St_Thomas:-14400", "America/St_Vincent:-14400", "America/Swift_Current:-21600", "America/Tegucigalpa:-20932", "America/Thule:-14400", "America/Thunder_Bay:-18000", "America/Tijuana:-28084", "America/Toronto:-18000", "America/Tortola:-14400", "America/Vancouver:-28800", "America/Virgin:-14400", "America/Whitehorse:-25200", "America/Winnipeg:-21600", "America/Yakutat:-32400", "America/Yellowknife:-25200", "Antarctica/Casey:0", "Antarctica/Davis:0", "Antarctica/DumontDUrville:35320", "Antarctica/Macquarie:0", "Antarctica/Mawson:0", "Antarctica/McMurdo:41944", "Antarctica/Palmer:-10800", "Antarctica/Rothera:-10800", "Antarctica/South_Pole:43200", "Antarctica/Syowa:10800", "Antarctica/Troll:0", "Antarctica/Vostok:21020", "Arctic/Longyearbyen:3208", "Asia/Aden:10800", "Asia/Almaty:18468", "Asia/Amman:7200", "Asia/Anadyr:42596", "Asia/Aqtau:12064", "Asia/Aqtobe:13720", "Asia/Ashgabat:14012", "Asia/Ashkhabad:18000", "Asia/Atyrau:12464", "Asia/Baghdad:10660", "Asia/Bahrain:10800", "Asia/Baku:11964", "Asia/Bangkok:24124", "Asia/Barnaul:20100", "Asia/Beirut:7200", "Asia/Bishkek:17904", "Asia/Brunei:26480", "Asia/Calcutta:19800", "Asia/Chita:27232", "Asia/Choibalsan:27480", "Asia/Chongqing:28800", "Asia/Chungking:28800", "Asia/Colombo:19164", "Asia/Dacca:21600", "Asia/Damascus:7200", "Asia/Dhaka:21600", "Asia/Dili:30140", "Asia/Dubai:13272", "Asia/Dushanbe:16512", "Asia/Famagusta:7200", "Asia/Gaza:7200", "Asia/Harbin:28800", "Asia/Hebron:7200", "Asia/Hong_Kong:27402", "Asia/Hovd:21996", "Asia/Ho_Chi_Minh:25200", "Asia/Irkutsk:25025", "Asia/Istanbul:7200", "Asia/Jakarta:25200", "Asia/Jayapura:32400", "Asia/Jerusalem:7200", "Asia/Kabul:16200", "Asia/Kamchatka:38076", "Asia/Karachi:16092", "Asia/Kashgar:21600", "Asia/Kathmandu:20476", "Asia/Katmandu:20700", "Asia/Khandyga:32400", "Asia/Kolkata:19800", "Asia/Krasnoyarsk:22286", "Asia/Kuala_Lumpur:24925", "Asia/Kuching:26480", "Asia/Kuwait:10800", "Asia/Macao:28800", "Asia/Macau:27250", "Asia/Magadan:36000", "Asia/Makassar:28656", "Asia/Manila:-57360", "Asia/Muscat:13272", "Asia/Nicosia:7200", "Asia/Novokuznetsk:20928", "Asia/Novosibirsk:19900", "Asia/Omsk:17610", "Asia/Oral:12324", "Asia/Phnom_Penh:24124", "Asia/Pontianak:25200", "Asia/Pyongyang:30180", "Asia/Qatar:10800", "Asia/Qostanay:15268", "Asia/Qyzylorda:15712", "Asia/Rangoon:23400", "Asia/Riyadh87:10800", "Asia/Riyadh88:10800", "Asia/Riyadh89:10800", "Asia/Riyadh:10800", "Asia/Saigon:25200", "Asia/Sakhalin:34248", "Asia/Samarkand:16073", "Asia/Seoul:30472", "Asia/Shanghai:28800", "Asia/Singapore:24925", "Asia/Srednekolymsk:36892", "Asia/Taipei:28800", "Asia/Tashkent:16631", "Asia/Tbilisi:10751", "Asia/Tehran:12344", "Asia/Tel_Aviv:7200", "Asia/Thimbu:21600", "Asia/Thimphu:21516", "Asia/Tokyo:32400", "Asia/Tomsk:20391", "Asia/Ujung_Pandang:28800", "Asia/Ulaanbaatar:25652", "Asia/Ulan_Bator:28800", "Asia/Urumqi:21020", "Asia/Ust-Nera:34374", "Asia/Vientiane:24124", "Asia/Vladivostok:31651", "Asia/Yakutsk:31138", "Asia/Yangon:23087", "Asia/Yekaterinburg:14553", "Asia/Yerevan:10680", "Atlantic/Azores:-3600", "Atlantic/Bermuda:-14400", "Atlantic/Canary:-3696", "Atlantic/Cape_Verde:-3600", "Atlantic/Faeroe:0", "Atlantic/Faroe:-1624", "Atlantic/Jan_Mayen:3600", "Atlantic/Madeira:-4056", "Atlantic/Reykjavik:-968", "Atlantic/Reykjavik:0", "Atlantic/South_Georgia:-7200", "Atlantic/Stanley:-10800", "Atlantic/St_Helena:-968", "Australia/ACT:36000", "Australia/Adelaide:33260", "Australia/Brisbane:36000", "Australia/Broken_Hill:33948", "Australia/Canberra:36000", "Australia/Currie:36000", "Australia/Darwin:31400", "Australia/Eucla:30928", "Australia/Hobart:35356", "Australia/LHI:37800", "Australia/Lindeman:35756", "Australia/Lord_Howe:37800", "Australia/Melbourne:34792", "Australia/North:34200", "Australia/NSW:36000", "Australia/Perth:27804", "Australia/Queensland:36000", "Australia/South:34200", "Australia/Sydney:36000", "Australia/Tasmania:36000", "Australia/Victoria:36000", "Australia/West:28800", "Australia/Yancowinna:34200", "Brazil/Acre:-18000", "Brazil/DeNoronha:-7200", "Brazil/East:-10800", "Brazil/West:-14400", "Canada/Atlantic:-14400", "Canada/Central:-21600", "Canada/East-Saskatchewan:-21600", "Canada/Eastern:-18000", "Canada/Mountain:-25200", "Canada/Newfoundland:-12600", "Canada/Pacific:-28800", "Canada/Saskatchewan:-21600", "Canada/Yukon:-28800", "CET:3600", "Chile/Continental:-10800", "Chile/EasterIsland:-18000", "CST6CDT:-21600", "Cuba:-18000", "EET:7200", "Egypt:7200", "Eire:0", "EST5EDT:-18000", "EST:-18000", "Etc/GMT+0:0", "Etc/GMT+1:-3600", "Etc/GMT+2:-7200", "Etc/GMT+3:-10800", "Etc/GMT+4:-14400", "Etc/GMT+5:-18000", "Etc/GMT+6:-21600", "Etc/GMT+7:-25200", "Etc/GMT+8:-28800", "Etc/GMT+9:-32400", "Etc/GMT+10:-36000", "Etc/GMT+11:-39600", "Etc/GMT+12:-43200", "Etc/GMT-0:0", "Etc/GMT-1:3600", "Etc/GMT-2:7200", "Etc/GMT-3:10800", "Etc/GMT-4:14400", "Etc/GMT-5:18000", "Etc/GMT-6:21600", "Etc/GMT-7:25200", "Etc/GMT-8:28800", "Etc/GMT-9:32400", "Etc/GMT-10:36000", "Etc/GMT-11:39600", "Etc/GMT-12:43200", "Etc/GMT-13:46800", "Etc/GMT-14:50400", "Etc/GMT0:0", "Etc/GMT:0", "Etc/Greenwich:0", "Etc/UCT:0", "Etc/Universal:0", "Etc/UTC:0", "Etc/Zulu:0", "Europe/Amsterdam:1050", "Europe/Andorra:3600", "Europe/Astrakhan:11532", "Europe/Athens:5692", "Europe/Belfast:0", "Europe/Belgrade:3600", "Europe/Berlin:3208", "Europe/Bratislava:3464", "Europe/Brussels:1050", "Europe/Bucharest:6264", "Europe/Budapest:3600", "Europe/Busingen:2048", "Europe/Chisinau:6920", "Europe/Copenhagen:3208", "Europe/Dublin:-1521", "Europe/Gibraltar:-1284", "Europe/Guernsey:-75", "Europe/Helsinki:5989", "Europe/Isle_of_Man:-75", "Europe/Isle_of_Man:3600", "Europe/Istanbul:10800", "Europe/Jersey:-75", "Europe/Jersey:3600", "Europe/Kaliningrad:4920", "Europe/Kiev:7200", "Europe/Kirov:10800", "Europe/Kyiv:7324", "Europe/Lisbon:-2205", "Europe/Ljubljana:3600", "Europe/London:-75", "Europe/Luxembourg:1050", "Europe/Madrid:-884", "Europe/Malta:3484", "Europe/Mariehamn:5989", "Europe/Minsk:10800", "Europe/Monaco:3600", "Europe/Moscow:10800", "Europe/Nicosia:7200", "Europe/Oslo:3208", "Europe/Paris:3600", "Europe/Podgorica:3600", "Europe/Prague:3464", "Europe/Riga:5794", "Europe/Rome:2996", "Europe/Samara:12020", "Europe/San_Marino:2996", "Europe/Sarajevo:3600", "Europe/Saratov:11058", "Europe/Simferopol:10800", "Europe/Skopje:3600", "Europe/Sofia:5596", "Europe/Stockholm:3208", "Europe/Tallinn:5940", "Europe/Tirane:3600", "Europe/Tiraspol:7200", "Europe/Ulyanovsk:11616", "Europe/Uzhgorod:7200", "Europe/Vaduz:2048", "Europe/Vatican:2996", "Europe/Vienna:3600", "Europe/Vilnius:6076", "Europe/Volgograd:10660", "Europe/Warsaw:3600", "Europe/Zagreb:3600", "Europe/Zaporozhye:7200", "Europe/Zurich:2048", "Greenwich:0", "Hongkong:28800", "HST:-36000", "Iceland:0", "Indian/Antananarivo:10800", "Indian/Chagos:17380", "Indian/Christmas:24124", "Indian/Cocos:23087", "Indian/Comoro:10800", "Indian/Kerguelen:17640", "Indian/Mahe:13272", "Indian/Maldives:17640", "Indian/Mauritius:13800", "Indian/Mayotte:10800", "Indian/Reunion:13272", "Iran:12600", "Israel:7200", "Jamaica:-18000", "Japan:32400", "Kwajalein:43200", "Libya:7200", "MET:3600", "Mexico/BajaNorte:-28800", "Mexico/BajaSur:-25200", "Mexico/General:-21600", "Mideast/Riyadh87:0", "Mideast/Riyadh88:0", "Mideast/Riyadh89:0", "MST7MDT:-25200", "MST:-25200", "Navajo:0", "NZ-CHAT:45900", "NZ:43200", "Pacific/Apia:45184", "Pacific/Auckland:41944", "Pacific/Bougainville:37336", "Pacific/Chatham:44028", "Pacific/Chuuk:35320", "Pacific/Easter:-18000", "Pacific/Efate:39600", "Pacific/Enderbury:46800", "Pacific/Fakaofo:-41096", "Pacific/Fiji:42944", "Pacific/Funafuti:41524", "Pacific/Galapagos:-21504", "Pacific/Gambier:-32388", "Pacific/Guadalcanal:38388", "Pacific/Guam:-51660", "Pacific/Guam:36000", "Pacific/Honolulu:-36000", "Pacific/Johnston:-36000", "Pacific/Kanton:0", "Pacific/Kiritimati:-37760", "Pacific/Kosrae:-47284", "Pacific/Kwajalein:40160", "Pacific/Majuro:41524", "Pacific/Marquesas:-33480", "Pacific/Midway:-39600", "Pacific/Nauru:40060", "Pacific/Niue:-39600", "Pacific/Norfolk:39600", "Pacific/Noumea:39600", "Pacific/Pago_Pago:-39600", "Pacific/Palau:-54124", "Pacific/Pitcairn:-28800", "Pacific/Pohnpei:38388", "Pacific/Ponape:39600", "Pacific/Port_Moresby:35320", "Pacific/Port_Moresby:36000", "Pacific/Rarotonga:-36000", "Pacific/Saipan:-51660", "Pacific/Samoa:-39600", "Pacific/Tahiti:-35896", "Pacific/Tarawa:41524", "Pacific/Tongatapu:44352", "Pacific/Truk:36000", "Pacific/Wake:41524", "Pacific/Wallis:41524", "Pacific/Yap:36000", "Poland:3600", "Portugal:0", "PRC:0", "PST8PDT:0", "ROC:28800", "ROK:32400", "Singapore:28800", "Turkey:7200", "UCT:0", "Universal:0", "US/Alaska:-32400", "US/Aleutian:-36000", "US/Arizona:-25200", "US/Central:-21600", "US/East-Indiana:-18000", "US/Eastern:-18000", "US/Hawaii:-36000", "US/Indiana-Starke:-21600", "US/Michigan:-18000", "US/Mountain:-25200", "US/Pacific-New:-28800", "US/Pacific:-28800", "US/Samoa:-39600", "UTC:0", "W-SU:10800", "WET:0", "Zulu:0"])    
        
       
   
    def on_direct_method_dropdown_changed(self, index):
        if index == 0:  #Group
            self.limit_input_group.setVisible(True)
            self.limit_input_group2.setVisible(True)
            self.status_label1.setVisible(True)
            self.status_label2.setVisible(True)
            self.status_label3.setVisible(False)
            self.limit_input.setVisible(False)
            
        elif index == 1:  #Single
            self.limit_input_group.setVisible(False)
            self.limit_input_group2.setVisible(False)
            self.status_label1.setVisible(False)
            self.status_label2.setVisible(False)
            self.status_label3.setVisible(True)
            self.limit_input.setVisible(True)

    def on_direct_method_dropdown_changed2(self, index):
        print(index)
        if index == 'Group':  #Group
            self.limit_input_group.setVisible(True)
            self.limit_input_group2.setVisible(True)
            self.limit_input.setVisible(False) 
            self.status_label33.setVisible(False)
 
            self.status_label11.setVisible(True)
            self.status_label22.setVisible(True)

            
        elif index == 'Single':  #Single
            self.limit_input_group.setVisible(False)
            self.limit_input_group2.setVisible(False)
            self.limit_input.setVisible(True)
            self.status_label33.setVisible(True)
            self.status_label11.setVisible(False)
            self.status_label22.setVisible(False)
   
   
   
   
   
   
   
   
   
   
   
   
    def on_proxy_method_dropdown_changed(self, index):
        if index == 0:  #Manual
            self.proxy_method_manual_dropdown.setVisible(True)
            self.proxy_method_manual2_dropdown.setVisible(True)
            self.status_label1.setVisible(True)
            self.status_label2.setVisible(True)
            
            
        elif index == 1:  #ip-api
            self.proxy_method_manual_dropdown.setVisible(False)
            self.proxy_method_manual2_dropdown.setVisible(False)
            self.status_label1.setVisible(False)
            self.status_label2.setVisible(False)
            
            
           
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    if True: #VALIDITY   
        
        def open_check_validity_dialog(self):

            self.open_check_validity_dialog = QDialog(self)
            self.open_check_validity_dialog.setWindowTitle("Проверка валидности")  
            
            layout = QVBoxLayout()

            # Proxy group dropdown
            self.status_label = QLabel("Выберите прокси для этой задачи")
            self.proxy_group_dropdown = QComboBox(self.open_check_validity_dialog)
            self.load_proxy_groups_into_dropdown()
            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_group_dropdown)

            # Proxy group dropdown
            self.status_label = QLabel("Откуда брать информацию об IP")
            
            self.proxy_method_dropdown = QComboBox(self.open_check_validity_dialog)

            self.load_proxy_method_into_dropdown()
            self.proxy_method_dropdown.currentIndexChanged.connect(self.on_proxy_method_dropdown_changed)

            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_method_dropdown)

                
                
                
            self.status_label1 = QLabel("Locale")
            self.proxy_method_manual_dropdown = QComboBox(self.open_check_validity_dialog)
            self.load_proxy_method_manual_into_dropdown()
            layout.addWidget(self.status_label1)
            layout.addWidget(self.proxy_method_manual_dropdown)
            
            self.status_label2 = QLabel("Timezone")
            self.proxy_method_manual2_dropdown = QComboBox(self.open_check_validity_dialog)
            self.load_proxy_method_manual2_into_dropdown()
            layout.addWidget(self.status_label2)
            layout.addWidget(self.proxy_method_manual2_dropdown)

            # Number of processes input
            self.status_label = QLabel("Максимально кол-во процессов")
            self.processes_input = QSpinBox(self.open_check_validity_dialog)
            self.processes_input.setRange(1, 100)
            self.processes_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.processes_input)

            # Number of threads input
            self.status_label = QLabel("Кол-во потоков на процесс")
            self.threads_input = QSpinBox(self.open_check_validity_dialog)
            self.threads_input.setRange(1, 100)
            self.threads_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.threads_input)

            # Config name input
            self.status_label = QLabel("Сохранить конфиг?")
            self.config_name_input = QLineEdit(self.open_check_validity_dialog)
            self.config_name_input.setPlaceholderText("Название конфига")
            layout.addWidget(self.status_label)
            layout.addWidget(self.config_name_input)
            # Load config button
            save_config_button = QPushButton("Сохранить конфиг", self.open_check_validity_dialog)
            save_config_button.clicked.connect(self.saveConfigButton)
            layout.addWidget(save_config_button)

            # Config dropdown
            self.status_label = QLabel("Выберите конфиг для его загрузки")

            self.config_dropdown = QComboBox(self.open_check_validity_dialog)
            self.load_configs_into_dropdown()
            layout.addWidget(self.status_label)

            layout.addWidget(self.config_dropdown)

            # Load config button
            load_config_button = QPushButton("Загрузить конфиг", self.open_check_validity_dialog)
            load_config_button.clicked.connect(self.load_config)
            layout.addWidget(load_config_button)

            # OK button
            ok_button = QPushButton("OK", self.open_check_validity_dialog)
            ok_button.clicked.connect(self.save_and_start_validation)
            layout.addWidget(ok_button)
            
            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get('DEFAULT', {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.proxy_method_dropdown.setCurrentText(config.get('proxy_method_dropdown', ''))
                    self.proxy_method_manual_dropdown.setCurrentText(config.get('proxy_method_manual_dropdown', ''))
                    self.proxy_method_manual2_dropdown.setCurrentText(config.get('proxy_method_manual2_dropdown', ''))
                    
                    

                    
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
            except:
                none = ''
            layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            self.open_check_validity_dialog.setLayout(layout)
            
            
            self.open_check_validity_dialog.exec_()












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
                    self.proxy_method_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.proxy_method_manual_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.proxy_method_manual2_dropdown.setCurrentText(config.get('proxy_group', ''))
                    

                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
            except FileNotFoundError:
                pass
        def saveConfigButton(self):
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            
            proxy_method_dropdown = self.proxy_method_dropdown.currentText()
            proxy_method_manual_dropdown = self.proxy_method_manual_dropdown.currentText()
            proxy_method_manual2_dropdown = self.proxy_method_manual2_dropdown.currentText()
 
            processes = self.processes_input.value()
            threads = self.threads_input.value()

            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs[config_name] = {
                'proxy_group': proxy_group,
                'proxy_method_dropdown': proxy_method_dropdown,
                'proxy_method_manual_dropdown': proxy_method_manual_dropdown,
                'proxy_method_manual2_dropdown': proxy_method_manual2_dropdown,
                'processes': processes,
                'threads': threads
            }

            with open('configsValidity.json', 'w') as f:
                json.dump(configs, f)
        def save_and_start_validation(self):
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            proxy_method_dropdown = self.proxy_method_dropdown.currentText()
            proxy_method_manual_dropdown = self.proxy_method_manual_dropdown.currentText()
            proxy_method_manual2_dropdown = self.proxy_method_manual2_dropdown.currentText()
            processes = self.processes_input.value()
            threads = self.threads_input.value()

            try:
                with open('configsValidity.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs['DEFAULT'] = {
                'proxy_group': proxy_group,
                'proxy_method_dropdown': proxy_method_dropdown,
                'proxy_method_manual_dropdown': proxy_method_manual_dropdown,
                'proxy_method_manual2_dropdown': proxy_method_manual2_dropdown,
                'processes': processes,
                'threads': threads
            }

            with open('configsValidity.json', 'w') as f:
                json.dump(configs, f)
            self.open_check_validity_dialog.accept()    
                
            current_table = self.tab_widget.currentWidget()
            if current_table:
                selected_items = current_table.selectedItems()
                if len(selected_items) == 0:
                    QMessageBox.warning(self, "Ошибка", "Не выбраны аккаунты")
                    return
                if selected_items:
                    # Check if any selected account is already "In Progress"
                    selected_rows = list(set(item.row() for item in selected_items))
                    for row in selected_rows:
                        if current_table.item(row, 5) and current_table.item(row, 5).text() == "В работе":
                            QMessageBox.warning(self, "Задача не запустилась", "Выделенные аккаунты уже в работе.")
                            return
                    print(str(processes))
                    print(str(threads))
                    print(str(proxy_group))
                    self.check_validity(current_table, selected_items, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, processes, threads)

        
    if True: #PARSING    
        def open_check_parsing_dialog(self):

            self.open_check_parsing_dialog = QDialog(self)
            self.open_check_parsing_dialog.setWindowTitle("Парсинг")
            layout = QVBoxLayout()

            # Proxy group dropdown
            self.status_label = QLabel("Выберите прокси для этой задачи")
            self.proxy_group_dropdown = QComboBox(self.open_check_parsing_dialog)
            self.load_proxy_groups_into_dropdown()
            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_group_dropdown)

            # Proxy group dropdown
            self.status_label = QLabel("Откуда брать информацию об IP")
            
            self.proxy_method_dropdown = QComboBox(self.open_check_parsing_dialog)

            self.load_proxy_method_into_dropdown()
            self.proxy_method_dropdown.currentIndexChanged.connect(self.on_proxy_method_dropdown_changed)

            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_method_dropdown)


            self.status_label1 = QLabel("Locale")
            self.proxy_method_manual_dropdown = QComboBox(self.open_check_parsing_dialog)
            self.load_proxy_method_manual_into_dropdown()
            layout.addWidget(self.status_label1)
            layout.addWidget(self.proxy_method_manual_dropdown)
            
            self.status_label2 = QLabel("Timezone")
            self.proxy_method_manual2_dropdown = QComboBox(self.open_check_parsing_dialog)
            self.load_proxy_method_manual2_into_dropdown()
            layout.addWidget(self.status_label2)
            layout.addWidget(self.proxy_method_manual2_dropdown)


            
            self.status_label = QLabel("Введите список Username")
            self.list_username_for_parsing = QTextEdit()
            layout.addWidget(self.status_label)
            layout.addWidget(self.list_username_for_parsing)
            
            self.status_label = QLabel("Лимит сбора с каждого Username")
            self.limit_input = QSpinBox(self.open_check_parsing_dialog)
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
            self.status_label = QLabel("Максимально кол-во процессов")
            self.processes_input = QSpinBox(self.open_check_parsing_dialog)
            self.processes_input.setRange(1, 100)
            self.processes_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.processes_input)

            # Number of threads input
            self.status_label = QLabel("Кол-во потоков на процесс")
            self.threads_input = QSpinBox(self.open_check_parsing_dialog)
            self.threads_input.setRange(1, 100)
            self.threads_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.threads_input)

            # Config name input
            self.status_label = QLabel("Сохранить конфиг?")
            self.config_name_input = QLineEdit(self.open_check_parsing_dialog)
            self.config_name_input.setPlaceholderText("Название конфига")
            layout.addWidget(self.status_label)
            layout.addWidget(self.config_name_input)
            # Load config button
            save_config_button = QPushButton("Сохранить конфиг", self.open_check_parsing_dialog)
            save_config_button.clicked.connect(self.saveConfigButton_parsing)
            layout.addWidget(save_config_button)

            # Config dropdown
            self.status_label = QLabel("Выберите конфиг для его загрузки")

            self.config_dropdown = QComboBox(self.open_check_parsing_dialog)
            self.load_configs_into_dropdown_parsing()
            layout.addWidget(self.status_label)

            layout.addWidget(self.config_dropdown)

            # Load config button
            load_config_button = QPushButton("Загрузить конфиг", self.open_check_parsing_dialog)
            load_config_button.clicked.connect(self.load_config_parsing)
            layout.addWidget(load_config_button)

            # OK button
            ok_button = QPushButton("OK", self.open_check_parsing_dialog)
            ok_button.clicked.connect(self.save_and_start_parsing)
            layout.addWidget(ok_button)
            
            try:
                with open('configsParsing.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get('DEFAULT', {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.proxy_method_dropdown.setCurrentText(config.get('proxy_method_dropdown', ''))
                    self.proxy_method_manual_dropdown.setCurrentText(config.get('proxy_method_manual_dropdown', ''))
                    self.proxy_method_manual2_dropdown.setCurrentText(config.get('proxy_method_manual2_dropdown', ''))
                    

                    
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
                    self.limit_input.setValue(config.get('limit_input', 10))         
                    self.existing_group_combo.setCurrentText(config.get('existing_group_combo', ''))
                    self.combo_box.setCurrentText(config.get('combo_box', ''))
                    self.new_group_input.setText(config.get('new_group_input', ''))
                    self.list_username_for_parsing.setPlainText(config.get('listUsername', ''))

            except:
                none = ''
            layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  
            self.open_check_parsing_dialog.setLayout(layout)
            self.open_check_parsing_dialog.exec_()

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
                    
                    self.proxy_method_dropdown.setCurrentText(config.get('proxy_method_dropdown', ''))
                    self.proxy_method_manual_dropdown.setCurrentText(config.get('proxy_method_manual_dropdown', ''))
                    self.proxy_method_manual2_dropdown.setCurrentText(config.get('proxy_method_manual2_dropdown', ''))

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

            proxy_method_dropdown = self.proxy_method_dropdown.currentText()
            proxy_method_manual_dropdown = self.proxy_method_manual_dropdown.currentText()
            proxy_method_manual2_dropdown = self.proxy_method_manual2_dropdown.currentText()

            
                                




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
                'proxy_method_dropdown': proxy_method_dropdown,
                'proxy_method_manual_dropdown': proxy_method_manual_dropdown,
                'proxy_method_manual2_dropdown': proxy_method_manual2_dropdown,
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
            proxy_method_dropdown = self.proxy_method_dropdown.currentText()
            proxy_method_manual_dropdown = self.proxy_method_manual_dropdown.currentText()
            proxy_method_manual2_dropdown = self.proxy_method_manual2_dropdown.currentText()
            
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
                'proxy_method_dropdown': proxy_method_dropdown,
                'proxy_method_manual_dropdown': proxy_method_manual_dropdown,
                'proxy_method_manual2_dropdown': proxy_method_manual2_dropdown,
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
            self.open_check_parsing_dialog.accept()  
            current_table = self.tab_widget.currentWidget()
            if current_table:
                selected_items = current_table.selectedItems()
                if len(selected_items) == 0:
                    QMessageBox.warning(self, "Ошибка", "Не выбраны аккаунты")
                    return
                if selected_items:
                    # Check if any selected account is already "In Progress"
                    selected_rows = list(set(item.row() for item in selected_items))

                    for row in selected_rows:
                        if current_table.item(row, 5) and current_table.item(row, 5).text() == "В работе":
                            QMessageBox.warning(self, "Задача не запустилась", "Выделенные аккаунты уже в работе.")
                            return
                    

                    self.parse_audience(current_table, selected_items, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, processes, threads, listUsername, limit_input,group_name)

    if True: #DIRECT    
        def open_check_direct_dialog(self):

            self.open_check_direct_dialog = QDialog(self)
            self.open_check_direct_dialog.setWindowTitle("Рассылка")
            layout = QVBoxLayout()

            # Proxy group dropdown
            self.status_label = QLabel("Выберите прокси для этой задачи")
            self.proxy_group_dropdown = QComboBox(self.open_check_direct_dialog)
            self.load_proxy_groups_into_dropdown()
            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_group_dropdown)
            
            # Proxy group dropdown
            self.status_label = QLabel("Откуда брать информацию об IP")
            
            self.proxy_method_dropdown = QComboBox(self.open_check_direct_dialog)

            self.load_proxy_method_into_dropdown()
            self.proxy_method_dropdown.currentIndexChanged.connect(self.on_proxy_method_dropdown_changed)

            layout.addWidget(self.status_label)
            layout.addWidget(self.proxy_method_dropdown)


            self.status_label1 = QLabel("Locale")
            self.proxy_method_manual_dropdown = QComboBox(self.open_check_direct_dialog)
            self.load_proxy_method_manual_into_dropdown()
            layout.addWidget(self.status_label1)
            layout.addWidget(self.proxy_method_manual_dropdown)
            
            self.status_label2 = QLabel("Timezone")
            self.proxy_method_manual2_dropdown = QComboBox(self.open_check_direct_dialog)
            self.load_proxy_method_manual2_into_dropdown()
            layout.addWidget(self.status_label2)
            layout.addWidget(self.proxy_method_manual2_dropdown)
            

            
            
            self.status_label = QLabel("Введите шаблон сообщения")
            self.message_for_direct = QTextEdit()
            layout.addWidget(self.status_label)
            layout.addWidget(self.message_for_direct)
            
            
            self.status_label = QLabel("Режим сообщения")
            self.direct_methodmessage_dropdown = QComboBox(self.open_check_direct_dialog)
            self.direct_methodmessage_dropdown.addItems(['Text','Text+Link']) 
            layout.addWidget(self.status_label)
            layout.addWidget(self.direct_methodmessage_dropdown)
            
            
            self.status_label = QLabel("Режим отправки")
            self.direct_method_dropdown = QComboBox(self.open_check_direct_dialog)
            self.direct_method_dropdown.addItems(['Group','Single']) 
            layout.addWidget(self.status_label)
            layout.addWidget(self.direct_method_dropdown)
            
            self.status_label11 = QLabel("Кол-во участников в группе")
            self.limit_input_group = QSpinBox(self.open_check_direct_dialog)
            self.limit_input_group.setRange(1, 50)
            self.limit_input_group.setValue(5)
            layout.addWidget(self.status_label11)
            layout.addWidget(self.limit_input_group)            
            
            
            self.status_label22 = QLabel("Лимит созданных групп за запуск")
            self.limit_input_group2 = QSpinBox(self.open_check_direct_dialog)
            self.limit_input_group2.setRange(1, 50)
            self.limit_input_group2.setValue(4)
            layout.addWidget(self.status_label22)
            layout.addWidget(self.limit_input_group2)  
            
            
            
            
            
            self.status_label33 = QLabel("Лимит отправки сообщений за запуск")
            self.limit_input = QSpinBox(self.open_check_direct_dialog)
            self.limit_input.setRange(1, 1000)
            self.limit_input.setValue(20)
            layout.addWidget(self.status_label33)
            layout.addWidget(self.limit_input)
            #self.direct_method_dropdown.currentIndexChanged.connect(self.on_direct_method_dropdown_changed)
            self.direct_method_dropdown.currentTextChanged.connect(self.on_direct_method_dropdown_changed2)

            self.status_label44 = QLabel("Сон между сообщениями")
            self.limit_input_sleep = QSpinBox(self.open_check_direct_dialog)
            self.limit_input_sleep.setRange(1, 1000)
            self.limit_input_sleep.setValue(5)
            layout.addWidget(self.status_label44)
            layout.addWidget(self.limit_input_sleep)
            
            
            
            
            self.status_label = QLabel("Выберите группу аудитории для рссылки")
            self.existing_group_combo = QComboBox()
            self.existing_group_combo.clear()
            query = "SELECT DISTINCT group_name FROM audience_users"
            self.cursor.execute(query)
            existing_groups = [row[0] for row in self.cursor.fetchall()]
          
            if existing_groups:
                self.existing_group_combo.addItems(existing_groups)
            else:
                QMessageBox.warning(self, "Ошибка", "Нет существующих групп аудиторий.")
                self.existing_group_combo.addItems([''])
                
                
                
            layout.addWidget(self.status_label)
            layout.addWidget(self.existing_group_combo)



                    
                    
            # Number of processes input
            self.status_label = QLabel("Кол-во процессов")
            self.processes_input = QSpinBox(self.open_check_direct_dialog)
            self.processes_input.setRange(1, 100)
            self.processes_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.processes_input)

            # Number of threads input
            self.status_label = QLabel("Кол-во потоков")
            self.threads_input = QSpinBox(self.open_check_direct_dialog)
            self.threads_input.setRange(1, 100)
            self.threads_input.setValue(10)
            layout.addWidget(self.status_label)
            layout.addWidget(self.threads_input)

            # Config name input
            self.status_label = QLabel("Сохранить конфиг?")
            self.config_name_input = QLineEdit(self.open_check_direct_dialog)
            self.config_name_input.setPlaceholderText("Название конфига")
            layout.addWidget(self.status_label)
            layout.addWidget(self.config_name_input)
            # Load config button
            save_config_button = QPushButton("Сохранить конфиг", self.open_check_direct_dialog)
            save_config_button.clicked.connect(self.saveConfigButton_direct)
            layout.addWidget(save_config_button)

            # Config dropdown
            self.status_label = QLabel("Выберите конфиг для его загрузки")

            self.config_dropdown = QComboBox(self.open_check_direct_dialog)
            self.load_configs_into_dropdown_direct()
            layout.addWidget(self.status_label)

            layout.addWidget(self.config_dropdown)

            # Load config button
            load_config_button = QPushButton("Загрузить конфиг", self.open_check_direct_dialog)
            load_config_button.clicked.connect(self.load_config_direct)
            layout.addWidget(load_config_button)

            # OK button
            ok_button = QPushButton("OK", self.open_check_direct_dialog)
            ok_button.clicked.connect(self.save_and_start_direct)
            layout.addWidget(ok_button)
            print('LOAD DEFOLT')
            try:
                with open('configsDirect.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get('DEFAULT', {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.proxy_method_dropdown.setCurrentText(config.get('proxy_method_dropdown', ''))

                    self.proxy_method_manual_dropdown.setCurrentText(config.get('proxy_method_manual_dropdown', ''))
                    self.proxy_method_manual2_dropdown.setCurrentText(config.get('proxy_method_manual2_dropdown', ''))

                    self.limit_input_group.setValue(config.get('limit_input_group', 10))
                    self.limit_input_group2.setValue(config.get('limit_input_group2', 10))
                    self.limit_input.setValue(config.get('limit_input', 10))         

                    self.limit_input_sleep.setValue(config.get('limit_input_sleep', 10))         

                    self.direct_method_dropdown.setCurrentText(config.get('direct_method_dropdown', ''))
                    self.direct_methodmessage_dropdown.setCurrentText(config.get('direct_methodmessage_dropdown', ''))

                    
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
                    self.existing_group_combo.setCurrentText(config.get('existing_group_combo', ''))
                    self.message_for_direct.setPlainText(config.get('message_for_direct', ''))

            except:
                none = ''
                
            print('LOAsD DEFOLT')
 
            if self.direct_method_dropdown.currentText() == 'Group':  #Group
                print('GRO')
                self.limit_input_group.setVisible(True)
                self.limit_input_group2.setVisible(True)

     
                self.status_label11.setVisible(True)
                self.status_label22.setVisible(True)
                self.limit_input.setVisible(False) 
                self.status_label33.setVisible(False)
                
            elif self.direct_method_dropdown.currentText() == 'Single':  #Single
                print('SING')

                self.limit_input_group.setVisible(False)
                self.limit_input_group2.setVisible(False)

                self.status_label11.setVisible(False)
                self.status_label22.setVisible(False)
                self.limit_input.setVisible(True)
                self.status_label33.setVisible(True)
                
            layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)     
            self.open_check_direct_dialog.setLayout(layout)
            self.open_check_direct_dialog.exec_()
                





                
                
        def load_configs_into_dropdown_direct(self):
            # Load saved configs from a file or database
            # For simplicity, using a file here
            try:
                with open('configsDirect.json', 'r') as f:
                    configs = json.load(f)
                    self.config_dropdown.addItems(configs.keys())
            except:
                none = ''

        def load_config_direct(self):
            config_name = self.config_dropdown.currentText()
            try:
                with open('configsDirect.json', 'r') as f:
                    configs = json.load(f)
                    config = configs.get(config_name, {})
                    self.proxy_group_dropdown.setCurrentText(config.get('proxy_group', ''))
                    self.proxy_method_dropdown.setCurrentText(config.get('proxy_method_dropdown', ''))
                    self.proxy_method_manual_dropdown.setCurrentText(config.get('proxy_method_manual_dropdown', ''))
                    self.proxy_method_manual2_dropdown.setCurrentText(config.get('proxy_method_manual2_dropdown', ''))
                    self.direct_method_dropdown.setCurrentText(config.get('direct_method_dropdown', ''))
                    self.direct_methodmessage_dropdown.setCurrentText(config.get('direct_methodmessage_dropdown', ''))
                    
                    self.limit_input_group.setValue(config.get('limit_input_group', 10))
                    self.limit_input_group2.setValue(config.get('limit_input_group2', 10))
                    self.processes_input.setValue(config.get('processes', 10))
                    self.threads_input.setValue(config.get('threads', 10))
                    self.limit_input.setValue(config.get('limit_input', 10))
                    self.limit_input_sleep.setValue(config.get('limit_input_sleep', 10))

                    self.existing_group_combo.setCurrentText(config.get('existing_group_combo', ''))
                    self.message_for_direct.setPlainText(config.get('message_for_direct', ''))
            except FileNotFoundError:
                pass
        def saveConfigButton_direct(self):
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            proxy_method_dropdown = self.proxy_method_dropdown.currentText()
            proxy_method_manual_dropdown = self.proxy_method_manual_dropdown.currentText()
            proxy_method_manual2_dropdown = self.proxy_method_manual2_dropdown.currentText()

            direct_method_dropdown = self.direct_method_dropdown.currentText()
            direct_methodmessage_dropdown = self.direct_methodmessage_dropdown.currentText()
            
            limit_input_group = self.limit_input_group.value()
            limit_input_group2 = self.limit_input_group2.value()


            
            
            processes = self.processes_input.value()
            threads = self.threads_input.value()
            limit_input = self.limit_input.value()
            limit_input_sleep = self.limit_input_sleep.value()

            existing_group_combo = self.existing_group_combo.currentText()
            message_for_direct = self.message_for_direct.toPlainText()

            try:
                with open('configsDirect.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs[config_name] = {
                'proxy_group': proxy_group,
                'proxy_method_dropdown': proxy_method_dropdown,
                'proxy_method_manual_dropdown': proxy_method_manual_dropdown,
                'proxy_method_manual2_dropdown': proxy_method_manual2_dropdown,

                'direct_method_dropdown': direct_method_dropdown,
                'direct_methodmessage_dropdown': direct_methodmessage_dropdown,
                
                'limit_input_group': limit_input_group,
                'limit_input_group2': limit_input_group2,

                

            
            
                'processes': processes,
                'threads': threads,
                'limit_input': limit_input,
                'limit_input_sleep': limit_input_sleep,
                                                                             

                'existing_group_combo': existing_group_combo,
                'message_for_direct': message_for_direct
            }

            with open('configsDirect.json', 'w') as f:
                json.dump(configs, f)
        def save_and_start_direct(self,dialog):
            
            group_name = self.existing_group_combo.currentText()

                
            config_name = self.config_name_input.text()
            proxy_group = self.proxy_group_dropdown.currentText()
            proxy_method_dropdown = self.proxy_method_dropdown.currentText()
            proxy_method_manual_dropdown = self.proxy_method_manual_dropdown.currentText()
            proxy_method_manual2_dropdown = self.proxy_method_manual2_dropdown.currentText()
            direct_method_dropdown = self.direct_method_dropdown.currentText()
            direct_methodmessage_dropdown = self.direct_methodmessage_dropdown.currentText()
            
            limit_input_group = self.limit_input_group.value()
            limit_input_group2 = self.limit_input_group2.value() 
            processes = self.processes_input.value()
            threads = self.threads_input.value()
            limit_input = self.limit_input.value()
            limit_input_sleep = self.limit_input_sleep.value()
            existing_group_combo = self.existing_group_combo.currentText()
            message_for_direct = self.message_for_direct.toPlainText()

            try:
                with open('configsDirect.json', 'r') as f:
                    configs = json.load(f)
            except FileNotFoundError:
                configs = {}

            configs['DEFAULT'] = {
                'proxy_group': proxy_group,
                'proxy_method_dropdown': proxy_method_dropdown,
                'proxy_method_manual_dropdown': proxy_method_manual_dropdown,
                'proxy_method_manual2_dropdown': proxy_method_manual2_dropdown,
                'direct_method_dropdown': direct_method_dropdown,
                'direct_methodmessage_dropdown': direct_methodmessage_dropdown,
                
                'limit_input_group': limit_input_group,
                'limit_input_group2': limit_input_group2,  
                
                'processes': processes,
                'threads': threads,
                'limit_input': limit_input,
                'limit_input_sleep': limit_input_sleep,

                'existing_group_combo': existing_group_combo,
                'message_for_direct': message_for_direct

            }

            with open('configsDirect.json', 'w') as f:
                json.dump(configs, f)
            self.open_check_direct_dialog.accept()  
            current_table = self.tab_widget.currentWidget()
            if current_table:
                selected_items = current_table.selectedItems()
                if len(selected_items) == 0:
                    QMessageBox.warning(self, "Ошибка", "Не выбраны аккаунты")
                    return
                if selected_items:
                    # Check if any selected account is already "In Progress"
                    selected_rows = list(set(item.row() for item in selected_items))

                    for row in selected_rows:
                        if current_table.item(row, 5) and current_table.item(row, 5).text() == "В работе":
                            QMessageBox.warning(self, "Задача не запустилась", "Выделенные аккаунты уже в работе.")
                            return

                    self.direct_message(current_table, selected_items, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,direct_methodmessage_dropdown,direct_method_dropdown,limit_input_group,limit_input_group2, processes, threads, message_for_direct,limit_input_sleep, limit_input,group_name)


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
                query = f"SELECT type FROM {group[0]} LIMIT 1"
                self.cursor.execute(query)
                typeProxy = self.cursor.fetchone()[0]
                self.update_proxy_table(group_name, count, url_update, typeProxy)
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

        if not group_name  or not proxy_type:
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        # Read proxies from file
        if proxy_file != '':
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
        
        if proxy_file != '':

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
        else:
            query = f"INSERT INTO {table_name} (ip, port, login, password, type, url_update) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.execute(query, ('', '', '', '', proxy_type, update_url))
            
            
            
        self.conn.commit()

        # Update proxy table in the UI
        if proxy_file != '':

            self.update_proxy_table(group_name, len(proxies), update_url, proxy_type)
        else:
            self.update_proxy_table(group_name, 0, update_url, proxy_type)

        QMessageBox.information(self, "Успех", "Группа прокси создана успешно")
        self.load_proxy_groups()

    def update_proxy_table(self, group_name, proxy_count, update_url, proxy_type):
        row_position = self.proxy_table.rowCount()
        self.proxy_table.insertRow(row_position)
        self.proxy_table.setItem(row_position, 0, QTableWidgetItem(group_name))
        self.proxy_table.setItem(row_position, 1, QTableWidgetItem(str(proxy_count)))
        self.proxy_table.setItem(row_position, 2, QTableWidgetItem(proxy_type))
        self.proxy_table.setItem(row_position, 3, QTableWidgetItem(update_url))
        self.proxy_table.setItem(row_position, 4, QTableWidgetItem('-'))
    def show_audience_context_menu(self, position):
        context_menu = QMenu()
        delete_action = QAction("Удалить группу", self)
        delete_action.triggered.connect(self.delete_audience_group)
        context_menu.addAction(delete_action)
        savefile_action = QAction("Сохранить в файл всю аудиторию", self)
        savefile_action.triggered.connect(self.save_audience_group_to_file)
        context_menu.addAction(savefile_action)
        
        savefile2_action = QAction("Сохранить в файл пройденную аудиторию", self)
        savefile2_action.triggered.connect(self.save_passed_audience_to_file)
        context_menu.addAction(savefile2_action)  
        
        savefile3_action = QAction("Сохранить в файл не пройденную аудиторию", self)
        savefile3_action.triggered.connect(self.save_new_audience_to_file)
        context_menu.addAction(savefile3_action)  
        

        
        
        
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
            
            

    def save_audience_group_to_file(self):
        selected_rows = self.audience_table.selectionModel().selectedRows()
        for index in selected_rows:
            group_name = self.audience_table.item(index.row(), 0).text()
            
            # Получить аудиторию из базы данных (только второй столбец)
            try:
                conn = sqlite3.connect(self.db_filename)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM audience_users WHERE group_name=?", (group_name,))
                audience_data = cursor.fetchall()
                cursor.close()
                conn.close()
            except sqlite3.Error as e:
                print(f"Ошибка при получении аудитории из базы данных: {e}")
                return
            
            # Открыть диалоговое окно для сохранения файла
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить аудиторию в файл", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                try:
                    # Сохранить аудиторию в файл
                    with open(file_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        # Записываем данные второго столбца в файл
                        writer.writerows(audience_data)
                    print(f"Аудитория успешно сохранена в файл: {file_path}")
                except IOError as e:
                    print(f"Ошибка при сохранении аудитории в файл: {e}")
                


    def save_passed_audience_to_file(self):
        selected_rows = self.audience_table.selectionModel().selectedRows()
        for index in selected_rows:
            group_name = self.audience_table.item(index.row(), 0).text()

            # Получить аудиторию с указанным статусом из базы данных
            try:
                conn = sqlite3.connect(self.db_filename)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM audience_users WHERE group_name=? AND status='Пройден'", (group_name,))
                audience_data = cursor.fetchall()
                cursor.close()
                conn.close()
            except sqlite3.Error as e:
                print(f"Ошибка при получении аудитории из базы данных: {e}")
                return

            # Открыть диалоговое окно для сохранения файла
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить аудиторию в файл", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                try:
                    # Сохранить аудиторию в файл
                    with open(file_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        # Записываем данные второго столбца в файл
                        writer.writerows(audience_data)
                    print(f"Аудитория успешно сохранена в файл: {file_path}")
                except IOError as e:
                    print(f"Ошибка при сохранении аудитории в файл: {e}")
 
    def save_new_audience_to_file(self):
        selected_rows = self.audience_table.selectionModel().selectedRows()
        for index in selected_rows:
            group_name = self.audience_table.item(index.row(), 0).text()

            # Получить аудиторию с указанным статусом из базы данных
            try:
                conn = sqlite3.connect(self.db_filename)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM audience_users WHERE group_name=? AND status='Новый'", (group_name,))
                audience_data = cursor.fetchall()
                cursor.close()
                conn.close()
            except sqlite3.Error as e:
                print(f"Ошибка при получении аудитории из базы данных: {e}")
                return

            # Открыть диалоговое окно для сохранения файла
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить аудиторию в файл", "", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                try:
                    # Сохранить аудиторию в файл
                    with open(file_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        # Записываем данные второго столбца в файл
                        writer.writerows(audience_data)
                    print(f"Аудитория успешно сохранена в файл: {file_path}")
                except IOError as e:
                    print(f"Ошибка при сохранении аудитории в файл: {e}")          
            
            
            
            
            
    def terminate_audience_task(self, task_id):
        print('terminate_audience_task')
        try:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if hasattr(task, 'processes') and task.processes:
                    for process in task.processes:
                        if process.is_alive():
                            none = ''
                            process.terminate()
                            process.join()
                    print(f"All processes for task {task.task_name} have been terminated.")
                    
                    # Update account status to 'Остановлен'
                    for row in task.rows:
                        if task.table.item(row, 5).text() == "В работе" or "Собрал" in task.table.item(row, 5).text() or "Отправил" in task.table.item(row, 5).text():  # Use task.table instead of self.tab_widget.currentWidget()
                            task.table.setItem(row, 5, QTableWidgetItem("Остановлен"))
                            self.set_row_color(task.table, row, QColor(220,220,250))
                            print(f"Group {task.table.item(row, 0).text()} status set to 'Остановлен'")
                else:
                    print(f"No processes found for task {task.task_name}.")
            else:
                print(f"Task {task_id} not found.")
        except:
            print('err terminate_audience_task')
             
    def stop_task(self, task_id):
        print('stop_task')

        task_widget = self.tasks.get(task_id)
        if task_widget:
            task_widget.update_status(0,0,0, "Остановлен")
            self.terminate_audience_task(task_id)     
            
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
            query = f"CREATE TABLE IF NOT EXISTS {table_name} (login TEXT, password TEXT, device TEXT, api_ua TEXT, cookies TEXT, status TEXT, messages_sent INTEGER)"
            self.cursor.execute(query)
            self.conn.commit()
            self.add_table_tab(table_name)
            print(f"Создана таблица {table_name}")

    def add_table_tab(self, table_name):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Логин", "Пароль", "Device", "UA", "Cookies", "Статус", "Кол-во сообщений"])
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
            status_item = table.item(row, 5)
            if status_item is not None:
                status_text = status_item.text()
                if status_text == "Валид":
                    color = QColor(130,250,130)
                elif status_text == "Невалид":
                    color = QColor(250,140,140)
                elif status_text == "В работе":
                    color = QColor(250,250,140)
                    color = None
                    
                elif status_text == "Завершен":
                    color = QColor(220,220,250)
                elif status_text == "Закончил парсинг":
                    color = QColor(220,220,250)
                elif status_text == "Закончил рассылку":
                    color = QColor(220,220,250)
                else:
                    color = None
                    
        if color is not None:
            for col in range(table.columnCount()):
                table.item(row, col).setBackground(color)

    def load_audience_data(self):
        query = "SELECT group_name, COUNT(user_id), SUM(CASE WHEN status = 'Пройден' THEN 1 ELSE 0 END) FROM audience_users GROUP BY group_name"
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
                        
                        data_list.append((login, password, device, "", cookies, "-", 0))  # Замените "status" и "0" на нужные значения, если требуется

                query = f"INSERT INTO {table_name} (login, password, device, api_ua, cookies, status, messages_sent) VALUES (?, ?, ?, ?, ?, ?, ?)"
                self.cursor.executemany(query, data_list)
                self.conn.commit()

                for data in data_list:
                    row_pos = current_table.rowCount()
                    current_table.insertRow(row_pos)
                    for col_pos, value in enumerate(data):
                        current_table.setItem(row_pos, col_pos, QTableWidgetItem(str(value)))
                    self.set_row_color(current_table, row_pos)

                print(f"Аккаунты загружены в таблицу {table_name}")

    def check_validity(self, table, items, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, processesx, threads):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        status_queue = multiprocessing.Queue()
        infoUA_queue = multiprocessing.Queue()
        infoCookie_queue = multiprocessing.Queue()
        infoDevice_queue = multiprocessing.Queue()

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
            #login_list = [table.item(row, 0).text() for row in chunk]
            login_list = [
                (table.item(row, 0).text(), table.item(row, 1).text(), table.item(row, 2).text(), table.item(row, 3).text(), table.item(row, 4).text())
                for row in chunk
            ]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 5, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
                self.set_row_color(table, row, None)
            p = multiprocessing.Process(target=process_function, args=(list(zip(login_list, row_list)), table_name, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, threads))
            processes.append(p)
            p.start()

        task_widget.processes = processes  # Associate processes with the task_widget
        self.monitor_validity_processes(processes, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, table_name, table, task_id)
        print("Проверка валидности аккаунтов запущена")
              
    def monitor_validity_processes(self, processes, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, table_name, table, task_name):
        def check_results(task_name):
            conn = sqlite3.connect('total.db')
            cursor = conn.cursor()
            updates = []
            table_updates = []
            processed_rows = set()  # Keep track of processed rows to avoid double counting

            updatesUA = []
            table_updatesUA = []
            processed_rowsUA = set()

            updatesDevice = []
            table_updatesDevice = []
            processed_rowsDevice = set()

            updatesCookie = []
            table_updatesCookie = []
            processed_rowsCookie = set()
            
            
            valid_count = 0
            invalid_count = 0

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
                    
                    
                    
                    
            while not infoUA_queue.empty():
                login, api_ua, row = infoUA_queue.get()
                print(api_ua)
                if row in processed_rowsUA:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesUA.append((api_ua, login))
                table_updatesUA.append((row, api_ua))
                processed_rowsUA.add(row)  # Mark row as processed

            if updatesUA:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET api_ua = ? WHERE login = ?"
                    cursor.executemany(query, updatesUA)
                    conn.commit()
                    print(f"Обновил юзер агент  {str(updatesUA)} {len(updatesUA)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    
            while not infoDevice_queue.empty():
                login, device, row = infoDevice_queue.get()
                print(device)
                if row in processed_rowsDevice:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesDevice.append((device, login))
                table_updatesDevice.append((row, device))
                processed_rowsDevice.add(row)  # Mark row as processed

            if updatesDevice:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET device = ? WHERE login = ?"
                    cursor.executemany(query, updatesDevice)
                    conn.commit()
                    print(f"Обновил девайс  {str(updatesDevice)} {len(updatesDevice)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    

            while not infoCookie_queue.empty():
                login, cookie, row = infoCookie_queue.get()
                print(cookie)
                if row in processed_rowsCookie:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesUA.append((cookie, login))
                table_updatesCookie.append((row, cookie))
                processed_rowsCookie.add(row)  # Mark row as processed

            if updatesCookie:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET cookie = ? WHERE login = ?"
                    cursor.executemany(query, updatesCookie)
                    conn.commit()
                    print(f"Обновил cookie  {str(updatesCookie)} {len(updatesCookie)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    



            conn.close()
            for row, cookie in table_updatesCookie:
                table.setItem(row, 4, QTableWidgetItem(cookie))
                print(f"Updated table row {row} with status {cookie}")
                self.set_row_color(table, row, QColor(250,250,140))
                
            for row, device in table_updatesDevice:
                table.setItem(row, 2, QTableWidgetItem(device))
                print(f"Updated table row {row} with status {device}")
                self.set_row_color(table, row, QColor(250,250,140))
            
            for row, api_ua in table_updatesUA:
                table.setItem(row, 3, QTableWidgetItem(api_ua))
                print(f"Updated table row {row} with status {api_ua}")
                self.set_row_color(table, row, QColor(250,250,140))

            for row, valid_status in table_updates:
                table.setItem(row, 5, QTableWidgetItem(valid_status))
                self.set_row_color(table, row)
                print(f"Updated table row {row} with status {valid_status}")

            while not status_queue.empty():
                row, status = status_queue.get()
                table.setItem(row, 5, QTableWidgetItem(status))
                self.set_row_color(table, row)
                print(f"Updated status queue row {row} with status {status}")
        

            task_widget = self.tasks[task_name]
            task_widget.update_status(valid_count, invalid_count, '', "В работе")  # Example usage
            #print(f"Task widget updated: valid_count={valid_count}, invalid_count={invalid_count}, status='В работе'")

            for p in processes:
                if p.is_alive():
                    QTimer.singleShot(100, partial(check_results, task_name))
                    return

            task_widget.update_status(valid_count, invalid_count, '', "Завершен")
            print(f"Task widget final update: valid_count={valid_count}, invalid_count={invalid_count}, status='Завершен'")
            print("Проверка валидности аккаунтов завершена")

        QTimer.singleShot(100, partial(check_results, task_name))    
        
    def parse_audience(self, table, items, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, processesx, threads, listUsername, limit_input,group_name):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        status_queue = multiprocessing.Queue()
        infoUA_queue = multiprocessing.Queue()
        infoCookie_queue = multiprocessing.Queue()
        infoDevice_queue = multiprocessing.Queue()

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
            login_list = [
                (table.item(row, 0).text(), table.item(row, 1).text(), table.item(row, 2).text(), table.item(row, 3).text(), table.item(row, 4).text())
                for row in chunk
            ]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 5, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
                self.set_row_color(table, row, None)
            p = multiprocessing.Process(target=process_audience_function, args=(list(zip(login_list, row_list)), table_name, group_name, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown, threads, listUsername_queue, limit_input))

            processes.append(p)
            p.start()

        task_widget.processes = processes  # Associate processes with the task_widget
        self.monitor_audience_processes(processes, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, table_name, table, task_id,group_name)
        print("Парсинг аудитории запущен")
    
    def monitor_audience_processes(self, processes, result_queue, status_queue, infoUA_queue,infoCookie_queue,infoDevice_queue, table_name, table, task_name,group_name):
        def check_results(task_name):
            conn = sqlite3.connect('total.db')
            cursor = conn.cursor()
            table_updates = []
            collected_users = 0         
            user_count = 0
            processed_rows = set()  # Keep track of processed rows to avoid double counting

            updatesUA = []
            table_updatesUA = []
            processed_rowsUA = set()

            updatesDevice = []
            table_updatesDevice = []
            processed_rowsDevice = set()

            updatesCookie = []
            table_updatesCookie = []
            processed_rowsCookie = set()


            while not result_queue.empty():
                login, status_acc, user_ids, row = result_queue.get()
                print('status_acc parsing: '+status_acc)
                if isinstance(user_ids, list):
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
                else:
                    if row in processed_rows:
                        print(f"Row {row} already processed, skipping.")
                        continue  # Skip already processed rows
                    table_updates.append((row, user_ids))
 

            while not infoUA_queue.empty():
                login, api_ua, row = infoUA_queue.get()
                print(api_ua)
                if row in processed_rowsUA:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesUA.append((api_ua, login))
                table_updatesUA.append((row, api_ua))
                processed_rowsUA.add(row)  # Mark row as processed

            if updatesUA:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET api_ua = ? WHERE login = ?"
                    cursor.executemany(query, updatesUA)
                    conn.commit()
                    print(f"Обновил юзер агент  {str(updatesUA)} {len(updatesUA)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    
            while not infoDevice_queue.empty():
                login, device, row = infoDevice_queue.get()
                print(device)
                if row in processed_rowsDevice:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesDevice.append((device, login))
                table_updatesDevice.append((row, device))
                processed_rowsDevice.add(row)  # Mark row as processed

            if updatesDevice:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET device = ? WHERE login = ?"
                    cursor.executemany(query, updatesDevice)
                    conn.commit()
                    print(f"Обновил девайс  {str(updatesDevice)} {len(updatesDevice)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    

            while not infoCookie_queue.empty():
                login, cookie, row = infoCookie_queue.get()
                print(cookie)
                if row in processed_rowsCookie:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesUA.append((cookie, login))
                table_updatesCookie.append((row, cookie))
                processed_rowsCookie.add(row)  # Mark row as processed

            if updatesCookie:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET cookie = ? WHERE login = ?"
                    cursor.executemany(query, updatesCookie)
                    conn.commit()
                    print(f"Обновил cookie  {str(updatesCookie)} {len(updatesCookie)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    




            
            
            
            conn.close()
            

            
            for row, cookie in table_updatesCookie:
                table.setItem(row, 4, QTableWidgetItem(cookie))
                print(f"Updated table row {row} with status {cookie}")
                self.set_row_color(table, row, QColor(250,250,140))
                
            for row, device in table_updatesDevice:
                table.setItem(row, 2, QTableWidgetItem(device))
                print(f"Updated table row {row} with status {device}")
                self.set_row_color(table, row, QColor(250,250,140))
            
            for row, api_ua in table_updatesUA:
                table.setItem(row, 3, QTableWidgetItem(api_ua))
                print(f"Updated table row {row} with status {api_ua}")
                self.set_row_color(table, row, QColor(250,250,140))
                
            for row, user_count in table_updates:
                print('ColorTableStatus: '+str(user_count))
                if 'Закончил парсинг' in status_acc:
                    table.setItem(row, 5, QTableWidgetItem('Закончил парсинг'))
                    self.set_row_color(table, row)  
                elif 'Невалид' in status_acc:
                    table.setItem(row, 5, QTableWidgetItem('Невалид. Закончил парсинг'))
                    self.set_row_color(table, row, QColor(250,140,140))        
                    
                    
                else:
                    table.setItem(row, 5, QTableWidgetItem('Собрал: '+str(user_count)+' ...'))
                    self.set_row_color(table, row, QColor(250,250,140))

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

    def direct_message(self, table, items, proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,direct_methodmessage_dropdown,direct_method_dropdown,limit_input_group,limit_input_group2, processesx, threads, message_for_direct,limit_input_sleep, limit_input,group_name):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table)).strip()
        selected_rows = list(set(item.row() for item in items))
        total_accounts = len(selected_rows)
        processes = []
        result_queue = multiprocessing.Queue()
        infoUA_queue = multiprocessing.Queue() 
        infoCookie_queue = multiprocessing.Queue()
        infoDevice_queue = multiprocessing.Queue()

        task_id = f"{table_name}_{time.time()}"  # Generate a unique task_id
        task_name = f"Direct Message ({table_name})"
        task_widget = TaskMonitorWidget(task_name, total_accounts, task_id, table, group_name)  # Pass table and group_name here

        task_widget.stop_task_signal.connect(lambda: self.stop_task(task_id))
        self.stats_layout.addWidget(task_widget)
        self.tasks[task_id] = task_widget
        task_widget.rows = selected_rows  # Associate rows with the task

        process_count = min(processesx, (total_accounts + 99) // 100)
        accounts_per_process = (total_accounts + process_count - 1) // process_count

        print(f"Starting {process_count} processes with {accounts_per_process} accounts each.")
        
        
        def get_new_users_from_group(group_name):
            conn = sqlite3.connect('total.db')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM audience_users WHERE status = 'Новый' AND group_name = ?", (group_name,))
            users = cursor.fetchall()
            conn.close()
            return [user[0] for user in users]
            
            
        listUserIdQueue = multiprocessing.Queue()  
        account_listId = get_new_users_from_group(group_name)
        for accountId in account_listId:
            listUserIdQueue.put(accountId)
            
  
  
            
        for i in range(0, total_accounts, accounts_per_process):
            chunk = selected_rows[i:i + accounts_per_process]
            login_list = [
                (table.item(row, 0).text(), table.item(row, 1).text(), table.item(row, 2).text(), table.item(row, 3).text(), table.item(row, 4).text())
                for row in chunk
            ]
            row_list = chunk
            for row in chunk:
                table.setItem(row, 5, QTableWidgetItem("В работе"))
                self.set_row_color(table, row, QColor(250,250,140))
                self.set_row_color(table, row, None)
            p = multiprocessing.Process(target=process_direct_function, args=(list(zip(login_list, row_list)), table_name, group_name, result_queue,infoUA_queue,infoCookie_queue,infoDevice_queue,  proxy_group,proxy_method_dropdown,proxy_method_manual_dropdown,proxy_method_manual2_dropdown,direct_methodmessage_dropdown,direct_method_dropdown,limit_input_group,limit_input_group2, threads, listUserIdQueue, message_for_direct,limit_input_sleep, limit_input))

            processes.append(p)
            p.start()

        task_widget.processes = processes  # Associate processes with the task_widget
        self.monitor_direct_processes(processes,  result_queue,infoUA_queue,infoCookie_queue,infoDevice_queue,  table_name, table, task_id,group_name)
        print("Рассылка запущена")
    
    def monitor_direct_processes(self, processes,  result_queue,infoUA_queue,infoCookie_queue,infoDevice_queue,  table_name, table, task_name,group_name):
        def check_results(task_name):
            conn = sqlite3.connect('total.db')
            cursor = conn.cursor()
            table_updates = []
            collected_users = 0
            user_count = 0
            messages_sentAll = 0
            messages_sent = 0
            processed_rows = set()  # Keep track of processed rows to avoid double counting
            
            
            updatesUA = []
            table_updatesUA = []
            processed_rowsUA = set()

            updatesDevice = []
            table_updatesDevice = []
            processed_rowsDevice = set()

            updatesCookie = []
            table_updatesCookie = []
            processed_rowsCookie = set()

            while not result_queue.empty():
                login, status_acc, user_ids, row = result_queue.get()
                print(login)
                print(status_acc)

  
                if row in processed_rows:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows
            
                
                
                if status_acc == "Невалид" or status_acc == "Спам-блок":
                    table_updates.append((row, user_ids))

                else:
                    
                    user_count = len(user_ids)  # Подсчет количества пользователей
                    messages_sentAll += user_count
                    table_updates.append((row, user_count))

                    processed_rows.add(row)  # Mark row as processed

                    for user_id in user_ids:
                        cursor.execute("UPDATE audience_users SET status = 'Пройден' WHERE user_id = ?", (user_id,))
                    print('table_name: '+table_name)    
                    cursor.execute("UPDATE "+table_name+" SET messages_sent = messages_sent + ? WHERE login = ?", (user_count, login,))
                    self.update_audiencefordirect_table((group_name, user_count, row, table_name))

                    cursor.execute("SELECT messages_sent FROM " + table_name + " WHERE login = ?", (login,))

                    result = cursor.fetchone()
                    if result:
                        messages_sent = result[0]
                        print('messages_sent'+str(messages_sent))
                        messages_sent = str(messages_sent)
                    else:
                        messages_sent = 'error'
            
            while not infoUA_queue.empty():
                login, api_ua, row = infoUA_queue.get()
                print(api_ua)
                if row in processed_rowsUA:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesUA.append((api_ua, login))
                table_updatesUA.append((row, api_ua))
                processed_rowsUA.add(row)  # Mark row as processed

            if updatesUA:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET api_ua = ? WHERE login = ?"
                    cursor.executemany(query, updatesUA)
                    conn.commit()
                    print(f"Обновил юзер агент  {str(updatesUA)} {len(updatesUA)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    
            while not infoDevice_queue.empty():
                login, device, row = infoDevice_queue.get()
                print(device)
                if row in processed_rowsDevice:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesDevice.append((device, login))
                table_updatesDevice.append((row, device))
                processed_rowsDevice.add(row)  # Mark row as processed

            if updatesDevice:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET device = ? WHERE login = ?"
                    cursor.executemany(query, updatesDevice)
                    conn.commit()
                    print(f"Обновил девайс  {str(updatesDevice)} {len(updatesDevice)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    

            while not infoCookie_queue.empty():
                login, cookie, row = infoCookie_queue.get()
                print(cookie)
                if row in processed_rowsCookie:
                    print(f"Row {row} already processed, skipping.")
                    continue  # Skip already processed rows

                updatesUA.append((cookie, login))
                table_updatesCookie.append((row, cookie))
                processed_rowsCookie.add(row)  # Mark row as processed

            if updatesCookie:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    query = f"UPDATE {table_name} SET cookie = ? WHERE login = ?"
                    cursor.executemany(query, updatesCookie)
                    conn.commit()
                    print(f"Обновил cookie  {str(updatesCookie)} {len(updatesCookie)} entries.")
                except sqlite3.OperationalError as e:
                    print(f"Database error: {str(e)}")
                    conn.rollback()       
                    

            
            
            
            
            
            
            conn.commit()
            conn.close()



            for row, cookie in table_updatesCookie:
                table.setItem(row, 4, QTableWidgetItem(cookie))
                print(f"Updated table row {row} with status {cookie}")
                self.set_row_color(table, row, QColor(250,250,140))
                
            for row, device in table_updatesDevice:
                table.setItem(row, 2, QTableWidgetItem(device))
                print(f"Updated table row {row} with status {device}")
                self.set_row_color(table, row, QColor(250,250,140))
            
            for row, api_ua in table_updatesUA:
                table.setItem(row, 3, QTableWidgetItem(api_ua))
                print(f"Updated table row {row} with status {api_ua}")
                self.set_row_color(table, row, QColor(250,250,140))


                    
                    
                    
            for row, user_count in table_updates:
                print('ColorTableStatus1: '+str(user_count))
                if 'Закончил рассылку' in status_acc:
                    table.setItem(row, 5, QTableWidgetItem('Закончил рассылку'))
                    table.setItem(row, 6, QTableWidgetItem(messages_sent))
                    self.set_row_color(table, row) 
                elif 'Невалид' in status_acc:
                    table.setItem(row, 5, QTableWidgetItem('Невалид. Закончил рассылку'))
                    self.set_row_color(table, row, QColor(250,140,140)) 
                elif 'Спам-блок' in status_acc:
                    table.setItem(row, 5, QTableWidgetItem('Спам-блок. Закончил рассылку'))
                    self.set_row_color(table, row, QColor(140,140,140))                  
                    
                    
                    
                else:
                    table.setItem(row, 5, QTableWidgetItem('Отправил: '+str(user_count)+' сообщений'))

                    table.setItem(row, 6, QTableWidgetItem(messages_sent))
                    self.set_row_color(table, row, QColor(250,250,140))
            #print('test1')
            task_widget = self.tasks[task_name]
            #print('test2')

            task_widget.update_status(0, 0, messages_sentAll, "В работе")  # Обновление статуса с учетом количества пользователей
            #print('test3')
            try:
                for p in processes:
                    
                    if p.is_alive():
                        QTimer.singleShot(100, partial(check_results, task_name))
                        return
                #print('test4')
            except:
                print('VAIOSJDn DOSAJ')
            task_widget.update_status(0, 0, messages_sentAll, "Завершен")

            print("Рассылка завершена")

        QTimer.singleShot(100, partial(check_results, task_name))

    def update_audiencefordirect_table(self, result):
        group_name, user_count, row, table_name = result
        print('1update_audiencefordirect_table ['+group_name+']')
        # Проверить, существует ли группа уже в таблице
        rows = self.audience_table.rowCount()
        group_row = -1
        for row in range(rows):
            print('self.audience_table.item(row, 0).text(): '+self.audience_table.item(row, 0).text()+'')
            if self.audience_table.item(row, 0).text() == group_name:
                group_row = row
                break
                
                
        print('2update_audiencefordirect_table')

        current_count = int(self.audience_table.item(group_row, 2).text())
        new_count = current_count + user_count
        print('new_count:'+str(new_count))
        self.audience_table.setItem(group_row, 2, QTableWidgetItem(str(new_count)))
            
        print(f"Updated group {group_name} with {user_count} ready users")

        # Вызов функции обновления пользовательского интерфейса после добавления группы
        self.audience_table.viewport().update()
      
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
    
    def table_context_menu(self, pos, table):
        menu = QMenu()
        delete_action = QAction("Удалить выбранные строки", self)
        delete_action.triggered.connect(lambda: self.delete_selected_rows(table))
        menu.addAction(delete_action)
        delete_action = QAction("Удалить все невалидные аккаунты", self)
        delete_action.triggered.connect(lambda: self.delete_invalid_accounts(table))
        menu.addAction(delete_action)
        menu.exec_(table.viewport().mapToGlobal(pos))
    
    def delete_invalid_accounts(self,table):
        table_name = self.tab_widget.tabText(self.tab_widget.indexOf(table))
        query = "DELETE FROM "+table_name+" WHERE status='Невалид'"
        self.cursor.execute(query)
        self.conn.commit()
        print("Deleted invalid accounts from database")

        # Отключение сигналов обновления таблицы
        table.blockSignals(True)
        
        rows = table.rowCount()
        for row in range(rows - 1, -1, -1):
            status = table.item(row, 5).text()
            print(status)
            if status == "Невалид":
                table.removeRow(row)
        
        # Включение сигналов обновления таблицы
        table.blockSignals(False)
        
        
        

        print("Deleted invalid accounts from active table")
             
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

class LicenseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter License Key")
        self.layout = QVBoxLayout()

        self.label = QLabel("Please enter your license key:")
        self.layout.addWidget(self.label)

        self.license_input = QLineEdit()
        self.layout.addWidget(self.license_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_license)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def submit_license(self):
        license_key = self.license_input.text()
        # Handle the license key (e.g., save it, validate it, etc.)
        self.accept()
    





def main():
    app = QApplication(sys.argv)

    license_data = read_license()
    if not license_data or license_data['expiration_time'] < time.time():
        license_data = prompt_license()

    if __name__ == '__main__':
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())    
    while True:
        result = validate_license(license_data['license_key'])
        if not result['valid']:
            QMessageBox.critical(None, 'Error', 'License expired or invalid.')
            sys.exit(1)
        time.sleep(60)

if __name__ == '__main__':
    main()
