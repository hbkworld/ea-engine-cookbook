classdef InputRecorder
    properties
        filename;
        sampleRate = 44100;
        channels = 1;
        volume = 1;
        bitRate = 24;
        recorder;
        deviceId;
    end
    methods
        function obj = InputRecorder(filename)
            import EA_Engine.*
            EA = EA_Engine();
            engine = EA.engine;
            inputChannelName = engine.GetSelectedWDMInputDevice().Name;
            obj.filename = filename;
            devices = audiodevinfo().input;
            for i = 1:length(devices)
                if strfind(string(devices(i).Name), string(inputChannelName))
                    deviceId = devices(i).ID;
                    break
                end
            end
            obj.recorder = audiorecorder(obj.sampleRate, obj.bitRate, obj.channels, deviceId);
        end

        function startRecording(obj)
            obj.recorder.record();
            fprintf("Recording started...")
        end

        function stopRecording(obj)
            obj.recorder.stop();
            recordingData = obj.recorder.getaudiodata();
            audiowrite(obj.filename, recordingData, obj.sampleRate);
            fprintf("Recording stopped and saved to %s", obj.filename);
            
        end

    end

end