# -*- coding: utf-8 -*-


##### designer
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QStackedWidget,
    QTableView, QVBoxLayout, QLabel, QHeaderView, QStyledItemDelegate, QAbstractItemView
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor, QBrush
from PyQt5.QtCore import QStateMachine, QState, Qt, QTimer, QRect, QSize

from PyQt5.uic import loadUi
import pygame.mixer

#### server
import sys
from threading import Thread
import socket
import json
import os
reload(sys)
sys.setdefaultencoding('utf-8')

class SocketServer(Thread):
    def __init__(self, server_ip, server_port):
        super(SocketServer, self).__init__()
        self.server_ip = server_ip
        self.server_port = server_port
        self.stop_thread = False
        self.file_path = None

    def stop(self):
        self.stop_thread = True

    def process_data_and_save(self, received_data):
        try:
            full_data = json.loads(received_data)
            data = full_data.get("Content", []) 
            for entry in data:
                game_type = entry.get("Game Type", "")
                team_name = entry.get("Team Name", "")
                time = entry.get("Time", "")
                group = entry.get("Group", "")
                timestamp = entry.get("Timestamp", "")

                print("Data received:")
                print("Timestamp:", timestamp)
                print("Game Type:", game_type)
                print("Team Name:", team_name.encode('utf-8'))
                print("Time:", time)
                print("Group:", group)

                if game_type in ["team", "group"]:
                    self.file_path = '_data/siege_{}_data.json'.format(game_type)
                    self.file_path = self.file_path.encode('utf-8')
                    
                    existing_data = []
                    if os.path.exists(self.file_path):
                        with open(self.file_path, 'r') as file:
                            try:
                                existing_data = json.load(file)
                            except ValueError:
                                print("Warning: The file {} seems to be empty or not formatted correctly.".format(self.file_path))
                                existing_data = []

                    duplicate_entry = next((x for x in existing_data if x['Team Name'] == team_name and x['Timestamp'] == timestamp), None)

                    if not duplicate_entry:
                        existing_data.append(entry)
                        with open(self.file_path, 'w') as file:
                            json.dump(existing_data, file, ensure_ascii=False, indent=4)  # Indent added for readability
                    else:
                        print("Entry with the same Timestamp and Team Name already exists.")
                else:
                    print("Invalid game type received.")
        except Exception as e:  # 여기를 수정하여 모든 예외를 포착하도록 합니다.
            print("Error:", e)


    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.server_ip, self.server_port))
        server_socket.listen(5)

        print("Listening on {}:{}".format(self.server_ip, self.server_port))

        while not self.stop_thread:
            server_socket.settimeout(1.0)
            try:
                client_socket, client_address = server_socket.accept()
                print("Connected to", client_address)
                
                client_socket.settimeout(3.0)
                buffer = []
                while True:
                    chunk = client_socket.recv(4096)  # chunk를 받습니다.
                    if not chunk:
                        break  # 더 이상 데이터가 없을 경우 loop를 종료합니다.
                    buffer.append(chunk.decode('utf-8'))
                received_data = ''.join(buffer)  # 모든 데이터를 합칩니다.
                
                print(received_data)
                self.process_data_and_save(received_data)
            except socket.timeout:
                continue
        server_socket.close()
        print("Server socket closed and thread terminated.")

class CLabel(QLabel, object):
    def __init__(self, type, text, parent):
        super(QLabel, self).__init__(parent=parent)
        self.setText(text)
        sshFile="_styles/main.qss"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        if type == "display":
            self.setObjectName('displaylabel')
        elif type == "state":
            self.setObjectName('statelabes')
            
class CenterIconDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Check if the item has an icon
        icon = index.data(Qt.DecorationRole)
        if icon:
            rect = option.rect
            
            # Calculate new icon size based on the row's height
            desiredHeight = int(rect.height() * 0.80)
            desiredWidth = int(rect.width() * 0.80)
            
            # Set iconSize to either the icon's actual size or the desired size, whichever is smaller
            iconSize = icon.actualSize(QSize(desiredWidth, desiredHeight))
            
            iconRect = QRect(
                rect.left() + (rect.width() - iconSize.width()) // 2,  # Center the icon horizontally
                rect.top() + (rect.height() - iconSize.height()) // 2,  # Center the icon vertically
                iconSize.width(),
                iconSize.height()
            )
            icon.paint(painter, iconRect)
        else:
            super(CenterIconDelegate, self).paint(painter, option, index)

