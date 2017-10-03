/**
 * g++ -g -O0 -o TRIFICsim TRIFICsim.cpp      ------------    compiler line
 * To run program, use following command:
 *		cat fileName (multiple files) |./TRIFICsim
 * or:
 *		./TRIFICSim fileName (multiple files)
 * Can handle SRIM collision data from multiple isotopes
 * Ability to change (multiple) parameters from the command line:
 *		./TRIFICSim --parameter value fileName
**/



/**
 * Program Name: TRIFIC Simulation, v0
 * File: TRIFICSim.cpp
 * Last Modified By: Brennan Undseth
 * Date: 2017-10-3
 * Purpose: This program is meant to take ion collision data (as simulated in TRIM) and simulate
 *	particle identification. This should be able to simulate usage of the TRIFIC detector with 
 * 	multiple isotopes of similar atomic mass number (example: Sr-94, Rb-94, and Mo-94). The 
 * 	simualtion is to determine if the expected constituents of a cocktail beam will be 
 *	distinguishable, and thus will help determine what to expect for beam tuning and the 
 *	performance of diagnostics.
**/

#include <iostream>
#include <istream>
#include <algorithm>
#include <string>
#include <fstream>
#include <vector>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <cstring>
#include <math.h>
#include <cmath>
#include <utility>
#include <string>

using namespace std;


int 	numIons 	= 10000;	// upper limit of ions that can be processed 
int	numGrids 	= 21;		// number of grids installed
float	spacing 	= 12.77;	// transverse distance between wire grids
float	windowToWires	= 23.78;	// transverse distance from window to first wires
float	windowToEnd	= 505.52;	// transverse distance from window to end of chamber
int	numIsotopes 	= 25;		// upper limit of unique isotopes that can be processed				
int   	arraySize 	= 10000; 	// size of all arrays in this program

// processSRIMData() fills the collectionRegions 2-D array with summed energies for each ion
// combination, partitioning, and other value printing done in printValues()

float processSRIMData (istream& srimCollisionDataSource, string isotopeName[], float isotopeMass[], float initialEnergy[], int ionNum[], int *totalIonsP, int *isotopeCountP, float collectionRegions[][10000]) {

	float 	X[arraySize]; 			// array of collision x-positions
	float	Z[arraySize]; 			// array of collision z-positions
	float 	E[arraySize]; 			// array of ion energies at each collision
	int 	index, ionCount;		
	string 	line;

	int 	colNum 		= 0; 		// counter of collisions in current input file
	int 	totalColNum 	= 0; 		// counter of collisions in all input files
	int	maxNum 		= 1;		
	bool 	readIon 	= false;

	while (getline(srimCollisionDataSource, line)) {
		
		// recording isotope names
		if ( (line.length() > 30) && (line.substr (6,8).compare("Ion Name") == 0)) { 

			isotopeName[*isotopeCountP] = line.substr (23,2);

		}

		// recording isotope masses
		if ( (line.length() > 30) && (line.substr (6,8).compare("Ion Mass") == 0)) { 

			isotopeMass[*isotopeCountP] = strtof((line.substr (22,7)).c_str(),NULL); 
		}

		// recording initial energy of isotope
		if ( (line.length() > 30) && (line.substr (6,10).compare("Ion Energy") == 0)) { 
			
			initialEnergy[*isotopeCountP] = strtof((line.substr (18,11)).c_str(),NULL);
			// incrementing a counter of all ions processed
			*totalIonsP += ionNum[*isotopeCountP];

			// incrementing a counter of all isotopes processed
			*isotopeCountP += 1;

		}

		// recording values from collisions
		if ( line.substr (1,1).compare("0") == 0 || line.substr (1,1).compare("1") == 0 ) {

			readIon = true;
			ionCount = strtof((line.substr(1,5)).c_str(),NULL);
			E[colNum]  = atof ( (line.substr (7,9)).c_str() );
			X[colNum]  = atof ( (line.substr (17,10)).c_str() );
			Z[colNum]  = atof ( (line.substr (39,10)).c_str() ); 
			colNum += 1;
		
		// end of ion's collisions reached, summing performed
		} else {
	
			if ( readIon == true ) {
				
				// unique index to the ion
				index = ionCount + *totalIonsP;
				// incrementing counter of ions processed of this isotope
				ionNum[*isotopeCountP] += 1;
				
				// summing energy loss into collection regions
				for (int i = 0; i < colNum; i++) {
					
					// converting angstrom to mm; keV to MeV
					float collisionDepth 	= X[i]*0.0000001;				
					float collisionVertical = Z[i]*0.0000001;
					float collisionEnergy 	= (E[i-1]-E[i])/1000;
					
					// summing energy loss between first and last grid
					if ((collisionDepth > windowToWires) && (collisionDepth < windowToWires+spacing*numGrids)) {
						
						// determining collection region of collision 
						int bin = (int)floor(((collisionDepth - windowToWires) + (collisionVertical / sqrt(3))) / spacing)+1;
						// adding energy to appropriate region
						
						collectionRegions[bin][index] += collisionEnergy;

					}

					// summing region between window to first wires
					// beware that extended drift not acounted for
					// else if (collisionDepth <= windowToWires) {
						
						//
						
					// }
					
					// summing region beyond final grid, before chamber end
					// beware that extended drift not acounted for
					// unlikely that collisions at far end will contribute
					// else if ((collisionDepth >= windowToWires+spacing*numGrids) && (collisionDepth <= )) {

						//					
			
					// }
						
				}

				readIon = false;
				totalColNum += colNum;
				colNum = 0;

			} else {

				readIon = false;

			}
		}

	}

}

