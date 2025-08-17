# Jet-Engine-Performance-Simulator
Hi everyone. The Jet Engine Performance Simulator is a python based  application to analyze the various jet engines types. The basic flight parameters are taken as user input and then the programme generates the end results of net thrust , overall efficiency, exhaust velocity , etc.  I have also used Tkinter and Matplotlib in this programme.

This is a multi engiene simulator that simulates the performance of aix different engines:
1. Turbojet
2. Turbofan
3. Turboprop
4. Turboshaft
5. Ramjet
6. Scramjet

It takes user input of basic flight parameters like:
1. Altitude
2. Mach Number
3. Air Mass Flow
4. Turbine Inlet Temperature
5. Compressor and Fan Ratios

The simulator calculates and displays essential performance outputs :- Net Thrust , TFSC , Overall Efficiency

It visualises engine performance with plots generated with the helo of Matplotlib. 
1. Performance vs Mach Number
2. Performance vs Altitued

Technologies Used
Python: The core programming language for the simulation logic and GUI.
Tkinter (ttk): Used for creating the cross-platform desktop GUI. The ttk module was utilized for professional, theme-able widgets.
Matplotlib: A powerful plotting library integrated to generate and display the performance graphs within the application.
NumPy: Used for efficient numerical calculations and array manipulation, particularly for generating data points for the graphs.

Engineering Principles
This simulator is based on the fundamental principles of aerospace propulsion and thermodynamics. The calculations for each engine component (intake, compressor, combustor, turbine, nozzle) are derived from the conservation of mass, momentum, and energy, assuming a gas turbine ideal Brayton cycle with real-world component efficiencies. The model accounts for standard atmospheric conditions and variations in stagnation properties as air flows through the engine. The phenomenon of normal and oblique shocks inside the engines have also been taken into consideration.
