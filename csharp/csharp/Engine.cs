using csharp.HelpFunctions;
using EA_Engine;
using NAudio.Wave;
using OxyPlot;

namespace EAProject
{
    public class FigureHandler : BaseFigureHandler
    {
        public FigureHandler(double sampleinterval = 0.1, double timewindow = 10.0, int size = 4096, string unit = "Pa")
            : base(sampleinterval, timewindow, size, unit)
        {
        }

        protected override void Update()
        {
            //updates frequency plot
            if(this.frequencyPlotFlag)
            {
                for (int i = 0; i < this.frequencyLineSeries.Length; i++)
                {
                    this.frequencyLineSeries[i].Points.Clear();
                    var xValues = Handlers.dataPoints[i].Item1;
                    var yValues = Handlers.dataPoints[i].Item2;

                    if (xValues.Length != yValues.Length)
                    {
                        throw new InvalidOperationException("The lengths of xValues and yValues arrays do not match.");
                    }

                    for (int j = 0; j < xValues.Length; j++)
                    {
                        this.frequencyLineSeries[i].Points.Add(new DataPoint(xValues[j], yValues[j]));
                    }
                }
            }
            // initializes frequency plot
            else if (Handlers.frequencyPlotReady)
            {
                FrequencyWindow();
                for (int i = 0; i < Handlers.channelInfo.GetLength(0); i++)
                {
                    this.frequencyPlotModels[i].Title = $"{Handlers.channelInfo[i,0]}: {Handlers.channelInfo[i,2]}";
                }
            }
            // runs the time domain plot
            else
            {
                if (this.lineSeries != null && this.x != null)
                {
                    double[] yValues = Buffer.GetPart(this.size);

                    if (this.x.Length == yValues.Length)
                    {
                        // Update the time signal plot
                        this.lineSeries.Points.Clear();
                        for (int i = 0; i < this.x.Length; i++)
                        {
                            this.lineSeries.Points.Add(new DataPoint(this.x[i], yValues[i]));
                        }
                    }
                    else
                    {
                        throw new InvalidOperationException("The lengths of x- and y-values arrays do not match.");
                    }
                }
                else
                {
                    throw new InvalidOperationException("LineSeries, or x is not properly initialized.");
                }
            }
        }
    }
    public class EA_Engine
    {
        private Engine engine;

        public Engine GetEngine()
        {
            return this.engine;
        }

        public EA_Engine()
        {
            var HelperEngine = new HelperEngine();
            this.engine = HelperEngine.GetEngine();
        }

        public void ResetEngine()
        {
            this.engine.ResetSettings();
        }

        public void Select3670Device()
        {
            var devices = engine.GetDetectedASIODevices();
            for (int ii = 0; ii < devices.Length; ii++)
            {
                var device = devices[ii];
                Console.WriteLine($"Device: {device.ASIODriverName}");
                if (device.Name.Contains("3670"))
                {
                    // We have found the 3670 device. Now select it (index is 1-based)
                    engine.SelectASIODevice(ii + 1, true);
                    Console.WriteLine($"Selected: {device.Name}");
                    break;
                }
            }
        }

        public void SetInputChannel(int number, string name, bool isActive, string referenceChannelName = "None", double sensitivity = -1, string sensitivityUnit = "none", double dbRef = -1)
        {
            var channels = this.engine.GetInputChannels(false);
            var channel = channels[number - 1];
            channel.Name = name;
            channel.IsActive = isActive;
            channel.ReferenceChannelName = referenceChannelName;

            if (sensitivity > 0)
            {
                channel.Sensitivity = (double)sensitivity;
            }

            if (sensitivityUnit != "none")
            {
                channel.SensitivityUnit = sensitivityUnit.ToString();
            }

            if (dbRef > 0)
            {
                channel.dBRef = (double)dbRef;
            }

            this.engine.SetInputChannels(channels);
        }

        public InputChannel[] GetActiveInputChannels()
        {
            return this.engine.GetInputChannels(true);
        }

        public void SetOutputChannel(int number,
									 string name,
									 bool isActive,
									 string referenceChannelName = "None",
									 double sensitivity = -1,
									 string sensitivityUnit = "none",
									 double dbRef = -1,
									 double outputLevel = 1)
        {
            var channels = this.engine.GetOutputChannels(false);
            var channel = channels[number - 1];
            channel.Name = name;
            channel.IsActive = isActive;
            channel.ReferenceChannelName = referenceChannelName;

            if (sensitivity > 0)
            {
                channel.Sensitivity = (double)sensitivity;
            }

            if (sensitivityUnit != "none")
            {
                channel.SensitivityUnit = sensitivityUnit.ToString();
            }

            if (dbRef > 0)
            {
                channel.dBRef = (double)dbRef;
            }

            channel.VMax = (double)outputLevel;

            this.engine.SetOutputChannels(channels);
        }

        public OutputChannel[] GetActiveOutputChannels()
        {
            return this.engine.GetOutputChannels(true);
        }

        public void SetAllChannelsToFalse()
        {
            var inputChannels = engine.GetInputChannels(false);
			for (int i = 0; i < inputChannels.Length; i++)
            {
                inputChannels[i].IsActive = false;
            }
            engine.SetInputChannels(inputChannels);
            var outputChannels = engine.GetOutputChannels(false);
            for (int i = 0; i < outputChannels.Length; i++)
            {
                outputChannels[i].IsActive = false;
            }
            engine.SetOutputChannels(outputChannels);
        }

        public void RunInputCalibration(int channelNumber, int refernceFrequency = 1000, double referenceLevel = 1, int duration = 10, string referenceUnit = "Pa rms")
        {
            var activeinputChannels = this.GetActiveInputChannels().Select(c => c.Number).ToList();
            if (!activeinputChannels.Contains(channelNumber))
            {
                Console.WriteLine($"Channel {channelNumber} is not an active input channel");
                return;
            }

            var calibrationsettings = this.engine.GetInputCalibrationSettings();
            calibrationsettings.ReferenceFrequency = refernceFrequency;
            calibrationsettings.ReferenceLevel = referenceLevel;
            calibrationsettings.Duration = duration;
            calibrationsettings.ReferenceUnit = referenceUnit;

            this.engine.SetInputCalibrationSettings(calibrationsettings);

            Console.WriteLine($"Calibration frequency {calibrationsettings.ReferenceFrequency} Hz");
            Console.WriteLine($"Reference level {calibrationsettings.ReferenceLevel} {calibrationsettings.ReferenceUnit}");

            this.engine.Execute($"Calibrate_Input_Channel {channelNumber}");
        }

