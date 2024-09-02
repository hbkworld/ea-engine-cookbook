import sys
import sounddevice as sd
import soundfile as sf
import pyaudio
import numpy as np
from HelpFunctions.buffer import buffer
import threading

class Handlers:
    DataBuffer = buffer(int(96e3*10))
    curves = [None] * 10
    timestamp = 0
    channelInfo = [['' for _ in range(3)] for _ in range(10)]
    testResults = None


    @staticmethod
    def initDataBuffer(buffer):
        DataBuffer = buffer
    
    @staticmethod
    def calfeedback(source, args):
        print(args.MessageType, " - ", args.Message)

    def averageupdated(source, args):
        if args.CurrentAverage < args.TotalAverages:
            print('\rAverage:', args.CurrentAverage, " / ", args.TotalAverages, end='')
        else:
            print('\rAverage:', args.TotalAverages, " / ", args.TotalAverages, end='')
            print('')

    @staticmethod
    def errormessage(source, args):
        if args.ErrorMessage != "":
            print(args.ErrorMessage)
            sys.exit()

    @staticmethod
    def feedback(source, args):
        print(args.MessageType, " - ", args.Message)

    @staticmethod
    def timedata(cls, source, args):
        if args.TimeBlocks is not None:
            data = args.TimeBlocks

            n = 0

            if args.TimeBlocks.GetLength(0) != 0:
                for j in range(0, args.TimeBlocks.GetLength(1)):
                    # if inputchannels[j].IsActive == True:
                    y = [None] * 4096
                    for i in range(0, args.TimeBlocks.GetLength(0)):
                        y[i] = data[i, j]
                    cls.curves[n].setData(cls.timestamp, y)
                    n = n + 1 

    @staticmethod
    def timeupdated(cls, source, args):
        if args.CurrentTime < args.Duration:
            print('\r{0}: {1:.2f}'.format(args.CurrentMessage, args.CurrentTime), end='')
            cls.timestamp = args.CurrentTime
        else:
            print('')

    @staticmethod
    def fftprocessingUpdated(cls, source, args):
        if args.AutoSpectrum is not None:
            cls.curves = [None] * (len(args.AutoSpectrumInfo))
            for i in range(len(args.AutoSpectrumInfo)):
                if args.AutoSpectrumInfo[i] is not None:
                    split_info = args.AutoSpectrumInfo[i].split('|')
                    for j in range(len(split_info)):
                        cls.channelInfo[i][j] = split_info[j]

            freq = args.FrequencyAxis
            data = args.AutoSpectrum
            if freq.Length != 0:
                for j in range(0, data.GetLength(1)):
                    x = np.zeros(freq.Length)
                    y = np.zeros(freq.Length)
                    for i in range(0, freq.Length):
                        x[i] = freq[i]
                        y[i] = data[i, j]
                    cls.curves[j] = (x, y)

    @staticmethod
    def stepProcessingUpdated(cls, source, args):
        if args.SpectrumAmplitude is not None:
            cls.curves = [None] * (len(args.SpectrumInfo))
            for i in range(len(args.SpectrumInfo)):
                if args.SpectrumInfo[i] is not None:
                    split_info = args.SpectrumInfo[i].split('|')
                    for j in range(len(split_info)):
                        cls.channelInfo[i][j] = split_info[j]
            freq = args.FrequencyAxis
            data = args.SpectrumAmplitude
            if freq.Length != 0:
                for j in range(0, data.GetLength(1)):
                    x = np.zeros(freq.Length)
                    y = np.zeros(freq.Length)
                    for i in range(0, freq.Length):
                        x[i] = freq[i]
                        y[i] = data[i, j]
                    cls.curves[j] = (x, y)

    @staticmethod
    def time_data_callback(cls, source, args):
        if args.TimeBlocks is not None:
            data = args.TimeBlocks
            if args.TimeBlocks.GetLength(0) != 0:
                y = np.zeros(4096)
                for i in range(0, args.TimeBlocks.GetLength(0)):
                    y[i] = data[i, 0]

                cls.DataBuffer.append(y)

    import HelpFunctions.ea_engine as EA
    engine = EA.getEngine()
    @staticmethod
    def stimulusCreatedHandler(cls, source, args):
        output_channel_name = cls.engine.GetSelectedWDMOutputDevice().Name.replace(" Left", "").replace(" Right", "")
        deviceNumber = None
        p = pyaudio.PyAudio()
        for i in range(0, p.get_device_count()):
            if (p.get_device_info_by_index(i)['name'] == output_channel_name):
                deviceNumber = i
                break
        if deviceNumber is None:
            print(f"Device {output_channel_name} not found")
            sys.exit()
        audioThread = threading.Thread(target=cls._playAudio, args=(args.FullPath, deviceNumber, p))
        audioThread.start()       

    @staticmethod
    def _playAudio(path, deviceNumber, p):
        data, samplerate = sf.read(path)

        if len(data.shape) == 1:
            data = np.stack((data, data), axis=1)

        stream = p.open(format=pyaudio.paFloat32,
                        channels=data.shape[1],
                        rate=samplerate,
                        output=True,
                        output_device_index=deviceNumber)

        if data.dtype != np.float32:
            data = data.astype(np.float32)

        stream.write(data.tobytes())
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    @staticmethod
    def testResultsReadyHandler(cls, source, args):
        if args.AutoSpectrum is not None:
            cls.curves = [None] * (len(args.AutoSpectrumInfo))
            for i in range(len(args.AutoSpectrumInfo)):
                if args.AutoSpectrumInfo[i] is not None:
                    split_info = args.AutoSpectrumInfo[i].split('|')
                    for j in range(len(split_info)):
                        cls.channelInfo[i][j] = split_info[j]

            freq = args.FrequencyAxis
            data = args.AutoSpectrum
            if freq.Length != 0:
                for j in range(0, data.GetLength(1)):
                    x = np.zeros(freq.Length)
                    y = np.zeros(freq.Length)
                    for i in range(0, freq.Length):
                        x[i] = freq[i]
                        y[i] = data[i, j]
                    cls.curves[j] = (x, y)

        cls.testResults = args

    @staticmethod
    def saveResultsToVarHandler(cls, source, args):
        cls.testResults = args
