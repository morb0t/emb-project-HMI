from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QGraphicsDropShadowEffect, QGridLayout, QComboBox, QLineEdit, QSizePolicy, QMessageBox, QScrollArea
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QElapsedTimer
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QBrush
import serial.tools.list_ports
import serial
import numpy as np
import re
import sqlite3

##############STATIC VARIABLES################
parity = {
    "Select parity": serial.PARITY_NONE,
    "None": serial.PARITY_NONE,
    "Even": serial.PARITY_EVEN,
    "Odd": serial.PARITY_ODD,
}
flow_control = {
    "Select flow control": "xonxoff=0",
    "None": "xonxoff=0",	
    "Xon/Xoff": "xonxoff=1",
    "RTS/CTS": "rtscts=1",
    "DSR/DTR": "dsrdtr=1",
}
################################################

class HistoryFrame(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("history_frame")
        self.setStyleSheet(''' 
            QFrame#history_frame {
                background-color: #ffffff;
                border-radius: 10px;
                margin: 30px;
                padding: 20px;
            }
            QFrame#recordFrame {
                background-color: #cbe2f0;
                border-radius: 10px;
                margin-top: 2px;
                margin-right: 10px;
                margin-left: 10px;
                padding: 5px;
                border: none;     
                
            }
            QFrame#recordFrame:hover {
                background-color: #a5c1d3;
            }

            QLabel#header {
                font-size: 20px;
                font-weight: bold;
                margin-right: 10px;
                margin-left: 10px;
                margin-bottom: 10px;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #ffffff;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbe2f0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a5c1d3;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        ''')

        self.layout = QVBoxLayout(self)
        self.header_layout = QHBoxLayout()
        self.header_layout.setObjectName("header_layout")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(0)

        self.fileName = QLabel("ID")
        self.fileName.setFixedWidth(300)
        self.fileName.setObjectName("header")
        self.header_layout.addWidget(self.fileName)

        self.date = QLabel("Lux")
        self.date.setFixedWidth(500)
        self.date.setObjectName("header")
        self.header_layout.addWidget(self.date)

        self.notes = QLabel("Date")
        self.notes.setObjectName("header")
        self.header_layout.addWidget(self.notes)

        self.layout.addLayout(self.header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)


        self.addRecord()

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(5)
        self.shadow.setColor(Qt.GlobalColor.gray)
        self.setGraphicsEffect(self.shadow)

    def addRecord(self):
        cursor = con.cursor()
        cursor.execute("SELECT * FROM luminosity")
        records = cursor.fetchall()
        for record in records:
            recordFrame = QFrame()
            recordFrame.setObjectName("recordFrame")
            recordFrame.setFixedHeight(50)
            recordFrame.setFixedWidth(970)

            recordLayout = QHBoxLayout(recordFrame)
            recordLayout.setContentsMargins(0, 0, 0, 0)
            recordLayout.setSpacing(0)

            id = QLabel(str(record[0]))
            id.setFixedWidth(300)
            recordLayout.addWidget(id)

            lux = QLabel(str(record[1]))
            lux.setFixedWidth(500)
            recordLayout.addWidget(lux)

            date = QLabel(str(record[2]))
            recordLayout.addWidget(date)

            self.scroll_layout.addWidget(recordFrame)



class SettingsFrame(QFrame):
    def __init__(self):
        super().__init__()

        self.setObjectName("settings_frame")
        self.setStyleSheet('''
            QFrame#settings_frame {
                background-color: #ffffff;
                border-radius: 10px;
                margin: 30px;
                padding-top: 0;
                padding-left: 20px;
                padding-right: 20px;
            }
            QLabel {
                font-size: 20px;
                font-weight: bold;
                margin-left: 10px;
                margin-top: 20px;
                margin-bottom: 20px;
                           
            }
            QComboBox, QLineEdit {
                margin-left: 10px;
                margin-right: 10px;
                margin-top: 5px;
                margin-bottom: 5px;
                padding-left: 5px;
                padding-top: 5px;
                padding-bottom: 5px;
                border: 1px solid #666666;
                border-radius: 5px;
                
            }
            QComboBox::down-arrow {
                image: url(img/down-arrow.png);
                margin-right: 10px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border: none;
                border-radius: 3px;
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid #666666;
                border-radius: 5px;
                background-color: #ffffff;
                selection-background-color: #0693e3;
            }
            QPushButton {
                margin-left: 10px;
                margin-right: 10px;
                margin-top: 5px;
                padding-top: 10px;
                padding-bottom: 10px;
                border: 1px solid #666666;
                border-radius: 5px;
                background-color: #ffffff;
                color: #000000;
                text-align: center;
                width: 100px;
            }
            QPushButton:hover {
                background-color: #0680c7;
                border: 1px solid #0680c7;
                color:  #ffffff;
            }
            QPushButton:pressed {
                background-color: #066ea0;
                border: 1px solid #066ea0;
                color:  #ffffff;
            }            
        ''')

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel("Serial port configuration")
        self.layout.addWidget(self.title, 0, 0, 1, 3)

        self.port = QComboBox()
        self.port.setObjectName("port")
        self.port.addItems(self.scan_ports())
        self.layout.addWidget(self.port, 1, 0, 1, 1)

        self.baudrate = QLineEdit()
        self.baudrate.setPlaceholderText("Baudrate")
        self.baudrate.setObjectName("baudrate")
        self.layout.addWidget(self.baudrate, 1, 1, 1, 1)

        self.parity = QComboBox()
        self.parity.setObjectName("parity")
        self.parity.addItems(parity.keys())
        self.layout.addWidget(self.parity, 1, 2, 1, 1)

        self.bits = QComboBox()
        self.bits.setObjectName("bits")
        self.bits.addItems(["Select bites", "5","6","7", "8", "9"])
        self.layout.addWidget(self.bits, 2, 0, 1, 1)

        self.stop_bits = QComboBox()
        self.stop_bits.setObjectName("stop_bits")
        self.stop_bits.addItems(["Select stop bits", "1", "1.5", "2"])
        self.layout.addWidget(self.stop_bits, 2, 1, 1, 1)

        self.flow_control = QComboBox()
        self.flow_control.setObjectName("flow_control")
        self.flow_control.addItems(flow_control.keys())
        self.layout.addWidget(self.flow_control, 2, 2, 1, 1)

        self.connect = QPushButton("Connect")
        self.connect.setObjectName("connect")
        self.layout.addWidget(self.connect, 3, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.connect.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.connect.clicked.connect(self.onConnectButtonClicked)

        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(0, 1)




        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(1)
        self.shadow.setYOffset(1)
        self.shadow.setColor(Qt.GlobalColor.gray)
        self.connect.setGraphicsEffect(self.shadow)

    def scan_ports(self):
        item = ["Select port"]
        if serial.tools.list_ports.comports():
            for port in serial.tools.list_ports.comports():
                item.append(port.device)
            
            return item
        else:
            item.append("No port available")
            return item
        
    def onConnectButtonClicked(self):
        port = self.port.currentText()
        baudrate = int(self.baudrate.text())
        part = parity[self.parity.currentText()]
        bits = int(self.bits.currentText())
        stop_bits = float(self.stop_bits.currentText())
        #flow_control = self.flow_control.currentText()

        try:
            global connection
            connection = serial.Serial(port, baudrate, parity=part, bytesize=bits, stopbits=stop_bits)
            message = QMessageBox()
            message.setWindowTitle("Connection")
            message.setText("Connection successful")
            message.setIcon(QMessageBox.Icon.Information)
            message.exec()
        except Exception as e:
            message = QMessageBox()
            message.setWindowTitle("Connection")
            message.setText("Connection failed\n"+str(e))
            message.setIcon(QMessageBox.Icon.Critical)
            message.exec()




class GraphFrame(QFrame):
    def __init__(self):
        super().__init__()

        # Set the background color for the graph frame
        self.setObjectName("graph_frame")
        self.setStyleSheet('''
            QFrame#graph_frame {
                background-color: #ffffff;
                border-radius: 10px;
                margin: 30px;
                padding: 20px;
            }
        ''')

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)


        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(5)
        self.shadow.setColor(Qt.GlobalColor.gray)
        self.setGraphicsEffect(self.shadow)

        self.chart = QChart()
        self.chart.setTitle("Light Sensor Data")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))
        self.chart.setBackgroundRoundness(0)


        self.series = QLineSeries()
        self.series.setName("Light Sensor Data")
        self.chart.addSeries(self.series)

        # Create the axes
        self.axisX = QValueAxis()
        self.axisX.setTitleText("Time")
        self.chart.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axisX)

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Light Intensity")
        self.chart.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setBackgroundBrush(QBrush(QColor("#ffffff")))
        self.layout.addWidget(self.chart_view)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

        self.curent_time = QElapsedTimer()
        self.curent_time.start()

    def update_data(self):
        if globals().get("connection") is None:
            return
        try:
            data = connection.readline().decode("utf-8").strip()
            findLuxValue = re.search(r'\d+', data)
            if findLuxValue:
                LuxVal = float(findLuxValue.group())
                elapsed_time = self.curent_time.elapsed()/1000
                print(elapsed_time, LuxVal)
                self.series.append(elapsed_time, LuxVal)
                
                self.axisX.setRange(0, elapsed_time)
                min_y = min([p.y() for p in self.series.points()])
                max_y = max([p.y() for p in self.series.points()])
                self.axisY.setRange(min_y, max_y)

                self.chart_view.update()

                try:
                    cursor = con.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS luminosity(id INTEGER PRIMARY KEY AUTOINCREMENT, lux REAL, date_time DATETIME)")
                    cursor.execute("INSERT INTO luminosity(lux, date_time) VALUES(?, datetime('now'))", (LuxVal,))
                
                    con.commit()
                except Exception as e:
                    message = QMessageBox()
                    message.setWindowTitle("Error")
                    message.setText("An error occured\n"+str(e))
                    message.setIcon(QMessageBox.Icon.Critical)
                    message.exec()

            else:
                print("No data")
        except Exception as e:
            self.timer.stop()
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("An error occured\n"+str(e))
            message.setIcon(QMessageBox.Icon.Critical)
            message.exec()




