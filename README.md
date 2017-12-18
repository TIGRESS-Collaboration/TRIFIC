## Overview ##

This repository contains SRIM simulation analysis programs for TRIFIC. A Python interface has been developed for fast setup, simulation and processing of SRIM data. Several different ions travelling through the TRIFIC chamber may be simulated with a single, easy-to-make script that will produce Particle Identification (PID) historgams from the simulation data. A quick guide to the repository:

The TRIFICsim program takes TRIM collision file(s) as input, and outputs deposited energy from ionization events for the different wire grid plane separated collection regions within TRIFIC.

The csv2h2 file is used to process data output by TRIFICsim and create 2-D PID plots.

TRIMIN.sav contains an example TRIM input file that may be useful for those new to simulating ions in TRIFIC. To load it, first open SRIM (installation described below). Copy the file to the 'SRIM Restore' sub-directory within the main SRIM-2013 directory. Then open the TRIM program and select 'TRIM Calculation'. Selecting 'Resume saved TRIM calc.' should restore the inputs from the TRIMIN.sav file to the GUI. Then select 'Resume Saved TRIM' which should resume a completed simulation. Save nothing, and exit the results window. Now, back in the TRIM input GUI, adjustments to the parameters can be made. Familiarity with the TRIM program will be very beneficial for TRIFIC simulations (go to srim.org for all the information you could ever need), but the TRIMbatch Python module will greatly reduce any need to use the GUI.

install-wine-i686-centos7.sh is an extremely useful shell script for getting 32-bit wine to run on a machine running CentOS 7 which is needed for the Python interface.

The make file compiles the C++ code for convenience.

examplesim.py contains an example script for simulating 4 ions in TRIFIC using the Python interface. For most future simulations, it should be sufficient to copy and paste the code, changing the necessary parameters and executing. The tutorial below contains a walkthrough of the code.

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

There are a lot of ways ions and target layers may be defined. The program will always use user-defined parameters (if given) above defaults, so making use of all the keyword arguments will give the most control. The program is smart enough to know what input combinations absolutely will not work and will give error messages accordingly. However, there are many ways to input garbage that TRIM will roll with, so double check what you feed the software if you want the results to make sense.

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

__init__(self,saveto,ion,mass,energy,number,angle=0,corr=0,autosave=10000)

The Batch object must be initialized with an ion and save location for a) it to know where to write .IN files and save TRIM outputs, b) your future reference of these files. The ion data is straightforward. 'ion' is the chemical symbol for the element, 'mass' is given in amu, 'energy' is given in keV, and 'number' is the number of ions we would like to simulate. For example 20 Gallium 80 ions @ 5.91MeV/u is input as:

Batch('save location','Ga',80,472800,20)

The arguments correspond to the parameters that are typically filled in at the top of the TRIM GUI. 'angle' can be changed if the direction of the travelling ions with respect to the target is to be changed. 'corr' is an ion correction with 0 corresponding to no correction (this is fine for TRIFIC simulations). 'autosave' is the number of atoms after which TRIM will automatically save an intermediate output, and shouldn't have to be used. Other TRIM options relating to detail and type of output created are hardcoded for the needs of TRIFIC but could easily be implemented as additional arguments in the future.

Target layers are added using the addTargetLayer() method:

batch.addTargetLayer(self,lnumber,lname,width=0,unit='Ang',density=0,pressure=0,corr=1,gas=0,compound=True)

