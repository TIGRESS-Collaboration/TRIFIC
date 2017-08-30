This repository contains SRIM simulation analysis programs for TRIFIC. The TRIFICsim program takes TRIM collision file(s) as input, and outputs deposited energy from ionization events for the different wire grid plane separated collection regions within TRIFIC. This data output can be processed in the csv2h2 file to produce a 2-D Particle Identification histogram. TRIMIN.sav is a template of TRIM calculation input for performing simulations in TRIM. It should be copied to the 'SR Restore' directory within SRIM, and then using the GUI to restore a saved calculation should bring up the input template.

More detailed information, and compilation instructions, can be found in the corresponding C++ files for each program. 

This repository has been modeled off of the simulation files for the TBragg, and represent a much simplified version iteration of that code.

= To-Do = 

The quoted section below is from the TRIM documentation, and details a more accurate way of calculating the energy deposition. It should be implemented for some fine improvement:
"Referring to 'COLLISON.txt': This file shows the three-dimensional position of each major collision between the ion and the target atoms. It also shows in column six the instantaneous electronic energy loss of the ion to the target in units of eV/Å. If you need the three-dimensional electronic energy loss of the ion to the target, you now have all the necessary information. To obtain the energy deposited, calculate the path length between two successive collisions and multiply by the specific energy loss. For example, the distance between the first two collisions shown above is 16.3Å, with an energy loss of 15.86 eV/Å. This means the ion loses 258 eV into electronic excitations in this segment." 

---

On the wiki, and in the sample simulation file, the absolute minimum distance for simulation is given as 279.18 mm with 21 grids installed. This neglects the bending of the mylar window towards the upstream beam line, roughly estimated to be about a centimetre. TRIM simulates incoming ions with no space distribution as to their entry, it is all from a single point. This is not physically the case with the upstream beam line arriving at TRIFIC, and also the fact of the window bend being convex means that the deviation from center of an ion's entering position will affect the point at which it first hits the aluminized layer. Such accuracy improvements may be overkill, but are interesting to consider as a future improvement. 

---
