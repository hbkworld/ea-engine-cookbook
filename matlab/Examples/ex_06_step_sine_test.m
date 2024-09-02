% Runs step sine test
addpath ..\;
engine = Engine();

% Sets all channels to inactive 
engine.deselectWdmInputDevice();
engine.setAllChannelsToFalse();

engine.setInputChannel(1, "4189 Ch.1", true);
engine.setOutputChannel(1, "3670-A", true);

% The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
res = engine.runStepSineTest(1, 2, 20, 20000);