class CTable(QTableView, object):
    HEADER_LABELS = ["등수","그룹", "팀이름", "시간", "날짜"]
    def __init__(self, game_type, parent=None):
        super(CTable, self).__init__(parent)
        self.parent_widget = self.parent()
        self.game_type = game_type
        
        self.vheader = self.verticalHeader()
        self.hheader = self.horizontalHeader()

        self.setShowGrid(False)  # Hide grid lines
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        self.vheader.setVisible(False)  # Hide vertical header (row numbers)
        self.hheader.setVisible(False)
        self.table_model = QStandardItemModel()
        self.setModel(self.table_model)
        self.setSelectionBehavior(QAbstractItemView.SelectRows) 
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.setItemDelegateForColumn(1, CenterIconDelegate(self))
        self.set_initial_row_height()
        self.set_font()

    def resizeEvent(self, event):
        super(CTable, self).resizeEvent(event)
        self.adjustColumnSizes()
        self.set_initial_row_height()
        self.set_font()
    
    def set_initial_row_height(self):
        # Calculate font size based on screen width
        screen_width = self.width()
        font_size = int(screen_width * 0.02)
        row_height = int(font_size * 2)  # Adjust the multiplier as needed
        for row in range(self.table_model.rowCount()):
            self.setRowHeight(row, row_height)
    
    def set_font(self):
        # Calculate font size based on screen width
        screen_width = self.width()
        font_size = int(screen_width * 0.02)  # Adjust the multiplier as needed

        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

        
    def adjustColumnSizes(self):
        total_width = self.parent_widget.width()
        self.hheader.resizeSection(0, total_width * 0.09)  # 10% of the width
        self.hheader.resizeSection(1, total_width * 0.09)  # 10% of the width
        self.hheader.resizeSection(2, total_width * 0.36)  # 35% of the width
        self.hheader.resizeSection(3, total_width * 0.29)  # 35% of the width
        self.hheader.resizeSection(4, total_width * 0.14)  # 20% of the width
        
    def extract_month_day_from_timestamp(self,timestamp):
        # 예: "2023-08-30 04:58:26" => "08-30"
        try:
            return timestamp.split(' ')[0][-5:]
        except:
            return "00-00"
        
    def read_data_from_file(self, file_path):
        data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    content = file.read().strip()  # Read the file content and remove any whitespace
                    
                    if not content:
                        print("Warning: The file {} is empty.".format(file_path))
                        return data
                    
                    parsed_data = json.loads(content)
                    for entry in parsed_data:
                        game_type = entry.get("Game Type", "")
                        team_name = entry.get("Team Name", "").strip()
                        time = entry.get("Time", "").strip()
                        group = entry.get("Group", "").strip()
                        timestamp  = entry.get("Timestamp")
                        month_day = self.extract_month_day_from_timestamp(timestamp)

                        if team_name and time:  # Check if both team_name and time are not empty
                            data.append((team_name, group, time, month_day))
                    
            except IOError:
                pass
                print("Error reading the file: '{}'.".format(file_path))
            except ValueError as e:
                
                print("Error parsing JSON from {}: {}".format(file_path, e))
            except Exception as e:
                print("An unexpected error occurred: {}".format(e))
        else:
            print("File '{}' does not exist. Creating...".format(file_path))
            try:
                with open(file_path, 'w') as file:
                    json.dump([], file, ensure_ascii=False, indent=4)
            except Exception as e:
                print("An error occurred while creating the file: {}".format(e))
        return data

    def load_data(self):
        self.table_model.clear()
        
        self.set_initial_row_height()
                    
        black_icon = QIcon('_photo/black.png')
        white_icon = QIcon('_photo/white.png')

        if self.game_type == "team":
            file_path = '_data/siege_team_data.json'
        else:
            return

        data = self.read_data_from_file(file_path)
        
        formatted_data = []

        for team_name, group, time, month_day in data:
            minutes, seconds, milliseconds = map(int, time.split(":"))
            total_milliseconds = (minutes * 60 + seconds) * 1000 + milliseconds
            formatted_time = "{:02}:{:02}:{:02}".format(minutes, seconds, milliseconds)
            formatted_data.append((team_name, group, formatted_time, total_milliseconds, month_day))

        # Sort the data based on total milliseconds
        sorted_data = sorted(formatted_data, key=lambda item: item[3])

        header_row = [QStandardItem(label) for label in self.HEADER_LABELS]
        for item in header_row:
            item.setTextAlignment(Qt.AlignCenter)
        self.table_model.appendRow(header_row)

        for rank, (team_name, group, formatted_time, total_milliseconds, month_day) in enumerate(sorted_data, start=1):
            
            rank_item = QStandardItem(str(rank))
            rank_item.setTextAlignment(Qt.AlignCenter)  # Center align rank
            
            # Highlight top 3 teams with different colors
            if rank == 1:
                font_color = QColor(255, 69, 0)  # 형광 주황색
                bg_color = QBrush(font_color.lighter(130))  # Slightly lighter version for background
            elif rank == 2:
                font_color = QColor(50, 205, 50)  # 형광 연두색
                bg_color = QBrush(font_color.lighter(130))
            elif rank == 3:
                font_color = QColor(135, 206, 250)  # 형광 하늘색
                bg_color = QBrush(font_color.lighter(130))
            else:
                font_color = None
                bg_color = None

            if font_color:
                rank_item.setForeground(font_color)

                
            # Check the content of the group and set the icon accordingly
            if "black" in group.lower():
                group_item = QStandardItem(black_icon, "")
            elif "white" in group.lower():
                group_item = QStandardItem(white_icon, "")
            else:
                group_item = QStandardItem(group)
            
            group_item.setTextAlignment(Qt.AlignCenter)

            team_name_item = QStandardItem(team_name.strip())
            team_name_item.setTextAlignment(Qt.AlignCenter)  # Center align team name

            time_item = QStandardItem(formatted_time)
            time_item.setTextAlignment(Qt.AlignCenter)  # Center align time
            
            month_day_item = QStandardItem(month_day)
            month_day_item.setTextAlignment(Qt.AlignCenter)
            
            row = [rank_item, group_item, team_name_item, time_item, month_day_item]
                        # 배경색 적용
            if bg_color:
                for item in row:
                    item.setBackground(bg_color)
                    
            self.table_model.appendRow(row)

        self.adjustColumnSizes()
        self.set_initial_row_height()



