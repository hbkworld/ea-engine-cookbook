classdef Handlers
    properties(Constant)
        EA = EA_Engine();
        engine = Handlers.EA.engine;
    end
    methods (Static)
        % static variables
        function timestamp = StaticTimestamp(newTimestamp)
            persistent currentTimestamp
            if nargin
                currentTimestamp = newTimestamp;
            end
            if isempty(currentTimestamp)
                currentTimestamp = 0;
            end
            timestamp = currentTimestamp;
        end
        function curves = StaticCurves(newCurves)
            persistent currentCurves
            if nargin
                currentCurves = newCurves;
            end
            if isempty(currentCurves)
                currentCurves = cell(1, 10);
            end
            curves = currentCurves;
        end
        function databuffer = StaticDataBuffer(newDataBuffer)
            persistent currentDataBuffer
            if nargin
                currentDataBuffer = newDataBuffer;
            end
            if isempty(currentDataBuffer)
                fs = 96e3;
                duration = 10;
                currentDataBuffer = Buffer(fs * duration);
            end
            databuffer = currentDataBuffer;
        end
        function channelInfo = StaticChannelInfo(newChannelInfo)
            persistent currentChannelInfo
            if nargin
                currentChannelInfo = newChannelInfo;
            end
            if isempty(currentChannelInfo)
                currentChannelInfo = cell(10,3);
            end
            channelInfo = currentChannelInfo;
        end
        function testResults = StaticTestResults(newTestResults)
            persistent currentTestResults
            if nargin
                currentTestResults = newTestResults;
            end
            if isempty(currentTestResults)
                currentTestResults = [];
            end
            testResults = currentTestResults;
        end

        % Static methods
        function initDataBuffer(buffer)
            Handlers.StaticDataBuffer(buffer);
        end

        function averageUpdatedHandler(source, args)
            if args.CurrentAverage < args.TotalAverages
                fprintf('Average: %d / %d\n', args.CurrentAverage, args.TotalAverages);
            else
                fprintf('Average: %d / %d\n', args.TotalAverages, args.TotalAverages);
                fprintf('\n');
            end
        end
        function calfeedbackHandler(source, args)
            fprintf('%s - %s\n', char(args.MessageType), char(args.Message));
        end
        function feedbackHandler(source, args)
            fprintf('%s - %s\n', char(args.MessageType), char(args.Message));
        end
        function timedataHandler(source, args)
            if ~isempty(args.TimeBlocks)
                data = args.TimeBlocks;

                n = 0;

                if data.Length ~= 0
                    for j = 1:data.GetLength(2)
                        % y = zeros(1, 4096);
                        y = cell(1, 4096); % Initialize a cell array to hold the data

                        for i = 1:data.GetLength(1)
                            y{i} = data.Get(i - 1, j - 1); % Adjusted indexing for MATLAB
                        end

                        % Convert cell array to numeric array before setting data
                        curves = Handlers.StaticCurves();
                        curves{n + 1}.YData = cell2mat(y);
                        curves{n + 1}.XData = timestamp;
                        Handlers.StaticCurves(curves);
                        n = n + 1;
                    end
                end
            end
        end
        function timeUpdatedHandler(source, args)
            if args.CurrentTime < args.Duration
                fprintf('%s: %.2f\n', char(args.CurrentMessage), args.CurrentTime);
                timestamp = args.CurrentTime;
                Handlers.StaticTimestamp(timestamp);
            else
                fprintf('\n');
            end
        end
        function fftprocessingUpdated(source, args)
            persistent plotTick
            if isempty(plotTick)
                plotTick = 0;
            end
            if ~isempty(args.AutoSpectrum)
                curves = cell(1,args.AutoSpectrumInfo.Length);
                autoSpectrumInfo = cell(args.AutoSpectrumInfo.Length,1);
                for i = 1:args.AutoSpectrumInfo.Length
                    autoSpectrumInfo{i} = char(args.AutoSpectrumInfo.GetValue(i-1));
                end
                channelInfo = Handlers.StaticChannelInfo();
                for i = 1:length(autoSpectrumInfo)
                    splitInfo = strsplit(autoSpectrumInfo{i}, '|');
                    for j = 1:length(splitInfo)
                        channelInfo{i, j} = splitInfo{j};
                    end
                end
                Handlers.StaticChannelInfo(channelInfo);
                freq = args.FrequencyAxis;
                data = args.AutoSpectrum;
                if ~isempty(freq)
                    for j = 1:length(curves)
                        x = zeros(freq.Length, 1);
                        y = zeros(freq.Length, 1);
                        for i = 1:freq.Length
                            x(i) = freq(i);
                            y(i) = data(i, j);
                        end
                        curves{j} = {x, y};

                    end
                    if plotTick <= 0  
                        plotTick = 5;
                        Handlers.frequencyPlots();
                    end
                    plotTick = plotTick - 1;
                end
            end
            Handlers.StaticCurves(curves);    
        end
        function stepProcessingUpdated(source, args)
            persistent plotTick
            if isempty(plotTick)
                plotTick = 0;
            end

            if ~isempty(args.SpectrumAmplitude)
                curves = cell(1, length(args.SpectrumInfo));
                spectrumInfo = cell(length(args.SpectrumInfo), 1);
                for i = 1:length(args.SpectrumInfo)
                    spectrumInfo{i} = char(args.SpectrumInfo.GetValue(i-1));
                end
                for i = 1:length(spectrumInfo)
                    splitInfo = strsplit(spectrumInfo{i}, '|');
                    for j = 1:length(splitInfo)
                        channelInfo = Handlers.StaticChannelInfo();
                        channelInfo{i, j} = splitInfo{j};
                    end
                end
                Handlers.StaticChannelInfo(channelInfo);
                freq = args.FrequencyAxis;
                data = args.SpectrumAmplitude;
                if ~isempty(freq)
                    for j = 1:length(curves)
                        x = zeros(freq.Length, 1);
                        y = zeros(freq.Length, 1);
                        for i = 1:freq.Length
                            x = freq;
                            y(i) = data(i, j);
                        end
                        curves{j} = {x, y};
                    end
                    if plotTick <= 0  
                        plotTick = 5;
                        Handlers.frequencyPlots();
                    end
                    plotTick = plotTick - 1;
                end
            end
            Handlers.StaticCurves(curves);
        end
        function time_data_callback(source, args)
            if ~isempty(args.TimeBlocks)
                data = args.TimeBlocks;
                if data.GetLength(0) ~= 0
                    for j = 1:data.GetLength(1)
                        y = zeros(1, 4096);
                        for i = 1:data.GetLength(0)
                            y(i) = data(i, j);
                        end
                        DataBuffer = Handlers.StaticDataBuffer();
                        DataBuffer = DataBuffer.append(y);
                        Handlers.StaticDataBuffer(DataBuffer);
                    end
                end
            end
        end
        function frequencyPlots()
            fig = findobj('Type', 'Figure', 'Name', 'FFT Plot');
            if isempty(fig)
                figure('Name', 'FFT Plot');
            else
                figure(fig);
            end
            curves = Handlers.StaticCurves();
            channelInfo = Handlers.StaticChannelInfo();
            for i = 1:length(curves)
                subplot(length(curves), 1, i);
                try
                    semilogx(curves{i}{1}, curves{i}{2});
                catch
                    return;
                end
                grid on;
                xlabel('Frequency');
                ylabel('Amplitude (dB)');
                title(sprintf('%s: %s', channelInfo{i, 1}, channelInfo{i, 3}));
            end
            drawnow;
        end
        function stimulusCreatedHandler(source, args)
            import EA_Engine.*
            EA = EA_Engine();
            engine = EA.engine;
            outputChannelName = engine.GetSelectedWDMOutputDevice().Name.Replace(" Left", "").Replace(" Right", "");
            deviceId = NaN;
            devices = audiodevinfo().output;
            for i = 1:length(devices)
                if strfind(string(devices(i).Name), string(outputChannelName))
                    deviceId = devices(i).ID;
                    break
                end
            end
            wavPath = string(args.FullPath);
            [audioData, sampleRate] = audioread(wavPath);
            persistent player;
            player = audioplayer(audioData, sampleRate, 24, deviceId);
            player.play();
        end

        function testResultsReadyHandler(source, args)
            if ~isempty(args.AutoSpectrum)
                curves = cell(1,args.AutoSpectrumInfo.Length);
                autoSpectrumInfo = cell(args.AutoSpectrumInfo.Length,1);
                for i = 1:args.AutoSpectrumInfo.Length
                    autoSpectrumInfo{i} = char(args.AutoSpectrumInfo.GetValue(i-1));
                end
                channelInfo = Handlers.StaticChannelInfo();
                for i = 1:length(autoSpectrumInfo)
                    splitInfo = strsplit(autoSpectrumInfo{i}, '|');
                    for j = 1:length(splitInfo)
                        channelInfo{i, j} = splitInfo{j};
                    end
                end
                Handlers.StaticChannelInfo(channelInfo);
                freq = args.FrequencyAxis;
                data = args.AutoSpectrum;
                if ~isempty(freq)
                    for j = 1:length(curves)
                        x = zeros(freq.Length, 1);
                        y = zeros(freq.Length, 1);
                        for i = 1:freq.Length
                            x(i) = freq(i);
                            y(i) = data(i, j);
                        end
                        curves{j} = {x, y};

                    end
                    Handlers.frequencyPlots();
                end
            end
            Handlers.StaticCurves(curves);    
            testResults = args;
            Handlers.StaticTestResults(testResults);
        end

        function saveResultsToVarHandler(source, args)
            testResults = args;
            Handlers.StaticTestResults(testResults);
        end
    end
end