import sys
import pythoncom

pythoncom.CoInitialize()
import clr
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
import pyqtgraph as pg
from GUI import Ui_Form

np.seterr(divide='ignore')

installPath = "C:\\Program Files\\HBK\\EA Engine"

clr.AddReference("C:\\Program Files\\HBK\\EA Engine\\EA_Engine.exe")
clr.AddReference("C:\\Program Files\\HBK\\EA Engine\\Signal Processing Library.dll")

from EA_Engine import *
from SignalProcessing.Library import *

engine = Engine(installPath)

global unit
unit = 'dB'

global dbRef
global timestamp
global switchedDone1, switchedDone2
global step

global inputchannels


def calfeedback(source, args):
    win.listWidget_InputCalibration.addItem(args.MessageType + " - " + args.Message)
    win.listWidget_InputCalibration.scrollToBottom()
    win.listWidget_InputCalibration.setCurrentRow(win.listWidget_InputCalibration.count() - 1)
    app.processEvents()


def outputcalfeedback(source, args):
    win.listWidget_OutputCalibration.addItem(args.MessageType + " - " + args.Message)
    win.listWidget_OutputCalibration.scrollToBottom()
    win.listWidget_OutputCalibration.setCurrentRow(win.listWidget_OutputCalibration.count() - 1)
    app.processEvents()


def calresultsupdated(source, args):
    global p1
    global p2
    global curve1
    global curve2
    global text1
    global unit

    if args.TimeAxis is not None:
        if args.TimeBlock.GetLength(0) != 0:
            x1 = []
            y1 = []
            for i in range(0, args.TimeAxis.GetLength(0)):
                x1.append(args.TimeAxis[i])
                y1.append(args.TimeBlock[i])
            curve1.setData(x1, y1)

        if args.FrequencyAxis.GetLength(0) != 0:
            x2 = []
            y2 = []
            for i in range(0, args.FrequencyAxis.GetLength(0)):
                if (args.FrequencyAxis[i] >= 500) and (args.FrequencyAxis[i] <= 1500):
                    x2.append(args.FrequencyAxis[i])
                    y2.append(args.ResponseAutoSpectrum[i])

            curve2.setData(x2, y2)

    s = "Time Block - Current time elapsed: {0:.2f} s ".format(args.CurrentTimeElapsed)
    p1.setTitle(s)

    s = "Averaged Autospectrum -  Current average: {0} / {1}".format(args.CurrentAverageNumber, args.TotalAverages)
    p2.setTitle(s)

    app.processEvents()


def outputcalresultsupdated(source, args):
    global p3
    global p4
    global curve3
    global curve4
    global text2
    global unit

    if args.TimeAxis is not None:
        if args.TimeBlock.GetLength(0) != 0:
            x1 = []
            y1 = []
            for i in range(0, args.TimeAxis.GetLength(0)):
                x1.append(args.TimeAxis[i])
                y1.append(args.TimeBlock[i])
            curve3.setData(x1, y1)

        if args.FrequencyAxis.GetLength(0) != 0:
            x2 = []
            y2 = []
            for i in range(0, args.FrequencyAxis.GetLength(0)):
                if (args.FrequencyAxis[i] >= 500) and (args.FrequencyAxis[i] <= 1500):
                    x2.append(args.FrequencyAxis[i])
                    y2.append(args.ResponseAutoSpectrum[i])

            curve4.setData(x2, y2)

    s = "Time Block - Current time elapsed: {0:.2f} s ".format(args.CurrentTimeElapsed)
    p3.setTitle(s)

    s = "Averaged Autospectrum -  Current average: {0} / {1}".format(args.CurrentAverageNumber, args.TotalAverages)
    p4.setTitle(s)

    app.processEvents()


def calresultsavailable(source, args):
    global p2
    global curve2
    global unit

    if args.AutoSpectrum.GetLength(0) != 0:
        x = []
        y = []
        for i in range(0, args.FrequencyAxis.GetLength(0)):
            if (args.FrequencyAxis[i] >= 500) and (args.FrequencyAxis[i] <= 1500):
                x.append(args.FrequencyAxis[i])
                if unit == "dB":
                    y.append(20 * np.log10(args.AutoSpectrum[i, 0] / 2e-5))
                else:
                    y.append(args.AutoSpectrum[i, 0])

        curve2.setData(x, y)

        app.processEvents()


def outputcalresultsavailable(source, args):
    global p4
    global curve4
    global unit

    if args.AutoSpectrum.GetLength(0) != 0:
        x = []
        y = []
        for i in range(0, args.FrequencyAxis.GetLength(0)):
            if (args.FrequencyAxis[i] >= 500) and (args.FrequencyAxis[i] <= 1500):
                x.append(args.FrequencyAxis[i])
                if unit == "dB":
                    y.append(20 * np.log10(args.AutoSpectrum[i, 0] / 2e-5))
                else:
                    y.append(args.AutoSpectrum[i, 0])

        curve4.setData(x, y)

        app.processEvents()


def timedatarecorded(source, args):
    global ps
    global curves
    global timestamp

    global inputchannels

    if args.TimeBlocks is not None:
        data = args.TimeBlocks

        n = 0

        if args.TimeBlocks.GetLength(0) != 0:
            for j in range(0, args.TimeBlocks.GetLength(1)):
                # if inputchannels[j].IsActive == True:
                y = [None] * 4096
                for i in range(0, args.TimeBlocks.GetLength(0)):
                    y[i] = data[i, j]
                curves[n].setData(timestamp, y)
                n = n + 1
        app.processEvents()


def eqfeedback(source, args):
    win.listWidget_OutputEqualization.addItem(args.MessageType + " - " + args.Message)
    win.listWidget_OutputEqualization.scrollToBottom()
    win.listWidget_OutputEqualization.setCurrentRow(win.listWidget_OutputEqualization.count() - 1)
    app.processEvents()


def randomfeedback(source, args):
    win.listWidget_RandomNoiseTest.addItem(args.MessageType + " - " + args.Message)
    win.listWidget_RandomNoiseTest.scrollToBottom()
    win.listWidget_RandomNoiseTest.setCurrentRow(win.listWidget_RandomNoiseTest.count() - 1)
    app.processEvents()


