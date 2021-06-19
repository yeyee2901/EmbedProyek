import socket
import time
import sys
import numpy as np

from sys import exit, argv
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout,QComboBox
from PyQt5.QtCore import QTimer
from figurewidget import *

import numpy as np
# AF INET AGAR SEPERT 192.168 (IPV4)
# AF6 IPV6 SEDANGKAN ESP SUPP IPV4
# Sockstream : Protocol tcp (data pasti terkirim dan benar);

datalength= 100

class WindowUtama(QMainWindow):
    def __init__(self):
        super().__init__()
        self.datategangan = [0]*datalength
        self.sampleindex = np.arange(0, datalength)
        self.dataarus=[0]*datalength
        self.datapower = [0]*datalength

        self.SelectedChannel = b'\x01'
        self.__changeChannelFlag = False
        
        self.initserver()
        # self.initSerial()
        self.initUi()  # Untuk membuat semua ui yan gada didalam
        self.showMaximized()  # Untuk full screen
        self.setTimer()  # Untuk update

    def initserver(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 6969

        # host name ip adreess laptop cek cmd
        # selalu cek karena ada kemungkinan berbeda beda
        self.hostname = "192.168.1.5"
        # hostname =  "192.168.0.104"
        # address pait itu harus tupple
        self.address_pair = (self.hostname, self.port)

        # buka server di address
        self.server.bind(self.address_pair)

        # server accept akan blocking process
        print(f"Server listening at: {self.address_pair}")
        self.server.listen()

        self.conn, self.client_addr = self.server.accept()
        print(f"Client: {self.client_addr}")

    def initUi(self):
        self.setWindowTitle("Proyek Embedded System")

        # config main widget
        self.MainWidget = QWidget()  # bikin widget utama
        self.MainWidgetLayout = QGridLayout()  # nentuin layout mode yaitu grid
        self.MainWidget.setLayout(self.MainWidgetLayout)  # untuk setnya
        
        # place the main widget in main window
        # jadi main widget nya di tengah
        self.setCentralWidget(self.MainWidget)

        # INIT DROP MENU ===========================================================
        self.dropMenu = QComboBox()
        self.dropMenu.addItems(["Channel1","Channel2"])
        self.dropMenu.activated.connect(self.dropMenuSelect)



        # INIT PLOTS -------------------------------------------------
        self.List_of_Plots = []  # unntuk membuat object grafik
        self.title_list = ["Data Tegangan(V)","Data Arus(mA)","Data Power(mW)"]
        for n in range(3):
            self.plot_n = FigureWidget(title=self.title_list[n], color=20*n)
            self.plot_n.Figure.showGrid(x=True,y=True,alpha=0.3)
            self.List_of_Plots.append(self.plot_n)
        
        self.List_of_Plots[1].Figure.setYRange(0,1000)
        self.List_of_Plots[2].Figure.setYRange(0,6000)

        
        # self.List_of_Plots[0].Figure.showGrid(x=True,y=True,alpha=0.3)
        # INIT CHANNEL INFO ------------------------------------------

        # ADD WIDGETS TO LAYOUT --------------------------------------
        # untuk menempelkan data grafik ke main widget
        self.MainWidgetLayout.addWidget(self.List_of_Plots[0], 0, 0,1,8)
        self.MainWidgetLayout.addWidget(self.List_of_Plots[1], 1, 0,1,8)
        self.MainWidgetLayout.addWidget(self.List_of_Plots[2], 2, 0,1,8)
        self.MainWidgetLayout.addWidget(self.dropMenu,3,0,1,1 )
        
        # self.MainWidgetLayout.addWidget(self.List_of_Plots[1], 0, 1)
        # self.MainWidgetLayout.addWidget(self.List_of_Plots[2], 1, 0)
        # self.MainWidgetLayout.addWidget(self.List_of_Plots[3], 1, 1)

    def setTimer(self):
        self.timer = QTimer()
        # ketika waktu habis dia ngapain
        self.timer.timeout.connect(self.updateAll)
        self.timer.start(0)  # start setelah berapa detik

    def updateAll(self):
        # recv() = blocking process
        self.alldata = self.conn.recv(1024).decode("utf-8")
        if not self.alldata:
            print("Client disconnected")
            self.conn.close()
            self.server.close()
            exit(1)
        
        # send channel data
        if self.__changeChannelFlag:
            self.SelectedChannel = self.SelectedChannel
            self.__changeChannelFlag = False
        else:
            self.SelectedChannel = b"\x00"

        self.conn.send(self.SelectedChannel)

        self.tegangan,self.arus,self.power =  self.alldata.split(',')
        self.tegangan = float(self.tegangan)
        self.arus = float(self.arus)
        self.power = float(self.power)

        
        # Update list tegangan
        self.datategangan.append(self.tegangan)
        self.datategangan.pop(0)
        
        # Update list arus
        self.dataarus.append(self.arus)
        self.dataarus.pop(0)
        
        # Update list arus
        self.datapower.append(self.power)
        self.datapower.pop(0)

        # for plot_n in self.List_of_Plots:
        self.List_of_Plots[0].PlotData(self.sampleindex,self.datategangan)
        self.List_of_Plots[1].PlotData(self.sampleindex,self.dataarus)
        self.List_of_Plots[2].PlotData(self.sampleindex,self.datapower)

    def dropMenuSelect(self):
        self.__changeChannelFlag = True
        self.SelectedChannel = self.dropMenu.currentText()

        if self.SelectedChannel == "Channel1":
            self.SelectedChannel = b"\x01"
        else:
            self.SelectedChannel = b"\x02"

        print(self.SelectedChannel)




if __name__ == '__main__':
    app = QApplication(argv)

    main = WindowUtama()

    exit(app.exec_())