        public void RunOutputCalibration(int inputChannel, int outputChannel, int frequency = 1000, double level = 0.01, int duration = 10)
        {
            var activeinputChannels = this.GetActiveInputChannels().Select(c => c.Number).ToList();
            if (!activeinputChannels.Contains(inputChannel))
            {
                Console.WriteLine($"Channel {inputChannel} is not an active input channel");
                return;
            }

            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return;
            }

            var calibrationSettings = this.engine.GetOutputCalibrationSettings();
            calibrationSettings.Frequency = frequency;
            calibrationSettings.Level = level;
            calibrationSettings.Duration = duration;

            this.engine.SetOutputCalibrationSettings(calibrationSettings);

            Console.WriteLine($"Calibration frequency {frequency} Hz");
            Console.WriteLine($"Reference level {level} EU rms");

            this.engine.Execute($"Calibrate_Output_Channel {inputChannel} {outputChannel}");
        }

        public TestResultsAvailableArgs? RunOutputEqualization(int inputChannel,
										  int outputChannel,
										  int filterLength = 8193,
										  int frequencyStart = 100,
										  int frequencyEnd = 10000,
										  bool measureAndRemoveExtraLatency = true,
										  double referenceFrequency = -1,
										  ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
										  ScaleTypes scaleType = ScaleTypes.dB,
										  GeneratorSignalTypes stimulusType = GeneratorSignalTypes.Random,
                                          bool disablePlots = false)
        {
            var activeinputChannels = this.GetActiveInputChannels().Select(c => c.Number).ToList();
            if (!activeinputChannels.Contains(inputChannel))
            {
                Console.WriteLine($"Channel {inputChannel} is not an active input channel");
                return null;
            }

            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return null;
            }

            var eqSettings = engine.GetOutputEqualizationSettings();
            eqSettings.FilterLength = filterLength;
            eqSettings.FrequencyStart = frequencyStart;
            eqSettings.FrequencyEnd = frequencyEnd;
            eqSettings.MeasureAndRemoveExtraLatency = measureAndRemoveExtraLatency;
            eqSettings.ReferenceFrequency = referenceFrequency;
            eqSettings.ResultFileFormatType = resultFileFormat;
            eqSettings.ScaleType = scaleType;
            eqSettings.StimulusType = stimulusType;
            engine.SetOutputEqualizationSettings(eqSettings);