// printValues() requires the user to comment/uncomment or write entirely new commands for...
// ... printing the desired outputs
float printValues(istream& srimCollisionDataSource, string isotopeName[], float isotopeMass[], float initialEnergy[], int ionNum[], int *totalIonsP, int *isotopeCountP, float collectionRegions[][10000]) {
	
	// LOOP PRINTS ION BY ION VALUES; FOR PID PLOTS
	printf("\nPID for %s-%.0f\n\n", isotopeName[*isotopeCountP-1].c_str(), ceil(isotopeMass[*isotopeCountP-1]));
	for (int i = *totalIonsP+1; i < *totalIonsP+ionNum[*isotopeCountP]+1; i++) { 

		// PRINTING FOR 3-3-4 PARTITION SCHEME
		float firstPart	  = 0;
		float secondPart  = 0;
		float thirdPart   = 0;

		for (int j = 1; j < 7; j++) {

			firstPart += collectionRegions[j][i];

		}

		for (int j = 7; j < 13; j++) {

			secondPart += collectionRegions[j][i];

		}

		for (int j = 13; j < 21; j++) {

			thirdPart += collectionRegions[j][i];

		}
			
		// PRINT GRIDS 1-3 V. 4-6	
	//	printf("%4.2f, %4.2f\n", firstPart, secondPart);
		
		// PRINT GRIDS 1-3 V. 7-10
		printf("%4.2f, %4.2f\n", firstPart, thirdPart);

		// PRINT GRIDS 4-6 V. 7-10
	//	printf("%4.2f, %4.2f\n", secondPart, thirdPart);

	}	
	
	// LOOP PRINTS ISOTOPE BY ISOTOPE VALUES; FOR BRAGG PLOTS
	/*
	printf("\nBragg for %s-%.0f\n\n", isotopeName[*isotopeCountP-1].c_str(), ceil(isotopeMass[*isotopeCountP-1]));
	for (int i = 1; i < numGrids; i+=2) {

	 	float collected = 0;
		
		for (int j = *totalIonsP+1; j < *totalIonsP+ionNum[*isotopeCountP]+1; j++) {
	
			collected += (collectionRegions[i][j] + collectionRegions[i+1][j]);

		} 
		
		// prints the inner signal grid collection from 1 to (numGrids-1)/2
		printf("%4.2f\n", (i+1)/2, collected);	

	}	
	*/
}

int main(int argc, char* argv[]) {

	int 	ionNum[arraySize]; 		// array for numbering ions of each isotope
	int	isotopeCount = 0; 		// counter for the number of isotopes
	int	totalIons = 0; 			// counter for the total ions
	string 	fileName;
	float 	initialEnergy[arraySize]; 	// array of isotope initial energies
	float 	isotopeMass[arraySize]; 	// array of ion masses.

	string *isotopeName = new string[arraySize];

	// array of collection regions within TRIFIC, for each ion
	float 	collectionRegions[numGrids+1][10000];  

	// The if/else case below represents the two methods of calling TRIFICsim
	
	// reads through the number of files after the call: "./TRIFICsim Si.txt Mo.txt ..."
	if (argc > 1) {

		// each argument in the call is looped over
		for (int i = 1; i < argc; i++) { 

			// argument is converted to a string for ease of manipulation
			string argv_ = argv[i];
			fileName = argv_;
			ifstream myfile;
			myfile.open(fileName.c_str());

			// reads that the file is open and completes the subroutine
			if(myfile.is_open()) { 

				processSRIMData(myfile, isotopeName, isotopeMass, initialEnergy, ionNum, &totalIons, &isotopeCount, collectionRegions);
				printValues(cin, isotopeName, isotopeMass, initialEnergy, ionNum, &totalIons, &isotopeCount, collectionRegions);

			}
			
		}

	// Processes and prints values from the line "cat filename (multiple) | ./TRIFICsim"
	} else { 

		processSRIMData(cin, isotopeName, isotopeMass, initialEnergy, ionNum, &totalIons, &isotopeCount, collectionRegions);
		printValues(cin, isotopeName, isotopeMass, initialEnergy, ionNum, &totalIons, &isotopeCount, collectionRegions);
		
	}

}
