classdef FigureHandler < handle
    properties
        size
        x
        curve
        fig
        timer
    end
    
    methods
        function obj = FigureHandler(sampleinterval, timewindow, size, unit)
            if nargin < 1, sampleinterval = 0.1; end
            if nargin < 2, timewindow = 10; end
            if nargin < 3, size = 4096; end
            if nargin < 4, unit = 'Pa'; end
            
            % Data storage
            obj.size = size;
            obj.x = linspace(0.0, timewindow, size(1));
            
            % MATLAB Plot setup
            obj.fig = figure('Name', 'Time signal', 'NumberTitle', 'off', 'Color', 'w');
            obj.curve = plot(obj.x, zeros(size,1), 'b');
            grid on;
            xlabel('Time (s)');
            ylabel(['Amplitude (', unit, ')']);
            obj.fig.Position = [100, 100, 800, 400];
            
            % Timer setup
            obj.timer = timer('ExecutionMode', 'fixedRate', 'Period', sampleinterval, 'TimerFcn', @(~,~)obj.update());
            start(obj.timer);
        end
        function update(obj)
            global DataBuffer;
            % Update the curve data
            y = DataBuffer.getPart(obj.size(1));
            set(obj.curve, 'YData', y);
            print('Updated')
            drawnow;
        end
    end
end
