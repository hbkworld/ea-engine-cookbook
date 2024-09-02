# CSharp example guide

This README will guide you through the setup process as well as how to run the different examples. 

## Requirements

 1. Visual Studio

These examples are made with visual studio. It is therefore required to use visual studio to run the solution file.

## Setup and how to run an example

To run the examples you first have to open the solution file with visual studio. All the dependencies get handle by the csproj-file which copies the DLL's from the EA Engine's installation folder.

To run an example, open the `Main.cs` file. In here you can choose the example to run by changing the exampleName variable.
E.g. to run `01_get_version` you simply change the variable name to:

```cs
string exampleName = "01_get_version";
```

The examples use the class `Engine` to simplify and automate the process of configure the different test. Feel free to tweak and customize the engine to your liking.
