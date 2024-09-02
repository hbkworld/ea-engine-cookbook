from HelpFunctions.Engine import EA_Engine


# Calibrates input channel and save the new sensitivity to "Input Channels.xml"
if __name__ == "__main__":
    engine = EA_Engine()

    # selecting the 3670 device resets all the channels metadata. This should therefore only be used in the beginning.
    engine.select3670Device()
    engine.setInputChannel(1, "4189", True)
    engine.runInputCalibration(1)