            FigureHandler? fh = null;
            if (!disablePlots) {
				int fs = 96000;
				Buffer.SetSize(fs * 10);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute($"Equalize_Output_Channel {inputChannel} {outputChannel}"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();
				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;
            return Handlers.testResults;

        }

        public TestResultsAvailableArgs? RunRandomTest(int outputChannel,
								  int duration = 10,
								  int lowerFrequency = 80,
								  int upperFrequency = 12000,
								  int slope = 0,
								  string filename = "random_noise_test",
								  MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
								  ResultFileFormatTypes resultFileFormatType = ResultFileFormatTypes.CSV,
								  bool disablePlots = false)
        {
            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return null;
            }


            this.engine.SetOutputChannelRandomSettings(outputChannel, true, lowerFrequency, upperFrequency, slope, duration);

            var randomSettings = this.engine.GetRandomNoiseTestSettings();
            randomSettings.Duration = duration;
            randomSettings.Filename = filename;
            randomSettings.MeasurementModeType = measurementModeType;
            randomSettings.ResultFileFormatType = resultFileFormatType;
            this.engine.SetRandomNoiseTestSettings(randomSettings);

            FigureHandler? fh = null;
            if (!disablePlots) {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;
            Thread backgroundThread = new Thread(() => this.engine.Execute("Random_Noise_Test"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();
				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;
            return Handlers.testResults;

        }

        public TestResultsAvailableArgs? RunStepSineTest(int outputChannel,
									int startFrequency = 100,
									int endFrequency = 10000,
									StepSineResolutionTypes resolutionType = StepSineResolutionTypes.R80,
									int minCycles = 5,
									double minDuration = 0.1,
									ScanningModeTypes stepMode = ScanningModeTypes.Linear,
									int stepIncrement = 1,
									int settlingPeriods = 5,
									int transitionPoints = 100,
                                    bool disablePlots = false)
        {
            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return null;
            }


            this.engine.SetOutputChannelStepSineSettings(outputChannel,
                                                        startFrequency,
                                                        endFrequency,
                                                        resolutionType,
                                                        minCycles,
                                                        minDuration,
                                                        stepMode,
                                                        stepIncrement,
                                                        settlingPeriods,
                                                        transitionPoints);
            var stepSineSettings = engine.GetStepSineTestSettings();
            stepSineSettings.Filename = "step_sine_test";
            stepSineSettings.MeasureAndRemoveExtraLatency = true;
            stepSineSettings.ApplyEqualization = false;
            stepSineSettings.MeasurementModeType = MeasurementModeTypes.Spectra;
            stepSineSettings.ResultFileFormatType = ResultFileFormatTypes.CSV;
            engine.SetStepSineTestSettings(stepSineSettings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * 10);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.HarmonicEstimatorProcessingResultsUpdated += Handlers.StepProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Step_Sine_Test"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();
            if (!disablePlots)
            {
				fh.Run();
				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.HarmonicEstimatorProcessingResultsUpdated -= Handlers.StepProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }

        public TestResultsAvailableArgs? RunSweptSineTest(int outputChannel,
									 int duration = 10,
									 int startFrequency = 100,
									 int endFrequency = 10000,
									 ScanningModeTypes scanningMode = ScanningModeTypes.Linear,
									 int repetition = 1,
									 int silenceDuration = 0,
									 FadeTypes fademode = FadeTypes.Cosine,
									 double fadeinDuration = 0.01,
									 double fadeoutDuration = 0.01,
                                     bool disablePlots = false)
        {
            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return null;
            }


            this.engine.SetOutputChannelSweptSineSettings(outputChannel,
                                                         startFrequency,
                                                         endFrequency,
                                                         scanningMode,
                                                         duration,
                                                         repetition,
                                                         silenceDuration,
                                                         fademode,
                                                         fadeinDuration,
                                                         fadeoutDuration);

            var sweptSineSettings = this.engine.GetSweptSineTestSettings();
            sweptSineSettings.Duration = duration * (repetition + 1);
            sweptSineSettings.Filename = "swept_sine_test";
            sweptSineSettings.MeasureAndRemoveExtraLatency = true;
            sweptSineSettings.ApplyEqualization = false;
            sweptSineSettings.MeasurementModeType = MeasurementModeTypes.Spectra;
            sweptSineSettings.ResultFileFormatType = ResultFileFormatTypes.CSV;
            sweptSineSettings.Recording = false;
            this.engine.SetSweptSineTestSettings(sweptSineSettings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration * (repetition + 1));
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Swept_Sine_Test"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }

        public TestResultsAvailableArgs? RunFixedSineTest(int outputChannel, int duration = 10, int frequency = 1000, bool disablePlots = false)
        {
            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return null;
            }


            this.engine.SetOutputChannelFixedSineSettings(outputChannel, frequency, duration);

            var fixedSineSettings = this.engine.GetFixedSineTestSettings();
            fixedSineSettings.Filename = "fixed_sine_test";
            fixedSineSettings.SettlingTime = true;
            fixedSineSettings.MeasureAndRemoveExtraLatency = true;
            fixedSineSettings.ResultFileFormatType = ResultFileFormatTypes.CSV;
            fixedSineSettings.ApplyEqualization = false;
            fixedSineSettings.MeasurementModeType = MeasurementModeTypes.Spectra;
            this.engine.SetFixedSineTestSettings(fixedSineSettings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Fixed_Sine_Test"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }

        public TestResultsAvailableArgs? RunWaveformStreamingTest(int outputChannel, string wavPath, int trackIndex = 1, bool disablePlots = false)
        {
            var activeOutputChannels = this.GetActiveOutputChannels().Select(c => c.Number).ToList();
            if (!activeOutputChannels.Contains(outputChannel))
            {
                Console.WriteLine($"Channel {outputChannel} is not an active output channel");
                return null;
            }


            wavPath = Path.Combine(Directory.GetCurrentDirectory(), wavPath);
            if (!File.Exists(wavPath))
            {
                Console.WriteLine($"File {wavPath} not found. Please execute the script within the correct directory.");
                return null;
            }
            WaveFileReader wf = new WaveFileReader(wavPath);
            int duration = (int)wf.TotalTime.TotalSeconds;

            this.engine.SetOutputChannelWaveformStreamingSettings(outputChannel, wavPath, trackIndex);

            var waveformStreamingSettings = this.engine.GetWaveformStreamingTestSettings();
            waveformStreamingSettings.Filename = "waveform_streaming_test";
            waveformStreamingSettings.MeasureAndRemoveExtraLatency = true;
            waveformStreamingSettings.ResultFileFormatType = ResultFileFormatTypes.CSV;
            waveformStreamingSettings.ApplyEqualization = false;
            waveformStreamingSettings.MeasurementModeType = MeasurementModeTypes.Spectra;
            waveformStreamingSettings.Recording = false;
            this.engine.SetWaveformStreamingTestSettings(waveformStreamingSettings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Waveform_Streaming_Test"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }

        public void SelectWdmInputDevice(string deviceName, bool isActive)
        {
            Console.WriteLine("\nWDM Inputs:");
            foreach (var device in this.engine.GetDetectedWDMInputDevices())
            {
                Console.WriteLine($"{device.Index}: {device.Name}");
                if (device.Name == deviceName)
                {
                    Console.WriteLine($"Device {device.Index}: {deviceName} found");
                    this.engine.Execute($"Select_WDM_Input_Device {device.Index}");
                    // may be an issue if more inputs gets added
                    SetInputChannel(9, $"{device.Name} Microphone", isActive);
                    return;
                }
            }
            Console.WriteLine($"Device {deviceName} not found");
        }
        public void SelectWdmOutputDevice(string deviceName, bool isActive)
        {
            Console.WriteLine("\nWDM Outputs:");
            foreach (var device in this.engine.GetDetectedWDMOutputDevices())
            {
                Console.WriteLine($"{device.Index}: {device.Name}");
                if (device.Name == deviceName)
                {
                    Console.WriteLine($"Device {device.Index}: {deviceName} found");
                    this.engine.Execute($"Select_WDM_Output_Device {device.Index}");
                    // may be an issue if more outputs gets added or if output is mono
                    SetOutputChannel(3, $"{device.Name} Left", isActive);
                    SetOutputChannel(4, $"{device.Name} Right", isActive);
                    return;
                }
            }
            Console.WriteLine($"Device {deviceName} not found");
        }
        public void DeselectWdmInputDevice()
        {
            engine.DeselectWDMInputDevice();
        }
        public void DeselectWdmOutputDevice()
        {
            engine.DeselectWDMOutputDevice();
        }

        public void AdjustWdmInputVolume(float volume)
        {
            var status = this.engine.AdjustWDMInputDeviceVolume(volume);
			if (status.Equals("OK"))
			{
                Console.WriteLine($"Input volume: {volume}");
            } else
            {
                Console.WriteLine($"ERROR: {status}");
            }
        }
        public void AdjustWdmOutputVolume(float volume)
        {
            var status = this.engine.AdjustWDMOutputDeviceVolume(volume);
			if (status.Equals("OK"))
			{
                Console.WriteLine($"Input volume: {volume}");
            } else
            {
                Console.WriteLine($"ERROR: {status}");
            }
        }

        public void CreateOpenLoopRandomNoiseStimulus(double silence = 1,
													  int duration = 10,
													  string stimulusFilename = "Open_Loop_Random_Noise_Test_Stimulus",
													  double level = 0.5,
													  int lowerFrequency = 20,
													  int upperFrequency = 20000,
													  int slope = 0,
													  double burstSineLevel = 0.5,
													  int burstSineFrequency = 1000,
													  int burstSineCycles = 1000)
        {
            var settings = this.engine.GetOpenLoopRandomNoiseTestSettings();
            settings.ExternalDeviceStimulusRandomSettings.Duration = duration;
            settings.ExternalDeviceStimulusRandomSettings.Slope = slope;
            settings.ExternalDeviceStimulusRandomSettings.HiPassFrequency = lowerFrequency;
            settings.ExternalDeviceStimulusRandomSettings.LoPassFrequency = upperFrequency;
            settings.ExternalDeviceStimulusRandomSettings.IsFiltered = true;
            settings.ExternalDeviceStimulusRandomSettings.Level = level;
            settings.StimulusName = stimulusFilename;
            settings.Silence = silence;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            this.engine.SetOpenLoopRandomNoiseTestSettings(settings);
            this.engine.Execute("Open_Loop_Random_Noise_Test StimulusOnly");
        }
        public TestResultsAvailableArgs? RunOpenLoopRandomNoiseTest(int triggerChannel,
											   double triggerLevel = 0.1,
											   int duration = 10,
											   MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
											   ResultFileFormatTypes resultFileFormatType = ResultFileFormatTypes.CSV,
											   string filename = "open_loop_random_noise_test",
                                               bool disablePlots = false)
        {
            var settings = this.engine.GetOpenLoopRandomNoiseTestSettings();
            settings.Filename = filename;
            settings.MeasurementModeType = measurementModeType;

            settings.ResultFileFormatType = resultFileFormatType;
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            this.engine.SetOpenLoopRandomNoiseTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Random_Noise_Test TestOnly"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }


        //Creates and runs the stimulus
        public TestResultsAvailableArgs? RunCompleteOpenLoopRandomNoiseTest(int triggerChannel,
													   double triggerLevel = 0.1,
													   string stimulusFilename = "Open_Loop_Random_Noise_Test_Stimulus",
													   int duration = 10,
													   double level = 0.5,
													   MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
													   ResultFileFormatTypes resultFileFormatTypes = ResultFileFormatTypes.CSV,
													   string filename = "open_loop_random_noise_test",
													   double silence = 1,
													   int lowerFrequency = 20,
													   int upperFrequency = 20000,
													   int slope = 0,
													   double burstSineLevel = 0.5,
													   int burstSineFrequency = 1000,
													   int burstSineCycles = 1000,
                                                       bool disablePlots = false)
        {
            var settings = this.engine.GetOpenLoopRandomNoiseTestSettings();
            settings.MeasurementModeType = measurementModeType;
            settings.ResultFileFormatType = resultFileFormatTypes;
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            settings.ExternalDeviceStimulusRandomSettings.Duration = duration;
            settings.ExternalDeviceStimulusRandomSettings.Slope = slope;
            settings.ExternalDeviceStimulusRandomSettings.HiPassFrequency = lowerFrequency;
            settings.ExternalDeviceStimulusRandomSettings.LoPassFrequency = upperFrequency;
            settings.ExternalDeviceStimulusRandomSettings.IsFiltered = true;
            settings.ExternalDeviceStimulusRandomSettings.Level = 0.5;
            settings.StimulusName = stimulusFilename;
            settings.Silence = silence;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            this.engine.SetOpenLoopRandomNoiseTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;
            //TODO HANDLER DOES NOT GET CALLED
            this.engine.StimulusCreated += Handlers.StimulusCreatedHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Random_Noise_Test Complete"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();
            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
				this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;
            this.engine.StimulusCreated -= Handlers.StimulusCreatedHandler;

            return Handlers.testResults;
        }

        public TestResultsAvailableArgs? RunPlaybackOpenLoopRandomNoiseTest(int outputChannel,
													   string stimulusFilename = "Open_Loop_Random_Noise_Test_Stimulus",
													   int duration = 10,
													   MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
													   ResultFileFormatTypes resultFileFormatTypes = ResultFileFormatTypes.CSV,
													   string filename = "open_loop_random_noise_test",
													   double silence = 1,
													   int lowerFrequency = 20,
													   int upperFrequency = 20000,
													   int slope = 0,
													   double burstSineLevel = 0.01,
													   int burstSineFrequency = 1000,
													   int burstSineCycles = 1000,
                                                       bool disablePlots = false)
        {
            var settings = this.engine.GetOpenLoopRandomNoiseTestSettings();
            settings.MeasurementModeType = measurementModeType;
            settings.ResultFileFormatType = resultFileFormatTypes;
            settings.StimulusName = stimulusFilename;
            settings.Silence = silence;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            this.engine.SetOpenLoopRandomNoiseTestSettings(settings);

            this.engine.SetOutputChannelRandomSettings(outputChannel,
                                                       true,
                                                       lowerFrequency,
                                                       upperFrequency,
                                                       slope,
                                                       duration);

            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Random_Noise_Test Playback"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            var recordingPath = this.engine.GetEngineSettings().DataFolder + "\\" + filename + ".wav";
            var inputRecorder = new InputRecording(recordingPath);
            try
            {
				inputRecorder.StartRecording(48000);
                backgroundThread.Join();
                inputRecorder.StopRecording();
				FigureHandler? fh = null;
				if (!disablePlots)
				{
					this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
					int fs = 96000;
					Buffer.SetSize(fs * duration);
					fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);
				}
                Console.WriteLine($"Recording can be found at: {recordingPath}");
				Thread processingThread = new Thread(() => this.engine.Execute($"Open_Loop_Random_Noise_Processing {filename} {stimulusFilename}"));
                processingThread.SetApartmentState(ApartmentState.STA);
                processingThread.Start();

                if (!disablePlots)
                {
                    fh.Run();
					this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
                }

            }
            catch (Exception)
            {
                Console.WriteLine("ERROR: Could not find input device.");
                engine.AbortTest();
            }
            this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }



        public void CreateOpenSweptSineTestStimulus(double silence = 1,
													int sweepTime = 10,
													string stimulusFileName = "Open_Loop_Swept_Sine_Test_Stimulus",
													double level = 0.5,
													int bitsDepth = 32,
													int startFrequency = 20,
													int endFrequency = 20000,
													int fadeIn = 0,
													FadeTypes fadeType = FadeTypes.Linear,
													int fadeOut = 0,
													int repetitions = 1,
													int repetitionSilence = 1,
													ScanningModeTypes sweepMode = ScanningModeTypes.Linear,
													double burstSineLevel = 0.5,
													int burstSineFrequency = 1000,
													int burstSineCycles = 1000,
													int samplingFrequency = 48000)
        {
            var settings = this.engine.GetOpenLoopSweptSineTestSettings();
            settings.ExternalDeviceStimulusBitsDepth = bitsDepth;
            settings.ExternalDeviceStimulusSweepSineSettings.StartFrequency = startFrequency;
            settings.ExternalDeviceStimulusSweepSineSettings.EndFrequency = endFrequency;
            settings.ExternalDeviceStimulusSweepSineSettings.FadeIn = fadeIn;
            settings.ExternalDeviceStimulusSweepSineSettings.FadeMode = fadeType;
            settings.ExternalDeviceStimulusSweepSineSettings.FadeOut = fadeOut;
            settings.ExternalDeviceStimulusSweepSineSettings.Repetitions = repetitions;
            settings.ExternalDeviceStimulusSweepSineSettings.Silence = repetitionSilence;
            settings.ExternalDeviceStimulusSweepSineSettings.SweepMode = sweepMode;
            settings.ExternalDeviceStimulusSweepSineSettings.SweepTime = sweepTime;
            settings.ExternalDeviceStimulusSweepSineSettings.Level = level;
            settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency;
            settings.StimulusName = stimulusFileName;
            settings.Silence = silence;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            this.engine.SetOpenLoopSweptSineTestSettings(settings);
            this.engine.Execute("Open_Loop_Swept_Sine_Test StimulusOnly");
        }
        public TestResultsAvailableArgs? RunOpenLoopSweptSineTest(int triggerChannel,
											 double triggerLevel = 0.1,
											 int duration = 10,
											 bool saveImpulseResponses = false,
											 int impulseResponseLength = 4096,
											 MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
											 ResultFileFormatTypes resultFileFormatType = ResultFileFormatTypes.CSV,
											 string filename = "open_loop_random_noise_test",
                                             bool disablePlots = false)
        {
            var settings = this.engine.GetOpenLoopSweptSineTestSettings();
            settings.Filename = filename;
            settings.MeasurementModeType = measurementModeType;
            settings.SaveImpulseResponses = saveImpulseResponses;
            settings.ImpulseResponseLength = impulseResponseLength;
            settings.ResultFileFormatType = resultFileFormatType;
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            this.engine.SetOpenLoopSweptSineTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
            }
                this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Swept_Sine_Test TestOnly"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
            }
                this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;

            return Handlers.testResults;
        }
		public TestResultsAvailableArgs? RunCompleteOpenLoopSweptSineTest(int triggerChannel,
											   double triggerLevel = 0.1,
											   string stimulusFilename = "Open_Loop_Swept_Sine_Test_Stimulus",
											   double level = 0.5,
											   int duration = 10,
											   bool saveImpulseResponses = false,
											   int impulseResponseLength = 4096,
											   MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
											   ResultFileFormatTypes resultFileFormatType = ResultFileFormatTypes.CSV,
											   string filename = "open_loop_swept_sine_test",
											   int samplingFrequency = 48000,
											   double silence = 1,
											   int sweepTime = 10,
											   int bitsDepth = 32,
											   int startFrequency = 20,
											   int endFrequency = 20000,
											   int fadeIn = 0,
											   FadeTypes fadeType = FadeTypes.Linear,
											   int fadeOut = 0,
											   int repetitions = 1,
											   int repetitionSilence = 1,
											   ScanningModeTypes sweepMode = ScanningModeTypes.Linear,
											   double burstSineLevel = 0.5,
											   int burstSineFrequency = 1000,
											   int burstSineCycles = 1000,
                                               bool disablePlots = false)
		{
			var settings = this.engine.GetOpenLoopSweptSineTestSettings();
			settings.ExternalDeviceStimulusBitsDepth = bitsDepth;
			settings.ExternalDeviceStimulusSweepSineSettings.StartFrequency = startFrequency;
			settings.ExternalDeviceStimulusSweepSineSettings.EndFrequency = endFrequency;
			settings.ExternalDeviceStimulusSweepSineSettings.FadeIn = fadeIn;
			settings.ExternalDeviceStimulusSweepSineSettings.FadeMode = fadeType;
			settings.ExternalDeviceStimulusSweepSineSettings.FadeOut = fadeOut;
			settings.ExternalDeviceStimulusSweepSineSettings.Repetitions = repetitions;
			settings.ExternalDeviceStimulusSweepSineSettings.Silence = repetitionSilence;
			settings.ExternalDeviceStimulusSweepSineSettings.SweepMode = sweepMode;
			settings.ExternalDeviceStimulusSweepSineSettings.SweepTime = sweepTime;
            settings.ExternalDeviceStimulusSweepSineSettings.Level = level;
            settings.ExternalDeviceStimulusSamplingFrequency = 48000;
            settings.StimulusName = stimulusFilename;
			settings.Silence = silence;
			settings.BurstSineSettings.Level = burstSineLevel;
			settings.BurstSineSettings.Frequency = burstSineFrequency;
			settings.BurstSineSettings.Cycles = burstSineCycles;

			settings.Filename = filename;
			settings.MeasurementModeType = measurementModeType;
			settings.SaveImpulseResponses = saveImpulseResponses;
			settings.ImpulseResponseLength = impulseResponseLength;
			settings.ResultFileFormatType = resultFileFormatType;
			settings.TriggerChannel = triggerChannel;
			settings.TriggerLevel = triggerLevel;
			this.engine.SetOpenLoopSweptSineTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * duration);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated += Handlers.StimulusCreatedHandler;

			Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Swept_Sine_Test Complete"));
			backgroundThread.SetApartmentState(ApartmentState.STA);
			backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated -= Handlers.StimulusCreatedHandler;

            return Handlers.testResults;
		}

        public TestResultsAvailableArgs? RunPlaybackOpenLoopSweptSineTest(int outputChannel,
													 string stimulusFilename = "Open_Loop_Swept_Sine_Test_Stimulus",
													 string filename = "Open_Loop_Swept_Sine_Test",
													 double silence = 1,
													 int sweepTime = 10,
													 int startFrequency = 20,
													 int endFrequency = 20000,
													 int fadeIn = 0,
													 FadeTypes fadeType = FadeTypes.Linear,
													 int fadeOut = 0,
													 int repetitions = 1,
													 int repetitionSilence = 1,
													 ScanningModeTypes sweepMode = ScanningModeTypes.Linear,
													 double burstSineLevel = 0.01,
													 int burstSineFrequency = 1000,
													 int burstSineCycles = 1000,
													 bool saveImpulseResponses = false,
													 int impulseResponseLength = 4096,
													 MeasurementModeTypes measurementModeType = MeasurementModeTypes.Spectra,
													 ResultFileFormatTypes resultFileFormatType = ResultFileFormatTypes.CSV,
                                                     bool disablePlots = false)
        {
			var settings = this.engine.GetOpenLoopSweptSineTestSettings();
			settings.MeasurementModeType = measurementModeType;
			settings.SaveImpulseResponses = saveImpulseResponses;
			settings.ImpulseResponseLength = impulseResponseLength;
			settings.ResultFileFormatType = resultFileFormatType;
            settings.StimulusName = stimulusFilename;
			settings.Silence = silence;
			settings.BurstSineSettings.Level = burstSineLevel;
			settings.BurstSineSettings.Frequency = burstSineFrequency;
			settings.BurstSineSettings.Cycles = burstSineCycles;
			this.engine.SetOpenLoopSweptSineTestSettings(settings);

            this.engine.SetOutputChannelSweptSineSettings(outputChannel,
                                                          startFrequency,
                                                          endFrequency,
                                                          sweepMode,
                                                          sweepTime,
                                                          repetitions,
                                                          repetitionSilence,
                                                          fadeType,
                                                          fadeIn,
                                                          fadeOut);

            this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Swept_Sine_Test Playback"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            var recordingPath = this.engine.GetEngineSettings().DataFolder + "\\" + filename + ".wav";
            var inputRecorder = new InputRecording(recordingPath);
            try
            {
				inputRecorder.StartRecording(48000);
                backgroundThread.Join();
                inputRecorder.StopRecording();
				FigureHandler? fh = null;
				if (!disablePlots)
				{
					int fs = 96000;
					Buffer.SetSize(fs * 10);
					fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);
				}
                Console.WriteLine($"Recording can be found at: {recordingPath}");
				Thread processingThread = new Thread(() => this.engine.Execute($"Open_Loop_Swept_Sine_Processing {filename} {stimulusFilename}"));
                processingThread.SetApartmentState(ApartmentState.STA);
                processingThread.Start();

                if (!disablePlots)
                {
					fh.Run();
                }

            }
            catch (Exception)
            {
                Console.WriteLine("ERROR: Could not find input device.");
                engine.AbortTest();
            }
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }

        public void CreateOpenLoopStepSineTestStimulus(string stimulusFilename = "Open_Loop_Step_Sine_Test_Stimulus",
													   double silence = 1,
													   double level = 0.5,
													   int minCycles = 6,
													   double minDuration = 0.003,
													   int bitsDepth = 32,
													   int startFrequency = 20,
													   int endFrequency = 20000,
													   StepSineResolutionTypes resolutionType = StepSineResolutionTypes.R40,
													   int settlingPeriods = 5,
													   int stepIncrement = 1,
													   ScanningModeTypes stepMode = ScanningModeTypes.Linear,
													   int transitionPoints = 500,
													   double burstSineLevel = 0.5,
													   int burstSineFrequency = 1000,
													   int burstSineCycles = 1000,
													   int samplingFrequency = 48000)
        {
            var settings = this.engine.GetOpenLoopStepSineTestSettings();
            settings.ExternalDeviceStimulusBitsDepth = bitsDepth;
            settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency;
            settings.ExternalDeviceStimulusStepSineSettings.StartFrequency = startFrequency;
            settings.ExternalDeviceStimulusStepSineSettings.EndFrequency = endFrequency;
            settings.ExternalDeviceStimulusStepSineSettings.MinCycles = minCycles;
            settings.ExternalDeviceStimulusStepSineSettings.MinDuration = minDuration;
            settings.ExternalDeviceStimulusStepSineSettings.ResolutionType = resolutionType;
            settings.ExternalDeviceStimulusStepSineSettings.SettlingPeriods = settlingPeriods;
            settings.ExternalDeviceStimulusStepSineSettings.StepIncrement = stepIncrement;
            settings.ExternalDeviceStimulusStepSineSettings.StepMode = stepMode;
            settings.ExternalDeviceStimulusStepSineSettings.TransitionPoints = transitionPoints;
            settings.ExternalDeviceStimulusStepSineSettings.Level = level;
            settings.StimulusName = stimulusFilename;
            settings.Silence = silence;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Cycles = burstSineCycles;

            this.engine.SetOpenLoopStepSineTestSettings(settings);
            this.engine.Execute("Open_Loop_Step_Sine_Test StimulusOnly");
        }

        public TestResultsAvailableArgs? RunOpenLoopStepSineTest(int triggerChannel,
											double triggerLevel = 0.1,
											string filename = "Open_Loop_Step_Sine_Test",
											MeasurementModeTypes measurementMode = MeasurementModeTypes.Spectra,
											ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
                                            bool disablePlots = false)
        {
            var settings = this.engine.GetOpenLoopStepSineTestSettings();
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            settings.Filename = filename;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            this.engine.SetOpenLoopStepSineTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * 10);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
            }
                this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;

			Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Step_Sine_Test TestOnly"));
			backgroundThread.SetApartmentState(ApartmentState.STA);
			backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
            }
                this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;

