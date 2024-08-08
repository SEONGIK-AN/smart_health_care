import serial, csv, datetime, sys, os, random
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from numpy import sum, sqrt, mean

# Set the path of data file
path = '/home/ubuntu/dataFile'
fileName = path + datetime.datetime.now().strftime("/%Y_%B_%d_%H_%M_%S_01.csv")
fileName_2 = path + datetime.datetime.now().strftime("/%Y_%B_%d_%H_%M_%S_02.csv")

# Board setting
port = '/dev/ttyACM0'   # Set the port address
port_2 = '/dev/ttyACM1'

baud = 115200           # Baud rate

# Begin the serial communication
ser = serial.Serial(port,baud)
ser_2 = serial.Serial(port_2,baud)

data_rms_1 = []
data_rms_2 = []

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        
        self.axes = fig.add_subplot(211, xlim = (0, 50), ylim = (-500, 1500)) # Set the limit of axis 
        self.axes2 = fig.add_subplot(212, xlim = (0,50), ylim = (-500,1500)) # Set the limit of axis

        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
    def compute_initial_figure(self):
        pass

class AnimationWidget(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        self.canvas = MyMplCanvas(self, width=6, height=4, dpi=100)
        self.setWindowTitle('Smart Health Care Application')
        grid = QGridLayout()
        grid_2 = QGridLayout()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.start_button = QPushButton("start", self)
        self.stop_button = QPushButton("stop", self)
        self.EMG_button = QPushButton("EMG1", self)
        self.EMG_button2 = QPushButton("EMG2", self)
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        hbox.addWidget(self.canvas)
        
        grid.addWidget(self.start_button,0,0)
        grid.addWidget(self.stop_button,0,1)
        
        grid_2.addWidget(self.EMG_button,0,0)
        grid_2.addWidget(self.EMG_button2,0,1)
        
        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        vbox.addLayout(grid_2)
        self.setLayout(vbox)
        
        max_points = 50
        self.x = np.arange(max_points)
        self.y = np.ones(max_points, dtype=np.float)*np.nan

        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=1, c='blue', ms=1)
        self.line2, = self.canvas.axes2.plot(self.x, self.y, animated=True, lw=1, c='red', ms=1)
       

    def update_line(self, i):
        global data_rms_1
        data_rms_1 = data_rms_1
        ser_data = ser.readline()                 # Read serial data
        ser_data = ser_data.decode()[:-1]         # Decode the serial data without escape string (\r)
        with open(fileName , 'a') as f:
            f.write(ser_data)
        ser_data = float(ser_data[:-1])           # Remove escape string (\n) and transform data type   
        old_ser_data = self.line.get_ydata()
        new_ser_data = np.r_[old_ser_data[1:], ser_data]
        self.line.set_ydata(new_ser_data)
        if len(data_rms_1) < 11:
            data_rms_1.append(ser_data)
        elif len(data_rms_1) == 11:
            data_rms_1.pop(0)
            rms_1 = []
            for i in data_rms_1:
                rms_1.append(i**2)
            rms_1 = (np.sqrt(sum(rms_1)/10))
            if float(rms_1) >= 400:
                self.EMG_button.setEnabled(True)
            else:
                self.EMG_button.setDisabled(True)
            print(rms_1)

        return [self.line]
        
    def update_line2(self, i):
        global data_rms_2
        data_rms_2 = data_rms_2
        ser_data_2 = ser_2.readline()
        ser_data_2 = ser_data_2.decode()[:-1]
        with open(fileName_2, 'a') as f_2:
            f_2.write(ser_data_2)
        ser_data_2 = float(ser_data_2[:-1])
        old_ser_data_2 = self.line2.get_ydata()
        new_ser_data_2 = np.r_[old_ser_data_2[1:], ser_data_2]
        self.line2.set_ydata(new_ser_data_2)
        if len(data_rms_2) < 11:
            data_rms_2.append(ser_data_2)
        elif len(data_rms_2) == 11:
            data_rms_2.pop(0)
            rms_2 = []
            for i in data_rms_2:
                rms_2.append(i**2)
            rms_2 = (np.sqrt(sum(rms_2)/10))
            if float(rms_2) >= 400:
                self.EMG_button2.setEnabled(True)
            else:
                self.EMG_button2.setDisabled(True)
            print(rms_2)

        return [self.line2]


    def on_start(self):
        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line, blit=True, interval=50)
        self.ani2 = animation.FuncAnimation(self.canvas.figure, self.update_line2, blit=True, interval=50)
        
    def on_stop(self):
        self.ani._stop()
        self.ani2._stop()
        
if __name__ == '__main__':
     qApp = QApplication(sys.argv)
     aw = AnimationWidget()
     aw.show()
     sys.exit(qApp.exec_())
