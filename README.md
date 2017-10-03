## Overview ##

This repository contains SRIM simulation analysis programs for TRIFIC. The TRIFICsim program takes TRIM collision file(s) as input, and outputs deposited energy from ionization events for the different wire grid plane separated collection regions within TRIFIC. This data output can be processed in the csv2h2 file to produce a 2-D Particle Identification histogram. TRIMIN.sav is a template of TRIM calculation input for performing simulations in TRIM. It should be copied to the 'SR Restore' directory within SRIM, and then using the GUI to restore a saved calculation should bring up the input template.

More detailed information, and compilation instructions, can be found in the corresponding C++ files for each program. 

This repository has been modeled off of the simulation files for the TBragg, and represent a much simplified version iteration of that code.

## Step by Step Guide ##

Step 1: TRIM calculation

The TRIMIN.sav file in this repository should be copied to the 'SRIM Restore' sub-directory within the main SRIM directory. Then open the SRIM program and select 'TRIM Calculation'. Selecting 'Resume saved TRIM calc.' should restore the inputs from the TRIMIN.sav file to the GUI. Then select 'Resume Saved TRIM' which should resume a completed simulation. Save nothing, and exit the results window. Now, back in the TRIM input GUI, adjustments to the parameters can  be made. The fields to review before running a simulation are:
- Basic Plots; set to NO Graphics for fastest run time
- Element, Mass, and Energy
- Layers (single or double side aluminised mylar? mylar window thickness? gas layer width if more/less grids are inserted; gas density?)
- Total number of Ions simulated; 100 per isotope seems to be sufficient
- Output disk files; only 'Collision Details' are necessary
Once these input fields are reviewed, 'Save Input & Run TRIM' can be selected. TRIM will prompt the user with a warning about the input target layer densities. Only the Mylar and Al2O3 densities should appear on this prompt, as the user should have input a custom density for the gas. Upon continuing, TRIM will simulate the specified number of ions. The user will be prompted to save or to calculate for more ions. Saving, and storing in the SRIM Directory, will result in a file named COLISON.txt being generated in the 'SRIM Outputs' sub-directory. The TRIM output window can now be closed, and the user will be prompted to save the calculation, which generates a TRIMIN.sav file for the calculation. This can be useful to generate if you will want to come back to the calculation in another session as you will not need to adjust all the input fields once more. 

Step 2: Analysis in TRIFIC simulation directory

The user will need to have this repository cloned onto a linux machine. Using a windows terminal program, such as MobaXterm, secure copy the COLISON.txt file(s) to an accesible location in the file system of the linux machine. SSH into the linux machine and open up the TRIFICsim.cpp file in a text editor. Note the constants defined at the start of the program.
- numGrids, spacing, windowToWires, may all need to be adjusted depending upon the mounted configuration
Note the structure of the printValues() function. The user needs to comment/uncomment the sections that correspond to the value generation they desire. The possible iterations are many, but they all center around the 2-D collectionRegions array. This array contains the summed energy losses by grid region (first array dimension), for every ion simulated (second array dimension). Refer to the processSRIMData() function for reference to this array construction. The two main types of plots one might want to create are PID plots, which are histograms that present data from every ion simulated, and Bragg plots, which are generally presented as line graphs containing the energy loss data per isotope simulated. See TRIFIC ELog post with ID 50 for examples of these plots. 

With the TRIFICSim.cpp file tuned to the user's output preferences, the program can be compiled using the compile line given at the top of TRIFICsim.cpp. If generating a Bragg plot, simply running the program as described in the comments at the top of TRIFICsim.cpp should suffice. The data can be plotted and inspected in excel afterwards. If generating a PID, the output will need to be piped into ROOT. Open up the csv2h2.cpp file in a text editor. On lines 101-103 the plot and axis titles are defined, they should be adjusted to match the plot being generated. The file can be exited and compiled.

As described at the top of csv2h2.cpp the data output from TRIFICsim can be piped directly into csv2h2. Some command line parameter inputs are available, notably adjustment of the x and y axis ranges. A typical run of the program for PID generation would be:

./TRIFICsim /home/<user>/MyCollisionFiles/* | ./csv2h2 -rx 200 -ry 200

## To-do ##

The TRIM calculations performed up to this point have all assumed that ions enter the chamber at a single position, and then experience straggling as they pass through the layers. A more realistic situation would be that the ions enter at a range of positions and more importantly, angles. This could be effected in the simulations by applying a random entering angle and position to each ion, and then adjusting the z-positions of every collision accordingly. The position distribution in z is all we are concerned with.

---

The quoted section below is from the TRIM documentation, and details a more accurate way of calculating the energy deposition. It should be implemented for some fine improvement:
"Referring to 'COLLISON.txt': This file shows the three-dimensional position of each major collision between the ion and the target atoms. It also shows in column six the instantaneous electronic energy loss of the ion to the target in units of eV/Å. If you need the three-dimensional electronic energy loss of the ion to the target, you now have all the necessary information. To obtain the energy deposited, calculate the path length between two successive collisions and multiply by the specific energy loss. For example, the distance between the first two collisions shown above is 16.3Å, with an energy loss of 15.86 eV/Å. This means the ion loses 258 eV into electronic excitations in this segment." 

---

On the wiki, and in the sample simulation file, the absolute minimum distance for simulation is given as 279.18 mm with 21 grids installed. This neglects the bending of the mylar window towards the upstream beam line, roughly estimated to be about a centimetre. TRIM simulates incoming ions with no space distribution as to their entry, it is all from a single point. This is not physically the case with the upstream beam line arriving at TRIFIC, and also the fact of the window bend being convex means that the deviation from center of an ion's entering position will affect the point at which it first hits the aluminized layer. Such accuracy improvements may be overkill, but are interesting to consider as a future improvement. 

---
