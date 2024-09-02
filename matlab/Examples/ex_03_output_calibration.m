% Calibrates output channel and save the new sensitivty to "Output Channels.xml"
addpath ..\;
engine = Engine();
% Output calibration needs a calibrated input
engine.setInputChannel(1, "4189 Ch.1", true);

engine.setOutputChannel(1, "3670-A", true);
engine.runOutputCalibration(1, 1, 1000, 0.3, 10);
