% Runs an Open Loop Swept Sine Test which makes the user able to test
% an output or an input that is not directly connected to the 3670-A. 

addpath ..\;

% External Output: The external output plays the stimulus which gets captured by the inputs connected to the 3670-A
function externalOutput()
   engine = Engine();

   % Sets all channels to be inactive
   engine.setAllChannelsToFalse();

   % In this case we are using the sensitivty from the Head and Torso
   % Simulator. The sensitivty could also be found using input calibration
   engine.setInputChannel(1, "Left ear", true, "none", 15.8, "mV/Pa");
   engine.setInputChannel(2, "Right ear", true, "none", 15.8, "mV/Pa");
   
   % Selects your wdm device
   engine.selectWdmOutputDevice("Headphones", true);

   % The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
   res = engine.runCompleteOpenLoopSweptSineTest(1);
end

% External Input: The external input records the stimulus played by the output channel of the 3670-A
function externalInput()
   engine = Engine();

   % Sets all channels to be inactive
   engine.setAllChannelsToFalse();

   engine.setOutputChannel(1, "3670-A Ch.1", true);
      
   % Selects your wdm device
   engine.selectWdmInputDevice("Headset", true);
   % remember to use the correct senitivity for the microphone
   engine.setInputChannel(9, "Headset", true, 'None', 10, "mV/Pa")

   % The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
   res = engine.runPlaybackOpenLoopSweptSineTest(1);
end


%externalOutput();
externalInput();