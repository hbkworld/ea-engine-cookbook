import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets
import sys
import HelpFunctions.ea_engine as EA

class FigureHandler:
    def __init__(self, sampleinterval=0.1, timewindow=10., size=(4096,), unit='Pa'):
        # Data storage
        self.size = size
        self.x = np.linspace(0.0, timewindow, size[0])

        # PyQtGraph setup
        self.app = QtWidgets.QApplication(sys.argv)
        self.win = pg.GraphicsLayoutWidget(title="EA Engine")
        
        self.win.resize(800, 400)
        self.plotTime = self.win.addPlot()
        self.curveTime = self.plotTime.plot(self.x, np.zeros(size))
        self.win.setBackground('w')
        self.curveTime.setPen('b')

        self.plotTime.showGrid(x=True, y=True)
        self.plotTime.setLabel('bottom', 'Time', 's')
        self.plotTime.setLabel('left', 'Amplitude', unit)
        self.plotTime.setYRange(-30, 30)
        #self.plotFreq = [None] * (EA.engine.GetOutputChannels(True).Length + EA.engine.GetInputChannels(True).Length)
        self.plotFreq = []
        self.curveFreq = [None] * (EA.engine.GetOutputChannels(True).Length + EA.engine.GetInputChannels(True).Length)

        self.win.show()

        # QTimer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(int(sampleinterval*1000))

    def run(self):
        QtWidgets.QApplication.instance().exec_()
    
    def pause(self, source, args):
        if args.MessageType == "END":
            pg.QtCore.QMetaObject.invokeMethod(self.timer, "stop", pg.QtCore.Qt.QueuedConnection)

    def stop(self, source, args):
        if args.MessageType == "END":
            self.app.quit()