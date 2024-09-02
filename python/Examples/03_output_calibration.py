from HelpFunctions.Engine import EA_Engine

# Calibrates output channel and save the new sensitivity to "Output Channels.xml"
if __name__ == "__main__":
    engine = EA_Engine()
    engine.setOutputChannel(1, "3670-A", True)
    engine.runOutputCalibration(1, 1)