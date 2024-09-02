classdef EA_Engine < handle
    properties
        engine
        curves
        timestamp
    end
    methods
        function obj = EA_Engine(~)
            % Initialize .NET environment in MATLAB
            NET.addAssembly('System');
            import System.*;

            % EA Engine installation path
            installPath = 'C:\Program Files\HBK\EA Engine';

            % Add the EA Engine .NET assembly
            NET.addAssembly([installPath, '\EA_Engine.exe']);

            % Add the Signal Processing Library .NET assembly
            NET.addAssembly([installPath, '\Signal Processing Library.dll']);

            % Import the assemblies namespace
            import EA_Engine.*;
            import SignalProcessing.Library.*;

            % Declare and instantiate a new Engine object (the installation path is mandatory)
            obj.engine = EA_Engine.Engine(installPath);
            obj.curves = NET.createArray('System.Object', 10);
            obj.timestamp = 0;

            % Define handlers for a .NET object (here the engine object)
            % Events are:
            % - Feedback: returns information during a task execution
            % - TimeUpdated: returns the time elapsed during data acquisition
            % - AverageUpdated: return the average updated during processing (FFT)

            % Add the event listeners to the engine object
            addlistener(obj.engine, 'Feedback', @Handlers.feedbackHandler);
            addlistener(obj.engine, 'TimeUpdated', @Handlers.timeUpdatedHandler);
            addlistener(obj.engine, 'AverageUpdated', @Handlers.averageUpdatedHandler);
        end
    end
end