Every target is given a number corresponding to its position in the layer stack, with 1 being the first layer. No duplicates or gaps in the stack are allowed and an error will be thrown if detected. Layers can be defined and changed out of order without having to create a new object. An example where this is useful is finding the ideal operating pressure of TRIFIC (or any IC) where, instead of re-entering a bunch of parameters, only the gas layer could be changed so that a sweep over several pressures could be done in a single script. Layers may either be single atoms or compounds. If an atom, give the chemical symbol (ie. 'Ar' for Argon gas). If a compound, it must be one existing in either the default TRIM directory or be user defined in the parser (see below). The exact name must be used, otherwise an error will be raised. A good approach for using an unfamiliar compound in the TRIM directory would be to copy and paste the name given in the TRIM GUI. The 'width' may be given in Angstrom ('Ang'), or in 'cm' or 'um' by changing the 'unit' argument. There are different ways to input the density depending on how much the user knows about the material and how much they have faith in TRIM's defaults (which are usually ok but sometimes not). If the target layer is not gaseous, a 'density' may be given in g/cm3, or not given if the user wishes to keep the TRIM default. This is usually fine for very thin layers ie. micron-thick Mylar windows. If the target is gaseous, a 'density' in g/cm3 or a 'pressure' in Torr may be given. If both are defined, the density will be used. If only a pressure is given, the program will take the default gas density (assumed to be given for 760 torr) and scale it according to the ideal gas law. This is convenient since gas densities in g/cm3 are very small and tedious to calculate, but this should only be used when the user has checked the default gas density and understands the assumptions being made. Give the density in g/cm3 if you want absolute control. The state MUST be given with either 'gas'=True or 'gas'=False. The program will not make any assumptions about the state of a layer but has the courtesy to not run if a layer's state is not given. This avoids TRIM spitting out garbage. A correction 'corr' may be given, but for quick calculations the default is ok. Full disclosure, I *think* TRIM calculates these on-the-fly during normal GUI input, or maybe I just can't find them in the files. If you want to use compound corrections, the best approach would be to look up the ion/target layer compound correction in the GUI can copy/paste the number to the script. Finally, a 'compound'=False argument is needed if the user wants to use a single atom layer. This is because some elements occupy both atom and compound directories, and this clarifies where to look. 

If a compound does not exist in the TRIM default directory, one may be easily made by editing the compoundparse.py parser within the TRIMbatch module. At the bottom is a clearly marked section and a template to use. 'CF4' is given as an example. Compounds are stored in a structure where the name is a key for a dictionary containing 'Density' and 'Stoich' keys. The density should be what one would expect at STP. The stoichimetry is given as a list of tuples, each of the form ['atomic number','%']. For example, CF4 is defined by adding the line:

compounds['CF4'] = {'Density': 0.00372, 'Stoich': [[6,0.2],[9,0.8]]}

This only has to be done once, and then the compound may be used in any future script by adding a target layer with the given name.

Batch files are written with the makeBatch() method, which takes no additional arguments. The program takes care of naming files by concatenating the mass, chemical symbol, and energy of the ion.

The nextIon() method takes the same ion arguments as initialization:

batch.nextIon(self,ion,mass,energy,number,angle=0,corr=0,autosave=10000)

It will use the target information currently known to the object and automatically write a TRIM input file with the new ion data.

batch.batchFiles()

The method batchFiles() will return a list of files created using the Batch object. This is useful for passing files to the simulation and plotting functions.

Simulations are run in groups using:

Sim(dirname,fs)

'dirname' is the name of the directory (within TRIFIC/TRIMDATA) where the input files to simulate live, the same argument that was used to initialize Batch objects. 'fs' is a list of files that may be given by the user, or passed using the batchFiles() method or the getFiles() function. TRIM will be run using wine, and simulation windows will open and close automatically for each ion to be simulated. The function will take care of saving output files to the 'saveto' directory given.

The only plotting function is a wrapper for old C++ code used to make PID histograms:

PIDPlot(dirname,fs,Xrange=0,Yrange=0,Xbins=50,Ybins=50)

'dirname' and 'fs' are a location and list of files to plot, as before. The latter four arguments are passed to C++ and give ranges and bin sizes for the generated histograms. The C++ is hardcoded for 3 grid regions within TRIFIC, and therefore 3 PID plots are generated (each one comparing 2 grid regions) simultaneously. The function will block until user input is received so that ROOT is closed responsibly.

getFiles(dirname)

A simple function that returns all simulation outputs for the given directory. Its intended use is for looking up files for generating plots without having to re-simulate or manually check what ions have been simulated.

## Development Notes ##

Some useful notes and ideas for future improvements.

PID plots may be generated without using the Python interface at all provided the C++ code from the repository has been cloned onto a linux machine and compiled. When the desired TRIM simulation outputs (typically called COLLISON.txt) have been secure copied from the simulating machine to the linux machine, use the following line:

