import HelpFunctions.ea_engine as EA
import numpy as np
import sys
from HelpFunctions.Handlers import Handlers
from HelpFunctions.buffer import buffer
from HelpFunctions.FigureHandler import FigureHandler
from HelpFunctions.sta_thread_wrapper import run_in_sta_thread
from HelpFunctions.InputRecording import InputRecording
import os
import librosa
from PyQt5 import QtWidgets


class figureHandler(FigureHandler):
    def update(self):

        self.curveTime.setData(self.x, Handlers.DataBuffer.getPart(self.size[0]))

        for i in range(0, len(Handlers.channelInfo)):
            if (Handlers.channelInfo[i][0] == ''):
                ChannelLength = i
                break
        if Handlers.curves[0] is not None and not self.plotFreq:
            self.win.removeItem(self.plotTime)
            self.win.resize(1200, 400)
            for i in range(0, ChannelLength):
                if Handlers.curves[i] is not None:
                    self.plotFreq.append(
                        self.win.addPlot(title=f"{Handlers.channelInfo[i][0]}: {Handlers.channelInfo[i][2]}"))
                    self.plotFreq[i].setXRange(20, 20e3)
                    self.curveFreq[i] = self.plotFreq[i].plot(Handlers.curves[i][0], Handlers.curves[i][1])
                    self.curveFreq[i].setPen('b')
                    self.plotFreq[i].setLogMode(x=True, y=False)
                    self.plotFreq[i].showGrid(x=True, y=True)
                    self.plotFreq[i].setLabel('bottom', 'Frequency', 'Hz')
                    self.plotFreq[i].setLabel('left', 'Gain', 'dB')

        if self.plotFreq:
            while Handlers.curves[0] is None:
                pass
            for i in range(0, ChannelLength):
                if self.curveFreq[i] is not None and Handlers.curves[i] is not None:
                    self.curveFreq[i].setData(Handlers.curves[i][0], Handlers.curves[i][1])

    def frequencyPlot(self):
        x = np.array(Handlers.DataBuffer.get())
        w = np.fft.fft(x)
        frequency = 95e3 * np.fft.fftfreq(len(w))
        amplitude = np.abs(w) / 100e3
        self.win.removeItem(self.plotTime)
        self.freq_plot = self.win.addPlot()
        #self.freq_curve = self.freq_plot.plot(frequency, 20*np.log10((abs(amplitude)+20e-5)/20e-6))
        self.freq_curve = self.freq_plot.plot(frequency, amplitude)
        self.freq_curve.setPen('b')
        self.freq_plot.setLogMode(x=True, y=False)
        self.freq_plot.showGrid(x=True, y=True)
        self.freq_plot.setLabel('bottom', 'Frequency', 'Hz')
        self.freq_plot.setLabel('left', 'Amplitude', 'Pa')
        self.win.show()
        QtWidgets.QApplication.instance().exec_()


