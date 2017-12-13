## Overview ##

This repository contains SRIM simulation analysis programs for TRIFIC. A Python interface has been developed for fast setup, simulation and processing of SRIM data. Several different ions travelling through the TRIFIC chamber may be simulated with a single, easy-to-make script that will produce Particle Identification (PID) historgams from the simulation data. A quick guide to the repository:

The TRIFICsim program takes TRIM collision file(s) as input, and outputs deposited energy from ionization events for the different wire grid plane separated collection regions within TRIFIC.

The csv2h2 file is used to process data output by TRIFICsim and create 2-D PID plots.

TRIMIN.sav contains an example TRIM input file that may be useful for those new to simulating ions in TRIFIC. To load it, first open SRIM (installation described below). Copy the file to the 'SRIM Restore' sub-directory within the main SRIM-2013 directory. Then open the TRIM program and select 'TRIM Calculation'. Selecting 'Resume saved TRIM calc.' should resotre the inputs from the TRIMIN.sav file to the GUI. Then select 'Resume Saved TRIM' which should resume a completed simulation. Save nothing, and exit the results window. Now, back in the TRIM input GUI, adjustments to the parameters can be made. Familiarity with the TRIM program will be very beneficial for TRIFIC simulations (go to srim.org for all the information you could ever need), but the TRIMbatch Python module will greatly reduce any need to use the GUI.

install-wine-i686-centos7.sh is an extremely useful shell script for getting 32-bit wine to run on a machine running CentOS 7 which is needed for the Python interface.

The make file compiles the C++ code for convenience.

examplesim.py contains an example script for simulating 4 ions in TRIFIC using the Python. For most future simulations, it should be sufficient to copy and paste the code, changing the necessary parameters and executing. A complete explination lives in the tutorial below.

The TRIMbatch module contains scripts for parsing TRIM's default atom and compound directories as well as the interface used for running TRIM in batch mode automatically. It requires only standard Python 3 modules.

See Getting Started for a step-by-step guide to installing SRIM on CentOS 7 to begin TRIFIC simulations.

For a quick guide to using the Python interface to run TRIM in batch mode, see the Tutorial.

For extra notes and ideas for future work, see the Development Notes.

## Getting Started ##

All files used for setup/simulations/tutorial are included in the TRIFIC repository. SRIM software can be sownloaded from http://www.srim.org/SRIM/SRIMLEGL.htm. Here you should find all the documentation and tutorials needed to use the software. I recommend you familiarize yourself with the GUI and some basic simulations before using this software, although hopefully it is user-friendly enough that it is not a requirement! From here onwards, competency with SRIM is assumed. The first section below details all the setup required for a windows user who can ssh into a linux machine (CentOS 7). Alternatively, for the fastest way to hit the ground running, the user could use the "bundseth" account on smilodon, where SRIM-2013 has been set up and works with the existing code in the TRIFIC repository, and get going with simulations immediately (see the Tutorial).

To begin, clone the TRIFIC repository into the user's home directory:

git clone https://github.com/TIGRESS-Collaboration/TRIFIC.git

### Installing Wine ###

Note: If using smilodon, you should be able to skip the wine32 build and begin with running "winecfg" (see Installing SRIM).

