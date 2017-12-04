import os
import pathlib
import subprocess
from compoundparse import compoundparse
from ionparse import ionparse

class Batch:
	def __init__(self,saveto,ion,mass,energy,number,angle=0,corr=0,autosave=10000):
		# Batch object must be initialized with an ion and location for the Batch object to write a .IN file to within the TRIMDATA dir in the user's home dir
		# (an example location could be 'TRIFIC 11-19-2017' where all batch files and simulation outputs for a single experiment will be stored). To define the ion,
		# give the symbol (e.g. 'Ga' for Gallium), its mass in amu (e.g. 80 for 80Ga), its energy in keV (e.g. 381600 for 80Ga @ 4.77MeV/u), and the number of ions
		# to simulate (50 is usually a reasonable number). Other ion parameters such as the Angle, Bragg Correction, and AutoSave Number are set to TRIM defaults
		# (0, 0, and 10000 respectively) as they do not need to be changed for most simulations.

		self.saveto = saveto # save to IN/OUT of this given dir in TRIMDATA i.e check everything exists
		self.ion = ion # pull from text file along with all additional parameters
		self.mass = mass
		self.energy = energy
		self.number = number
		self.angle = angle
		self.corr = corr
		self.autosave = autosave

		self._atoms = ionparse()
		self._compounds = compoundparse()

		self._fnames = [] # stores file names written using data from this object

		# create empty dictionary for target layers (not a list so that layers may be defined out of order)
		self._layers = {}
	def addTargetLayer(self,lnumber,lname,width,density=0,corr=1,gas=False,compound=True):
		# Adds a layer to the list: give integer number of layer (begin with 1), name as a string (must exactly match either an atom or compound in the TRIM catalogue),
		# width (in Angstrom), density (in g/cm3; don't define if you would like to use the TRIM default), compound correction (either define alongside using the TRIM
		# gui, or don't define at all which works fine for most simulations; could also hardcode this into the compound parser), gas bool (True if the layer is gaseous),
		# and compound bool (False if we are using a single atom layer that is not already given in the compount directory; can hardcode more compounds in the compound
		# parser as necessary as has already been done for CF4)
	 	self._layers[str(lnumber)]=	{
					'Name': lname,
					'Width': width,
					'Density': density,
					'Corr': corr,
					'Gas': gas,
					'Compound': compound
			  		}
	def nextIon(self,ion,mass,energy,number,angle=0,corr=0,autosave=10000):
		# Given an existing batch object, changes the ion data and writes another .IN file with the same target info
		self.ion = ion
		self.mass = mass
		self.energy = energy
		self.number = number
		self.angle = angle
		self.corr = corr
		self.autosave = autosave

		self.makeBatch()
	def makeBatch(self):
		# Method writes .IN file for TRIM to run in batch mode
		
		###### create file to write to ######
		self._fnames.append(str(self.mass)+self.ion+str(self.energy)+'.txt')

		###### get ion parameters ######
		# quick and dirty search for atomic number
		for atnb, atdata in self._atoms.items():
			if atdata['Symbol'] == self.ion:
				self._Z1 = atnb
		
		###### get target parameters ######
		# get number of layers
		self._nolayers = len(self._layers.keys())
		# get atomic makeup of layers
		self._layermakeup = [] # list corresponding to number of atoms in each layer, in order
		for i in range(1,self._nolayers+1):
			if self._layers[str(i)]['Compound'] == False:
				# look up atom in atom dictionary
				for atnb, atdata in self._atoms.items():
					if atdata['Symbol'] == self._layers[str(i)]['Name']:
						self._layers[str(i)]['Atom List'] = [[int(atnb), 1.0]]
						if self._layers[str(i)]['Density'] == 0:
							self._layers[str(i)]['Density'] = atdata['Density']
				self._layermakeup.append(1)
			else:
				# look up compound in compound dictionary
				self._layers[str(i)]['Atom List'] = self._compounds[self._layers[str(i)]['Name']]['Stoich']
				if self._layers[str(i)]['Density'] == 0:
					self._layers[str(i)]['Density'] = self._compounds[self._layers[str(i)]['Name']]['Density']
				self._layermakeup.append(len(self._layers[str(i)]['Atom List']))
		self._nolayeratoms = sum(self._layermakeup)
		# compile atomic data for layers
		self._targetatoms = [] # list of dictionaries for each atom, indexed by position in layers
		for i in range(1,self._nolayers+1):
			for j in self._layers[str(i)]['Atom List']:
				self._targetatoms.append(	{
								'Symbol': self._atoms[str(j[0])]['Symbol'],
								'Z': j[0],
								'Mass': self._atoms[str(j[0])]['Natural Weight'],
								'Stoich': j[1],
								'Disp': self._atoms[str(j[0])]['Disp'],
								'Latt': self._atoms[str(j[0])]['Latt'],
								'Surf': self._atoms[str(j[0])]['Surf'] 
								})
		###### write .IN file ######
		# write ion data and options as selected below (some are hardcoded)
		# print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False) from docs

		# create directories if they do not already exist
		savetodir = os.path.join(self._homedir,'TRIMDATA',self.saveto)
		pathlib.Path(os.path.join(savetodir,'IN')).mkdir(parents=True, exist_ok=True)
		pathlib.Path(os.path.join(savetodir,'OUT')).mkdir(parents=True, exist_ok=True)
		# write to a file given ion information; will overwrite any existing file with the same name (same ion data)
		with open(os.path.join(savetodir,'IN',self._fnames[-1]),'w') as infile:
			print('==> SRIM-2013.00 This file controls TRIM Calculations.', end='\r\n', file=infile)
			print('Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.', end='\r\n', file=infile)
			print('{} {} {} {} {} {} {}'.format(self._Z1, self.mass, self.energy, 0, self.number, 0, 10000), end='\r\n', file=infile)
			print('Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Reminders', end='\r\n', file=infile)
			print('{} {} {}'.format(1, 0, 0), end='\r\n', file=infile)
			print('Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Ion;2=Ion+Recoils), Special EXYZ.txt file', end='\r\n', file=infile)
			print('{} {} {} {} {} {}'.format(0, 0, 0, 0, 2, 0), end='\r\n', file=infile)
			print('Target material : Number of Elements & Layers', end='\r\n', file=infile)
			print('\"{} ({}) into '.format(self.ion, self.energy), end='', file=infile)
			for i in range(1,self._nolayers+1):
				if i == self._nolayers:
					print('{}\" '.format(self._layers[str(i)]['Name']), end='', file=infile)
				else:
					print('{}+'.format(self._layers[str(i)]['Name']), end='', file=infile)
			print('{} {}'.format(self._nolayeratoms, self._nolayers), end='\r\n', file=infile)
			print('PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]', end='\r\n', file=infile)
			print('{} {} {}'.format(5, 0, 0), end='\r\n', file=infile)
			print('Target Elements:    Z   Mass(amu)', end='\r\n', file=infile)
			for i in range(len(self._targetatoms)):
				print('Atom {} = {} =   {} {}'.format(i+1, self._targetatoms[i]['Symbol'], self._targetatoms[i]['Z'], self._targetatoms[i]['Mass']), end='\r\n', file=infile)
			# print layer header
			print('Layer Layer Name / Width Density ', end='', file=infile)
			for i in range(len(self._targetatoms)):
				print('{}({}) '.format(self._targetatoms[i]['Symbol'], self._targetatoms[i]['Z']), end='', file=infile)
			print('', end='\r\n', file=infile)
			print('Numb. Description (Ang) (g/cm3) ', end='', file=infile)
			for i in range(len(self._targetatoms)):
				print('Stoich ', end='', file=infile)
			print('', end='\r\n', file=infile)
			# print layer information, this is the clunkiest part
			printedstoich = 0 # track printing of stoichiometry for each atom in each layer
			for i in range(1,self._nolayers+1):
				print(' {} \"{}\" {} {} '.format(i, self._layers[str(i)]['Name'], self._layers[str(i)]['Width'], self._layers[str(i)]['Density']), end='', file=infile)
				for j in range(printedstoich):
					print('{} '.format(0), end='', file=infile)
				for j in range(printedstoich,printedstoich+len(self._layers[str(i)]['Atom List'])):
					print('{} '.format(self._targetatoms[j]['Stoich']), end='', file=infile)
					printedstoich += 1
				for j in range(self._nolayeratoms-printedstoich):
					print('{} '.format(0), end='', file=infile)
				print('', end='\r\n', file=infile)
			# print gas details for each layer
			print('0  Target layer phases (0=Solid, 1=Gas)', end='\r\n', file=infile)
			for i in range(1,self._nolayers+1):
				if self._layers[str(i)]['Gas'] == True:
					print('1 ', end='', file=infile)
				else:
					print('0 ', end='', file=infile)
			print('', end='\r\n', file=infile)
			# print compound correction for each layer
			print('Target Compound Corrections (Bragg)', end='\r\n', file=infile)
			for i in range(1,self._nolayers+1):
				print('{} '.format(self._layers[str(i)]['Corr']), end='', file=infile)
			print('', end='\r\n', file=infile)
			# print target atom displacement energies
			print('Individual target atom displacement energies (eV)', end='\r\n', file=infile)
			for i in range(self._nolayeratoms):
				print('{} '.format(self._targetatoms[i]['Disp']), end='', file=infile)
			print('', end='\r\n', file=infile)
			# print target atom lattice binding energies
			print('Individual target atom lattice binding energies (eV)', end='\r\n', file=infile)
			for i in range(self._nolayeratoms):
				print('{} '.format(self._targetatoms[i]['Latt']), end='', file=infile)
			print('', end='\r\n', file=infile)
			# print target atom surface binding energies
			print('Individual target atom surface binding energies (eV)', end='\r\n', file=infile)
			for i in range(self._nolayeratoms):
				print('{} '.format(self._targetatoms[i]['Surf']), end='', file=infile)
			print('', end='\r\n', file=infile)
			print('Stopping Power Version (1=2011, 0=2011)', end='\r\n', file=infile)
			print(' 0', end='\r\n', file=infile)
	def batchFiles(self):
		return self._fnames
		
