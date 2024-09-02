% calibrates input channel and save the new sensitivity to "Input Channels.xml"
addpath ..\;
engine = Engine();

% selecting the 3670 device resets all the channels metadata. This should therefore only be used in the beginning.
engine.select3670Device();
engine.setInputChannel(1, "4189 Ch.1", true);
engine.runInputCalibration(1);