            return Handlers.testResults;
        }
		public TestResultsAvailableArgs? RunCompleteOpenLoopStepSineTest(int triggerChannel,
											  double triggerLevel = 0.1,
											  double level = 0.5,
											  string stimulusFilename = "Open_Loop_Step_Sine_Test_Stimulus",
											  string filename = "Open_Loop_Step_Sine_Test",
											  MeasurementModeTypes measurementMode = MeasurementModeTypes.Spectra,
											  ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
											  double silence = 1,
											  int minCycles = 6,
											  double minDuration = 0.003,
											  int bitsDepth = 32,
											  int startFrequency = 20,
											  int endFrequency = 20000,
											  StepSineResolutionTypes resolutionType = StepSineResolutionTypes.R40,
											  int settlingPeriods = 5,
											  int stepIncrement = 1,
											  ScanningModeTypes stepMode = ScanningModeTypes.Linear,
											  int transitionPoints = 500,
											  double burstSineLevel = 0.5,
											  int burstSineFrequency = 1000,
											  int burstSineCycles = 1000,
											  int samplingFrequency = 48000,
                                              bool disablePlots = false)
		{
			var settings = this.engine.GetOpenLoopStepSineTestSettings();
			settings.ExternalDeviceStimulusBitsDepth = bitsDepth;
			settings.ExternalDeviceStimulusSamplingFrequency = samplingFrequency;
			settings.ExternalDeviceStimulusStepSineSettings.StartFrequency = startFrequency;
			settings.ExternalDeviceStimulusStepSineSettings.EndFrequency = endFrequency;
			settings.ExternalDeviceStimulusStepSineSettings.MinCycles = minCycles;
			settings.ExternalDeviceStimulusStepSineSettings.MinDuration = minDuration;
			settings.ExternalDeviceStimulusStepSineSettings.ResolutionType = resolutionType;
			settings.ExternalDeviceStimulusStepSineSettings.SettlingPeriods = settlingPeriods;
			settings.ExternalDeviceStimulusStepSineSettings.StepIncrement = stepIncrement;
			settings.ExternalDeviceStimulusStepSineSettings.StepMode = stepMode;
			settings.ExternalDeviceStimulusStepSineSettings.TransitionPoints = transitionPoints;
            settings.ExternalDeviceStimulusStepSineSettings.Level = level;
			settings.StimulusName = stimulusFilename;
			settings.Silence = silence;
			settings.BurstSineSettings.Frequency = burstSineFrequency;
			settings.BurstSineSettings.Level = burstSineLevel;
			settings.BurstSineSettings.Cycles = burstSineCycles;

			settings.TriggerChannel = triggerChannel;
			settings.TriggerLevel = triggerLevel;
			settings.Filename = filename;
			settings.MeasurementModeType = measurementMode;
			settings.ResultFileFormatType = resultFileFormat;
			this.engine.SetOpenLoopStepSineTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * 10);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated += Handlers.StimulusCreatedHandler;

			Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Step_Sine_Test Complete"));
			backgroundThread.SetApartmentState(ApartmentState.STA);
			backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated -= Handlers.StimulusCreatedHandler;

            return Handlers.testResults;
		}

        public TestResultsAvailableArgs? RunPlaybackOpenLoopStepSineTest(int outputChannel,
													string stimulusFilename = "Open_Loop_Step_Sine_Test_Stimulus",
													string filename = "Open_Loop_Step_Sine_Test",
													double silence = 1,
													int minCycles = 6,
													double minDuration = 0.003,
													int startFrequency = 20,
													int endFrequency = 20000,
													StepSineResolutionTypes resolutionType = StepSineResolutionTypes.R40,
													int settlingPeriods = 5,
													int stepIncrement = 1,
													ScanningModeTypes stepMode = ScanningModeTypes.Linear,
													int transitionPoints = 500,
													double burstSineLevel = 0.01,
													int burstSineFrequency = 1000,
													int burstSineCycles = 1000,
													MeasurementModeTypes measurementMode = MeasurementModeTypes.Spectra,
													ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
                                                    bool disablePlots = false)
        { 
			var settings = this.engine.GetOpenLoopStepSineTestSettings();
			settings.StimulusName = stimulusFilename;
            settings.Filename = filename;
			settings.Silence = silence;
			settings.BurstSineSettings.Frequency = burstSineFrequency;
			settings.BurstSineSettings.Level = burstSineLevel;
			settings.BurstSineSettings.Cycles = burstSineCycles;
			settings.MeasurementModeType = measurementMode;
			settings.ResultFileFormatType = resultFileFormat;
			this.engine.SetOpenLoopStepSineTestSettings(settings);

            this.engine.SetOutputChannelStepSineSettings(outputChannel,
                                                         startFrequency,
                                                         endFrequency,
                                                         resolutionType,
                                                         minCycles,
                                                         minDuration,
                                                         stepMode,
                                                         stepIncrement,
                                                         settlingPeriods,
                                                         transitionPoints);

            this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Step_Sine_Test Playback"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            var recordingPath = this.engine.GetEngineSettings().DataFolder + "\\" + filename + ".wav";
            var inputRecorder = new InputRecording(recordingPath);
            try
            {
				inputRecorder.StartRecording(48000);
                backgroundThread.Join();
                inputRecorder.StopRecording();
				FigureHandler? fh = null;
				if (!disablePlots)
				{
					int fs = 96000;
					Buffer.SetSize(fs * 10);
					fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);
				}
                Console.WriteLine($"Recording can be found at: {recordingPath}");
				Thread processingThread = new Thread(() => this.engine.Execute($"Open_Loop_Step_Sine_Processing {filename} {stimulusFilename}"));
                processingThread.SetApartmentState(ApartmentState.STA);
                processingThread.Start();

                if (!disablePlots)
                {
					fh.Run();
                }
            }
            catch (Exception)
            {
                Console.WriteLine("ERROR: Could not find input device.");
                engine.AbortTest();
            }
            this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;

            return Handlers.testResults;
        }


        public void CreateOpenLoopWaveformStreamingStimulus(string path,
															string stimulusFilename = "Open_Loop_Waveform_Streaming_Stimulus",
															double level = 0.5,
															int trackIndex = 1,
															int bitDepth = 32,
															int samplingRate = 48000,
															double burstSineLevel = 0.5,
															int burstSineFrequency = 1000,
															int burstSineCycles = 1000,
															double silence = 1)
        {
            var settings = this.engine.GetOpenLoopWaveformStreamingTestSettings();
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            settings.ExternalDeviceStimulusBitsDepth = bitDepth;
            settings.ExternalDeviceStimulusSamplingFrequency = samplingRate;
            settings.ExternalDeviceStimulusWaveformStreamingSettings.Level = level;
            settings.ExternalDeviceStimulusWaveformStreamingSettings.ChannelIndex = trackIndex;
            settings.ExternalDeviceStimulusWaveformStreamingSettings.Filename = path;
            settings.Silence = silence;
            settings.StimulusName = stimulusFilename;

            this.engine.SetOpenLoopWaveformStreamingTestSettings(settings);
            this.engine.Execute("Open_Loop_Waveform_Streaming_Test StimulusOnly");
        }

        public TestResultsAvailableArgs? RunOpenLoopWaveformStreamingTest(int triggerChannel,
													 double triggerLevel = 0.1,
													 string filename = "Open_Loop_Waveform_Streaming_Test",
													 MeasurementModeTypes measurementMode = MeasurementModeTypes.Spectra,
													 ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
                                                     bool disablePlots = false)
        {
            var settings = this.engine.GetOpenLoopWaveformStreamingTestSettings();
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            settings.Filename = filename;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            this.engine.SetOpenLoopWaveformStreamingTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * 10);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;

			Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Waveform_Streaming_Test RunOnly"));
			backgroundThread.SetApartmentState(ApartmentState.STA);
			backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated -= Handlers.StimulusCreatedHandler;

            return Handlers.testResults;
        }

		public TestResultsAvailableArgs? RunCompleteOpenLoopWaveformStreamingTest(string path,
													   int triggerChannel,
													   double triggerLevel = 0.1,
													   double level = 0.5,
													   string stimulusFilename = "Open_Loop_Waveform_Streaming_Stimulus",
													   string filename = "Open_Loop_Waveform_Streaming_Test",
													   MeasurementModeTypes measurementMode = MeasurementModeTypes.Spectra,
													   ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
													   int trackIndex = 1,
													   int bitDepth = 32,
													   int samplingRate = 48000,
													   double burstSineLevel = 0.5,
													   int burstSineFrequency = 1000,
													   int burstSineCycles = 1000,
													   double silence = 1,
                                                       bool disablePlots = false)
		{
			var settings = this.engine.GetOpenLoopWaveformStreamingTestSettings();
			settings.BurstSineSettings.Level = burstSineLevel;
			settings.BurstSineSettings.Frequency = burstSineFrequency;
			settings.BurstSineSettings.Cycles = burstSineCycles;
			settings.ExternalDeviceStimulusBitsDepth = bitDepth;
			settings.ExternalDeviceStimulusSamplingFrequency = samplingRate;
			settings.ExternalDeviceStimulusWaveformStreamingSettings.Level = level;
			settings.ExternalDeviceStimulusWaveformStreamingSettings.ChannelIndex = trackIndex;
			settings.ExternalDeviceStimulusWaveformStreamingSettings.Filename = path;
			settings.Silence = silence;
			settings.StimulusName = stimulusFilename;

			settings.TriggerChannel = triggerChannel;
			settings.TriggerLevel = triggerLevel;
			settings.Filename = filename;
			settings.MeasurementModeType = measurementMode;
			settings.ResultFileFormatType = resultFileFormat;
			this.engine.SetOpenLoopWaveformStreamingTestSettings(settings);

            FigureHandler? fh = null;
            if (!disablePlots)
            {
				int fs = 96000;
				Buffer.SetSize(fs * 10);
				fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);

				this.engine.TimeDataRecorded += Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable += Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated += Handlers.StimulusCreatedHandler;

			Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Waveform_Streaming_Test Complete"));
			backgroundThread.SetApartmentState(ApartmentState.STA);
			backgroundThread.Start();

            if (!disablePlots)
            {
				fh.Run();

				this.engine.TimeDataRecorded -= Handlers.TimeDataCallback;
            }
			this.engine.TestResultsAvailable -= Handlers.TestResultsReadyHandler;
			this.engine.StimulusCreated -= Handlers.StimulusCreatedHandler;

            return Handlers.testResults;
		}

        public TestResultsAvailableArgs? RunPlaybackOpenLoopWaveformStreamingTest(int outputChannel,
															 string path,
															 string stimulusFilename = "Open_Loop_Waveform_Streaming_Stimulus",
															 string filename = "Open_Loop_Waveform_Streaming_Test",
															 int trackIndex = 1,
															 double burstSineLevel = 0.01,
															 int burstSineFrequency = 1000,
															 int burstSineCycles = 1000,
															 double silence = 1,
															 MeasurementModeTypes measurementMode = MeasurementModeTypes.Spectra,
															 ResultFileFormatTypes resultFileFormat = ResultFileFormatTypes.CSV,
                                                             bool disablePlots = false)
        {
			var settings = this.engine.GetOpenLoopWaveformStreamingTestSettings();
			settings.BurstSineSettings.Level = burstSineLevel;
			settings.BurstSineSettings.Frequency = burstSineFrequency;
			settings.BurstSineSettings.Cycles = burstSineCycles;
			settings.Silence = silence;
			settings.StimulusName = stimulusFilename;
			settings.Filename = filename;
			settings.MeasurementModeType = measurementMode;
			settings.ResultFileFormatType = resultFileFormat;
			this.engine.SetOpenLoopWaveformStreamingTestSettings(settings);

            this.engine.SetOutputChannelWaveformStreamingSettings(outputChannel, path, trackIndex);

            this.engine.MultiSIMOFFTProcessingResultsUpdated += Handlers.FftProcessingUpdated;
            this.engine.TestResultsAvailable += Handlers.SaveResultsToVarHandler;

            Thread backgroundThread = new Thread(() => this.engine.Execute("Open_Loop_Waveform_Streaming_Test Playback"));
            backgroundThread.SetApartmentState(ApartmentState.STA);
            backgroundThread.Start();

            var recordingPath = this.engine.GetEngineSettings().DataFolder + "\\" + filename + ".wav";
            var inputRecorder = new InputRecording(recordingPath);
            try
            {
				inputRecorder.StartRecording(48000);
                backgroundThread.Join();
                inputRecorder.StopRecording();
				FigureHandler? fh = null;
				if (!disablePlots)
				{
					int fs = 96000;
					Buffer.SetSize(fs * 10);
					fh = new FigureHandler(sampleinterval: 0.1, timewindow: 1, size: 4096);
				}
                Console.WriteLine($"Recording can be found at: {recordingPath}");
				Thread processingThread = new Thread (() => this.engine.Execute($"Open_Loop_Waveform_Streaming_Processing {filename} {stimulusFilename}"));
                processingThread.SetApartmentState(ApartmentState.STA);
                processingThread.Start();

                if (!disablePlots)
                {
                    fh.Run();
                }

            }
            catch (Exception)
            {
                Console.WriteLine("ERROR: Could not find input device.");
                engine.AbortTest();
            }
            this.engine.MultiSIMOFFTProcessingResultsUpdated -= Handlers.FftProcessingUpdated;
            this.engine.TestResultsAvailable -= Handlers.SaveResultsToVarHandler;

            return Handlers.testResults;
        }

        


	}
}