def Sim(saveto,fs):
	homedir = os.path.expanduser('~')
	os.chdir(os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013'))

	for f in fs:
        	filetosim = f
        	tocopy = os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'IN',filetosim)
        	topaste = os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013','TRIM.IN')
        	subprocess.call(['cp',tocopy,topaste])
        	subprocess.call(['wine','TRIM.exe'])
        	copyto = os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013','SRIM Outputs','COLLISON.txt')
       		pasteto = os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT',filetosim)
        	subprocess.call(['cp',copyto,pasteto])

def PIDPlot(saveto,fs,bins=50,Xrange=0,Yrange=0):
	# Creates PID plots given a list of file names and a location where to look for them.
	# Takes up to 4 additional arguments to be passed to the plotter (args are checked to disallow potential shell insertion).
	# grids arg should be '12', '13', or '23' depending on how the anode signals in TRIFIC are collected.
	# bins arg determines how many bins exist in the x and y axes of the histogram. 50-100 is often a reasonable default.
	# Setting Xrange (Yrange) forces the x-axis (y-axis) range of the plot. 0 (default) lets the plotter pick a reasonable value given the range of the data.
	homedir = os.path.expanduser('~')
	if saveto not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA')):
		raise ValueError('Given directory not found')
	elif any(f not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT')) for f in fs):
		raise ValueError('File not found in given directory')
	elif any(isinstance(kwarg,int) is False for kwarg in [bins,Xrange,Yrange]):
		raise ValueError('Plotter arguments (bins, ranges) must be integers')
	os.chdir(os.path.join(homedir,'TRIFIC'))
	toplot = []
	for f in fs:
		toplot.append(os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT',f)
	tocall12 = './TsPID12 '
	tocall13 = './TsPID13 '
	tocall23 = './TsPID23 '
	for f in toplot:
		tocall12 = tocall12+f+' '
		tocall13 = tocall13+f+' '
		tocall23 = tocall23+f+' '
	tocall12 = tocall12+'| ./rp12 -nx '+str(bins)+' -ny '+str(bins)
	tocall13 = tocall13+'| ./rp13 -nx '+str(bins)+' -ny '+str(bins)
	tocall23 = tocall23+'| ./rp23 -nx '+str(bins)+' -ny '+str(bins)
	subprocess.Popen(tocall12,shell=True)
	subprocess.Popen(tocall13,shell=True)
	subprocess.Popen(tocall23,shell=True)