We would like to have SRIM running on our Linux machine. This can be done (http://www.calel.org/srim.html) using wine. However, at the time of setting this up (October 2017), installing 32-bit wine on CentOS 7 is not straightforward (https://wiki.winehq.org/CentOS/RHEL). Luckily for us, smart people have figured out a way to make it happen (https://www.systutorials.com/239913/install-32-bit-wine-1-8-centos-7/). The shell script contained in the last link has been saved in the repo for future use.

As administrator (su -), copy the install-wine-i686-centos7.sh file from github to a new file of the same name, save and make executable, then run. The same file can be used to uninstall wine if need be.

### Insatlling SRIM ###

On the Linux machine, run: winecfg

This will set up a .wine directory. As wine started, it prompted certain missing packages to be installed, and all were accepted until a configuration GUI appeared. Select OK.

Ideally, we'd like to have the latest version of SRIM (2013) running on Linux. If the machine has never had SRIM on it, installing the 2013 version immediately likely won't work as there are some Windows files missing. The easiest workaround is to install SRIM-2008 first, as its setup will automatically take care of this.

SRIM-2008 was downloaded from srim.org and then secure copied to the linux /tmp directory, changing the self-extracting zip file to .exe.

scp SRIM-2008.e bundseth@smilodon:/tmp/SRIM-2008.exe

Now extract the files. From the /tmp directory on the linux machine, run:

wine SRIM-2008.exe

Click 'Extract' on the wine gui that pops up, OK on the status message, then select Done.

To install SRIM, change to the home directory and run:

wine /tmp/SETUP.EXE

Accept the default options as the setup runs. This will put SRIM-2008 files in the directory /home/bundseth/.wine/drive_c/Program Files (x86)/SRIM.

Now we can get SRIM-2013.

In the Program Files (x86) directory, make a new directory for SRIM-2013. SRIM-2013 (Standard) was downloaded from srim.org and then secure copied to a new .wine/drive_c/Program Files (x86)/SRIM-2013 directory, changing the self-extracting zip file to .exe.

mkdir SRIM-2013
scp SRIM-2013-Std.e bundseth@smilodon:/home/bundseth/SRIM-2013.exe
ssh -Y bundseth@smilodon
mv SRIM-2013.exe /home/bundseth/.wine/drive_c/Program\ Files\ \(x86\)/SRIM-2013/SRIM-2013.exe

In the SRIM-2013 directory, run:

wine SRIM-2013.exe

Let wine extract all the files as before.

Now we can see if the setup worked. Try opening the main menu:

wine /home/bundseth/.wine/drive_c/Program\ Files\ \(x86\)/SRIM-2013/SRIM.exe

Note that the first couple of times this is done, a readme will pop up. Close this to continue to SRIM. The GUI is slow, but should work fine. Try generating a stopping range table and allow SRIM to save it in the default directory (SRIM Outputs). Check that the generated table did indeed show up. If SRIM (either version) crashes, try editing the file .wine/drive_c/Program\ Files\ \(x86\)/SRIM/Data/VERSION as described below. If for some reason SRIM (2008 or 2013) can't be installed with wine, check out https://appdb.winehq.org/ and search for SRIM as a starting point to troubleshoot.

If editing the VERSION file, there should be no problems as long as the file is not empty. If it is, enter:

"""
SRIM-2008.04

SRIM software version.

See VERSION.rtf for details.
"""

For the 2013 version, change 2008.04 to 2013.00. This is one possible cause of TRIM crashing on execution.

The last piece of setup is required to run TRIM in batch mode (and therefore the Python interface), which means calling the TRIM executable to simulate based off of the data in the TRIM.IN file. Edit the file TRIMAUTO (not TRIMAUTO.TXT) and change the number at the top of the file from a 0 (default) to a 1.

### Installing ROOT ###

ROOT is used to generate plots from the processed simulation results. Go to https://root.cern.ch/downloading-root and download the most recent production binary distribution for CentOS. Copy the download to the root directory of the linux machine, then run something like:

tar zxvf root_v6.10.06.Linux-centos7-x86_64-gcc4.8.tar.gz

This will create a new directory called "root". To set up necessary environment variables, run:
. /home/bundseth/root/bin/thisroot.sh

Add this line to the bottom of ~/.bashrc. If this is not done (manually or otherwise), the software will not work. Try typing "root" into the terminal. The interactive shell should start if everything is good to go.

### Setup Python 3 Environment ###

CentOS 7 comes with Python 2, but Python 3 is good practice. More importantly, the interface will absolutely not work with Python 2. As root:

yum update
yum install yum-utils https://centos7.iuscommunity.org/ius-release.rpm python 36u python36u-pip python36u-devel

If continuing to develop the interface, setting up a virtual environment is a good idea.

cd
mkdir environments
cd environments
python3.6 -m venv TRIFIC
source environments/TRIFIC/bin/activate

For the current version of the interface, only standard modules are used.

### Last Steps ###

For convenience, a small make file is included to compile the C++ files. Before running ./make, make sure you have run the thisroot.sh shell script.

That's it! To test if everything works, you should be able to run the tutorial script examplesim.py. You will notice a new directory pop up in the cloned repo where the interface stores intermediate input/output files for interacting with TRIM. TRIM simulation windows will appear as the software runs. It is best to leave them alone, they will close on their own when everything is finished. Windows containing ROOT histograms will also open and show the results of the simulation. Simply close them when you are done and hit enter in the terminal for the program to finish.

## Tutorial ##

This section will describe in detail the lines contained within examplesim.py. For use of the Python interface for TRIFIC simulations, simply changing the parameters in this code should be adequate. However, this interface may be useful for more than just simulations pertaining to TRIFIC, so a brief rundown of all the features available with the interface is included afterwards. Simulation and analysis may still be performed without the interface, albeit with more gruntwork. How to use the C++ files directly is noted in the Development Notes.

A typical script will begin by importing the TRIMbatch module:

from TRIMbatch.batch import *

In order to keep track of each simulation input/output, a directory containing input and output files will be created inside ~/TRIFIC/TRIMDATA. The user selects the name for the directory in case they would like to look up simulation input or output. This name is defined at the beginning of the script for ease.

nameofexp = 'IRIS-2017-09-29'

We begin setting up our simulation by creating a Batch object. This object will contain all the information necessary to create a TRIM input file (ion data, target info, corrections, etc.). To initialize a Batch object, we must give it ion info as well as a place to save data. We start with wanting to simulate 20 atoms of Gallium-80 @ 5.91MeV/u (note that 80u x 5.91MeV/u = 472800keV).

batch = Batch(nameofexp,'Ga',80,472800,20)

Next, we need to define the target data. We use the addTargetLayer method, giving the layer number (in order, starting with 1), then the name of the compound/atom that makes up the target (more on this later), the width and corresponding unit, density/pressure information, and whether or not the layer is gaseous. For TRIFIC, the ions will travel through a Mylar window with a thickness on the order of microns. TRIM knows what Mylar is, and we omit any density information as a way to let the program know to use the TRIM default density (we know from the GUI that this density is accurate). Once through the window, the ions will pass through up to ~30cm of CF4 gas. Unlike Mylar, TRIM's info for carbon tetrafluoride is not very accurate, so we have defined our own compound in the comopund parser with the name 'CF4' (this is easy to do and explained below). When we defined it, we gave a density at STP that we believe is accurate enough for reference, and instead of calculating some small density by hand, the interface lets us give the pressure of a gas in Torr. It will take care of scaling the known value as an ideal gas.

batch.addTargetLayer(1,'Mylar',width=25,unit='um',gas=False)
batch.addTargetLayer(2,'CF4',width=30,unit='cm',gas=True)

There are a lot of ways ions and target layers may be defined. The program will always use user-defined parameters above defaults, so making use of all the keyword arguments will give the most control. The program is smart enough to know what input combinations absolutely will not work and will give error messages accordingly. However, there are many ways to input garbage that TRIM will roll with, so double check what you feed the software if you want the results to make sense.

Once our target is defined, we tell the program to create a batch file using the information we have given. This is done by calling the makeBatch method. It will also throw error messages if anything seems awry with the parameters it has been given.

batch.makeBatch()

For simulations pertaining to TRIFIC, we are interested in firing different ions through the same target. Rather than creating a new object and re-entering redundant information, we can tell the program to hotswap the ion and generate a new simulation file with a single method. Just like when initializing the Batch object, we simply give the method new ion parameters to work with. Note that changes to the target layer are allowed and can be changed in between generating input files. Calling the nextIon method will produce a batch file for the given ion using the current target info.

batch.nextIon('Se',80,452000,20)
batch.nextIon('Kr',80,437600,20)
batch.nextIon('Rb',80,429600,20)

Now that all of our input files are prepared, we are ready to let TRIM do its thing. We call Sim() to do this, and give it the name of the dataset we're working with along with a list of files to simulate. Our Batch object keeps track of the files it generates, and these are available on demand using the batchFiles method.

Sim(nameofexp,batch.batchFiles())

Finally, we have our simulation outputs and are ready to generate a PID plot using the C++ files in the repository. Our interface also provides a wrapper for those, and simply calling PIDPlot(), passing the dataset name, the files, and parameters for generating the histograms, will generate all plots simultaneously in their own windows. The program blocks until the windows  are closed (best is to use File --> Quite ROOT) or user input is received.

### Interface Description ###

The example script covers everything needed for TRIFIC simulations, but doesn't bring up every detail. Here, the full capabilities of the interface are described as it currently exists.

The full Batch object initialization is as follows:



The arguments correspond to the parameters that would be filled in near the top of the TRIM GUI. 



## Development Notes ##

Some useful notes and ideas for future improvements.





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