class Team(QWidget, object):
    def __init__(self, parent=None):
        super(Team, self).__init__(parent)

        self.label = CLabel("display","공성전 팀전",self)
        # Create QTableView
        self.tableView = CTable(game_type="team", parent=self)  # Use CTable class with type="team"
        
        # Create a QVBoxLayout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableView)
        self.setLayout(self.layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data_periodically)
        self.timer.start(5000)  # 5000 milliseconds = 5 seconds
        
    def load_data_periodically(self):
        print("Reloading data...")
        self.tableView.load_data()

    def showEvent(self, event):
        super(Team, self).showEvent(event)
        self.tableView.load_data()

    def resizeEvent(self, event):
        # 폰트 크기를 화면의 폭에 따라 조절
        screen_width = self.width()
        font_size = int(screen_width * 0.02)  # 이 값을 조절하여 원하는 비율을 설정하세요.
        font = self.label.font()
        font.setPointSize(font_size)
        self.label.setFont(font)
        
        # Set the geometry here
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.label.adjustSize()
        self.labelX=int((self.parent().width())*0.015)
        self.labelY=int((self.parent().height())*0.15)
        self.label.move(self.labelX,self.labelY)
        
        # Adjust the margins of the layout to position it under the label
        label_height = self.label.height()
        top_margin = self.labelY + label_height + 10  # adjust the '10' if you want more or less spacing
        self.layout.setContentsMargins(0, top_margin, 0, 0)


class MainWindow(QMainWindow, object):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi('_ui/mainwindow.ui', self)  # load the ui file

        pygame.mixer.init()
        
        # Load the music
        pygame.mixer.music.load('_music/cham.wav')
        
        # Play the music
        pygame.mixer.music.play(-1)
        
        # set mainwindow background
        sshFile="_styles/mainwindow.qss"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
            
        self.showMaximized()
        self.showFullScreen()
        # Remove the top menu bar (menubar)
        self.setWindowFlags(Qt.FramelessWindowHint)
                
        self.team_widget = Team(self)

        # Create a QStackedWidget
        self.stacked_widget = QStackedWidget()
        
        self.stacked_widget.addWidget(self.team_widget)
                
        self.setCentralWidget(self.stacked_widget)

        # Create a QStateMachine and QStates
        self.state_machine = QStateMachine(self)
        
        self.team_state = QState()

        
        # Add states to the state machine
        self.state_machine.addState(self.team_state)

        self.team_state.entered.connect(lambda: self.stacked_widget.setCurrentWidget(self.team_widget))

        # Set the initial state
        self.state_machine.setInitialState(self.team_state)
        
        # Start the state machine
        self.state_machine.start()
        

        
if __name__ == "__main__":
    DEFAULT_IP = '192.168.0.48'
    DEFAULT_PORT = 1010
    
    # Check if command line arguments are provided
    if len(sys.argv) >= 2:
        # Parse the IP and port from the command line argument
        ip_port = sys.argv[1].split(":")
        if len(ip_port) != 2:
            print("Invalid format. Usage: python main.py <IP:PORT>")
            sys.exit(1)
        server_ip, server_port = ip_port[0], int(ip_port[1])
    else:
        server_ip, server_port = DEFAULT_IP, DEFAULT_PORT
    
    # Create instance of SocketServer using the provided IP and port
    server = SocketServer(server_ip=server_ip, server_port=server_port)

    # # Start the server threads
    server.start()
    app = QApplication([])
    mainWindow = MainWindow()  # Pass the server instance to MainWindow
    
    mainWindow.show()
    sys.exit(app.exec_())