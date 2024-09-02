classdef Buffer
    properties
        size
        data
    end
    
    methods
        function obj = Buffer(size)
            obj.size = size;
            obj.data = zeros(1, size);
        end
        
        function obj = append(obj, x)
            % Adds data in the front of the buffer. Discards the oldest data if buffer is full
            obj.data = [obj.data(end-(obj.size - length(x))+1:end), x(:)'];
        end
        
        function data = get(obj)
            % Returns the whole buffer
            data = obj.data;
        end
        
        function part = getPart(obj, start)
            % Returns X points of the newest data
            if nargin < 2
                start = 2^16;
            end
            part = obj.data(end-start+1:end);
        end
    end
end