class SideBar(QFrame):
    onMeasureButtonClicked = pyqtSignal()
    onHistoryButtonClicked = pyqtSignal()
    onSettingsButtonClicked = pyqtSignal() 
    def __init__(self):
        super().__init__()

        self.logo_enib = QPixmap("IHM/img/logo.png")
        self.logo_enib = self.logo_enib.scaled(90, 44)
        self.measure = QIcon("IHM/img/speedometer.png")
        self.hist = QIcon("IHM/img/file.png")
        self.settings = QIcon("IHM/img/settings.png")

        self.setFixedWidth(100)
        
        self.setObjectName("sidebar")
        self.setStyleSheet('''
            QFrame#sidebar {
                background-color: #ffffff;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                padding-left: 5px;
                padding-right: 5px;
                /*padding-bottom: 400px;*/
                padding-top: 0;
                margin: 0;
            }
            QPushButton::menu-indicator {
                image: none;
            }
            QPushButton {
                border: none;
                text-align: center;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
                padding-bottom: 10px;
                
            }
            QPushButton:hover {
                background-color: #0693e3;
            }
            QPushButton:pressed {
                background-color: #0680c7;
            }
            QPushButton#measure_button {
                background-color: #0693e3;
            }
            QLabel {
                font-weight: bold;
                max-height: 44px;
                margin-top: 10px;    
                margin-bottom: 20px;
                
            }
        ''')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel(self)
        self.title.setPixmap(self.logo_enib)
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignTop)

        self.measure_button = QPushButton(self)
        self.measure_button.setObjectName("measure_button")
        self.measure_button.setIcon(self.measure)
        self.measure_button.setIconSize(self.measure.actualSize(QSize(28, 28)))
        self.measure_button.clicked.connect(self.onMeasureButtonClicked.emit)
        self.measure_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.measure_button)

        self.history_button = QPushButton(self)
        self.history_button.setObjectName("history_button")
        self.history_button.setIcon(self.hist)
        self.history_button.setIconSize(self.hist.actualSize(QSize(28, 28)))
        self.history_button.clicked.connect(self.onHistoryButtonClicked.emit)
        self.history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.history_button)

        self.settings_button = QPushButton(self)
        self.settings_button.setObjectName("settings_button")
        self.settings_button.setIcon(self.settings)
        self.settings_button.setIconSize(self.settings.actualSize(QSize(28, 28)))
        self.settings_button.clicked.connect(self.onSettingsButtonClicked.emit)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.settings_button)


        self.setLayout(layout)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(3)
        self.shadow.setYOffset(3)
        self.shadow.setColor(Qt.GlobalColor.gray)
        self.setGraphicsEffect(self.shadow)

        self.btnShadow = QGraphicsDropShadowEffect()
        self.btnShadow.setBlurRadius(15)
        self.btnShadow.setXOffset(1)
        self.btnShadow.setYOffset(1)
        self.btnShadow.setColor(Qt.GlobalColor.gray)
        self.measure_button.setGraphicsEffect(self.btnShadow)

        self.title_shadow = QGraphicsDropShadowEffect()
        self.title_shadow.setBlurRadius(15)
        self.title_shadow.setXOffset(1)
        self.title_shadow.setYOffset(1)
        self.title_shadow.setColor(Qt.GlobalColor.gray)
        self.title.setGraphicsEffect(self.title_shadow)

        

class LightSensorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Light Sensor Data Logger")
        self.setGeometry(100, 50, 1200, 800)
        self.setWindowIcon(QIcon("img/log-format.png"))

        self.side_nav = SideBar()
        self.graph_frame = GraphFrame()
        self.settings_frame = SettingsFrame()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.side_nav)
        # main_layout.addWidget(self.graph_frame)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_layout.addWidget(self.graph_frame)
        main_layout.addWidget(self.content_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.side_nav.onMeasureButtonClicked.connect(self.onMeasureButtonClicked)
        self.side_nav.onHistoryButtonClicked.connect(self.onHistoryButtonClicked)
        self.side_nav.onSettingsButtonClicked.connect(self.onSettingsButtonClicked)

        self.active_frame = self.graph_frame

        global con
        con = sqlite3.connect("IHM/DB/embDB.db")


    def onMeasureButtonClicked(self):
        self.side_nav.measure_button.setStyleSheet('''background-color: #0693e3;''')
        self.side_nav.history_button.setStyleSheet('''background-color: #ffffff;''')
        self.side_nav.settings_button.setStyleSheet('''background-color: #ffffff;''')

        self.side_nav.measure_button.setGraphicsEffect(self.side_nav.btnShadow)
        
        self.removeActiveFrame()
        self.active_frame = GraphFrame()
        self.content_layout.addWidget(self.active_frame)



    def onHistoryButtonClicked(self):
        self.side_nav.measure_button.setStyleSheet('''background-color: #ffffff;''')
        self.side_nav.history_button.setStyleSheet('''background-color: #0693e3;''')
        self.side_nav.settings_button.setStyleSheet('''background-color: #ffffff;''')

        self.side_nav.history_button.setGraphicsEffect(self.side_nav.btnShadow)

        self.removeActiveFrame()

        # self.history_frame = HistoryFrame()
        # self.history_frame.addRecord()

        # self.scroll_area = QScrollArea()
        # self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setWidget(self.history_frame)

        self.active_frame = HistoryFrame()
        self.content_layout.addWidget(self.active_frame)
        

    def onSettingsButtonClicked(self):
        self.side_nav.measure_button.setStyleSheet('''background-color: #ffffff;''')
        self.side_nav.history_button.setStyleSheet('''background-color: #ffffff;''')
        self.side_nav.settings_button.setStyleSheet('''background-color: #0693e3;''')

        self.side_nav.settings_button.setGraphicsEffect(self.side_nav.btnShadow)

        self.removeActiveFrame()
        self.active_frame = SettingsFrame()
        self.content_layout.addWidget(self.active_frame)


    def removeActiveFrame(self):
        if self.active_frame is not None:
            self.content_layout.removeWidget(self.active_frame)
            self.active_frame.deleteLater()
            self.active_frame = None



        


if __name__ == "__main__":
    app = QApplication([])
    window = LightSensorApp()
    window.show()
    app.exec()
