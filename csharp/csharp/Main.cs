using EAProject.Examples;
using EA_Engine;
using System.Runtime.InteropServices;
namespace EAProject
{
    class Program
    {

        //EA Engine needs the program to be run in STA
        [STAThread]
        static void Main()
        {

            string exampleName = "05_random_test";
            //string exampleName = "02_input_calibration";

            switch (exampleName)
            {
                case "01_get_version":
                    Get_version.Main();
                    break;
                case "02_input_calibration":
                    Input_calibration.Main();
                    break;
                case "03_output_calibration":
                    Output_calibration.Main();
                    break;
                case "04_output_equalization":
                    Output_Equalization.Main();
                    break;
                case "05_random_test":
                    Random_test.Main();
                    break;
                case "06_step_sine_test":
                    Step_sine_test.Main();
                    break;
                case "07_swept_sine_test":
                    Swept_sine_test.Main();
                    break;
                case "08_fixed_sine_test":
                    Fixed_sine_test.Main();
                    break;
                case "09_waveform_streaming_test":
                    Waveform_streaming_test.Main();
                    break;
                case "10_OpenLoopRandomNoiseTest":
                    OpenLoopRandomNoiseTest.Main();
                    break;
                case "11_OpenLoopSweptSineTest":
                    OpenLoopSweptSineTest.Main();
                    break;
                case "12_OpenLoopStepSineTest":
                    OpenLoopStepSineTest.Main();
                    break;
                case "13_OpenLoopWaveformStreaming":
                    OpenLoopWaveformStreaming.Main();
                    break;
            }
        }
    }
}