class EA_Engine:

    def __init__(self):
        self.engine = EA.engine

    def resetEngine(self):
        self.engine.ResetSettings()

    def select3670Device(self):
        devices = self.engine.GetDetectedASIODevices()

        for ii, device in enumerate(devices):
            if "3670" in device.Name:
                self.engine.SelectASIODevice(ii + 1, False)
                print(f"Selected: {device.Name}")
                break

    def setInputChannel(self, number, name, isActive, referenceChannelName="None", sensitivity=None,
                        sensitivityUnit=None, dbRef=None):
        channel = self.engine.GetInputChannels(False)
        channel[number - 1].Name = name
        channel[number - 1].IsActive = isActive
        channel[number - 1].ReferenceChannelName = referenceChannelName
        if sensitivity is not None:
            channel[number - 1].Sensitivity = sensitivity
        if sensitivityUnit is not None:
            channel[number - 1].SensitivityUnit = sensitivityUnit
        if dbRef is not None:
            channel[number - 1].dBRef = dbRef
        self.engine.SetInputChannels(channel)

    def getActiveInputChannels(self):
        return self.engine.GetInputChannels(True)

    def setOutputChannel(self, number, name, isActive, referenceChannelName="None", sensitivity=None,
                         sensitivityUnit=None, dbRef=None, outputLevel=0.5):
        channel = self.engine.GetOutputChannels(False)
        channel[number - 1].Name = name
        channel[number - 1].IsActive = isActive
        channel[number - 1].ReferenceChannelName = referenceChannelName
        if sensitivity is not None:
            channel[number - 1].Sensitivity = sensitivity
        if sensitivityUnit is not None:
            channel[number - 1].SensitivityUnit = sensitivityUnit
        if dbRef is not None:
            channel[number - 1].dBRef = dbRef
        channel.VMax = outputLevel
        self.engine.SetOutputChannels(channel)

    def getActiveOutputChannels(self):
        return self.engine.GetOutputChannels(True)

    def setAllChannelsToFalse(self):
        inputChannels = self.engine.GetInputChannels(False)
        for i in range(len(inputChannels)):
            inputChannels[i].IsActive = False
        self.engine.SetInputChannels(inputChannels)
        outputChannels = self.engine.GetOutputChannels(False)
        for i in range(len(outputChannels)):
            outputChannels[i].IsActive = False
        self.engine.SetOutputChannels(outputChannels)

    def runInputCalibration(self, channelNumber, refernceFrequency=1000, referenceLevel=1, duration=10,
                            referenceUnit="Pa rms"):
        #checks if the channel is active
        activeinputChannels = [channel.Number for channel in self.getActiveInputChannels()]
        if channelNumber not in activeinputChannels:
            print(f"Channel {channelNumber} is not an active input channel")
            return

        calibrationsettings = self.engine.GetInputCalibrationSettings()
        calibrationsettings.ReferenceFrequency = refernceFrequency
        calibrationsettings.ReferenceLevel = referenceLevel
        calibrationsettings.Duration = duration
        calibrationsettings.ReferenceUnit = referenceUnit

        self.engine.SetInputCalibrationSettings(calibrationsettings)

        print(f"Calibration frequency {calibrationsettings.ReferenceFrequency} Hz")
        print(f"Refference level {calibrationsettings.ReferenceLevel}  {calibrationsettings.ReferenceUnit}")

        self.engine.Execute(f"Calibrate_Input_Channel {channelNumber}")

    def runOutputCalibration(self, inputChannel, outputChannel, frequency=1000, level=0.01, duration=10):
        #checks if the input channel is active
        activeinputChannels = [channel.Number for channel in self.getActiveInputChannels()]
        if inputChannel not in activeinputChannels:
            print(f"Channel {inputChannel} is not an active input channel")
            return

        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        calibrationSettings = self.engine.GetOutputCalibrationSettings()
        calibrationSettings.Frequency = frequency
        calibrationSettings.Level = level
        calibrationSettings.Duration = duration

        self.engine.SetOutputCalibrationSettings(calibrationSettings)

        print(f"Calibration frequency {frequency} Hz")
        print(f"Refference level {level}  EU rms")

        self.engine.Execute(f"Calibrate_Output_Channel {inputChannel} {outputChannel}")

    def runOutputEqualization(self, inputChannel, outputChannel, filterLength = 8193, frequencyStart = 100,
                              frequencyEnd = 10000, measureAndRemoveExtraLatency = True, referenceFrequency = -1,
                              resultFileFormat = EA.ResultFileFormatTypes.CSV, scaleType = EA.ScaleTypes.dB,
                              stimulusType = EA.GeneratorSignalTypes.Random, disablePlots = False):

        #checks if the input channel is active
        activeinputChannels = [channel.Number for channel in self.getActiveInputChannels()]
        if inputChannel not in activeinputChannels:
            print(f"Channel {inputChannel} is not an active input channel")
            return

        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        eqSettings = self.engine.GetOutputEqualizationSettings()
        eqSettings.FilterLength = filterLength
        eqSettings.FrequencyStart = frequencyStart
        eqSettings.FrequencyEnd = frequencyEnd
        eqSettings.MeasureAndRemoveExtraLatency = measureAndRemoveExtraLatency
        eqSettings.ReferenceFrequency = referenceFrequency
        eqSettings.ResultFileFormatType = resultFileFormat
        eqSettings.ScaleType = scaleType
        eqSettings.StimulusType = stimulusType
        self.engine.SetOutputEqualizationSettings(eqSettings)

        if not disablePlots:
            fs = int(96e3)
            DataBuffer = buffer(fs * 10)
            Handlers.initDataBuffer(DataBuffer)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))
            self.engine.Feedback += fh.pause
            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(Handlers, source, args)

        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, f"Equalize_Output_Channel {inputChannel} {outputChannel}")

        if not disablePlots:
            fh.run()

        return Handlers.testResults


    def runRandomTest(self, outputChannel, duration=10, lowerFrequency=80, upperFrequency=12000, slope=0,
                      filename="random_noise_test", measurementModeType=EA.MeasurementModeTypes.Spectra,
                      resultFileFormatType=EA.ResultFileFormatTypes.CSV, disablePlots=False):

        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        # Define settings for the output
        self.engine.SetOutputChannelRandomSettings(outputChannel, False, lowerFrequency, upperFrequency, slope,
                                                   duration)

        # Define settings for the test
        randomSettings = self.engine.GetRandomNoiseTestSettings()
        randomSettings.Duration = duration
        randomSettings.Filename = filename
        randomSettings.MeasurementModeType = measurementModeType
        randomSettings.ResultFileFormatType = resultFileFormatType
        #FFT settings
        randomSettings.AnalysisFFTSettings.AveragingTime = 0.5
        self.engine.SetRandomNoiseTestSettings(randomSettings)

        if not disablePlots:
            fs = int(96e3)  # sampling frequency
            DataBuffer = buffer(fs * duration)
            Handlers.initDataBuffer(DataBuffer)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))
            self.engine.Feedback += fh.pause
            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)

        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, 'Random_Noise_Test')

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def runStepSineTest(self, outputChannel, startFrequency=100, endFrequency=10e3,
                        resolutionType=EA.StepSineResolutionTypes.R80, minCycles=5, minDuration=0.1,
                        stepMode=EA.ScanningModeTypes.Linear, stepIncrement=1, settlingPeriods=5, transitionPoints=100,
                        disablePlots=False):
        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        # Define settings for the output
        self.engine.SetOutputChannelStepSineSettings(outputChannel,
                                                     startFrequency,
                                                     endFrequency,
                                                     resolutionType,
                                                     minCycles,
                                                     minDuration,
                                                     stepMode,
                                                     stepIncrement,
                                                     settlingPeriods,
                                                     transitionPoints)

        stepSineSettings = EA.engine.GetStepSineTestSettings()
        stepSineSettings.Filename = "step_sine_test"
        stepSineSettings.MeasureAndRemoveExtraLatency = True
        stepSineSettings.ApplyEqualization = False
        stepSineSettings.MeasurementModeType = EA.MeasurementModeTypes.Spectra
        stepSineSettings.ResultFileFormatType = EA.ResultFileFormatTypes.CSV
        EA.engine.SetStepSineTestSettings(stepSineSettings)

        if not disablePlots:
            fs = int(96e3)  # sampling frequency
            DataBuffer = buffer(fs * 10)
            Handlers.initDataBuffer(DataBuffer)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))
            self.engine.Feedback += fh.pause
            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.HarmonicEstimatorProcessingResultsUpdated += lambda source, args: Handlers.stepProcessingUpdated(
                Handlers, source, args)

        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        run_in_sta_thread(self.engine.Execute, 'Step_Sine_Test')

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def runSweptSineTest(self, outputChannel, duration=10, startFrequency=100, endFrequency=10e3,
                         scanningMode=EA.ScanningModeTypes.Linear, repetition=1, silenceDuration=0,
                         fademode=EA.FadeTypes.Cosine, fadeinDuration=0.01, fadeoutDuration=0.01, disablePlots=False):
        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        # Here were are setting the callback function for the TimeDataRecorded event

        # Define settings for the output
        EA.engine.SetOutputChannelSweptSineSettings(outputChannel,
                                                    startFrequency,
                                                    endFrequency,
                                                    scanningMode,
                                                    duration,
                                                    repetition,
                                                    silenceDuration,
                                                    fademode,
                                                    fadeinDuration,
                                                    fadeoutDuration)

        sweptSineSettings = EA.engine.GetSweptSineTestSettings()
        sweptSineSettings.Duration = duration * (repetition + 1)
        sweptSineSettings.Filename = "swept_sine_test"
        sweptSineSettings.MeasureAndRemoveExtraLatency = True
        sweptSineSettings.ApplyEqualization = False
        sweptSineSettings.MeasurementModeType = EA.MeasurementModeTypes.Spectra
        sweptSineSettings.ResultFileFormatType = EA.ResultFileFormatTypes.CSV
        sweptSineSettings.Recording = False
        sweptSineSettings.Processing = True
        EA.engine.SetSweptSineTestSettings(sweptSineSettings)

        if not disablePlots:
            fs = int(96e3)  # sampling frequency
            DataBuffer = buffer(fs * duration * (repetition + 1))
            Handlers.initDataBuffer(DataBuffer)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.Feedback += fh.pause
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, 'Swept_Sine_Test')

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def runFixedSineTest(self, outputChannel, duration=10, frequency=1000, disablePlots=False):
        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        # Define settings for the output
        self.engine.SetOutputChannelFixedSineSettings(outputChannel, frequency, duration)

        # Define settings for the test
        fixedSineSettings = EA.engine.GetFixedSineTestSettings()
        fixedSineSettings.Filename = "fixed_sine_test"
        fixedSineSettings.SettlingTime = True
        fixedSineSettings.MeasureAndRemoveExtraLatency = True
        fixedSineSettings.ResultFileFormatType = EA.ResultFileFormatTypes.CSV
        fixedSineSettings.ApplyEqualization = False
        fixedSineSettings.MeasurementModeType = EA.MeasurementModeTypes.Spectra
        fixedSineSettings.Recording = False
        EA.engine.SetFixedSineTestSettings(fixedSineSettings)

        if not disablePlots:
            fs = int(96e3)  # sampling frequency
            DataBuffer = buffer(fs * duration)
            Handlers.initDataBuffer(DataBuffer)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.Feedback += fh.stop
            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, 'Fixed_Sine_Test')

        if not disablePlots:
            fh.run()
            fh.frequencyPlot()

        return Handlers.testResults

    def runWaveformStreamingTest(self, outputChannel, wavPath, trackIndex=1, disablePlots=False):
        #checks if the output channel is active
        activeOutputChannels = [channel.Number for channel in self.getActiveOutputChannels()]
        if outputChannel not in activeOutputChannels:
            print(f"Channel {outputChannel} is not an active output channel")
            return

        # copy the file to the new directory
        #wavPath = f"{os.getcwd()}\{wavPath}"
        wavPath = os.path.join(os.getcwd(), wavPath)
        if not os.path.exists(wavPath):
            print(f"File {wavPath} not found. Please exeute the script within the python examples directory.")
            sys.exit()

        duration = int(librosa.get_duration(path=wavPath))

        #If the WAV have multiple tracks, this specify the track to be used. Default is 1.
        trackIndex = 1

        self.engine.SetOutputChannelWaveformStreamingSettings(outputChannel, wavPath, trackIndex)

        waveformStreamingSettings = EA.engine.GetWaveformStreamingTestSettings()
        waveformStreamingSettings.Filename = "waveform_streaming_test"
        waveformStreamingSettings.MeasureAndRemoveExtraLatency = True
        waveformStreamingSettings.ResultFileFormatType = EA.ResultFileFormatTypes.CSV
        waveformStreamingSettings.ApplyEqualization = False
        waveformStreamingSettings.MeasurementModeType = EA.MeasurementModeTypes.Spectra
        waveformStreamingSettings.Recording = False
        self.engine.SetWaveformStreamingTestSettings(waveformStreamingSettings)

        if not disablePlots:
            fs = int(96e3)  # sampling frequency
            DataBuffer = buffer(fs * duration)
            Handlers.initDataBuffer(DataBuffer)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.Feedback += fh.pause
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)
            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)

        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, 'Waveform_Streaming_Test')

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def selectWdmInputDevice(self, deviceName, isActive):
        print("WDM Input Devices:")
        for device in self.engine.GetDetectedWDMInputDevices():
            print(f"{device.Index}: {device.Name}")
            if device.Name == deviceName:
                print(f"Device {device.Index}: {deviceName} found")
                self.engine.Execute(f"Select_WDM_Input_Device {device.Index}")
                # may be an issue if more inputs gets added
                self.setInputChannel(9, f"{deviceName} Microphone", isActive)
                return
        print(f"Device {deviceName} not found")

    def selectWdmOutputDevice(self, deviceName, isActive):
        print("WDM Output Devices:")
        for device in self.engine.GetDetectedWDMOutputDevices():
            print(f"{device.Index}: {device.Name}")
            if device.Name == deviceName:
                print(f"Device {device.Index}: {deviceName} found")
                self.engine.Execute(f"Select_WDM_Output_Device {device.Index}")
                # may be an issue if more outputs gets added or if output is mono
                self.setOutputChannel(3, f"{deviceName} Left", isActive)
                self.setOutputChannel(4, f"{deviceName} Right", isActive)
                return
        print(f"Device {deviceName} not found")

    def deselectWdmInputDevice(self):
        self.engine.DeselectWDMInputDevice()

    def deselectWdmOutputDevice(self):
        self.engine.DeselectWDMOutputDevice()

    # 0.0 = 0% volume, 1.0 = 100% volume
    def adjustWdmInputVolume(self, volume):
        status = self.engine.AdjustWDMInputDeviceVolume(volume)
        if status == "OK":
            print(f"WDM Volume: {volume}")
        else:
            print(f"ERROR: {status}")

    # 0.0 = 0% volume, 1.0 = 100% volume
    def adjustWdmOutputVolume(self, volume):
        status = self.engine.AdjustWDMOutputDeviceVolume(volume)
        if status == "OK":
            print(f"WDM Volume: {volume}")
        else:
            print(f"ERROR: {status}")

    def CreateOpenLoopRandomNoiseStimulus(self, silence=1, duration=10,
                                          stimulusFilename="Open_Loop_Random_Noise_Test_Stimulus", level=0.5,
                                          lowerFrequency=20, upperFrequency=20000, slope=0, burstSineLevel=0.5,
                                          burstSineFrequency=1000, burstSineCycles=1000):
        settings = self.engine.GetOpenLoopRandomNoiseTestSettings()
        settings.ExternalDeviceStimulusRandomSettings.Duration = duration
        settings.ExternalDeviceStimulusRandomSettings.Slope = slope
        settings.ExternalDeviceStimulusRandomSettings.HiPassFrequency = lowerFrequency
        settings.ExternalDeviceStimulusRandomSettings.LoPassFrequency = upperFrequency
        settings.ExternalDeviceStimulusRandomSettings.IsFiltered = True
        settings.ExternalDeviceStimulusRandomSettings.Level = level
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        self.engine.SetOpenLoopRandomNoiseTestSettings(settings)
        self.engine.Execute("Open_Loop_Random_Noise_Test StimulusOnly")

    def RunOpenLoopRandomNoiseTest(self, triggerChannel, triggerLevel=0.1, duration=10,
                                   measurementModeType=EA.MeasurementModeTypes.Spectra,
                                   resultFileFormatType=EA.ResultFileFormatTypes.CSV,
                                   filename="open_loop_random_noise_test", disablePlots=False):
        settings = self.engine.GetOpenLoopRandomNoiseTestSettings()
        settings.Filename = filename
        settings.MeasurementModeType = measurementModeType
        settings.ResultFileFormatType = resultFileFormatType
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        self.engine.SetOpenLoopRandomNoiseTestSettings(settings)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * duration)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Random_Noise_Test TestOnly")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunCompleteOpenLoopRandomNoiseTest(self, triggerChannel, triggerLevel=0.1,
                                           stimulusFilename="Open_Loop_Random_Noise_Test_Stimulus", duration=10,
                                           level=0.5, measurementModeType=EA.MeasurementModeTypes.Spectra,
                                           resultFileFormatTypes=EA.ResultFileFormatTypes.CSV,
                                           filename="open_loop_random_noise_test", silence=1, lowerFrequency=20,
                                           upperFrequency=20000, slope=0, burstSineLevel=0.5, burstSineFrequency=1000,
                                           burstSineCycles=1000, disablePlots=False):
        settings = self.engine.GetOpenLoopRandomNoiseTestSettings()
        settings.MeasurementModeType = measurementModeType
        settings.ResultFileFormatType = resultFileFormatTypes
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        settings.ExternalDeviceStimulusRandomSettings.Duration = duration
        settings.ExternalDeviceStimulusRandomSettings.Slope = slope
        settings.ExternalDeviceStimulusRandomSettings.HiPassFrequency = lowerFrequency
        settings.ExternalDeviceStimulusRandomSettings.LoPassFrequency = upperFrequency
        settings.ExternalDeviceStimulusRandomSettings.IsFiltered = True
        settings.ExternalDeviceStimulusRandomSettings.Level = level
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        self.engine.SetOpenLoopRandomNoiseTestSettings(settings)

        self.engine.StimulusCreated += lambda source, args: Handlers.stimulusCreatedHandler(Handlers, source, args)
        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * duration)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)
            self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(
                Handlers,
                source,
                args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Random_Noise_Test Complete")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunPlaybackOpenLoopRandomNoiseTest(self, outputChannel, stimulusFilename="Open_Loop_Random_Noise_Test_Stimulus",
                                           duration=10, measurementModeType=EA.MeasurementModeTypes.Spectra,
                                           resultFileFormatTypes=EA.ResultFileFormatTypes.CSV,
                                           filename="open_loop_random_noise_test", silence=1, lowerFrequency=20,
                                           upperFrequency=20000, slope=0, burstSineLevel=0.01, burstSineFrequency=1000,
                                           burstSineCycles=1000, disablePlots=False):
        settings = self.engine.GetOpenLoopRandomNoiseTestSettings()
        settings.MeasurementModeType = measurementModeType
        settings.ResultFileFormatType = resultFileFormatTypes
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        self.engine.SetOpenLoopRandomNoiseTestSettings(settings)

        self.engine.SetOutputChannelRandomSettings(outputChannel, True, lowerFrequency, upperFrequency, slope, duration)

        self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(Handlers,
                                                                                                               source,
                                                                                                               args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)


        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Random_Noise_Test Playback")

        executionThread.join()
        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * duration)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

        run_in_sta_thread(self.engine.Execute, f"Open_Loop_Random_Noise_Processing {filename} {stimulusFilename}")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def CreateOpenSweptSineTestStimulus(self, silence=1, sweepTime=10,
                                        stimulusFileName="Open_Loop_Swept_Sine_Test_Stimulus", level=0.5, bitsDepth=32,
                                        startFrequency=20, endFrequency=20000, fadeIn=0, fadeType=EA.FadeTypes.Linear,
                                        fadeOut=0, repetitions=1, repetitionSilence=1,
                                        sweepMode=EA.ScanningModeTypes.Linear, burstSineLevel=0.5,
                                        burstSineFrequency=1000, burstSineCycles=1000, samplingFrequency=48000):
        settings = self.engine.GetOpenLoopSweptSineTestSettings()
        settings.ExternalDeviceStimulusBitsDepth = bitsDepth
        settings.ExternalDeviceStimulusSweepSineSettings.StartFrequency = startFrequency
        settings.ExternalDeviceStimulusSweepSineSettings.EndFrequency = endFrequency
        settings.ExternalDeviceStimulusSweepSineSettings.FadeIn = fadeIn
        settings.ExternalDeviceStimulusSweepSineSettings.FadeMode = fadeType
        settings.ExternalDeviceStimulusSweepSineSettings.FadeOut = fadeOut
        settings.ExternalDeviceStimulusSweepSineSettings.Repetitions = repetitions
        settings.ExternalDeviceStimulusSweepSineSettings.Silence = repetitionSilence
        settings.ExternalDeviceStimulusSweepSineSettings.SweepMode = sweepMode
        settings.ExternalDeviceStimulusSweepSineSettings.SweepTime = sweepTime
        settings.ExternalDeviceStimulusSweepSineSettings.Level = level
        settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency
        settings.StimulusName = stimulusFileName
        settings.Silence = silence
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        self.engine.SetOpenLoopSweptSineTestSettings(settings)
        self.engine.Execute("Open_Loop_Swept_Sine_Test StimulusOnly")

    def RunOpenLoopSweptSineTest(self, triggerChannel, triggerLevel=0.1, duration=10, saveImpulseResponses=False,
                                 impulseResponseLength=4096, measurementModeType=EA.MeasurementModeTypes.Spectra,
                                 resultFileFormatType=EA.ResultFileFormatTypes.CSV,
                                 filename="open_loop_random_noise_test", disablePlots=False):
        settings = self.engine.GetOpenLoopSweptSineTestSettings()
        settings.Filename = filename
        settings.MeasurementModeType = measurementModeType
        settings.SaveImpulseResponses = saveImpulseResponses
        settings.ImpulseResponseLength = impulseResponseLength
        settings.ResultFileFormatType = resultFileFormatType
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        self.engine.SetOpenLoopSweptSineTestSettings(settings)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * duration)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(
            Handlers,
            source,
            args)
        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Swept_Sine_Test TestOnly")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunCompleteOpenLoopSweptSineTest(self, triggerChannel, triggerLevel=0.1,
                                         stimulusFilename="Open_Loop_Swept_Sine_Test_Stimulus", level=0.5,
                                         saveImpulseResponses=False, impulseResponseLength=4096,
                                         measurementModeType=EA.MeasurementModeTypes.Spectra,
                                         resultFileFormatType=EA.ResultFileFormatTypes.CSV,
                                         filename="open_loop_swept_sine_test", samplingFrequency=48000, silence=1,
                                         sweepTime=10, bitsDepth=32, startFrequency=20, endFrequency=20000, fadeIn=0,
                                         fadeType=EA.FadeTypes.Linear, fadeOut=0, repetitions=1, repetitionSilence=1,
                                         sweepMode=EA.ScanningModeTypes.Linear, burstSineLevel=0.5,
                                         burstSineFrequency=1000, burstSineCycles=1000, disablePlots=False):
        settings = self.engine.GetOpenLoopSweptSineTestSettings()
        settings.ExternalDeviceStimulusBitsDepth = bitsDepth
        settings.ExternalDeviceStimulusSweepSineSettings.StartFrequency = startFrequency
        settings.ExternalDeviceStimulusSweepSineSettings.EndFrequency = endFrequency
        settings.ExternalDeviceStimulusSweepSineSettings.FadeIn = fadeIn
        settings.ExternalDeviceStimulusSweepSineSettings.FadeMode = fadeType
        settings.ExternalDeviceStimulusSweepSineSettings.FadeOut = fadeOut
        settings.ExternalDeviceStimulusSweepSineSettings.Repetitions = repetitions
        settings.ExternalDeviceStimulusSweepSineSettings.Silence = repetitionSilence
        settings.ExternalDeviceStimulusSweepSineSettings.SweepMode = sweepMode
        settings.ExternalDeviceStimulusSweepSineSettings.SweepTime = sweepTime
        settings.ExternalDeviceStimulusSweepSineSettings.Level = level
        settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        settings.Filename = filename
        settings.MeasurementModeType = measurementModeType
        settings.SaveImpulseResponses = saveImpulseResponses
        settings.ImpulseResponseLength = impulseResponseLength
        settings.ResultFileFormatType = resultFileFormatType
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        self.engine.SetOpenLoopSweptSineTestSettings(settings)

        self.engine.StimulusCreated += lambda source, args: Handlers.stimulusCreatedHandler(Handlers, source, args)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * (sweepTime * repetitions + repetitionSilence))
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(
            Handlers,
            source,
            args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Swept_Sine_Test Complete")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunPlaybackOpenLoopSweptSineTest(self, outputChannel, stimulusFilename="Open_Loop_Swept_Sine_Test_Stimulus",
                                         filename="Open_Loop_Swept_Sine_Test", silence=1, sweepTime=10,
                                         startFrequency=20, endFrequency=20000, fadeIn=0, fadeType=EA.FadeTypes.Linear,
                                         fadeOut=0, repetitions=1, repetitionSilence=1,
                                         sweepMode=EA.ScanningModeTypes.Linear, burstSineLevel=0.01,
                                         burstSineFrequency=1000, burstSineCycles=1000, saveImpulseResponses=False,
                                         impulseResponseLength=4096,
                                         measurementModeType=EA.MeasurementModeTypes.Spectra,
                                         resultFileFormatType=EA.ResultFileFormatTypes.CSV, disablePlots=False):
        settings = self.engine.GetOpenLoopSweptSineTestSettings()
        settings.MeasurementModeType = measurementModeType
        settings.SaveImpulseResponses = saveImpulseResponses
        settings.ImpulseResponseLength = impulseResponseLength
        settings.ResultFileFormatType = resultFileFormatType
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        self.engine.SetOpenLoopSweptSineTestSettings(settings)

        self.engine.SetOutputChannelSweptSineSettings(outputChannel, startFrequency, endFrequency, sweepMode, sweepTime,
                                                      repetitions, repetitionSilence, fadeType, fadeIn, fadeOut)

        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Swept_Sine_Test Playback")

        executionThread.join()

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

        run_in_sta_thread(self.engine.Execute, f"Open_Loop_Random_Noise_Processing {filename} {stimulusFilename}")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def CreateOpenLoopStepSineTestStimulus(self, stimulusFilename="Open_Loop_Step_Sine_Test_Stimulus", silence=1,
                                           level=0.5, minCycles=6, minDuration=0.003, bitsDepth=32, startFrequency=20,
                                           endFrequency=20000, resolutionType=EA.StepSineResolutionTypes.R40,
                                           settlingPeriods=5, stepIncrement=1, stepMode=EA.ScanningModeTypes.Linear,
                                           transitionPoints=500, burstSineLevel=0.5, burstSineFrequency=1000,
                                           burstSineCycles=1000, samplingFrequency=48000):
        settings = self.engine.GetOpenLoopStepSineTestSettings()
        settings.ExternalDeviceStimulusBitsDepth = bitsDepth
        settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency
        settings.ExternalDeviceStimulusStepSineSettings.StartFrequency = startFrequency
        settings.ExternalDeviceStimulusStepSineSettings.EndFrequency = endFrequency
        settings.ExternalDeviceStimulusStepSineSettings.MinCycles = minCycles
        settings.ExternalDeviceStimulusStepSineSettings.MinDuration = minDuration
        settings.ExternalDeviceStimulusStepSineSettings.ResolutionType = resolutionType
        settings.ExternalDeviceStimulusStepSineSettings.SettlingPeriods = settlingPeriods
        settings.ExternalDeviceStimulusStepSineSettings.StepIncrement = stepIncrement
        settings.ExternalDeviceStimulusStepSineSettings.StepMode = stepMode
        settings.ExternalDeviceStimulusStepSineSettings.TransitionPoints = transitionPoints
        settings.ExternalDeviceStimulusStepSineSettings.Level = level
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Cycles = burstSineCycles
        self.engine.SetOpenLoopStepSineTestSettings(settings)
        self.engine.Execute("Open_Loop_Step_Sine_Test StimulusOnly")

    def RunOpenLoopStepSineTest(self, triggerChannel, triggerLevel=0.1, filename="Open_Loop_Step_Sine_Test",
                                measurementMode=EA.MeasurementModeTypes.Spectra,
                                resultFileFormat=EA.ResultFileFormatTypes.CSV, disablePlots=False):
        settings = self.engine.GetOpenLoopStepSineTestSettings()
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        settings.Filename = filename
        settings.MeasurementModeType = measurementMode
        settings.ResultFileFormatType = resultFileFormat
        self.engine.SetOpenLoopStepSineTestSettings(settings)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(
            Handlers,
            source,
            args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Step_Sine_Test TestOnly")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunCompleteOpenLoopStepSineTest(self, triggerChannel, triggerLevel=0.1, level=0.5,
                                        stimulusFilename="Open_Loop_Step_Sine_Test_Stimulus",
                                        filename="Open_Loop_Step_Sine_Test",
                                        measurementMode=EA.MeasurementModeTypes.Spectra,
                                        resultFileFormat=EA.ResultFileFormatTypes.CSV, silence=1, minCycles=6,
                                        minDuration=0.003, bitsDepth=32, startFrequency=20, endFrequency=20000,
                                        resolutionType=EA.StepSineResolutionTypes.R40, settlingPeriods=5,
                                        stepIncrement=1, stepMode=EA.ScanningModeTypes.Linear, transitionPoints=500,
                                        burstSineLevel=0.5, burstSineFrequency=1000, burstSineCycles=1000,
                                        samplingFrequency=48000, disablePlots=False):
        settings = self.engine.GetOpenLoopStepSineTestSettings()
        settings.ExternalDeviceStimulusBitsDepth = bitsDepth
        settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency
        settings.ExternalDeviceStimulusStepSineSettings.StartFrequency = startFrequency
        settings.ExternalDeviceStimulusStepSineSettings.EndFrequency = endFrequency
        settings.ExternalDeviceStimulusStepSineSettings.MinCycles = minCycles
        settings.ExternalDeviceStimulusStepSineSettings.MinDuration = minDuration
        settings.ExternalDeviceStimulusStepSineSettings.ResolutionType = resolutionType
        settings.ExternalDeviceStimulusStepSineSettings.SettlingPeriods = settlingPeriods
        settings.ExternalDeviceStimulusStepSineSettings.StepIncrement = stepIncrement
        settings.ExternalDeviceStimulusStepSineSettings.StepMode = stepMode
        settings.ExternalDeviceStimulusStepSineSettings.TransitionPoints = transitionPoints
        settings.ExternalDeviceStimulusStepSineSettings.Level = level
        settings.StimulusName = stimulusFilename
        settings.Silence = silence
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Cycles = burstSineCycles
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        settings.Filename = filename
        settings.MeasurementModeType = measurementMode
        settings.ResultFileFormatType = resultFileFormat
        self.engine.SetOpenLoopStepSineTestSettings(settings)

        self.engine.StimulusCreated += lambda source, args: Handlers.stimulusCreatedHandler(Handlers, source, args)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(
            Handlers,
            source,
            args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Step_Sine_Test Complete")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunPlaybackOpenLoopStepSineTest(self, outputChannel, stimulusFilename="Open_Loop_Step_Sine_Test_Stimulus",
                                        filename="Open_Loop_Step_Sine_Test", silence=1, minCycles=6, minDuration=0.003,
                                        startFrequency=20, endFrequency=20000,
                                        resolutionType=EA.StepSineResolutionTypes.R40, settlingPeriods=5,
                                        stepIncrement=1, stepMode=EA.ScanningModeTypes.Linear, transitionPoints=500,
                                        burstSineLevel=0.01, burstSineFrequency=1000, burstSineCycles=1000,
                                        measurementMode=EA.MeasurementModeTypes.Spectra,
                                        resultFileFormat=EA.ResultFileFormatTypes.CSV, disablePlots=False):
        settings = self.engine.GetOpenLoopStepSineTestSettings()
        settings.StimulusName = stimulusFilename
        settings.Filename = filename
        settings.Silence = silence
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Cycles = burstSineCycles
        settings.MeasurementModeType = measurementMode
        settings.ResultFileFormatType = resultFileFormat
        self.engine.SetOpenLoopStepSineTestSettings(settings)

        self.engine.SetOutputChannelStepSineSettings(outputChannel, startFrequency, endFrequency, resolutionType,
                                                     minCycles, minDuration, stepMode, stepIncrement, settlingPeriods,
                                                     transitionPoints)

        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Step_Sine_Test Playback")

        executionThread.join()

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

        run_in_sta_thread(self.engine.Execute,f"Open_Loop_Step_Sine_Processing {filename} {stimulusFilename}")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def CreateOpenLoopWaveformStreamingStimulus(self, path, stimulusFilename="Open_Loop_Waveform_Streaming_Stimulus",
                                                level=0.2, trackIndex=1, bitDepth=32, samplingRate=48000,
                                                burstSineLevel=0.5, burstSineFrequency=1000, burstSineCycles=1000,
                                                silence=1):
        settings = self.engine.GetOpenLoopWaveformStreamingTestSettings()
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        settings.ExternalDeviceStimulusBitsDepth = bitDepth
        settings.ExternalDeviceStimulusSamplingFrequency = samplingRate
        settings.ExternalDeviceStimulusWaveformStreamingSettings.Level = level
        settings.ExternalDeviceStimulusWaveformStreamingSettings.ChannelIndex = trackIndex
        settings.ExternalDeviceStimulusWaveformStreamingSettings.Filename = path
        settings.Silence = silence
        settings.StimulusName = stimulusFilename
        self.engine.SetOpenLoopWaveformStreamingTestSettings(settings)
        self.engine.Execute("Open_Loop_Waveform_Streaming_Test StimulusOnly")

    def RunOpenLoopWaveformStreamingTest(self, triggerChannel, triggerLevel=0.1,
                                         filename="Open_Loop_Waveform_Streaming_Test",
                                         measurementModeType=EA.MeasurementModeTypes.Spectra,
                                         resultFileFormatType=EA.ResultFileFormatTypes.CSV, disablePlots=False):
        settings = self.engine.GetOpenLoopWaveformStreamingTestSettings()
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        settings.Filename = filename
        settings.MeasurementModeType = measurementModeType
        settings.ResultFileFormatType = resultFileFormatType
        self.engine.SetOpenLoopWaveformStreamingTestSettings(settings)

        self.engine.StimulusCreated += lambda source, args: Handlers.stimulusCreatedHandler(Handlers, source, args)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(
            Handlers,
            source,
            args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Waveform_Streaming_Test TestOnly")

        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunCompleteOpenLoopWaveformStreamingTest(self, path, triggerChannel, triggerLevel=0.1, level=0.2,
                                                 stimulusFilename="Open_Loop_Waveform_Streaming_Stimulus",
                                                 filename="Open_Loop_Waveform_Streaming_Test",
                                                 measurementModeType=EA.MeasurementModeTypes.Spectra,
                                                 resultFileFormatType=EA.ResultFileFormatTypes.CSV, trackIndex=1,
                                                 bitDepth=32, samplingRate=48000, burstSineLevel=0.5,
                                                 burstSineFrequency=1000, burstSineCycles=1000, silence=1, disablePlots=False):
        settings = self.engine.GetOpenLoopWaveformStreamingTestSettings()
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        settings.ExternalDeviceStimulusBitsDepth = bitDepth
        settings.ExternalDeviceStimulusSamplingFrequency = samplingRate
        settings.ExternalDeviceStimulusWaveformStreamingSettings.Level = level
        settings.ExternalDeviceStimulusWaveformStreamingSettings.ChannelIndex = trackIndex
        settings.ExternalDeviceStimulusWaveformStreamingSettings.Filename = path
        settings.Silence = silence
        settings.StimulusName = stimulusFilename
        settings.TriggerChannel = triggerChannel
        settings.TriggerLevel = triggerLevel
        settings.Filename = filename
        settings.MeasurementModeType = measurementModeType
        settings.ResultFileFormatType = resultFileFormatType
        self.engine.SetOpenLoopWaveformStreamingTestSettings(settings)

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

            self.engine.TimeDataRecorded += lambda source, args: Handlers.time_data_callback(Handlers, source, args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.testResultsReadyHandler(
            Handlers,
            source,
            args)
        self.engine.StimulusCreated += lambda source, args: Handlers.stimulusCreatedHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Waveform_Streaming_Test Complete")
        if not disablePlots:
            fh.run()

        return Handlers.testResults

    def RunPlaybackOpenLoopWaveformStreamingTest(self, outputChannel, path,
                                                 stimulusFilename="Open_Loop_Waveform_Streaming_Stimulus",
                                                 filename="Open_Loop_Waveform_Streaming_Test", trackIndex=1,
                                                 burstSineLevel=0.01, burstSineFrequency=1000, burstSineCycles=1000,
                                                 silence=1, measurementModeType=EA.MeasurementModeTypes.Spectra,
                                                 resultFileFormatType=EA.ResultFileFormatTypes.CSV, disablePlots=False):
        settings = self.engine.GetOpenLoopWaveformStreamingTestSettings()
        settings.BurstSineSettings.Level = burstSineLevel
        settings.BurstSineSettings.Frequency = burstSineFrequency
        settings.BurstSineSettings.Cycles = burstSineCycles
        settings.Silence = silence
        settings.StimulusName = stimulusFilename
        settings.Filename = filename
        settings.MeasurementModeType = measurementModeType
        settings.ResultFileFormatType = resultFileFormatType
        self.engine.SetOpenLoopWaveformStreamingTestSettings(settings)

        self.engine.SetOutputChannelWaveformStreamingSettings(outputChannel, path, trackIndex)

        self.engine.MultiSIMOFFTProcessingResultsUpdated += lambda source, args: Handlers.fftprocessingUpdated(Handlers,
                                                                                                               source,
                                                                                                               args)
        self.engine.TestResultsAvailable += lambda source, args: Handlers.saveResultsToVarHandler(Handlers, source, args)

        executionThread = run_in_sta_thread(self.engine.Execute, "Open_Loop_Waveform_Streaming_Test Playback")

        executionThread.join()

        if not disablePlots:
            fs = 96000
            DataBuffer = buffer(fs * 10)
            fh = figureHandler(sampleinterval=0.1, timewindow=1, size=(fs,))

        run_in_sta_thread(self.engine.Execute, f"Open_Loop_Waveform_Streaming_Processing {filename} {stimulusFilename}")

        if not disablePlots:
            fh.run()

        return Handlers.testResults