def eqtimeupdated(source, args):
    if args.CurrentTime < args.Duration:
        win.label_Info_Output_Equalization.setText("{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime))
        print("\r{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime), end="")
    else:
        print("")

    app.processEvents()


def randomtimeupdated(source, args):
    if win.comboBox_MeasType_RandomNoiseTest.currentText() == "CPB":
        win.label_Info_RandomNoiseTest.setText("{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime))
        print("\r{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime), end="")
    else:
        if args.CurrentTime < args.Duration:
            win.label_Info_RandomNoiseTest.setText("{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime))
            print("\r{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime), end="")
        else:
            print("")
    app.processEvents()


def eqaverageupdated(source, args):
    if args.CurrentAverage < args.TotalAverages:
        win.label_Info_Output_Equalization.setText(
            "Average: " + str(args.CurrentAverage) + " / " + str(args.TotalAverages))
        print("\rAverage: ", args.CurrentAverage, " / ", args.TotalAverages, end="")
    else:
        win.label_Info_Output_Equalization.setText(
            "Average: " + str(args.TotalAverages) + " / " + str(args.TotalAverages))
        print("\rAverage: ", args.TotalAverages, " / ", args.TotalAverages, end="")
        print("")
    app.processEvents()


def randomaverageupdated(source, args):
    if args.CurrentAverage < args.TotalAverages:
        win.label_Info_RandomNoiseTest.setText("Average: " + str(args.CurrentAverage) + " / " + str(args.TotalAverages))
        print("\rAverage: ", args.CurrentAverage, " / ", args.TotalAverages, end="")
    else:
        win.label_Info_RandomNoiseTest.setText("Average: " + str(args.TotalAverages) + " / " + str(args.TotalAverages))
        print("\rAverage: ", args.TotalAverages, " / ", args.TotalAverages, end="")
        print("")
    app.processEvents()


def fftprocessingResultsUpdated(source, args):
    global ps
    global curves
    global switchedDone1

    if switchedDone1 == False:
        outputchannels = engine.GetOutputChannels(True)
        inputchannels = engine.GetInputChannels(True)

        win.graphicsView_RandomNoiseTest.clear()

        ps = [None] * (outputchannels.Length + inputchannels.Length)
        curves = [None] * (outputchannels.Length + inputchannels.Length)

        n = 0

        for outputchannel in outputchannels:
            ps[n] = win.graphicsView_RandomNoiseTest.addPlot(title="Averaged Autopower - " + outputchannel.Name)
            ps[n].showGrid(x=True, y=True)
            ps[n].setLabel("bottom", "Frequency", units="Hz")
            ps[n].setLabel("left", "Amplitude", units=outputchannel.SensitivityUnit.replace("/V", "") + " rms")
            curves[n] = ps[n].plot(pen="b")
            if (n + 1) % 2 == 0:
                win.graphicsView_RandomNoiseTest.nextRow()
            n = n + 1

        for inputchannel in inputchannels:
            ps[n] = win.graphicsView_RandomNoiseTest.addPlot(title="Averaged Autopower - " + inputchannel.Name)
            ps[n].showGrid(x=True, y=True)
            ps[n].setLabel("bottom", "Frequency", units="Hz")
            ps[n].setLabel("left", "Amplitude", units=inputchannel.SensitivityUnit.replace("mV/", "") + " rms")
            curves[n] = ps[n].plot(pen="b")
            if (n + 1) % 2 == 0:
                win.graphicsView_RandomNoiseTest.nextRow()
            n = n + 1

        switchedDone1 = True

    if args.AutoSpectrum is not None:
        freq = args.FrequencyAxis
        data = args.AutoSpectrum

        if freq.Length != 0:
            for j in range(0, data.GetLength(1)):
                x = np.zeros(freq.Length)
                y = np.zeros(freq.Length)
                for i in range(0, freq.Length):
                    x[i] = freq[i]
                    y[i] = data[i, j]
                curves[j].setData(x, y)

        app.processEvents()


def eqtestresultsavailable(source, args):
    global ps
    global curves
    global switchedDone2
    global dbRef

    if switchedDone2 == False:
        outputchannels = engine.GetOutputChannels(True)
        inputchannels = engine.GetInputChannels(True)
        crosschannels = engine.CrossChannels

        win.graphicsView_OutputEqualization.clear()

        ps = [None] * 2
        curves = [None] * 2

        n = 0

        for outputchannel in outputchannels:
            ps[n] = win.graphicsView_OutputEqualization.addPlot(title="Averaged Autopower - " + outputchannel.Name)
            ps[n].showGrid(x=True, y=True)
            ps[n].setLabel("bottom", "Frequency", units="Hz")
            ps[n].setLabel("left", "Amplitude", units=outputchannel.SensitivityUnit.replace("/V", "") + " rms")
            curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
            if (n + 1) % 2 == 0:
                win.graphicsView_OutputEqualization.nextRow()
            n = n + 1

        for inputchannel in inputchannels:
            ps[n] = win.graphicsView_OutputEqualization.addPlot(title="Averaged Autopower - " + inputchannel.Name)
            ps[n].showGrid(x=True, y=True)
            ps[n].setLabel("bottom", "Frequency", units="Hz")
            ps[n].setLabel("left", "Amplitude", units=inputchannel.SensitivityUnit.replace("mV/", "") + " rms")
            curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
            if (n + 1) % 2 == 0:
                win.graphicsView_OutputEqualization.nextRow()
            n = n + 1

        switchedDone2 = True

    nn = 0

    if args.AutoSpectrum is not None:
        freq = args.FrequencyAxis
        data = args.AutoSpectrum

        if freq.Length != 0:
            for j in range(0, data.GetLength(1)):
                x = np.zeros(freq.Length)
                y = np.zeros(freq.Length)
                for i in range(0, freq.Length):
                    x[i] = freq[i]
                    y[i] = data[i, j]
                curves[nn].setData(x, y)
                nn = nn + 1

        app.processEvents()


def randomtestresultsavailable(source, args):
    global ps
    global curves
    global switchedDone2
    global dbRef

    if switchedDone2 == False:
        outputchannels = engine.GetOutputChannels(True)
        inputchannels = engine.GetInputChannels(True)
        crosschannels = engine.CrossChannels

        win.graphicsView_RandomNoiseTest.clear()

        if win.comboBox_MeasType_RandomNoiseTest.currentText() == "Spectra":
            ps = [None] * (outputchannels.Length + inputchannels.Length)
            curves = [None] * (outputchannels.Length + inputchannels.Length)
        if win.comboBox_MeasType_RandomNoiseTest.currentText() == "FRF":
            ps = [None] * (outputchannels.Length + inputchannels.Length + len(crosschannels))
            curves = [None] * (outputchannels.Length + inputchannels.Length + len(crosschannels))
        if win.comboBox_MeasType_RandomNoiseTest.currentText() == "CPB":
            ps = [None] * (outputchannels.Length + inputchannels.Length)
            curves = [None] * (outputchannels.Length + inputchannels.Length)

        n = 0

        if win.comboBox_MeasType_RandomNoiseTest.currentText() == "Spectra":
            for outputchannel in outputchannels:
                ps[n] = win.graphicsView_RandomNoiseTest.addPlot(title="Averaged Autopower - " + outputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude", units=outputchannel.SensitivityUnit.replace("/V", "") + " rms")
                curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                if (n + 1) % 2 == 0:
                    win.graphicsView_RandomNoiseTest.nextRow()
                n = n + 1

            for inputchannel in inputchannels:
                ps[n] = win.graphicsView_RandomNoiseTest.addPlot(title="Averaged Autopower - " + inputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude", units=inputchannel.SensitivityUnit.replace("mV/", "") + " rms")
                curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                if (n + 1) % 2 == 0:
                    win.graphicsView_RandomNoiseTest.nextRow()
                n = n + 1

        if win.comboBox_MeasType_RandomNoiseTest.currentText() == "FRF":
            for i in range(0, len(crosschannels)):
                ps[n] = win.graphicsView_RandomNoiseTest.addPlot(
                    title="Averaged FRF - " + crosschannels[i].RespChannelName + " / " + crosschannels[
                        i].RefChannelName)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude",
                               units=crosschannels[i].RespChannelUnit + "/" + crosschannels[i].RefChannelUnit)
                curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                if (n + 1) % 2 == 0:
                    win.graphicsView_RandomNoiseTest.nextRow()
                n = n + 1

                # ps[n] = win.graphicsView_RandomNoiseTest.addPlot(title="Averaged FRF - " + crosschannels[i].RespChannelName + " / " + crosschannels[i].RefChannelName)
                # ps[n].showGrid(x=True, y=True)
                # ps[n].setLabel("bottom", "Frequency", units="Hz")
                # ps[n].setLabel("left", "Phase", units="°")
                # curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                # if (n + 1) % 2 == 0:
                #     win.graphicsView_RandomNoiseTest.nextRow()
                # n = n + 1

        if win.comboBox_MeasType_RandomNoiseTest.currentText() == "CPB":
            dbRef = np.ones(outputchannels.Length + inputchannels.Length)

            div = 2
            if win.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/1":
                div = 1
            if win.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/3":
                div = 2
            if win.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/6":
                div = 6
            if win.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/12":
                div = 12

            freq = args.FrequencyAxis
            x = []
            xval = np.zeros(freq.Length)
            y = np.zeros(freq.Length)
            for i in range(0, freq.Length):
                xval[i] = i
                if i % div == 0:
                    if str(freq[i]).endswith(".0"):
                        x.append(str(freq[i]).replace(".0", ""))
                    else:
                        x.append("{:.2f}".format(freq[i]))
                else:
                    x.append("")

            xdict = dict(enumerate(x))

            for outputchannel in outputchannels:
                stringaxis = pg.AxisItem(orientation="bottom")
                stringaxis.setTicks([xdict.items()])
                ps[n] = win.graphicsView_RandomNoiseTest.addPlot(axisItems={'bottom': stringaxis},
                                                                 title="Averaged Autopower - " + outputchannel.Name)
                ps[n].showGrid(x=False, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude", units="dB [ref = " + str(
                    outputchannel.dBRef) + " " + outputchannel.SensitivityUnit.replace("/V", "") + "]")
                curves[n] = pg.BarGraphItem(x=xval, height=y, width=1, brush="r")
                ps[n].addItem(curves[n])

                dbRef[n] = outputchannel.dBRef

                if (n + 1) % 2 == 0:
                    win.graphicsView_RandomNoiseTest.nextRow()
                n = n + 1

            for inputchannel in inputchannels:
                stringaxis = pg.AxisItem(orientation="bottom")
                stringaxis.setTicks([xdict.items()])
                ps[n] = win.graphicsView_RandomNoiseTest.addPlot(axisItems={'bottom': stringaxis},
                                                                 title="Averaged Autopower - " + inputchannel.Name)
                ps[n].showGrid(x=False, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude", units="dB [ref = " + str(
                    inputchannel.dBRef) + " " + inputchannel.SensitivityUnit.replace("mV/", "") + "]")
                curves[n] = pg.BarGraphItem(x=xval, height=y, width=1, brush="r")
                ps[n].addItem(curves[n])

                dbRef[n] = inputchannel.dBRef

                if (n + 1) % 2 == 0:
                    win.graphicsView_RandomNoiseTest.nextRow()
                n = n + 1

        switchedDone2 = True

    nn = 0

    if win.comboBox_MeasType_RandomNoiseTest.currentText() == "Spectra":
        if args.AutoSpectrum is not None:
            freq = args.FrequencyAxis
            data = args.AutoSpectrum

            if freq.Length != 0:
                for j in range(0, data.GetLength(1)):
                    x = np.zeros(freq.Length)
                    y = np.zeros(freq.Length)
                    for i in range(0, freq.Length):
                        x[i] = freq[i]
                        y[i] = data[i, j]
                    curves[nn].setData(x, y)
                    nn = nn + 1

            app.processEvents()

    if win.comboBox_MeasType_RandomNoiseTest.currentText() == "CPB":
        if args.AutoSpectrum is not None:
            freq = args.FrequencyAxis
            data = args.AutoSpectrum

            if freq.Length != 0:
                for j in range(0, data.GetLength(1)):
                    x = np.zeros(freq.Length)
                    y = np.zeros(freq.Length)
                    for i in range(0, freq.Length):
                        x[i] = freq[i]
                        y[i] = 10 * np.log10(data[i, j] / (dbRef[nn] * dbRef[nn]))
                    curves[nn].setOpts(height=y)
                    nn = nn + 1

            app.processEvents()

    if win.comboBox_MeasType_RandomNoiseTest.currentText() == "FRF":
        if args.FrfAmplitude is not None:
            freq = args.FrequencyAxis
            data = args.FrfAmplitude
            # datap = args.FrfPhase

        if freq.Length != 0:
            for j in range(0, data.GetLength(1)):
                x = np.zeros(freq.Length)
                y = np.zeros(freq.Length)
                # yp = np.zeros(freq.Length)
                for i in range(0, freq.Length):
                    x[i] = freq[i]
                    y[i] = data[i, j]
                    # yp[i] = datap[i, j]
                curves[nn].setData(x, y)
                nn = nn + 1
                # curves[nn].setData(x, yp)
                # nn = nn + 1

        app.processEvents()


def stepfeedback(source, args):
    win.listWidget_StepSineTest.addItem(args.MessageType + " - " + args.Message)
    win.listWidget_StepSineTest.scrollToBottom()
    win.listWidget_StepSineTest.setCurrentRow(win.listWidget_StepSineTest.count() - 1)
    app.processEvents()


def steptimeupdated(source, args):
    if args.CurrentTime < args.Duration:
        win.label_Info_StepSineTest.setText("{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime))
        print("\r{0}: {1:.2f}".format(args.CurrentMessage, args.CurrentTime), end="")
    else:
        print("")

    app.processEvents()


def stepfrequencyupdated(source, args):
    global step

    step = args.CurrentStep

    if args.CurrentStep < args.TotalSteps:
        win.label_Info_StepSineTest.setText(
            "Frequency (Hz): {0:.2f} - Step {1} / {2}".format(args.CurrentFrequency, args.CurrentStep, args.TotalSteps))
        print('\rFrequency (Hz): {0:.2f} - Step {1} / {2}'.format(args.CurrentFrequency, args.CurrentStep,
                                                                  args.TotalSteps), end='')
    else:
        win.label_Info_StepSineTest.setText(
            "Frequency (Hz): {0:.2f} - Step {1} / {2}".format(args.CurrentFrequency, args.TotalSteps, args.TotalSteps))
        print('\rFrequency (Hz): {0:.2f} - Step {1} / {2}'.format(args.CurrentFrequency, args.TotalSteps,
                                                                  args.TotalSteps), end='')
        print('')
    app.processEvents()


def stepProcessingResultsUpdated(source, args):
    global ps
    global curves
    global switchedDone1
    global dbRef
    global step

    if switchedDone1 == False:
        outputchannels = engine.GetOutputChannels(True)
        inputchannels = engine.GetInputChannels(True)

        win.graphicsView_StepSineTest.clear()

        ps = [None] * (outputchannels.Length + inputchannels.Length)
        curves = [None] * (outputchannels.Length + inputchannels.Length)

        n = 0

        for outputchannel in outputchannels:
            ps[n] = win.graphicsView_StepSineTest.addPlot(title="Harmonic Spectrum - " + outputchannel.Name)
            ps[n].showGrid(x=True, y=True)
            ps[n].setLabel("bottom", "Frequency", units="Hz")
            ps[n].setLabel("left", "Amplitude", units=outputchannel.SensitivityUnit.replace("/V", "") + " rms")
            curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
            if (n + 1) % 2 == 0:
                win.graphicsView_StepSineTest.nextRow()
            n = n + 1

        for inputchannel in inputchannels:
            ps[n] = win.graphicsView_StepSineTest.addPlot(title="Harmonic Spectrum - " + inputchannel.Name)
            ps[n].showGrid(x=True, y=True)
            ps[n].setLabel("bottom", "Frequency", units="Hz")
            ps[n].setLabel("left", "Amplitude", units=inputchannel.SensitivityUnit.replace("mV/", "") + " rms")
            curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
            if (n + 1) % 2 == 0:
                win.graphicsView_StepSineTest.nextRow()
            n = n + 1

        switchedDone1 = True

    nn = 0

    if args.SpectrumAmplitude is not None:
        freq = args.FrequencyAxis
        data = args.SpectrumAmplitude

        if freq.Length != 0:
            for j in range(0, data.GetLength(1)):
                x = np.zeros(step)
                y = np.zeros(step)
                for i in range(0, step):
                    x[i] = freq[i]
                    y[i] = data[i, j]
                curves[nn].setData(x, y)
                nn = nn + 1

        app.processEvents()


def steptestresultsavailable(source, args):
    global ps
    global curves
    global switchedDone2
    global dbRef

    if switchedDone2 == False:
        outputchannels = engine.GetOutputChannels(True)
        inputchannels = engine.GetInputChannels(True)
        crosschannels = engine.CrossChannels

        win.graphicsView_StepSineTest.clear()

        if win.comboBox_MeasType_StepSineTest.currentText() == "Spectra":
            ps = [None] * (outputchannels.Length + inputchannels.Length)
            curves = [None] * (outputchannels.Length + inputchannels.Length)
        if win.comboBox_MeasType_StepSineTest.currentText() == "FRF":
            ps = [None] * (outputchannels.Length + inputchannels.Length + len(crosschannels))
            curves = [None] * (outputchannels.Length + inputchannels.Length + len(crosschannels))

        n = 0

        if win.comboBox_MeasType_StepSineTest.currentText() == "Spectra":
            for outputchannel in outputchannels:
                ps[n] = win.graphicsView_StepSineTest.addPlot(title="Averaged Autopower - " + outputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude", units=outputchannel.SensitivityUnit.replace("/V", "") + " rms")
                curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                if (n + 1) % 2 == 0:
                    win.graphicsView_StepSineTest.nextRow()
                n = n + 1

            for inputchannel in inputchannels:
                ps[n] = win.graphicsView_StepSineTest.addPlot(title="Averaged Autopower - " + inputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude", units=inputchannel.SensitivityUnit.replace("mV/", "") + " rms")
                curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                if (n + 1) % 2 == 0:
                    win.graphicsView_StepSineTest.nextRow()
                n = n + 1

        if win.comboBox_MeasType_StepSineTest.currentText() == "FRF":
            for i in range(0, len(crosschannels)):
                ps[n] = win.graphicsView_StepSineTest.addPlot(
                    title="Averaged FRF - " + crosschannels[i].RespChannelName + " / " + crosschannels[
                        i].RefChannelName)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Frequency", units="Hz")
                ps[n].setLabel("left", "Amplitude",
                               units=crosschannels[i].RespChannelUnit + "/" + crosschannels[i].RefChannelUnit)
                curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                if (n + 1) % 2 == 0:
                    win.graphicsView_StepSineTest.nextRow()
                n = n + 1

                # ps[n] = win.graphicsView_StepSineTest.addPlot(title="Averaged FRF - " + crosschannels[i].RespChannelName + " / " + crosschannels[i].RefChannelName)
                # ps[n].showGrid(x=True, y=True)
                # ps[n].setLabel("bottom", "Frequency", units="Hz")
                # ps[n].setLabel("left", "Phase", units="°")
                # curves[n] = ps[n].plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))
                # if (n + 1) % 2 == 0:
                #     win.graphicsView_StepSineTest.nextRow()
                # n = n + 1

        switchedDone2 = True

    nn = 0

    if win.comboBox_MeasType_StepSineTest.currentText() == "Spectra":
        if args.AutoSpectrum is not None:
            freq = args.FrequencyAxis
            data = args.AutoSpectrum

            if freq.Length != 0:
                for j in range(0, data.GetLength(1)):
                    x = np.zeros(freq.Length)
                    y = np.zeros(freq.Length)
                    for i in range(0, freq.Length):
                        x[i] = freq[i]
                        y[i] = data[i, j]
                    curves[nn].setData(x, y)
                    nn = nn + 1

            app.processEvents()

    if win.comboBox_MeasType_StepSineTest.currentText() == "FRF":
        if args.FrfAmplitude is not None:
            freq = args.FrequencyAxis
            data = args.FrfAmplitude
            # datap = args.FrfPhase

        if freq.Length != 0:
            for j in range(0, data.GetLength(1)):
                x = np.zeros(freq.Length)
                y = np.zeros(freq.Length)
                # yp = np.zeros(freq.Length)
                for i in range(0, freq.Length):
                    x[i] = freq[i]
                    y[i] = data[i, j]
                    # yp[j] = datap[i, j]
                curves[nn].setData(x, y)
                nn = nn + 1
                # curves[nn].setData(x, yp)
                # nn = nn + 1

        app.processEvents()


class Window(QMainWindow, Ui_Form):
    global idx
    global p1
    global p2
    global p3
    global p4
    global curve1
    global curve2
    global curve3
    global curve4
    global unit
    global timestamp

    global ps
    global curves

    global switchedDone1, switchedDone2

    global inputchannels

    idx = -1

    def __init__(self, parent=None):
        global p1
        global p2
        global p3
        global p4
        global curve1
        global curve2
        global curve3
        global curve4

        super().__init__(parent)
        self.setupUi(self)

        self.tabWidget.currentChanged.connect(self.tabChanged)

        self.pushButton_DetectDevices.clicked.connect(self.detectDevices)
        self.listWidget_Devices.itemSelectionChanged.connect(self.selectedDeviceChanged)
        self.pushButton_UseSelectedDevice.clicked.connect(self.selectDevice)
        self.pushButton_Save.clicked.connect(self.saveChannels)

        self.pushButton_InputCalibration.clicked.connect(self.inputCalibration)

        self.pushButton_OutputCalibration.clicked.connect(self.outputCalibration)

        self.pushButton_OutputEqualization.clicked.connect(self.outputEqualization)
        self.pushButton_OutputEqualizationVerify.clicked.connect(self.outputEqualizationVerify)

        self.pushButton_Previous_RandomNoiseTest.clicked.connect(self.previousSettingsRandomNoiseTest)
        self.pushButton_Next_RandomNoiseTest.clicked.connect(self.nextSettingsRandomNoiseTest)
        self.pushButton_RandomNoiseTest.clicked.connect(self.randomNoiseTest)

        self.comboBo_SignalType.currentTextChanged.connect(self.randomNoiseSignalType)
        self.lineEdit_Level_RandomNoiseTest.textChanged.connect(self.randomNoiseLevel)
        self.checkBox_Filtered.clicked.connect(self.randomNoiseFiltered)
        self.lineEdit_Fmin_Output_RandomNoiseTest.textChanged.connect(self.randomNoiseFmin)
        self.lineEdit_Fmax_Output_RandomNoiseTest.textChanged.connect(self.randomNoiseFmax)

        self.comboBox_MeasType_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseMeasType)
        self.lineEdit_Duration_RandomNoiseTest.textChanged.connect(self.randomNoiseDuration)
        self.checkBox_Latencies_RandomNoiseTest.clicked.connect(self.randomNoiseLatencies)
        self.checkBox_EQ_RandomNoiseTest.clicked.connect(self.randomNoiseEQ)
        self.comboBox_ResultsFormat_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseResultFormat)
        self.lineEdit_Filename_RandomNoiseTest.textChanged.connect(self.randomNoiseFilename)

        self.comboBox_FreqLines_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseFreqLines)
        self.comboBox_FFTBlocksize_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseFFTBlocksize)
        self.comboBox_AveragingFFT_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseFFTAveraging)
        self.lineEdit_Overlap_RandomNoiseTest.textChanged.connect(self.randomNoiseOverlap)
        self.comboBox_RefWeighting_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseRefWeighting)
        self.comboBox_RespWeighting_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseRespWeighting)

        self.comboBox_Bandwidth_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseCPBBandwidth)
        self.lineEdit_Fmin_CPB_RandomNoiseTest.textChanged.connect(self.randomNoiseCPBFmin)
        self.lineEdit_Fmax_CPB_RandomNoiseTest.textChanged.connect(self.randomNoiseCPBFmax)
        self.comboBox_AveragingCPB_RandomNoiseTest.currentTextChanged.connect(self.randomNoiseCPBAveraging)
        self.lineEdit_Tau_RandomNoiseTest.textChanged.connect(self.randomNoiseCPBTau)
        self.checkBox_SkipFilter_RandomNoiseTest.clicked.connect(self.randomNoiseCPBSkip)

        self.pushButton_Previous_StepSineTest.clicked.connect(self.previousSettingsStepSineTest)
        self.pushButton_Next_StepSineTest.clicked.connect(self.nextSettingsStepSineTest)
        self.pushButton_StepSineTest.clicked.connect(self.stepSineTest)

        self.lineEdit_Level_StepSineTest.textChanged.connect(self.stepSineLevel)
        self.lineEdit_Fstart_Output_StepSineTest.textChanged.connect(self.stepSineFstart)
        self.lineEdit_Fend_Output_StepSineTest.textChanged.connect(self.stepSineFend)
        self.comboBox_Resolution_StepSineTest.currentTextChanged.connect(self.stepSineResolution)
        self.lineEdit_MinCycles_StepSineTest.textChanged.connect(self.stepSineMinCycles)
        self.lineEdit_MinDuration_StepSineTest.textChanged.connect(self.stepSineMinDuration)

        self.comboBox_MeasType_StepSineTest.currentTextChanged.connect(self.stepSineMeasType)
        self.checkBox_Latencies_StepSineTest.clicked.connect(self.stepSineLatencies)
        self.checkBox_EQ_StepSineTest.clicked.connect(self.stepSineEQ)
        self.comboBox_ResultsFormat_StepSineTest.currentTextChanged.connect(self.stepSineResultFormat)
        self.lineEdit_Filename_StepSineTest.textChanged.connect(self.stepSineFilename)

        self.checkBox_THD_StepSineTest.clicked.connect(self.stepSineTHD)
        self.lineEdit_THD_StepSineTest.textChanged.connect(self.stepSineHarmonicsTHD)
        self.checkBox_RubbBuzz_StepSineTest.clicked.connect(self.stepSineRubbBuzz)
        self.lineEdit_RubbBuzz_StepSineTest.textChanged.connect(self.stepSineHarmonicsRubbBuzz)

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self.graphicsView_InputCalibration.setBackground("w")
        self.graphicsView_OutputCalibration.setBackground("w")
        self.graphicsView_OutputEqualization.setBackground("w")
        self.graphicsView_RandomNoiseTest.setBackground("w")
        self.graphicsView_StepSineTest.setBackground("w")

        p1 = self.graphicsView_InputCalibration.addPlot(title="Time Block")
        p1.showGrid(x=True, y=True)
        p1.setLabel("bottom", "Time", units="s")
        p1.setLabel("left", "Real", units="Pa")
        curve1 = p1.plot(pen="b")

        self.graphicsView_InputCalibration.nextRow()

        p2 = self.graphicsView_InputCalibration.addPlot(title="Averaged Autospectrum")
        p2.showGrid(x=True, y=True)
        p2.setLabel("bottom", "Frequency", units="Hz")
        p2.setLabel("left", "Amplitude", units="Pa rms")
        curve2 = p2.plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))

        p3 = self.graphicsView_OutputCalibration.addPlot(title="Time Block")
        p3.showGrid(x=True, y=True)
        p3.setLabel("bottom", "Time", units="s")
        p3.setLabel("left", "Real", units="Pa")
        curve3 = p3.plot(pen="b")

        self.graphicsView_OutputCalibration.nextRow()

        p4 = self.graphicsView_OutputCalibration.addPlot(title="Averaged Autospectrum")
        p4.showGrid(x=True, y=True)
        p4.setLabel("bottom", "Frequency", units="Hz")
        p4.setLabel("left", "Amplitude", units="Pa rms")
        curve4 = p4.plot(pen="r", fillLevel=0, brush=(255, 0, 0, 80))

    def previousSettingsRandomNoiseTest(self):
        self.stackedWidget_RandomNoiseTest.setCurrentIndex(self.stackedWidget_RandomNoiseTest.currentIndex() - 1)

    def nextSettingsRandomNoiseTest(self):
        self.stackedWidget_RandomNoiseTest.setCurrentIndex(self.stackedWidget_RandomNoiseTest.currentIndex() + 1)

    def previousSettingsStepSineTest(self):
        self.stackedWidget_StepSineTest.setCurrentIndex(self.stackedWidget_StepSineTest.currentIndex() - 1)

    def nextSettingsStepSineTest(self):
        self.stackedWidget_StepSineTest.setCurrentIndex(self.stackedWidget_StepSineTest.currentIndex() + 1)

    def tabChanged(self):
        global ps
        global curves

        if self.tabWidget.currentIndex() == 1:
            calibrationsettings = engine.GetInputCalibrationSettings()
            self.lineEdit_RefFrequency.setText(str(calibrationsettings.ReferenceFrequency))
            self.lineEdit_RefLevel.setText(str(calibrationsettings.ReferenceLevel))
            self.comboBox_RefLevelUnit.setCurrentText(calibrationsettings.ReferenceUnit)
            self.lineEdit_Duration_InputCalibration.setText(str(calibrationsettings.Duration))
            if calibrationsettings.ResultFileFormatType == 0:
                self.comboBox_ResultsFormat_InputCalibration.setCurrentText("XML")
            if calibrationsettings.ResultFileFormatType == 1:
                self.comboBox_ResultsFormat_InputCalibration.setCurrentText("MATLAB")
            if calibrationsettings.ResultFileFormatType == 2:
                self.comboBox_ResultsFormat_InputCalibration.setCurrentText("CSV")
            if calibrationsettings.CalculateTHD == True:
                self.checkBox_HarmonicsTHD.setCheckState(QtCore.Qt.Checked)
            if calibrationsettings.CalculateTHD == False:
                self.checkBox_HarmonicsTHD.setCheckState(QtCore.Qt.Unchecked)
            self.lineEdit_HarmonicsTHD.setText(calibrationsettings.HarmonicsTHD)
            self.comboBox_FFTBlocksize.setCurrentText(str(calibrationsettings.AnalysisFFTSettings.BlockSize))

        if self.tabWidget.currentIndex() == 2:
            outputchannels = engine.GetOutputChannels(False)
            engine.SetOutputChannels(outputchannels)

            outputcalibrationsettings = engine.GetOutputCalibrationSettings()

            self.lineEdit_Frequency.setText(str(outputcalibrationsettings.Frequency))
            self.lineEdit_Level.setText(str(outputcalibrationsettings.Level))
            self.lineEdit_Duration_OutputCalibration.setText(str(outputcalibrationsettings.Duration))
            if outputcalibrationsettings.ResultFileFormatType == 0:
                self.comboBox_ResultsFormat_OutputCalibration.setCurrentText("XML")
            if outputcalibrationsettings.ResultFileFormatType == 1:
                self.comboBox_ResultsFormat_OutputCalibration.setCurrentText("MATLAB")
            if outputcalibrationsettings.ResultFileFormatType == 2:
                self.comboBox_ResultsFormat_OutputCalibration.setCurrentText("CSV")
            if outputcalibrationsettings.CalculateTHD == True:
                self.checkBox_HarmonicsTHD_2.setCheckState(QtCore.Qt.Checked)
            if outputcalibrationsettings.CalculateTHD == False:
                self.checkBox_HarmonicsTHD_2.setCheckState(QtCore.Qt.Unchecked)
            self.lineEdit_HarmonicsTHD_2.setText(outputcalibrationsettings.HarmonicsTHD)
            self.comboBox_FFTBlocksize_2.setCurrentText(str(outputcalibrationsettings.AnalysisFFTSettings.BlockSize))

        if self.tabWidget.currentIndex() == 3:
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].Level = 1
            outputchannels[0].Random.Duration = 10
            engine.SetOutputChannels(outputchannels)

            inputchannels = engine.GetInputChannels(False)
            outputchannels = engine.GetOutputChannels(False)
            outputequalizationsettings = engine.GetOutputEqualizationSettings()

            self.lineEdit_RefFrequency_2.setText(str(outputequalizationsettings.ReferenceFrequency))
            self.lineEdit_Fmin_Output_Equalization.setText(str(outputequalizationsettings.FrequencyStart))
            self.lineEdit_Fmax_Output_Equalization.setText(str(outputequalizationsettings.FrequencyEnd))
            self.lineEdit_Fmax_Output_Equalization.setText(str(outputequalizationsettings.FrequencyEnd))
            self.lineEdit_FilterLength_Output_Equalization.setText(str(outputequalizationsettings.FilterLength))
            if outputequalizationsettings.ResultFileFormatType == 0:
                self.comboBox_ResultsFormat_OutputEqualization.setCurrentText("XML")
            if outputequalizationsettings.ResultFileFormatType == 1:
                self.comboBox_ResultsFormat_OutputEqualization.setCurrentText("MATLAB")
            if outputequalizationsettings.ResultFileFormatType == 2:
                self.comboBox_ResultsFormat_OutputEqualization.setCurrentText("CSV")
            if outputequalizationsettings.MeasureAndRemoveExtraLatency == True:
                self.checkBox_Latencies_Equalization.setCheckState(QtCore.Qt.Checked)
            if outputequalizationsettings.MeasureAndRemoveExtraLatency == False:
                self.checkBox_Latencies_Equalization.setCheckState(QtCore.Qt.Unchecked)
            self.comboBox_FFTBlocksize_3.setCurrentText(str(outputequalizationsettings.AnalysisFFTSettings.BlockSize))

            self.graphicsView_OutputEqualization.clear()

            ps = [None] * 1
            curves = [None] * 1

            n = 0
            for inputchannel in inputchannels:
                if inputchannel.IsActive == True:
                    ps[n] = self.graphicsView_OutputEqualization.addPlot(title="Time Block - " + inputchannel.Name)
                    ps[n].showGrid(x=True, y=True)
                    ps[n].setLabel("bottom", "Time", units="s")
                    ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                    curves[n] = ps[n].plot(pen="b")
                    if (n + 1) % 2 == 0:
                        self.graphicsView_OutputEqualization.nextRow()
                    n = n + 1

        if self.tabWidget.currentIndex() == 4:
            inputchannels = engine.GetInputChannels(False)
            outputchannels = engine.GetOutputChannels(False)
            randomnoisetestsettings = engine.GetRandomNoiseTestSettings()

            self.comboBo_SignalType.setCurrentText("White")
            outputchannels[0].Random.Slope = 0
            engine.SetOutputChannels(outputchannels)

            self.lineEdit_Level_RandomNoiseTest.setText(str(outputchannels[0].Level))
            if outputchannels[0].Random.IsFiltered == True:
                self.checkBox_Filtered.setCheckState(QtCore.Qt.Checked)
            if outputchannels[0].Random.IsFiltered == False:
                self.checkBox_Filtered.setCheckState(QtCore.Qt.Unchecked)
            self.lineEdit_Fmin_Output_RandomNoiseTest.setText(str(outputchannels[0].Random.HiPassFrequency))
            self.lineEdit_Fmax_Output_RandomNoiseTest.setText(str(outputchannels[0].Random.LoPassFrequency))

            if randomnoisetestsettings.MeasurementModeType == MeasurementModeTypes.Spectra:
                self.comboBox_MeasType_RandomNoiseTest.setCurrentText("Spectra")
            if randomnoisetestsettings.MeasurementModeType == MeasurementModeTypes.FRF:
                self.comboBox_MeasType_RandomNoiseTest.setCurrentText("FRF")
            if randomnoisetestsettings.MeasurementModeType == MeasurementModeTypes.CPB:
                self.comboBox_MeasType_RandomNoiseTest.setCurrentText("CPB")
            self.lineEdit_Duration_RandomNoiseTest.setText(str(randomnoisetestsettings.Duration))
            if randomnoisetestsettings.MeasureAndRemoveExtraLatency == True:
                self.checkBox_Latencies_RandomNoiseTest.setCheckState(QtCore.Qt.Checked)
            if randomnoisetestsettings.MeasureAndRemoveExtraLatency == False:
                self.checkBox_Latencies_RandomNoiseTest.setCheckState(QtCore.Qt.Unchecked)
            if randomnoisetestsettings.ApplyEqualization == True:
                self.checkBox_EQ_RandomNoiseTest.setCheckState(QtCore.Qt.Checked)
            if randomnoisetestsettings.ApplyEqualization == False:
                self.checkBox_EQ_RandomNoiseTest.setCheckState(QtCore.Qt.Unchecked)
            if randomnoisetestsettings.ResultFileFormatType == ResultFileFormatTypes.CSV:
                self.comboBox_ResultsFormat_RandomNoiseTest.setCurrentText("CSV")
            if randomnoisetestsettings.ResultFileFormatType == ResultFileFormatTypes.XML:
                self.comboBox_ResultsFormat_RandomNoiseTest.setCurrentText("XML")
            if randomnoisetestsettings.ResultFileFormatType == ResultFileFormatTypes.MATLAB:
                self.comboBox_ResultsFormat_RandomNoiseTest.setCurrentText("MATLAB")
            self.lineEdit_Filename_RandomNoiseTest.setText(randomnoisetestsettings.Filename)

            self.comboBox_FreqLines_RandomNoiseTest.setCurrentText(
                str(randomnoisetestsettings.AnalysisFFTSettings.FrequencyLines))
            self.lineEdit_FreqResolution_RandomNoiseTest.setText(
                str(randomnoisetestsettings.AnalysisFFTSettings.FrequencyResolution))
            self.comboBox_FFTBlocksize_RandomNoiseTest.setCurrentText(
                str(randomnoisetestsettings.AnalysisFFTSettings.BlockSize))
            if randomnoisetestsettings.AnalysisFFTSettings.AveragingType == AveragingTypes.Linear:
                self.comboBox_AveragingFFT_RandomNoiseTest.setCurrentText("Linear")
            if randomnoisetestsettings.AnalysisFFTSettings.AveragingType == AveragingTypes.Exponential:
                self.comboBox_AveragingFFT_RandomNoiseTest.setCurrentText("Exponential")
            self.lineEdit_Overlap_RandomNoiseTest.setText(str(randomnoisetestsettings.AnalysisFFTSettings.Overlap))
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.Uniform:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("Uniform")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.Hanning:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("Hanning")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.KaiserBessel:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("KaiserBessel")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.Flattop:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("Flattop")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.Uniform:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("Uniform")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.Hanning:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("Hanning")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.KaiserBessel:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("KaiserBessel")
            if randomnoisetestsettings.AnalysisFFTSettings.ReferenceWeightingType == WeightingTypes.Flattop:
                self.comboBox_RefWeighting_RandomNoiseTest.setCurrentText("Flattop")

            if randomnoisetestsettings.AnalysisCPBSettings.BandwidthType == BandwidthTypes.One:
                self.comboBox_Bandwidth_RandomNoiseTest.setCurrentText("1/1")
            if randomnoisetestsettings.AnalysisCPBSettings.BandwidthType == BandwidthTypes.Third:
                self.comboBox_Bandwidth_RandomNoiseTest.setCurrentText("1/3")
            if randomnoisetestsettings.AnalysisCPBSettings.BandwidthType == BandwidthTypes.Sixth:
                self.comboBox_Bandwidth_RandomNoiseTest.setCurrentText("1/6")
            if randomnoisetestsettings.AnalysisCPBSettings.BandwidthType == BandwidthTypes.Twelfth:
                self.comboBox_Bandwidth_RandomNoiseTest.setCurrentText("1/12")
            self.lineEdit_Fmin_CPB_RandomNoiseTest.setText(
                str(randomnoisetestsettings.AnalysisCPBSettings.LowFrequency))
            self.lineEdit_Fmax_CPB_RandomNoiseTest.setText(
                str(randomnoisetestsettings.AnalysisCPBSettings.HighFrequency))
            if randomnoisetestsettings.AnalysisCPBSettings.AveragingType == AveragingTypes.Linear:
                self.comboBox_AveragingCPB_RandomNoiseTest.setCurrentText("Linear")
            if randomnoisetestsettings.AnalysisCPBSettings.AveragingType == AveragingTypes.Exponential:
                self.comboBox_AveragingCPB_RandomNoiseTest.setCurrentText("Exponential")
            self.lineEdit_Tau_RandomNoiseTest.setText(str(randomnoisetestsettings.AnalysisCPBSettings.Tau))
            if randomnoisetestsettings.AnalysisCPBSettings.SkipFiltersSettlingData == True:
                self.checkBox_SkipFilter_RandomNoiseTest.setCheckState(QtCore.Qt.Checked)
            if randomnoisetestsettings.AnalysisCPBSettings.SkipFiltersSettlingData == False:
                self.checkBox_SkipFilter_RandomNoiseTest.setCheckState(QtCore.Qt.Unchecked)

            self.graphicsView_RandomNoiseTest.clear()

            ps = [None] * 8
            curves = [None] * 8

            n = 0
            for inputchannel in inputchannels:
                if inputchannel.IsActive == True:
                    ps[n] = self.graphicsView_RandomNoiseTest.addPlot(title="Time Block - " + inputchannel.Name)
                    ps[n].showGrid(x=True, y=True)
                    ps[n].setLabel("bottom", "Time", units="s")
                    ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                    curves[n] = ps[n].plot(pen="b")
                    if (n + 1) % 2 == 0:
                        self.graphicsView_RandomNoiseTest.nextRow()
                    n = n + 1

        if self.tabWidget.currentIndex() == 5:
            inputchannels = engine.GetInputChannels(False)
            outputchannels = engine.GetOutputChannels(False)
            stepsinetestsettings = engine.GetStepSineTestSettings()

            engine.SetOutputChannels(outputchannels)

            self.lineEdit_Level_StepSineTest.setText(str(outputchannels[0].Level))
            self.lineEdit_Fstart_Output_StepSineTest.setText(str(outputchannels[0].StepSine.StartFrequency))
            self.lineEdit_Fend_Output_StepSineTest.setText(str(outputchannels[0].StepSine.EndFrequency))
            if outputchannels[0].StepSine.ResolutionType == StepSineResolutionTypes.R10:
                self.comboBox_Resolution_StepSineTest.setCurrentText("R10")
            if outputchannels[0].StepSine.ResolutionType == StepSineResolutionTypes.R20:
                self.comboBox_Resolution_StepSineTest.setCurrentText("R20")
            if outputchannels[0].StepSine.ResolutionType == StepSineResolutionTypes.R40:
                self.comboBox_Resolution_StepSineTest.setCurrentText("R40")
            if outputchannels[0].StepSine.ResolutionType == StepSineResolutionTypes.R80:
                self.comboBox_Resolution_StepSineTest.setCurrentText("R80")
            self.lineEdit_MinCycles_StepSineTest.setText(str(outputchannels[0].StepSine.MinCycles))
            self.lineEdit_MinDuration_StepSineTest.setText(str(outputchannels[0].StepSine.MinDuration))

            if stepsinetestsettings.MeasurementModeType == MeasurementModeTypes.Spectra:
                self.comboBox_MeasType_StepSineTest.setCurrentText("Spectra")
            if stepsinetestsettings.MeasurementModeType == MeasurementModeTypes.FRF:
                self.comboBox_MeasType_StepSineTest.setCurrentText("FRF")
            if stepsinetestsettings.MeasureAndRemoveExtraLatency == True:
                self.checkBox_Latencies_StepSineTest.setCheckState(QtCore.Qt.Checked)
            if stepsinetestsettings.MeasureAndRemoveExtraLatency == False:
                self.checkBox_Latencies_StepSineTest.setCheckState(QtCore.Qt.Unchecked)
            if stepsinetestsettings.ApplyEqualization == True:
                self.checkBox_EQ_StepSineTest.setCheckState(QtCore.Qt.Checked)
            if stepsinetestsettings.ApplyEqualization == False:
                self.checkBox_EQ_StepSineTest.setCheckState(QtCore.Qt.Unchecked)
            if stepsinetestsettings.ResultFileFormatType == ResultFileFormatTypes.CSV:
                self.comboBox_ResultsFormat_StepSineTest.setCurrentText("CSV")
            if stepsinetestsettings.ResultFileFormatType == ResultFileFormatTypes.XML:
                self.comboBox_ResultsFormat_StepSineTest.setCurrentText("XML")
            if stepsinetestsettings.ResultFileFormatType == ResultFileFormatTypes.MATLAB:
                self.comboBox_ResultsFormat_StepSineTest.setCurrentText("MATLAB")
            self.lineEdit_Filename_StepSineTest.setText(stepsinetestsettings.Filename)

            if stepsinetestsettings.DistortionAnalysisSettings.CalculateTHD == True:
                self.checkBox_THD_StepSineTest.setCheckState(QtCore.Qt.Checked)
            if stepsinetestsettings.DistortionAnalysisSettings.CalculateTHD == False:
                self.checkBox_THD_StepSineTest.setCheckState(QtCore.Qt.Unchecked)
            self.lineEdit_THD_StepSineTest.setText(stepsinetestsettings.DistortionAnalysisSettings.HarmonicsTHD)
            if stepsinetestsettings.DistortionAnalysisSettings.CalculateRubAndBuzz == True:
                self.checkBox_RubbBuzz_StepSineTest.setCheckState(QtCore.Qt.Checked)
            if stepsinetestsettings.DistortionAnalysisSettings.CalculateRubAndBuzz == False:
                self.checkBox_RubbBuzz_StepSineTest.setCheckState(QtCore.Qt.Unchecked)
            self.lineEdit_RubbBuzz_StepSineTest.setText(
                stepsinetestsettings.DistortionAnalysisSettings.HarmonicsRubAndBuzz)

            self.graphicsView_StepSineTest.clear()

            ps = [None] * 8
            curves = [None] * 8

            n = 0
            for inputchannel in inputchannels:
                if inputchannel.IsActive == True:
                    ps[n] = self.graphicsView_StepSineTest.addPlot(title="Time Block - " + inputchannel.Name)
                    ps[n].showGrid(x=True, y=True)
                    ps[n].setLabel("bottom", "Time", units="s")
                    ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                    curves[n] = ps[n].plot(pen="b")
                    if (n + 1) % 2 == 0:
                        self.graphicsView_StepSineTest.nextRow()
                    n = n + 1

    def detectDevices(self):
        self.listWidget_Devices.clear()
        devices = engine.GetASIODevices()
        for device in devices:
            s = "Index: " + str(device.Index) + " - " + device.Name + " (" + device.ASIODriverName + ")"
            self.listWidget_Devices.addItem(s)

    def selectedDeviceChanged(self):
        global idx
        idx = self.listWidget_Devices.currentRow()

    def selectDevice(self):
        global idx
        if idx != -1:
            if self.checkBox_Reset.isChecked():
                device = engine.SelectASIODevice(idx + 1, True)
            else:
                device = engine.SelectASIODevice(idx + 1, False)
            if engine.ErrorMessage != "":
                QMessageBox.about(self, "EA Engine Demonstrator", engine.ErrorMessage)
            else:
                inputchannels = engine.GetInputChannels(False)
                self.tableWidget_Inputs.clear()
                self.tableWidget_Inputs.setRowCount(inputchannels.Length)
                self.tableWidget_Inputs.setColumnCount(9)
                self.tableWidget_Inputs.setHorizontalHeaderLabels(("Active", "Name", "Ref. Name", "Sens.", "Sens. Unit",
                                                                   "Calib. Date", "db Ref", "VMax",
                                                                   "Latency (samples)"))  # set header text
                row = 0
                for inputchannel in inputchannels:
                    cellinfo = QTableWidgetItem()
                    cellinfo.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    if inputchannel.IsActive == True:
                        cellinfo.setCheckState(QtCore.Qt.Checked)
                    else:
                        cellinfo.setCheckState(QtCore.Qt.Unchecked)
                    self.tableWidget_Inputs.setItem(row, 0, cellinfo)
                    cellinfo = QTableWidgetItem(inputchannel.Name)
                    self.tableWidget_Inputs.setItem(row, 1, cellinfo)
                    cellinfo = QTableWidgetItem(inputchannel.ReferenceChannelName)
                    self.tableWidget_Inputs.setItem(row, 2, cellinfo)
                    cellinfo = QTableWidgetItem(str(inputchannel.Sensitivity))
                    self.tableWidget_Inputs.setItem(row, 3, cellinfo)
                    cellinfo = QTableWidgetItem(inputchannel.SensitivityUnit)
                    self.tableWidget_Inputs.setItem(row, 4, cellinfo)
                    cellinfo = QTableWidgetItem(str(inputchannel.CalibrationDate))
                    cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # make it not editable
                    self.tableWidget_Inputs.setItem(row, 5, cellinfo)
                    cellinfo = QTableWidgetItem(str(inputchannel.dBRef))
                    self.tableWidget_Inputs.setItem(row, 6, cellinfo)
                    cellinfo = QTableWidgetItem(str(inputchannel.VMax))
                    cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # make it not editable
                    self.tableWidget_Inputs.setItem(row, 7, cellinfo)
                    cellinfo = QTableWidgetItem(str(inputchannel.Latency))
                    self.tableWidget_Inputs.setItem(row, 8, cellinfo)
                    row += 1

                self.tableWidget_Inputs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                outputchannels = engine.GetOutputChannels(False)
                self.tableWidget_Outputs.clear()
                self.tableWidget_Outputs.setRowCount(outputchannels.Length)
                self.tableWidget_Outputs.setColumnCount(9)
                self.tableWidget_Outputs.setHorizontalHeaderLabels((
                    "Active", "Name", "Ref. Name", "Sens.", "Sens. Unit",
                    "Calib. Date", "db Ref", "VMax",
                    "EQ File"))  # set header text
                row = 0
                for outputchannel in outputchannels:
                    cellinfo = QTableWidgetItem()
                    cellinfo.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    if outputchannel.IsActive == True:
                        cellinfo.setCheckState(QtCore.Qt.Checked)
                    else:
                        cellinfo.setCheckState(QtCore.Qt.Unchecked)
                    self.tableWidget_Outputs.setItem(row, 0, cellinfo)
                    cellinfo = QTableWidgetItem(outputchannel.Name)
                    self.tableWidget_Outputs.setItem(row, 1, cellinfo)
                    cellinfo = QTableWidgetItem(outputchannel.ReferenceChannelName)
                    self.tableWidget_Outputs.setItem(row, 2, cellinfo)
                    cellinfo = QTableWidgetItem(str(outputchannel.Sensitivity))
                    self.tableWidget_Outputs.setItem(row, 3, cellinfo)
                    cellinfo = QTableWidgetItem(outputchannel.SensitivityUnit)
                    self.tableWidget_Outputs.setItem(row, 4, cellinfo)
                    cellinfo = QTableWidgetItem(str(outputchannel.CalibrationDate))
                    cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # make it not editable
                    self.tableWidget_Outputs.setItem(row, 5, cellinfo)
                    cellinfo = QTableWidgetItem(str(outputchannel.dBRef))
                    self.tableWidget_Outputs.setItem(row, 6, cellinfo)
                    cellinfo = QTableWidgetItem(str(outputchannel.VMax))
                    cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # make it not editable
                    self.tableWidget_Outputs.setItem(row, 7, cellinfo)
                    cellinfo = QTableWidgetItem(outputchannel.EQFile)
                    self.tableWidget_Outputs.setItem(row, 8, cellinfo)
                    row += 1

                self.tableWidget_Outputs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def saveChannels(self):
        for i in range(0, self.tableWidget_Inputs.rowCount()):
            if self.tableWidget_Inputs.item(i, 0).checkState() == 0:
                active = False
            else:
                active = True
            engine.SetInputChannel(int(i + 1), self.tableWidget_Inputs.item(i, 1).text(), active,
                                   self.tableWidget_Inputs.item(i, 2).text(), float(self.tableWidget_Inputs.item(i, 3).text()),
                                   self.tableWidget_Inputs.item(i, 4).text(), float(self.tableWidget_Inputs.item(i, 6).text()),
                                   int(self.tableWidget_Inputs.item(i, 8).text()))

        for i in range(0, self.tableWidget_Outputs.rowCount()):
            if self.tableWidget_Outputs.item(i, 0).checkState() == 0:
                active = False
            else:
                active = True
            engine.SetOutputChannel(int(i + 1), self.tableWidget_Outputs.item(i, 1).text(), active,
                                    self.tableWidget_Outputs.item(i, 2).text(),
                                    float(self.tableWidget_Outputs.item(i, 3).text()),
                                    self.tableWidget_Outputs.item(i, 4).text(),
                                    float(self.tableWidget_Outputs.item(i, 6).text()), 1.0)

    def inputCalibration(self):
        global unit
        global p2

        calibrationSettings = CalibrationSettings()
        calibrationSettings.ReferenceFrequency = float(self.lineEdit_RefFrequency.text())
        calibrationSettings.ReferenceLevel = float(self.lineEdit_RefLevel.text())
        calibrationSettings.ReferenceUnit = self.comboBox_RefLevelUnit.currentText()
        calibrationSettings.Duration = float(self.lineEdit_Duration_InputCalibration.text())
        if self.comboBox_ResultsFormat_InputCalibration.currentText() == "XML":
            calibrationSettings.ResultFileFormatType = ResultFileFormatTypes.XML
        if self.comboBox_ResultsFormat_InputCalibration.currentText() == "MATLAB":
            calibrationSettings.ResultFileFormatType = ResultFileFormatTypes.MATLAB
        if self.comboBox_ResultsFormat_InputCalibration.currentText() == "CSV":
            calibrationSettings.ResultFileFormatType = ResultFileFormatTypes.CSV
        if self.checkBox_HarmonicsTHD.checkState() == 0:
            calibrationSettings.CalculateTHD = False
        else:
            calibrationSettings.CalculateTHD = True
        calibrationSettings.HarmonicsTHD = self.lineEdit_HarmonicsTHD.text()
        calibrationSettings.AnalysisFFTSettings.BlockSize = int(self.comboBox_FFTBlocksize.currentText())

        engine.SetInputCalibrationSettings(calibrationSettings)

        unit = self.comboBox_RefLevelUnit.currentText()
        if unit == "dB":
            p2.setLabel("left", "Amplitude", units="dB")
        else:
            p2.setLabel("left", "Amplitude", units="Pa rms")

        self.listWidget_InputCalibration.clear()
        engine.Feedback += calfeedback
        engine.CalibrationResultsUpdated += calresultsupdated
        engine.TestResultsAvailable += calresultsavailable
        activeInputChannels = engine.GetInputChannels(True)
        if activeInputChannels.Length > 0:
            print("WARNING: More than one input channel active, only the first one will be calibrated.")
        engine.Execute("Calibrate_Input_Channel {}".format(activeInputChannels[0].Number))
        engine.Feedback -= calfeedback
        engine.CalibrationResultsUpdated -= calresultsupdated
        engine.TestResultsAvailable -= calresultsavailable

    def outputCalibration(self):
        global unit
        global p4

        outputcalibrationSettings = OutputCalibrationSettings()
        outputcalibrationSettings.Frequency = float(self.lineEdit_Frequency.text())
        outputcalibrationSettings.Level = float(self.lineEdit_Level.text())
        outputcalibrationSettings.Duration = float(self.lineEdit_Duration_OutputCalibration.text())
        if self.comboBox_ResultsFormat_OutputCalibration.currentText() == "XML":
            outputcalibrationSettings.ResultFileFormatType = ResultFileFormatTypes.XML
        if self.comboBox_ResultsFormat_OutputCalibration.currentText() == "MATLAB":
            outputcalibrationSettings.ResultFileFormatType = ResultFileFormatTypes.MATLAB
        if self.comboBox_ResultsFormat_OutputCalibration.currentText() == "CSV":
            outputcalibrationSettings.ResultFileFormatType = ResultFileFormatTypes.CSV
        if self.checkBox_HarmonicsTHD_2.checkState() == 0:
            outputcalibrationSettings.CalculateTHD = False
        else:
            outputcalibrationSettings.CalculateTHD = True
        outputcalibrationSettings.HarmonicsTHD = self.lineEdit_HarmonicsTHD_2.text()
        outputcalibrationSettings.AnalysisFFTSettings.BlockSize = int(self.comboBox_FFTBlocksize_2.currentText())

        engine.SetOutputCalibrationSettings(outputcalibrationSettings)

        unit = "V"
        if unit == "dB":
            p2.setLabel("left", "Amplitude", units="dB")
        else:
            p2.setLabel("left", "Amplitude", units="V rms")

        self.listWidget_OutputCalibration.clear()
        engine.Feedback += outputcalfeedback
        engine.CalibrationResultsUpdated += outputcalresultsupdated
        engine.TestResultsAvailable += outputcalresultsavailable
        activeInputChannels = engine.GetInputChannels(True)
        activeOutputChannels = engine.GetOutputChannels(True)      
        if activeInputChannels.Length > 0:
            print("WARNING: More than one input channel active, only the first one will be used in calibrated.")
        if activeOutputChannels.Length > 0:
            print("WARNING: More than one output channel active, only the first one will be calibrated.")
        engine.Execute("Calibrate_Output_Channel {} {}".format(activeInputChannels[0].Number, activeOutputChannels[0].Number))
        engine.Feedback -= outputcalfeedback
        engine.CalibrationResultsUpdated -= outputcalresultsupdated
        engine.TestResultsAvailable -= outputcalresultsavailable

    def outputEqualization(self):
        global timestamp
        global switchedDone1, switchedDone2
        global ps
        global curves

        global inputchannels

        timestamp = np.arange(0, 4096 / 96000, 1 / 96000)
        switchedDone1 = False
        switchedDone2 = False

        inputchannels = engine.GetInputChannels(False)
        outputchannel = engine.GetOutputChannel(1)

        self.graphicsView_OutputEqualization.clear()

        ps = [None] * 1
        curves = [None] * 1

        n = 0
        for inputchannel in inputchannels:
            if inputchannel.IsActive == True:
                ps[n] = self.graphicsView_OutputEqualization.addPlot(title="Time Block - " + inputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Time", units="s")
                ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                curves[n] = ps[n].plot(pen="b")
                if (n + 1) % 2 == 0:
                    self.graphicsView_OutputEqualization.nextRow()
                n = n + 1

        self.label_Info_Output_Equalization.setText("")
        self.listWidget_OutputEqualization.clear()
        engine.Feedback += eqfeedback
        engine.TimeUpdated += eqtimeupdated
        engine.TimeDataRecorded += timedatarecorded
        engine.AverageUpdated += eqaverageupdated
        engine.MultiSIMOFFTProcessingResultsUpdated += fftprocessingResultsUpdated
        engine.TestResultsAvailable += eqtestresultsavailable
        activeInputChannels = engine.GetInputChannels(True)
        activeOutputChannels = engine.GetOutputChannels(True)
        if activeInputChannels.Length > 0:
            print("WARNING: More than one input channel active, only the first one will be used.")
        if activeOutputChannels.Length > 0:
            print("WARNING: More than one output channel active, only the first one will be used.")
        engine.Execute("Equalize_Output_Channel {} {}".format(activeInputChannels[0].Number, activeOutputChannels[0].Number))
        engine.Feedback -= eqfeedback
        engine.TimeUpdated -= eqtimeupdated
        engine.TimeDataRecorded -= timedatarecorded
        engine.AverageUpdated -= eqaverageupdated
        engine.TestResultsAvailable -= eqtestresultsavailable
        engine.MultiSIMOFFTProcessingResultsUpdated -= fftprocessingResultsUpdated

    def outputEqualizationVerify(self):
        global timestamp
        global switchedDone1, switchedDone2
        global ps
        global curves

        global inputchannels

        timestamp = np.arange(0, 4096 / 96000, 1 / 96000)
        switchedDone1 = False
        switchedDone2 = False

        inputchannels = engine.GetInputChannels(False)
        outputchannel = engine.GetOutputChannel(1)

        self.graphicsView_OutputEqualization.clear()

        ps = [None] * 1
        curves = [None] * 1

        n = 0
        for inputchannel in inputchannels:
            if inputchannel.IsActive == True:
                ps[n] = self.graphicsView_OutputEqualization.addPlot(title="Time Block - " + inputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Time", units="s")
                ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                curves[n] = ps[n].plot(pen="b")
                if (n + 1) % 2 == 0:
                    self.graphicsView_OutputEqualization.nextRow()
                n = n + 1

        self.label_Info_Output_Equalization.setText("")
        self.listWidget_OutputEqualization.clear()
        engine.Feedback += eqfeedback
        engine.TimeUpdated += eqtimeupdated
        engine.TimeDataRecorded += timedatarecorded
        engine.AverageUpdated += eqaverageupdated
        engine.MultiSIMOFFTProcessingResultsUpdated += fftprocessingResultsUpdated
        engine.TestResultsAvailable += eqtestresultsavailable
        activeInputChannels = engine.GetInputChannels(True)
        activeOutputChannels = engine.GetOutputChannels(True)
        if activeInputChannels.Length > 0:
            print("WARNING: More than one input channel active, only the first one will be used.")
        if activeOutputChannels.Length > 0:
            print("WARNING: More than one output channel active, only the first one will be used.")
        engine.Execute("Equalize_Output_Channel {} {} v".format(activeInputChannels[0].Number, activeOutputChannels[0].Number))
        engine.Feedback -= eqfeedback
        engine.TimeUpdated -= eqtimeupdated
        engine.TimeDataRecorded -= timedatarecorded
        engine.AverageUpdated -= eqaverageupdated
        engine.TestResultsAvailable -= eqtestresultsavailable
        engine.MultiSIMOFFTProcessingResultsUpdated -= fftprocessingResultsUpdated

    def randomNoiseLevel(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].Level = float(self.lineEdit_Level_RandomNoiseTest.text())
        engine.SetOutputChannels(outputchannels)

    def randomNoiseFiltered(self):
        if self.checkBox_Filtered.isChecked():
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].Random.IsFiltered = True
            engine.SetOutputChannels(outputchannels)
        else:
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].Random.IsFiltered = False
            engine.SetOutputChannels(outputchannels)

    def randomNoiseFmin(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].Random.HiPassFrequency = float(self.lineEdit_Fmin_Output_RandomNoiseTest.text())
        engine.SetOutputChannels(outputchannels)

    def randomNoiseFmax(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].Random.LoPassFrequency = float(self.lineEdit_Fmax_Output_RandomNoiseTest.text())
        engine.SetOutputChannels(outputchannels)

    def randomNoiseSignalType(self):
        if self.comboBo_SignalType.currentText() == "White":
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].Random.Slope = 0
            engine.SetOutputChannels(outputchannels)
        if self.comboBo_SignalType.currentText() == "Pink":
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].Random.Slope = 6
            engine.SetOutputChannels(outputchannels)

    def randomNoiseMeasType(self):
        if self.comboBox_MeasType_RandomNoiseTest.currentText() == "Spectra":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.MeasurementModeType = MeasurementModeTypes.Spectra
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_MeasType_RandomNoiseTest.currentText() == "FRF":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.MeasurementModeType = MeasurementModeTypes.FRF
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_MeasType_RandomNoiseTest.currentText() == "CPB":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.MeasurementModeType = MeasurementModeTypes.CPB
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseDuration(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.Duration = float(self.lineEdit_Duration_RandomNoiseTest.text())
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseLatencies(self):
        if self.checkBox_Latencies_RandomNoiseTest.isChecked():
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.MeasureAndRemoveExtraLatency = True
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        else:
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.MeasureAndRemoveExtraLatency = False
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseEQ(self):
        if self.checkBox_EQ_RandomNoiseTest.isChecked():
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.ApplyEqualization = True
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        else:
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.ApplyEqualization = False
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseResultFormat(self):
        if self.comboBox_ResultsFormat_RandomNoiseTest.currentText() == "CSV":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.ResultFileFormatType = ResultFileFormatTypes.CSV
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_ResultsFormat_RandomNoiseTest.currentText() == "XML":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.ResultFileFormatType = ResultFileFormatTypes.XML
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_ResultsFormat_RandomNoiseTest.currentText() == "MATLAB":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.ResultFileFormatType = ResultFileFormatTypes.MATLAB
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseFilename(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.Filename = self.lineEdit_Filename_RandomNoiseTest.text()
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseFreqLines(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.AnalysisFFTSettings.FrequencyLines = int(self.comboBox_FreqLines_RandomNoiseTest.currentText())
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        self.lineEdit_FreqResolution_RandomNoiseTest.setText(
            str(randomNoiseTestSettings.AnalysisFFTSettings.FrequencyResolution))
        self.comboBox_FFTBlocksize_RandomNoiseTest.setCurrentText(
            str(randomNoiseTestSettings.AnalysisFFTSettings.BlockSize))

    def randomNoiseFFTBlocksize(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.AnalysisFFTSettings.BlockSize = int(self.comboBox_FFTBlocksize_RandomNoiseTest.currentText())
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        self.lineEdit_FreqResolution_RandomNoiseTest.setText(
            str(randomNoiseTestSettings.AnalysisFFTSettings.FrequencyResolution))
        self.comboBox_FreqLines_RandomNoiseTest.setCurrentText(
            str(randomNoiseTestSettings.AnalysisFFTSettings.FrequencyLines))

    def randomNoiseFFTAveraging(self):
        if self.comboBox_AveragingFFT_RandomNoiseTest.currentText() == "Linear":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.AveragingType = AveragingTypes.Linear
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_AveragingFFT_RandomNoiseTest.currentText() == "Exponential":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.AveragingType = AveragingTypes.Exponential
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseOverlap(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.AnalysisFFTSettings.Overlap = float(self.lineEdit_Overlap_RandomNoiseTest.text())
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseRefWeighting(self):
        if self.comboBox_RefWeighting_RandomNoiseTest.currentText() == "Uniform":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ReferenceWeightingType = WeightingTypes.Uniform
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_RefWeighting_RandomNoiseTest.currentText() == "Hanning":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ReferenceWeightingType = WeightingTypes.Hanning
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_RefWeighting_RandomNoiseTest.currentText() == "KaiserBessel":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ReferenceWeightingType = WeightingTypes.KaiserBessel
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_RefWeighting_RandomNoiseTest.currentText() == "Flattop":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ReferenceWeightingType = WeightingTypes.Flattop
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseRespWeighting(self):
        if self.comboBox_RespWeighting_RandomNoiseTest.currentText() == "Uniform":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ResponseWeightingType = WeightingTypes.Uniform
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_RespWeighting_RandomNoiseTest.currentText() == "Hanning":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ResponseWeightingType = WeightingTypes.Hanning
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_RespWeighting_RandomNoiseTest.currentText() == "KaiserBessel":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ResponseWeightingType = WeightingTypes.KaiserBessel
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_RespWeighting_RandomNoiseTest.currentText() == "Flattop":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisFFTSettings.ResponseWeightingType = WeightingTypes.Flattop
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseCPBBandwidth(self):
        if self.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/1":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.BandwidthType = BandwidthTypes.One
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/3":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.BandwidthType = BandwidthTypes.Third
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/6":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.BandwidthType = BandwidthTypes.Sixth
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_Bandwidth_RandomNoiseTest.currentText() == "1/12":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.BandwidthType = BandwidthTypes.Twelfth
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseCPBFmin(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.AnalysisCPBSettings.LowFrequency = float(self.lineEdit_Fmin_CPB_RandomNoiseTest.text())
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseCPBFmax(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.AnalysisCPBSettings.HighFrequency = float(self.lineEdit_Fmax_CPB_RandomNoiseTest.text())
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseCPBAveraging(self):
        if self.comboBox_AveragingCPB_RandomNoiseTest.currentText() == "Linear":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.AveragingType = AveragingTypes.Linear
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        if self.comboBox_AveragingCPB_RandomNoiseTest.currentText() == "Exponential":
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.AveragingType = AveragingTypes.Exponential
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseCPBTau(self):
        randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
        randomNoiseTestSettings.AnalysisCPBSettings.Tau = self.lineEdit_Tau_RandomNoiseTest.text()
        engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def randomNoiseCPBSkip(self):
        if self.checkBox_SkipFilter_RandomNoiseTest.isChecked():
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.SkipFiltersSettlingData = True
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)
        else:
            randomNoiseTestSettings = engine.GetRandomNoiseTestSettings()
            randomNoiseTestSettings.AnalysisCPBSettings.SkipFiltersSettlingData = False
            engine.SetRandomNoiseTestSettings(randomNoiseTestSettings)

    def stepSineLevel(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].Level = float(self.lineEdit_Level_StepSineTest.text())
        engine.SetOutputChannels(outputchannels)

    def stepSineFstart(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].StepSine.StartFrequency = float(self.lineEdit_Fstart_Output_StepSineTest.text())
        engine.SetOutputChannels(outputchannels)

    def stepSineFend(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].StepSine.EndFrequency = float(self.lineEdit_Fend_Output_StepSineTest.text())
        engine.SetOutputChannels(outputchannels)

    def stepSineResolution(self):
        if self.comboBox_Resolution_StepSineTest.currentText() == "R10":
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].StepSine.ResolutionType = StepSineResolutionTypes.R10
            engine.SetOutputChannels(outputchannels)
        if self.comboBox_Resolution_StepSineTest.currentText() == "R20":
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].StepSine.ResolutionType = StepSineResolutionTypes.R20
            engine.SetOutputChannels(outputchannels)
        if self.comboBox_Resolution_StepSineTest.currentText() == "R40":
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].StepSine.ResolutionType = StepSineResolutionTypes.R40
            engine.SetOutputChannels(outputchannels)
        if self.comboBox_Resolution_StepSineTest.currentText() == "R80":
            outputchannels = engine.GetOutputChannels(False)
            outputchannels[0].StepSine.ResolutionType = StepSineResolutionTypes.R80
            engine.SetOutputChannels(outputchannels)

    def stepSineMinCycles(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].StepSine.MinCycles = int(self.lineEdit_MinCycles_StepSineTest.text())
        engine.SetOutputChannels(outputchannels)

    def stepSineMinDuration(self):
        outputchannels = engine.GetOutputChannels(False)
        outputchannels[0].StepSine.MinDuration = float(self.lineEdit_MinDuration_StepSineTest.text())
        engine.SetOutputChannels(outputchannels)

    def stepSineMeasType(self):
        if self.comboBox_MeasType_StepSineTest.currentText() == "Spectra":
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.MeasurementModeType = MeasurementModeTypes.Spectra
            engine.SetStepSineTestSettings(stepSineTestSettings)
        if self.comboBox_MeasType_StepSineTest.currentText() == "FRF":
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.MeasurementModeType = MeasurementModeTypes.FRF
            engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineLatencies(self):
        if self.checkBox_Latencies_StepSineTest.isChecked():
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.MeasureAndRemoveExtraLatency = True
            engine.SetStepSineTestSettings(stepSineTestSettings)
        else:
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.MeasureAndRemoveExtraLatency = False
            engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineEQ(self):
        if self.checkBox_EQ_StepSineTest.isChecked():
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.ApplyEqualization = True
            engine.SetStepSineTestSettings(stepSineTestSettings)
        else:
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.ApplyEqualization = False
            engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineResultFormat(self):
        if self.comboBox_ResultsFormat_StepSineTest.currentText() == "CSV":
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.ResultFileFormatType = ResultFileFormatTypes.CSV
            engine.SetStepSineTestSettings(stepSineTestSettings)
        if self.comboBox_ResultsFormat_StepSineTest.currentText() == "XML":
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.ResultFileFormatType = ResultFileFormatTypes.XML
            engine.SetStepSineTestSettings(stepSineTestSettings)
        if self.comboBox_ResultsFormat_StepSineTest.currentText() == "MATLAB":
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.ResultFileFormatType = ResultFileFormatTypes.MATLAB
            engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineFilename(self):
        stepSineTestSettings = engine.GetStepSineTestSettings()
        stepSineTestSettings.Filename = self.lineEdit_Filename_StepSineTest.text()
        engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineTHD(self):
        if self.checkBox_THD_StepSineTest.isChecked():
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.DistortionAnalysisSettings.CalculateTHD = True
            engine.SetStepSineTestSettings(stepSineTestSettings)
        else:
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.DistortionAnalysisSettings.CalculateTHD = False
            engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineHarmonicsTHD(self):
        stepSineTestSettings = engine.GetStepSineTestSettings()
        stepSineTestSettings.DistortionAnalysisSettings.HarmonicsTHD = self.lineEdit_THD_StepSineTest.text()
        engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineRubbBuzz(self):
        if self.checkBox_RubbBuzz_StepSineTest.isChecked():
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.DistortionAnalysisSettings.CalculateRubAndBuzz = True
            engine.SetStepSineTestSettings(stepSineTestSettings)
        else:
            stepSineTestSettings = engine.GetStepSineTestSettings()
            stepSineTestSettings.DistortionAnalysisSettings.CalculateRubAndBuzz = False
            engine.SetStepSineTestSettings(stepSineTestSettings)

    def stepSineHarmonicsRubbBuzz(self):
        stepSineTestSettings = engine.GetStepSineTestSettings()
        stepSineTestSettings.DistortionAnalysisSettings.HarmonicsRubAndBuzz = self.lineEdit_RubbBuzz_StepSineTest.text()
        engine.SetStepSineTestSettings(stepSineTestSettings)

    def randomNoiseTest(self):
        global timestamp
        global switchedDone1, switchedDone2
        global ps
        global curves

        global inputchannels

        timestamp = np.arange(0, 4096 / 96000, 1 / 96000)
        switchedDone1 = False
        switchedDone2 = False

        inputchannels = engine.GetInputChannels(False)
        outputchannel = engine.GetOutputChannel(1)

        self.graphicsView_RandomNoiseTest.clear()

        ps = [None] * 8
        curves = [None] * 8

        n = 0
        for inputchannel in inputchannels:
            if inputchannel.IsActive == True:
                ps[n] = self.graphicsView_RandomNoiseTest.addPlot(title="Time Block - " + inputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Time", units="s")
                ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                curves[n] = ps[n].plot(pen="b")
                if (n + 1) % 2 == 0:
                    self.graphicsView_RandomNoiseTest.nextRow()
                n = n + 1

        self.label_Info_RandomNoiseTest.setText("")
        self.listWidget_RandomNoiseTest.clear()
        engine.Feedback += randomfeedback
        engine.TimeUpdated += randomtimeupdated
        engine.TimeDataRecorded += timedatarecorded
        engine.AverageUpdated += randomaverageupdated
        engine.MultiSIMOFFTProcessingResultsUpdated += fftprocessingResultsUpdated
        engine.TestResultsAvailable += randomtestresultsavailable
        engine.Execute("Random_Noise_Test")
        engine.Feedback -= randomfeedback
        engine.TimeUpdated -= randomtimeupdated
        engine.TimeDataRecorded -= timedatarecorded
        engine.AverageUpdated -= randomaverageupdated
        engine.TestResultsAvailable -= randomtestresultsavailable
        engine.MultiSIMOFFTProcessingResultsUpdated -= fftprocessingResultsUpdated

    def stepSineTest(self):
        global timestamp
        global switchedDone1, switchedDone2
        global ps
        global curves

        global inputchannels

        timestamp = np.arange(0, 4096 / 96000, 1 / 96000)
        switchedDone1 = False
        switchedDone2 = False

        inputchannels = engine.GetInputChannels(False)
        outputchannel = engine.GetOutputChannel(1)

        self.graphicsView_StepSineTest.clear()

        ps = [None] * 8
        curves = [None] * 8

        n = 0
        for inputchannel in inputchannels:
            if inputchannel.IsActive == True:
                ps[n] = self.graphicsView_StepSineTest.addPlot(title="Time Block - " + inputchannel.Name)
                ps[n].showGrid(x=True, y=True)
                ps[n].setLabel("bottom", "Time", units="s")
                ps[n].setLabel("left", "Real", units=inputchannel.SensitivityUnit.replace("mV/", ""))
                curves[n] = ps[n].plot(pen="b")
                if (n + 1) % 2 == 0:
                    self.graphicsView_StepSineTest.nextRow()
                n = n + 1

        self.label_Info_StepSineTest.setText("")
        self.listWidget_StepSineTest.clear()
        engine.Feedback += stepfeedback
        engine.TimeUpdated += steptimeupdated
        engine.TimeDataRecorded += timedatarecorded
        engine.FrequencyUpdated += stepfrequencyupdated
        engine.HarmonicEstimatorProcessingResultsUpdated += stepProcessingResultsUpdated
        engine.TestResultsAvailable += steptestresultsavailable
        engine.Execute("Step_Sine_Test")
        engine.Feedback -= stepfeedback
        engine.TimeUpdated -= steptimeupdated
        engine.TimeDataRecorded -= timedatarecorded
        engine.FrequencyUpdated -= stepfrequencyupdated
        engine.TestResultsAvailable -= steptestresultsavailable
        engine.HarmonicEstimatorProcessingResultsUpdated -= stepProcessingResultsUpdated


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