./TRIFICsim 12 /home/bundseth/... /home/bundseth/... * | ./csv2h2 -nx 50 -ny 50 -rx 200 -ry 200 -gn 12

TRIFICsim calculates the cumulative energy lost per ion for the grid regions as defined by the constants in the program. It outputs data for each ion of each file given and is piped to csv2h2, which takes care of plotting a ROOT histogram.

The above will plot the PID histogram for grid regions 1 & 2. Change the occurences of '12' above to either '13' or '23' for the other two grid regions. As many TRIM output files may be given to TRIFICsim as desired, provided the full path is given and spaces separate the files. csv2h2 is the plotting code and takes -nx and -ny arguments for number of bins and -rx and -ry for range.

The TRIFICsim program is also capable of generating values needed for Bragg curves, but no dedicated plotter exists. In the past, they have been made by copying the output of the following to Excel: 

cat ./TRIFICsim /home/bundseth/... /home/bundseth/... *

TRIFICsim.cpp must be compiled with the proper lines uncommented to receive the proper output. Note the constants defined at the start of the program. numGrids, spacing, windowToWires, may all need to be adjusted depending upon the mounted configuration. Note the structure of the printValues() function. The user needs to comment/uncomment the sections that correspond to the value generation they desire. The possible iterations are many, but they all center around the 2-D collectionRegions array. This array contains the summed energy losses by grid region (first array dimension), for every ion simulated (second array dimension). Refer to the processSRIMData() function for reference to this array construction. See TRIFIC ELog post with ID 50 for examples of PID and Bragg plots.

The process for generating Bragg plots is as cumbersome as generating EVERYTHING was before the interface was made. Making a plotter for Bragg curves is something to do moving forward. The C++ code for PID plots is also hard-coded and should be made more versatile. The wrapper currently existing in the interface is only a temporary solution.

Another common piece of information we use the simulations for is to find an operating pressure for the chamber. Ideally, we'd like the farthest-travelling ion to stop just before the end of the ~28cm TRIFIC chamber. Writing a function to sweep over a pressure range and return the optimal pressure is something else to do.

I have made the program responsible for all file naming to ease user input. Currently, there may be only one ion of a given mass and energy per directory in TRIMDATA. Re-creating a batch file with the same ion parameters will overwrite the original input file, and simulating will overwrite any simulation output for the ion. There are definitely cases where this is not ideal, and adding some extra keyword arguments to allow multiple ions (possibly with slighly different target parameters) per experiment would be a useful addition.

Some other thoughts left behind, pertaining to the simulations & analysis:

The TRIM calculations performed up to this point have all assumed that ions enter the chamber at a single position, and then experience straggling as they pass through the layers. A more realistic situation would be that the ions enter at a range of positions and more importantly, angles. This could be effected in the simulations by applying a random entering angle and position to each ion, and then adjusting the z-positions of every collision accordingly. The position distribution in z is all we are concerned with.

The quoted section below is from the TRIM documentation, and details a more accurate way of calculating the energy deposition. It should be implemented for some fine improvement:
"Referring to 'COLLISON.txt': This file shows the three-dimensional position of each major collision between the ion and the target atoms. It also shows in column six the instantaneous electronic energy loss of the ion to the target in units of eV/Å. If you need the three-dimensional electronic energy loss of the ion to the target, you now have all the necessary information. To obtain the energy deposited, calculate the path length between two successive collisions and multiply by the specific energy loss. For example, the distance between the first two collisions shown above is 16.3Å, with an energy loss of 15.86 eV/Å. This means the ion loses 258 eV into electronic excitations in this segment."

On the wiki, and in the sample simulation file, the absolute minimum distance for simulation is given as 279.18 mm with 21 grids installed. This neglects the bending of the mylar window towards the upstream beam line, roughly estimated to be about a centimetre. TRIM simulates incoming ions with no space distribution as to their entry, it is all from a single point. This is not physically the case with the upstream beam line arriving at TRIFIC, and also the fact of the window bend being convex means that the deviation from center of an ion's entering position will affect the point at which it first hits the aluminized layer. Such accuracy improvements may be overkill, but are interesting to consider as a future improvement. 

