% Import HelpFunctions
%import HelpFunctions.*

classdef Engine < handle
    properties
        engine
    end
    
    methods
        function obj = Engine()
            import EA_Engine.*;
            EA = EA_Engine();
            obj.engine = EA.engine;
        end


        function resetEngine(obj)
            obj.engine.ResetSettings();
        end

        function select3670Device(obj)
            devices = obj.engine.GetDetectedASIODevices();

            for ii = 1:devices.Length
                device = devices(ii);
                if contains(char(device.Name), '3670')
                    obj.engine.SelectASIODevice(ii, false);
                    fprintf('Selected: %s\n', char(device.Name));
                    break;
                end
            end
        end
        
        function setInputChannel(obj, number, name, isActive, referenceChannelName, sensitivity, sensitivityUnit, dbRef)
            if nargin < 5, referenceChannelName = 'None'; end
            if nargin < 6, sensitivity = []; end
            if nargin < 7, sensitivityUnit = []; end
            if nargin < 8, dbRef = []; end
            
            channels = obj.engine.GetInputChannels(false);
            channels(number).Name = name;
            channels(number).IsActive = isActive;
            channels(number).ReferenceChannelName = referenceChannelName;

            if ~isempty(sensitivity)
                channels(number).Sensitivity = sensitivity;
            end
            if ~isempty(sensitivityUnit)
                channels(number).SensitivityUnit = sensitivityUnit;
            end
            if ~isempty(dbRef)
                channels(number).dBRef = dbRef;
            end

            obj.engine.SetInputChannels(channels);
        end
        
        function channels = getActiveInputChannels(obj)
            channels = obj.engine.GetInputChannels(true);
        end
        
        function setOutputChannel(obj, number, name, isActive, referenceChannelName, sensitivity, sensitivityUnit, dbRef, outputLevel)
            if nargin < 5, referenceChannelName = 'None'; end
            if nargin < 6, sensitivity = []; end
            if nargin < 7, sensitivityUnit = []; end
            if nargin < 8, dbRef = []; end
            if nargin < 9, outputLevel = 0.5; end

            channels = obj.engine.GetOutputChannels(false);
            channels(number).Name = name;
            channels(number).IsActive = isActive;
            channels(number).ReferenceChannelName = referenceChannelName;
            channels(number).VMax = outputLevel;

            if ~isempty(sensitivity)
                channels(number).Sensitivity = sensitivity;
            end
            if ~isempty(sensitivityUnit)
                channels(number).SensitivityUnit = sensitivityUnit;
            end
            if ~isempty(dbRef)
                channels(number).dBRef = dbRef;
            end
            
            obj.engine.SetOutputChannels(channels);
        end

        function setAllChannelsToFalse(obj)
            inputChannels = obj.engine.GetInputChannels(false);
            for i = 1:inputChannels.Length
                inputChannels(i).IsActive = false;
            end
            obj.engine.SetInputChannels(inputChannels);
            outputChannels = obj.engine.GetOutputChannels(false);
            for i = 1:outputChannels.Length
                outputChannels(i).IsActive = false;
            end
            obj.engine.SetOutputChannels(outputChannels);
        end
        
        function channels = getActiveOutputChannels(obj)
            channels = obj.engine.GetOutputChannels(true);
        end
        
        function runInputCalibration(obj, channelNumber, referenceFrequency, referenceLevel, duration, referenceUnit)
            if nargin < 3, referenceFrequency = 1000; end
            if nargin < 4, referenceLevel = 1; end
            if nargin < 5, duration = 10; end
            if nargin < 6, referenceUnit = 'Pa rms'; end
            
            activeInputChannels = arrayfun(@(x) x.Number, obj.getActiveInputChannels());
            if ~ismember(channelNumber, activeInputChannels)
                fprintf('Channel %d is not an active input channel\n', channelNumber);
                return;
            end
            
            calibrationSettings = obj.engine.GetInputCalibrationSettings();
            calibrationSettings.ReferenceFrequency = referenceFrequency;
            calibrationSettings.ReferenceLevel = referenceLevel;
            calibrationSettings.Duration = duration;
            calibrationSettings.ReferenceUnit = referenceUnit;
            
            obj.engine.SetInputCalibrationSettings(calibrationSettings);
            
            fprintf('Calibration frequency %d Hz\n', calibrationSettings.ReferenceFrequency);
            fprintf('Reference level %f %s\n', calibrationSettings.ReferenceLevel, calibrationSettings.ReferenceUnit);
            
            obj.engine.Execute(sprintf('Calibrate_Input_Channel %d', channelNumber));
        end
        
        function runOutputCalibration(obj, inputChannel, outputChannel, frequency, level, duration)
            if nargin < 4, frequency = 1000; end
            if nargin < 5, level = 0.01; end
            if nargin < 6, duration = 10; end
            
            activeInputChannels = arrayfun(@(x) x.Number, obj.getActiveInputChannels());
            if ~ismember(inputChannel, activeInputChannels)
                fprintf('Channel %d is not an active input channel\n', inputChannel);
                return;
            end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end
            
            calibrationSettings = obj.engine.GetOutputCalibrationSettings();
            calibrationSettings.Frequency = frequency;
            calibrationSettings.Level = level;
            calibrationSettings.Duration = duration;
            
            obj.engine.SetOutputCalibrationSettings(calibrationSettings);
            
            fprintf('Calibration frequency %d Hz\n', frequency);
            fprintf('Reference level %f EU rms\n', level);
            
            obj.engine.Execute(sprintf('Calibrate_Output_Channel %d %d', inputChannel, outputChannel));
        end

        function result = runOutputEqualization(obj, inputChannel, outputChannel, filterLength, frequencyStart, frequencyEnd, measureAndRemoveExtraLatency, referenceFrequency, resultFileFormat, scaleType, stimulusType, disablePlots)
            if nargin < 4, filterLength = 8193; end
            if nargin < 5, frequencyStart = 10; end
            if nargin < 6, frequencyEnd = 10000; end
            if nargin < 7, measureAndRemoveExtraLatency = true; end
            if nargin < 8, referenceFrequency = -1; end
            if nargin < 9, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 10, scaleType = EA_Engine.ScaleTypes.dB; end
            if nargin < 11, stimulusType = EA_Engine.GeneratorSignalTypes.Random; end
            if nargin < 12, disablePlots = false; end

            activeInputChannels = arrayfun(@(x) x.Number, obj.getActiveInputChannels());
            if ~ismember(inputChannel, activeInputChannels)
                fprintf('Channel %d is not an active input channel\n', inputChannel);
                return;
            end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end

            eqSettings = obj.engine.GetOutputEqualizationSettings();
            eqSettings.FilterLength = filterLength;
            eqSettings.FrequencyStart = frequencyStart;
            eqSettings.FrequencyEnd = frequencyEnd;
            eqSettings.MeasureAndRemoveExtraLatency = measureAndRemoveExtraLatency;
            eqSettings.ReferenceFrequency = referenceFrequency;
            eqSettings.ResultFileFormatType = resultFileFormat;
            eqSettings.ScaleType = scaleType;
            eqSettings.StimulusType = stimulusType;
            obj.engine.SetOutputEqualizationSettings(eqSettings);

            if ~disablePlots 
                fs = 96e3; % sampling frequency
                DataBuffer = Buffer(fs * 10);
                Handlers.initDataBuffer(DataBuffer);    
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
                saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            
            obj.engine.Execute(sprintf('Equalize_Output_Channel %d %d', inputChannel, outputChannel));

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(saveResultsToVarHandler);
            result = Handlers.StaticTestResults();
        end
        
        function result = runRandomTest(obj, outputChannel, duration, lowerFrequency, upperFrequency, slope, filename, measurementModeType, resultFileFormatType, disablePlots)
            if nargin < 3, duration = 10; end
            if nargin < 4, lowerFrequency = 80; end
            if nargin < 5, upperFrequency = 12000; end
            if nargin < 6, slope = 0; end
            if nargin < 7, filename = 'random_noise_test'; end
            if nargin < 8, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 9, resultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 10, disablePlots = false; end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end
            
            
            obj.engine.SetOutputChannelRandomSettings(outputChannel, true, lowerFrequency, upperFrequency, slope, duration);
            
            randomSettings = obj.engine.GetRandomNoiseTestSettings();
            randomSettings.Duration = duration;
            randomSettings.Filename = filename;
            randomSettings.MeasurementModeType = measurementModeType;
            randomSettings.ResultFileFormatType = resultFileFormatType;
            obj.engine.SetRandomNoiseTestSettings(randomSettings);
            
            if ~disablePlots 
                fs = 96e3; % sampling frequency
                DataBuffer = Buffer(fs * duration);
                Handlers.initDataBuffer(DataBuffer);    
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
                saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            
            obj.engine.Execute('Random_Noise_Test');

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(saveResultsToVarHandler);
            result = Handlers.StaticTestResults();
        end
        
        function result = runStepSineTest(obj, outputChannel, duration, startFrequency, endFrequency, resolutionType, minCycles, minDuration, stepMode, stepIncrement, settlingPeriods, transitionPoints, disablePlots)
            if nargin < 3, duration = 10; end
            if nargin < 4, startFrequency = 100; end
            if nargin < 5, endFrequency = 10e3; end
            if nargin < 6, resolutionType = EA_Engine.StepSineResolutionTypes.R80; end
            if nargin < 7, minCycles = 5; end
            if nargin < 8, minDuration = 0.1; end
            if nargin < 9, stepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 10, stepIncrement = 1; end
            if nargin < 11, settlingPeriods = 5; end
            if nargin < 12, transitionPoints = 100; end
            if nargin < 13, disablePlots = false; end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end
            
            
            obj.engine.SetOutputChannelStepSineSettings(outputChannel, startFrequency, endFrequency, resolutionType, minCycles, minDuration, stepMode, stepIncrement, settlingPeriods, transitionPoints);
            
            if ~disablePlots
                fs = 96e3; % sampling frequency
                DataBuffer = Buffer(fs * duration);
                Handlers.initDataBuffer(DataBuffer);
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                harmonicEstimatorProcessingResultsUpdatedHandler = addlistener(obj.engine, 'HarmonicEstimatorProcessingResultsUpdated', @Handlers.stepProcessingUpdated);
            end	
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            
            obj.engine.Execute('Step_Sine_Test');

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(harmonicEstimatorProcessingResultsUpdatedHandler);
            end	
            delete(saveResultsToVarHandler);
            result = Handlers.StaticTestResults();
        end
        
        function result = runSweptSineTest(obj, outputChannel, duration, startFrequency, endFrequency, scanningMode, repetition, silenceDuration, fademode, fadeinDuration, fadeoutDuration, disablePlots)
            if nargin < 3, duration = 10; end
            if nargin < 4, startFrequency = 100; end
            if nargin < 5, endFrequency = 10e3; end
            if nargin < 6, scanningMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 7, repetition = 1; end
            if nargin < 8, silenceDuration = 0; end
            if nargin < 9, fademode = EA_Engine.FadeTypes.Cosine; end
            if nargin < 10, fadeinDuration = 0.01; end
            if nargin < 11, fadeoutDuration = 0.01; end
            if nargin < 12, disablePlots = false; end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end
            
            
            obj.engine.SetOutputChannelSweptSineSettings(outputChannel, startFrequency, endFrequency, scanningMode, duration, repetition, silenceDuration, fademode, fadeinDuration, fadeoutDuration);
            
            sweptSineSettings = obj.engine.GetSweptSineTestSettings();
            sweptSineSettings.Duration = duration * (repetition + 1);
            sweptSineSettings.Filename = 'swept_sine_test';
            sweptSineSettings.MeasureAndRemoveExtraLatency = true;
            sweptSineSettings.ApplyEqualization = false;
            sweptSineSettings.MeasurementModeType = EA_Engine.MeasurementModeTypes.Spectra;
            sweptSineSettings.ResultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV;
            sweptSineSettings.Recording = false;
            obj.engine.SetSweptSineTestSettings(sweptSineSettings);
            
            if ~disablePlots
                fs = 96e3; % sampling frequency
                DataBuffer = Buffer(fs * duration * (repetition + 1));
                Handlers.initDataBuffer(DataBuffer);
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);

            obj.engine.Execute('Swept_Sine_Test');

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(saveResultsToVarHandler);
            
            result = Handlers.StaticTestResults();
        end
        
        function result = runFixedSineTest(obj, outputChannel, duration, frequency, disablePlots)
            if nargin < 3, duration = 10; end
            if nargin < 4, frequency = 1000; end
            if nargin < 5, disablePlots = false; end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end
            
            
            obj.engine.SetOutputChannelFixedSineSettings(outputChannel, frequency, duration);
            
            fixedSineSettings = obj.engine.GetFixedSineTestSettings();
            fixedSineSettings.Filename = 'fixed_sine_test';
            fixedSineSettings.SettlingTime = true;
            fixedSineSettings.MeasureAndRemoveExtraLatency = true;
            fixedSineSettings.ResultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV;
            fixedSineSettings.ApplyEqualization = false;
            fixedSineSettings.MeasurementModeType = EA_Engine.MeasurementModeTypes.Spectra;
            obj.engine.SetFixedSineTestSettings(fixedSineSettings);
            
            if ~disablePlots
                fs = 96e3; % sampling frequency
                DataBuffer = Buffer(fs * duration);
                Handlers.initDataBuffer(DataBuffer);

                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
            end
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            
            obj.engine.Execute('Fixed_Sine_Test');
            
            if ~disablePlots
                obj.fixedSineFFT();
                delete(timeDataRecordedHandler);
            end
            delete(saveResultsToVarHandler);
            
            result = Handlers.StaticTestResults();
        end
        
        function result = runWaveformStreamingTest(obj, outputChannel, wavPath, trackIndex, disablePlots)
            if nargin < 4, trackIndex = 1; end
            if nargin < 5, disablePlots = false; end
            
            activeOutputChannels = arrayfun(@(x) x.Number, obj.getActiveOutputChannels());
            if ~ismember(outputChannel, activeOutputChannels)
                fprintf('Channel %d is not an active output channel\n', outputChannel);
                return;
            end
            
            
            wavPath = fullfile(pwd, wavPath);
            if ~exist(wavPath, 'file')
                fprintf('File %s not found. Please execute the script within the MATLAB examples directory.\n', wavPath);
                return;
            end
            
            [y, fs] = audioread(wavPath);
            duration = numel(y) / fs;
            
            obj.engine.SetOutputChannelWaveformStreamingSettings(outputChannel, wavPath, trackIndex);
            
            waveformStreamingSettings = obj.engine.GetWaveformStreamingTestSettings();
            waveformStreamingSettings.Filename = 'waveform_streaming_test';
            waveformStreamingSettings.MeasureAndRemoveExtraLatency = true;
            waveformStreamingSettings.ResultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV;
            waveformStreamingSettings.ApplyEqualization = false;
            waveformStreamingSettings.MeasurementModeType = EA_Engine.MeasurementModeTypes.Spectra;
            waveformStreamingSettings.Recording = false;
            obj.engine.SetWaveformStreamingTestSettings(waveformStreamingSettings);
            
            if ~disablePlots
                DataBuffer = Buffer(fs * duration);
                Handlers.initDataBuffer(DataBuffer);
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            
            obj.engine.Execute('Waveform_Streaming_Test');

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(saveResultsToVarHandler);
            
            result = Handlers.StaticTestResults();
        end
        
        function selectWdmInputDevice(obj, deviceName, isActive)
            devices = obj.engine.GetDetectedWDMInputDevices();
            for i = 1:devices.Length
                fprintf('%d: %s\n', devices(i).Index, devices(i).Name);
                if strcmp(string(devices(i).Name), deviceName)
                    fprintf('Device %d: %s found\n', devices(i).Index, deviceName);
                    obj.engine.Execute(sprintf('Select_WDM_Input_Device %d', devices(i).Index));
                    obj.engine.SelectWDMInputDevice(devices(i).Index);
                    % may be an issue if more inputs gets added
                    obj.setInputChannel(9, sprintf('%s Microphone', deviceName), isActive);
                    return;
                end
            end
            fprintf('Device %s not found\n', deviceName);
        end
        
        function selectWdmOutputDevice(obj, deviceName, isActive)
            devices = obj.engine.GetDetectedWDMOutputDevices();
            for i = 1:devices.Length
                fprintf('%d: %s\n', devices(i).Index, devices(i).Name);
                if strcmp(string(devices(i).Name), deviceName)
                    fprintf('Device %d: %s found\n', devices(i).Index, deviceName);
                    obj.engine.SelectWDMOutputDevice(devices(i).Index);
                    obj.engine.Execute(sprintf('Select_WDM_Output_Device %d', devices(i).Index));
                    % may be an issue if more output gets added
                    obj.setOutputChannel(3, sprintf('%s Left', deviceName), isActive);
                    obj.setOutputChannel(4, sprintf('%s Right', deviceName), isActive);
                    return;
                end
            end
            fprintf('Device %s not found\n', deviceName);
        end

        function deselectWdmInputDevice(obj)
            obj.engine.DeselectWDMInputDevice();
        end

        function deselectWdmOutputDevice(obj)
            obj.engine.DeselectWDMOutputDevice();
        end

        function AdjustWdmInputVolume(obj, volume)
            status = obj.engine.AdjustWDMInputDeviceVolume(volume);
            if strcmp(string(status), 'OK')
                fprintf('Input volume: %f\n', volume);
            else
                fprintf('ERROR: %s\n', status);
            end
        end

        function AdjustWdmOutputVolume(obj, volume)
            status = obj.engine.AdjustWDMOutputDeviceVolume(volume);
            if strcmp(string(status), 'OK')
                fprintf('Output volume: %f\n', volume);
            else
                fprintf('ERROR: %s\n', status);
            end
        end

        function createOpenLoopRandomNoiseStimulus(obj, silence, duration, stimulusFilename, level, lowerFrequency, upperFrequency, slope, burstSineLevel, burstSineFrequency, burstSineCycles)
            if nargin < 2, silence = 1; end
            if nargin < 3, duration = 10; end
            if nargin < 4, stimulusFilename = 'Open_Loop_Random_Noise_Test_Stimulus'; end
            if nargin < 5, level = 0.5; end
            if nargin < 6, lowerFrequency = 20; end
            if nargin < 7, upperFrequency = 20000; end
            if nargin < 8, slope = 0; end
            if nargin < 9, burstSineLevel = 0.5; end
            if nargin < 10, burstSineFrequency = 1000; end
            if nargin < 11, burstSineCycles = 1000; end
            
            settings = obj.engine.GetOpenLoopRandomNoiseTestSettings();
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
            obj.engine.SetOpenLoopRandomNoiseTestSettings(settings);
            obj.engine.Execute('Open_Loop_Random_Noise_Test StimulusOnly');
        end

        function result = runOpenLoopRandomNoiseTest(obj, triggerChannel, triggerLevel, measurementModeType, resultFileFormatType, filename, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 5, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 6, resultFileFormatType = EA_Engine.MeasurementModeTypes.CSV; end
            if nargin < 7, filename = 'open_loop_random_noise_test'; end
            if nargin < 8, disablePlots = false; end
            
            settings = obj.engine.GetOpenLoopRandomNoiseTestSettings();
            settings.Filename = filename;
            settings.MeasurementModeType = measurementModeType;
            settings.ResultFileFormatType = resultFileFormatType;
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            obj.engine.SetOpenLoopRandomNoiseTestSettings(settings);

            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);

            obj.engine.Execute('Open_Loop_Random_Noise_Test TestOnly');

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(saveResultsToVarHandler);

            result = Handlers.StaticTestResults();

        end

        function result = runCompleteOpenLoopRandomNoiseTest(obj, triggerChannel, triggerLevel, stimulusFilename, duration, level, measurementModeType, resultFileFormatTypes, filename, silence, lowerFrequency, upperFrequency, slope, burstSineLevel, burstSineFrequency, burstSineCycles, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 4, stimulusFilename = 'Open_Loop_Random_Noise_Test_Stimulus'; end
            if nargin < 5, duration = 10; end
            if nargin < 6, level = 0.5; end
            if nargin < 7, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 8, resultFileFormatTypes = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 9, filename = 'open_loop_random_noise_test'; end
            if nargin < 10, silence = 1; end
            if nargin < 11, lowerFrequency = 20; end
            if nargin < 12, upperFrequency = 20000; end
            if nargin < 13, slope = 0; end
            if nargin < 14, burstSineLevel = 0.5; end
            if nargin < 15, burstSineFrequency = 1000; end
            if nargin < 16, burstSineCycles = 1000; end
            if nargin < 17, disablePlots = false; end

            settings = obj.engine.GetOpenLoopRandomNoiseTestSettings();
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
            obj.engine.SetOpenLoopRandomNoiseTestSettings(settings);


            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
            
            % TODO HANDLER DOESNT GET CALLED
            stimulusCreatedHandler = addlistener(obj.engine, 'StimulusCreated', @Handlers.stimulusCreatedHandler);
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);

            obj.engine.Execute('Open_Loop_Random_Noise_Test Complete');

            if ~disablePlots
                delete(timeDataRecordedHandler);
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(stimulusCreatedHandler);
            delete(saveResultsToVarHandler);

            result = Handlers.StaticTestResults();
        end

        function result = runPlaybackOpenLoopRandomNoiseTest(obj, outputChannel, stimulusFilename, duration, measurementModeType, resultFileFormatTypes, filename, silence, lowerFrequency, upperFrequency, slope, burstSineLevel, burstSineFrequency, burstSineCycles, disablePlots)
            if nargin < 3, stimulusFilename = 'Open_Loop_Random_Noise_Test_Stimulus'; end
            if nargin < 4, duration = 10; end
            if nargin < 5, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 6, resultFileFormatTypes = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 7, filename = 'open_loop_random_noise_test'; end
            if nargin < 8, silence = 1; end
            if nargin < 9, lowerFrequency = 20; end
            if nargin < 10, upperFrequency = 20000; end
            if nargin < 11, slope = 0; end
            if nargin < 12, burstSineLevel = 0.01; end
            if nargin < 13, burstSineFrequency = 1000; end
            if nargin < 14, burstSineCycles = 1000; end
            if nargin < 15, disablePlots = false; end

            settings = obj.engine.GetOpenLoopRandomNoiseTestSettings();
            settings.MeasurementModeType = measurementModeType;
            settings.ResultFileFormatType = resultFileFormatTypes;
            settings.StimulusName = stimulusFilename;
            settings.Silence = silence;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            obj.engine.SetOpenLoopRandomNoiseTestSettings(settings);

            obj.engine.SetOutputChannelRandomSettings(outputChannel, true, lowerFrequency, upperFrequency, slope, duration);

            
            if ~disablePlots
                multiSIMOFFTProcessingResultsUpdatedHandler = addlistener(obj.engine, 'MultiSIMOFFTProcessingResultsUpdated', @Handlers.fftprocessingUpdated);
            end
            saveResultsToVarHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            recordingPath = fullfile(string(obj.engine.GetEngineSettings().DataFolder), strcat(filename, '.wav'));
            inputRecorder = InputRecorder(recordingPath);
            inputRecorder.startRecording();

            obj.engine.Execute('Open_Loop_Random_Noise_Test Playback');
            inputRecorder.stopRecording();
            fprintf('Recording can be found at: %s\n', recordingPath);
            obj.engine.Execute(sprintf('Open_Loop_Random_Noise_Processing %s %s', filename, stimulusFilename));
        
            if ~disablePlots
                delete(multiSIMOFFTProcessingResultsUpdatedHandler);
            end
            delete(saveResultsToVarHandler);

            result = Handlers.StaticTestResults();
        end

        function createOpenSweptSineTestStimulus(obj, silence, sweepTime, stimulusFileName, level, bitsDepth, startFrequency, endFrequency, fadeIn, fadeType, fadeOut, repetitions, repetitionSilence, sweepMode, burstSineLevel, burstSineFrequency, burstSineCycles, samplingFrequency)
            if nargin < 2, silence = 1; end
            if nargin < 3, sweepTime = 10; end
            if nargin < 4, stimulusFileName = 'Open_Loop_Swept_Sine_Test_Stimulus'; end
            if nargin < 5, level = 0.5; end
            if nargin < 6, bitsDepth = 32; end
            if nargin < 7, startFrequency = 20; end
            if nargin < 8, endFrequency = 20000; end
            if nargin < 9, fadeIn = 0; end
            if nargin < 10, fadeType = EA_Engine.FadeTypes.Linear; end
            if nargin < 11, fadeOut = 0; end
            if nargin < 12, repetitions = 1; end
            if nargin < 13, repetitionSilence = 1; end
            if nargin < 14, sweepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 15, burstSineLevel = 0.5; end
            if nargin < 16, burstSineFrequency = 1000; end
            if nargin < 17, burstSineCycles = 1000; end
            if nargin < 18, samplingFrequency = 48000; end

            settings = obj.engine.GetOpenLoopSweptSineTestSettings();
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
            obj.engine.SetOpenLoopSweptSineTestSettings(settings);
            obj.engine.Execute('Open_Loop_Swept_Sine_Test StimulusOnly');
        end

        function result = runOpenLoopSweptSineTest(obj, triggerChannel, triggerLevel, duration, saveImpulseResponses, impulseResponseLength, measurementModeType, resultFileFormatType, filename, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 4, duration = 10; end
            if nargin < 5, saveImpulseResponses = false; end
            if nargin < 6, impulseResponseLength = 4096; end
            if nargin < 7, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 8, resultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 9, filename = 'open_loop_random_noise_test'; end
            if nargin < 10, disablePlots = false; end

            settings = obj.engine.GetOpenLoopSweptSineTestSettings();
            settings.Filename = filename;
            settings.MeasurementModeType = measurementModeType;
            settings.SaveImpulseResponses = saveImpulseResponses;
            settings.ImpulseResponseLength = impulseResponseLength;
            settings.ResultFileFormatType = resultFileFormatType;
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            obj.engine.SetOpenLoopSweptSineTestSettings(settings);

            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end

            obj.engine.Execute('Open_Loop_Swept_Sine_Test TestOnly');

            if ~disablePlots
                delete(timeDataRecordedHandler);
            end
            delete(testResultsReadyHandler);

            result = Handlers.StaticTestResults();
        end

        function result = runCompleteOpenLoopSweptSineTest(obj, triggerChannel, triggerLevel, stimulusFilename, level, duration, saveImpulseResponses, impulseResponseLength, measurementModeType, resultFileFormatType, filename, samplingFrequency, silence, sweepTime, bitsDepth, startFrequency, endFrequency, fadeIn, fadeType, fadeOut, repetitions, repetitionSilence, sweepMode, burstSineLevel, burstSineFrequency, burstSineCycles, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 4, stimulusFilename = 'Open_Loop_Swept_Sine_Test_Stimulus'; end
            if nargin < 5, level = 0.5; end
            if nargin < 6, duration = 10; end
            if nargin < 7, saveImpulseResponses = false; end
            if nargin < 8, impulseResponseLength = 4096; end
            if nargin < 9, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 10, resultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 11, filename = 'open_loop_swept_sine_test'; end
            if nargin < 12, samplingFrequency = 48000; end
            if nargin < 13, silence = 1; end
            if nargin < 14, sweepTime = 10; end
            if nargin < 15, bitsDepth = 32; end
            if nargin < 16, startFrequency = 20; end
            if nargin < 17, endFrequency = 20000; end
            if nargin < 18, fadeIn = 0; end
            if nargin < 19, fadeType = EA_Engine.FadeTypes.Linear; end
            if nargin < 20, fadeOut = 0; end
            if nargin < 21, repetitions = 1; end
            if nargin < 22, repetitionSilence = 1; end
            if nargin < 23, sweepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 24, burstSineLevel = 0.5; end
            if nargin < 25, burstSineFrequency = 1000; end
            if nargin < 26, burstSineCycles = 1000; end
            if nargin < 27, disablePlots = false; end

            settings = obj.engine.GetOpenLoopSweptSineTestSettings();
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
            obj.engine.SetOpenLoopSweptSineTestSettings(settings);

            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end
            stimulusCreatedHandler = addlistener(obj.engine, 'StimulusCreated', @Handlers.stimulusCreatedHandler);

            obj.engine.Execute('Open_Loop_Swept_Sine_Test Complete');

            if ~disablePlots
                delete(timeDataRecordedHandler);
            end
            delete(testResultsReadyHandler);
            delete(stimulusCreatedHandler);

            result = Handlers.StaticTestResults();

        end

        function result = runPlaybackOpenLoopSweptSineTest(obj, outputChannel, stimulusFilename, filename, silence, sweepTime, startFrequency, endFrequency, fadeIn, fadeType, fadeOut, repetitions, repetitionSilence, sweepMode, burstSineLevel, burstSineFrequency, burstSineCycles, saveImpulseResponses, impulseResponseLength, measurementModeType, resultFileFormatType, disablePlots)
            if nargin < 3, stimulusFilename = 'Open_Loop_Swept_Sine_Test_Stimulus'; end
            if nargin < 4, filename = 'Open_Loop_Swept_Sine_Test'; end
            if nargin < 5, silence = 1; end
            if nargin < 6, sweepTime = 10; end
            if nargin < 7, startFrequency = 20; end
            if nargin < 8, endFrequency = 20000; end
            if nargin < 9, fadeIn = 0; end
            if nargin < 10, fadeType = EA_Engine.FadeTypes.Linear; end
            if nargin < 11, fadeOut = 0; end
            if nargin < 12, repetitions = 1; end
            if nargin < 13, repetitionSilence = 1; end
            if nargin < 14, sweepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 15, burstSineLevel = 0.01; end
            if nargin < 16, burstSineFrequency = 1000; end
            if nargin < 17, burstSineCycles = 1000; end
            if nargin < 18, saveImpulseResponses = false; end
            if nargin < 19, impulseResponseLength = 4096; end
            if nargin < 20, measurementModeType = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 21, resultFileFormatType = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 22, disablePlots = false; end

            settings = obj.engine.GetOpenLoopSweptSineTestSettings();
            settings.MeasurementModeType = measurementModeType;
            settings.SaveImpulseResponses = saveImpulseResponses;
            settings.ImpulseResponseLength = impulseResponseLength;
            settings.ResultFileFormatType = resultFileFormatType;
            settings.StimulusName = stimulusFilename;
            settings.Silence = silence;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            obj.engine.SetOpenLoopSweptSineTestSettings(settings);

            obj.engine.SetOutputChannelSweptSineSettings(outputChannel, startFrequency, endFrequency, sweepMode, sweepTime, repetitions, repetitionSilence, fadeType, fadeIn, fadeOut);

            if ~disablePlots
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end

            recordingPath = fullfile(string(obj.engine.GetEngineSettings().DataFolder), strcat(filename, '.wav'));
            inputRecorder = InputRecorder(recordingPath);
            inputRecorder.startRecording();
            obj.engine.Execute('Open_Loop_Swept_Sine_Test Playback')
            inputRecorder.stopRecording();
            fprintf('Recording can be found at: %s\n', recordingPath);
            obj.engine.Execute(sprintf('Open_Loop_Swept_Sine_Processing %s %s', filename, stimulusFilename));

            delete(testResultsReadyHandler);

            result = Handlers.StaticTestResults();
        end

        function createOpenLoopStepSineTestStimulus(obj, stimulusFilename, silence, level, minCycles, minDuration, bitsDepth, startFrequency, endFrequency, resolutionType, settlingPeriods, stepIncrement, stepMode, transitionPoints, burstSineLevel, burstSineFrequency, burstSineCycles, samplingFrequency)
            if nargin < 2, stimulusFilename = 'Open_Loop_Step_Sine_Test_Stimulus'; end
            if nargin < 3, silence = 1; end
            if nargin < 4, level = 0.5; end
            if nargin < 5, minCycles = 6; end
            if nargin < 6, minDuration = 0.003; end
            if nargin < 7, bitsDepth = 32; end
            if nargin < 8, startFrequency = 20; end
            if nargin < 9, endFrequency = 20000; end
            if nargin < 10, resolutionType = EA_Engine.StepSineResolutionTypes.R40; end
            if nargin < 11, settlingPeriods = 5; end
            if nargin < 12, stepIncrement = 1; end
            if nargin < 13, stepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 14, transitionPoints = 500; end
            if nargin < 15, burstSineLevel = 0.5; end
            if nargin < 16, burstSineFrequency = 1000; end
            if nargin < 17, burstSineCycles = 1000; end
            if nargin < 18, samplingFrequency = 48000; end

            settings = obj.engine.GetOpenLoopStepSineTestSettings();
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

            obj.engine.SetOpenLoopStepSineTestSettings(settings);
            obj.engine.Execute('Open_Loop_Step_Sine_Test StimulusOnly');
        end

        function result = runOpenLoopStepSineTest(obj, triggerChannel, triggerLevel, filename, measurementMode, resultFileFormat, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 4, filename = 'Open_Loop_Step_Sine_Test'; end
            if nargin < 5, measurementMode = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 6, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 7, disablePlots = false; end

            settings = obj.engine.GetOpenLoopStepSineTestSettings();
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            settings.Filename = filename;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            obj.engine.SetOpenLoopStepSineTestSettings(settings);


            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end

            obj.engine.Execute('Open_Loop_Step_Sine_Test TestOnly');

            if ~disablePlots
                delete(timeDataRecordedHandler);
            end
            delete(testResultsReadyHandler);

            result = Handlers.StaticTestResults();
        end

        function result = runCompleteOpenLoopStepSineTest(obj, triggerChannel, triggerLevel, level, stimulusFilename, filename, measurementMode, resultFileFormat, silence, minCycles, minDuration, bitsDepth, startFrequency, endFrequency, resolutionType, settlingPeriods, stepIncrement, stepMode, transitionPoints, burstSineLevel, burstSineFrequency, burstSineCycles, samplingFrequency, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 4, level = 0.5; end
            if nargin < 5, stimulusFilename = 'Open_Loop_Step_Sine_Test_Stimulus'; end
            if nargin < 6, filename = 'Open_Loop_Step_Sine_Test'; end
            if nargin < 7, measurementMode = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 8, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 9, silence = 1; end
            if nargin < 10, minCycles = 6; end
            if nargin < 11, minDuration = 0.003; end
            if nargin < 12, bitsDepth = 32; end
            if nargin < 13, startFrequency = 20; end
            if nargin < 14, endFrequency = 20000; end
            if nargin < 15, resolutionType = EA_Engine.StepSineResolutionTypes.R40; end
            if nargin < 16, settlingPeriods = 5; end
            if nargin < 17, stepIncrement = 1; end
            if nargin < 18, stepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 19, transitionPoints = 500; end
            if nargin < 20, burstSineLevel = 0.5; end
            if nargin < 21, burstSineFrequency = 1000; end
            if nargin < 22, burstSineCycles = 1000; end
            if nargin < 23, samplingFrequency = 48000; end
            if nargin < 24, disablePlots = false; end

            settings = obj.engine.GetOpenLoopStepSineTestSettings();
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
            obj.engine.SetOpenLoopStepSineTestSettings(settings);

            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end
            stimulusCreatedHandler = addlistener(obj.engine, 'StimulusCreated', @Handlers.stimulusCreatedHandler);

            obj.engine.Execute('Open_Loop_Step_Sine_Test Complete');

            if ~disablePlots
                delete(timeDataRecordedHandler);
            end
            delete(testResultsReadyHandler);
            delete(stimulusCreatedHandler);

            result = Handlers.StaticTestResults();
        end

        function result = runPlaybackOpenLoopStepSineTest(obj, outputChannel, stimulusFilename, filename, silence, minCycles, minDuration, startFrequency, endFrequency, resolutionType, settlingPeriods, stepIncrement, stepMode, transitionPoints, burstSineLevel, burstSineFrequency, burstSineCycles, measurementMode, resultFileFormat, disablePlots)
            if nargin < 3, stimulusFilename = 'Open_Loop_Step_Sine_Test_Stimulus'; end
            if nargin < 4, filename = 'Open_Loop_Step_Sine_Test'; end
            if nargin < 5, silence = 1; end
            if nargin < 6, minCycles = 6; end
            if nargin < 7, minDuration = 0.003; end
            if nargin < 8, startFrequency = 20; end
            if nargin < 9, endFrequency = 20000; end
            if nargin < 10, resolutionType = EA_Engine.StepSineResolutionTypes.R40; end
            if nargin < 11, settlingPeriods = 5; end
            if nargin < 12, stepIncrement = 1; end
            if nargin < 13, stepMode = EA_Engine.ScanningModeTypes.Linear; end
            if nargin < 14, transitionPoints = 500; end
            if nargin < 15, burstSineLevel = 0.01; end
            if nargin < 16, burstSineFrequency = 1000; end
            if nargin < 17, burstSineCycles = 1000; end
            if nargin < 18, measurementMode = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 19, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 20, disablePlots = false; end

            settings = obj.engine.GetOpenLoopStepSineTestSettings();
            settings.StimulusName = stimulusFilename;
            settings.Filename = filename;
            settings.Silence = silence;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            obj.engine.SetOpenLoopStepSineTestSettings(settings);

            obj.engine.SetOutputChannelStepSineSettings(outputChannel, startFrequency, endFrequency, resolutionType, minCycles, minDuration, stepMode, stepIncrement, settlingPeriods, transitionPoints);

            if ~disablePlots
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end

            recordingPath = fullfile(string(obj.engine.GetEngineSettings().DataFolder), strcat(filename, '.wav'));
            inputRecorder = InputRecorder(recordingPath);
            inputRecorder.startRecording();

            obj.engine.Execute('Open_Loop_Step_Sine_Test Playback');

            inputRecorder.stopRecording();
            fprintf('Recording can be found at: %s\n', recordingPath);
            obj.engine.Execute(sprintf('Open_Loop_Step_Sine_Processing %s %s', filename, stimulusFilename));

            delete(testResultsReadyHandler);
            result = Handlers.StaticTestResults();
        end

        function createOpenLoopWaveformStreamingStimulus(obj, path, stimulusFilename, level, trackIndex, bitDepth, samplingRate, burstSineLevel, burstSineFrequency, burstSineCycles, silence)
            if nargin < 3, stimulusFilename = 'Open_Loop_Waveform_Streaming_Stimulus'; end
            if nargin < 4, level = 0.5; end
            if nargin < 5, trackIndex = 1; end
            if nargin < 6, bitDepth = 32; end
            if nargin < 7, samplingRate = 48000; end
            if nargin < 8, burstSineLevel = 0.5; end
            if nargin < 9, burstSineFrequency = 1000; end
            if nargin < 10, burstSineCycles = 1000; end
            if nargin < 11, silence = 1; end

            settings = obj.engine.GetOpenLoopWaveformStreamingTestSettings();
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

            obj.engine.SetOpenLoopWaveformStreamingTestSettings(settings);
            obj.engine.Execute('Open_Loop_Waveform_Streaming_Test StimulusOnly');
        end

        function result = runOpenLoopWaveformStreamingTest(obj, triggerChannel, triggerLevel, filename, measurementMode, resultFileFormat, disablePlots)
            if nargin < 3, triggerLevel = 0.1; end
            if nargin < 4, filename = 'Open_Loop_Waveform_Streaming_Test'; end
            if nargin < 5, measurementMode = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 6, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end

            settings = obj.engine.GetOpenLoopWaveformStreamingTestSettings();
            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            settings.Filename = filename;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            obj.engine.SetOpenLoopWaveformStreamingTestSettings(settings);


            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end	

            obj.engine.Execute('Open_Loop_Waveform_Streaming_Test RunOnly');

            if ~disablePlots
                delete(timeDataRecordedHandler);
            end
            delete(testResultsReadyHandler);

            result = Handlers.StaticTestResults();
        end

        function result = runCompleteOpenLoopWaveformStreamingTest(obj, path, triggerChannel, triggerLevel, level, stimulusFilename, filename, measurementMode, resultFileFormat, trackIndex, bitDepth, samplingRate, burstSineLevel, burstSineFrequency, burstSineCycles, silence, disablePlots)
            if nargin < 4, triggerLevel = 0.1; end
            if nargin < 5, level = 0.3; end
            if nargin < 6, stimulusFilename = 'Open_Loop_Waveform_Streaming_Stimulus'; end
            if nargin < 7, filename = 'Open_Loop_Waveform_Streaming_Test'; end
            if nargin < 8, measurementMode = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 9, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 10, trackIndex = 1; end
            if nargin < 11, bitDepth = 32; end
            if nargin < 12, samplingRate = 48000; end
            if nargin < 13, burstSineLevel = 0.5; end
            if nargin < 14, burstSineFrequency = 1000; end
            if nargin < 15, burstSineCycles = 1000; end
            if nargin < 16, silence = 1; end
            if nargin < 17, disablePlots = false; end

            settings = obj.engine.GetOpenLoopWaveformStreamingTestSettings();
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            settings.ExternalDeviceStimulusBitsDepth = bitDepth;
            settings.ExternalDeviceStimulusSamplingFrequency = samplingRate;
            settings.ExternalDeviceStimulusWaveformStreamingSettings.Level = level;
            settings.ExternalDeviceStimulusWaveformStreamingSettings.ChannelIndex = trackIndex;
            path = fullfile(pwd, path);
            settings.ExternalDeviceStimulusWaveformStreamingSettings.Filename = path;
            settings.Silence = silence;
            settings.StimulusName = stimulusFilename;

            settings.TriggerChannel = triggerChannel;
            settings.TriggerLevel = triggerLevel;
            settings.Filename = filename;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            obj.engine.SetOpenLoopWaveformStreamingTestSettings(settings);


            if ~disablePlots
                timeDataRecordedHandler = addlistener(obj.engine, 'TimeDataRecorded', @Handlers.time_data_callback);
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end
            stimulusCreatedHandler = addlistener(obj.engine, 'StimulusCreated', @Handlers.stimulusCreatedHandler);

            obj.engine.Execute('Open_Loop_Waveform_Streaming_Test Complete');

            if ~disablePlots
                delete(timeDataRecordedHandler);
            end
            delete(testResultsReadyHandler);
            delete(stimulusCreatedHandler);

            result = Handlers.StaticTestResults();
        end

        function result = runPlaybackOpenLoopWaveformStreamingTest(obj, outputChannel, path, stimulusFilename, filename, trackIndex, burstSineLevel, burstSineFrequency, burstSineCycles, silence, measurementMode, resultFileFormat, disablePlots)
            if nargin < 4, stimulusFilename = 'Open_Loop_Waveform_Streaming_Stimulus'; end
            if nargin < 5, filename = 'Open_Loop_Waveform_Streaming_Test'; end
            if nargin < 6, trackIndex = 1; end
            if nargin < 7, burstSineLevel = 0.01; end
            if nargin < 8, burstSineFrequency = 1000; end
            if nargin < 9, burstSineCycles = 1000; end
            if nargin < 10, silence = 1; end
            if nargin < 11, measurementMode = EA_Engine.MeasurementModeTypes.Spectra; end
            if nargin < 12, resultFileFormat = EA_Engine.ResultFileFormatTypes.CSV; end
            if nargin < 13, disablePlots = false; end

            settings = obj.engine.GetOpenLoopWaveformStreamingTestSettings();
            settings.BurstSineSettings.Level = burstSineLevel;
            settings.BurstSineSettings.Frequency = burstSineFrequency;
            settings.BurstSineSettings.Cycles = burstSineCycles;
            settings.Silence = silence;
            settings.StimulusName = stimulusFilename;
            settings.Filename = filename;
            settings.MeasurementModeType = measurementMode;
            settings.ResultFileFormatType = resultFileFormat;
            obj.engine.SetOpenLoopWaveformStreamingTestSettings(settings);

            obj.engine.SetOutputChannelWaveformStreamingSettings(outputChannel, path, trackIndex);


            if ~disablePlots
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.testResultsReadyHandler);
            else
                testResultsReadyHandler = addlistener(obj.engine, 'TestResultsAvailable', @Handlers.saveResultsToVarHandler);
            end

            recordingPath = fullfile(string(obj.engine.GetEngineSettings().DataFolder), strcat(filename, '.wav'));
            inputRecorder = InputRecorder(recordingPath);
            inputRecorder.startRecording();

            obj.engine.Execute('Open_Loop_Waveform_Streaming_Test Playback');

            inputRecorder.stopRecording();
            fprintf('Recording can be found at: %s\n', recordingPath);
            obj.engine.Execute(sprintf('Open_Loop_Waveform_Streaming_Processing %s %s', filename, stimulusFilename));

            delete(testResultsReadyHandler);

            result = Handlers.StaticTestResults();
        end
    end
    methods(Access = private)
        function fixedSineFFT(obj)
            global DataBuffer;
            x = DataBuffer.get();
            fs = 96e3; % Sampling frequency (96 kHz)
            L = length(x); % Length of signal

            % Perform FFT
            Y = fft(x);

            % Calculate the two-sided spectrum P2. Then compute the single-sided spectrum P1.
            P2 = abs(Y/L);
            P1 = P2(1:L/2+1);
            P1(2:end-1) = 2*P1(2:end-1);

            % Define the frequency domain f
            f = fs*(0:(L/2))/L;

            % Plot single-sided amplitude spectrum
            figure;
            semilogx(f, P1);
            title('Spectrum of test');
        end
    end
end






