import os
import pathlib
import subprocess
from . import compoundparse
from . import ionparse

class Batch:
	def __init__(self,saveto,ion,mass,energy,number,angle=0,corr=0,autosave=10000):
		# Batch object must be initialized with an ion and location for the Batch object to write a .IN file to within the TRIMDATA directory created in the cloned TRIFIC dir
		# (an example location could be 'TRIFIC 11-19-2017' where all batch files and simulation outputs for a single experiment will be stored). To define the ion,
		# give the symbol (e.g. 'Ga' for Gallium), its mass in amu (e.g. 80 for 80Ga), its energy in keV (e.g. 381600 for 80Ga @ 4.77MeV/u), and the number of ions
		# to simulate (50 is usually a reasonable number). Other ion parameters such as the Angle, Bragg Correction, and AutoSave Number are set to TRIM defaults
		# (0, 0, and 10000 respectively) as they do not need to be changed for most simulations.

		self.saveto = str(saveto)
		self.ion = ion
		self.mass = mass
		self.energy = energy
		self.number = number
		self.angle = angle
		self.corr = corr
		self.autosave = autosave

		self._atoms = ionparse.ionparse()
		self._compounds = compoundparse.compoundparse()

		###### Check for legitimate inputs ######
		# ion symbol must be valid; if we can't find the atomic number, quit out; this is a quick and dirty search
		self._Z1 = 0
		for atnb, atdata in self._atoms.items():
			if atdata['Symbol'] == self.ion:
				self._Z1 = atnb
		if self._Z1 == 0:
			raise ValueError('Please enter a valid chemical symbol (H - U)')
		# check number and autosave are integers
		if any(isinstance(arg,int) is False for arg in [number,autosave]):
			raise ValueError('Please enter an integer for number and autosave values')
		# check mass, energy, angle and corr are numbers
		for val in [mass, energy, angle, corr]:
			try:
				val = int(val)
			except ValueError:
				print('Please enter a number for mass, energy, angle and correction')
		# check numerical arguments are all positive
		if any(numarg <= 0 for numarg in [mass,energy,number,autosave]):
			raise ValueError('Only positive values are accepted for ion parameters')
		self._homedir = os.path.expanduser('~')
		self._fnames = [] # stores file names written using data from this object

		# create empty dictionary for target layers (not a list so that layers may be defined out of order)
		self._layers = {}
	def addTargetLayer(self,lnumber,lname,width=0,unit='Ang',density=0,pressure=0,corr=1,gas=0,compound=True):
		# Adds a layer to the list of target layers: give integer number to layer to define it's position in the list (begin with 1); give name as a string
		# (this must exactly match a named compound in TRIM's compound directory or a chemical symbol of an atom, if a compound does not exist, define it at the bottom
		# of compoundparse.py); give width (default unit is Angstrom unless indicated otherwise by the next argument; mandatory gas boolean (the state of a layer is not
		# automatically pulled from the default TRIM directories, so it is mandatory for the user to explicitly give a True or False argument here so that the simulation
		# does not spew garbage); optional change unit (default is Angstrom, but may use 'cm' or 'um' for convenience); optional density in g/cm3 (leave blank if you would
		# like to use the TRIM default, most are okay but some are quite off, so be wary); optional pressure in Torr (if layer is a gas, may give pressure in Torr, in which
		# case we will use ideal gas scaling from TRIM default (taken to be given at STP), a user defined density will always take precedence over a given pressure, and an
		# error will be thrown if a pressure is given for a non-gas layer); optional compound correction may be given (this is calculated on-the-fly by TRIM and is not
		# accessible (yet) to this interface, the default 1 works fine for most simulations, but if this correction is desired, the fastest way would be to use the TRIM gui
		# and copy the value it spits out here); an optional compound boolean (if left blank, we will assume the name of the layer given should be found in the compound
		# directory, if made False, we will assume the layer is a single atom to be found in TRIM's atom directory, if the layer name is not found in either place, an error
		# will be thrown)
		# NOTE: If using a layer that doesn't exist in the TRIM compound directory, simply hardcode your new layer at the bottom of the compound parser (a template is given). All
		# that is needed is the compound's density and stoich. After defining once, the layer may be used freely afterwards just like any other compound.
		# NOTE: There must be a layer 1 and a unique layer number for each layer. If there are gaps, an error will be raised saying that layers are missing.

		###### Check for legitimate inputs ######
		# Check for valid atom/compound name
		if compound == False:
			goodatom = False
			for atnb, atdata in self._atoms.items():
				if atdata['Symbol'] == lname:
					goodatom = True
			if goodatom == False:
				raise ValueError('Single atom layer not found')
		if compound == True:
			if lname not in self._compounds.keys():
				raise ValueError('Compound not found. Check name matches in compound directory, or add your own in the parser')
		# Check for valid width
		try:
			val = int(width)
		except ValueError:
			print('Width must be a number')
		# Check for valid unit
		if unit not in ['Ang','cm','um']:
			raise ValueError('Unit must be Ang, cm or um')
		# Check for valid density
		try:
			val = int(density)
		except ValueError:
			print('Density must be a number in g/cm3')
		if density != 0 or gas == False:
			# density takes precedence over pressure
			pressure = 0
		# Check for valid pressure
		try:
			val = int(pressure)
		except ValueError:
			print('Pressure must be a number in Torr')
		# Check for valid compound correction
		try:
			val = int(corr)
		except ValueError:
			print('Compound correction must be a number')
		# Make sure gas bool is properly defined
		if isinstance(gas,bool) is False:
			raise ValueError('Enter boolean True/False for gas variable')
		# Make sure all numerical values are positive or zero
		if any(numarg < 0 for numarg in [width,density,pressure,corr]):
			raise ValueError('Only positive values accepted for target layer parameters')

		###### Continue with valid inputs ######
		if unit == 'um':
			width *= 10000
		if unit == 'cm':
			width *= 100000000
		self._layers[str(lnumber)] = {
						'Name': lname,
						'Width': width,
						'Density': density,
						'Corr': corr,
						'Gas': gas,
						'Pressure': pressure,
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

		self._Z1 = 0
		for atnb, atdata in self._atoms.items():
			if atdata['Symbol'] == self.ion:
				self._Z1 = atnb
		if self._Z1 == 0:
			raise ValueError('Please enter a valid chemical symbol (H - U)')
		# check number and autosave are integers
		if any(isinstance(arg,int) is False for arg in [number,autosave]):
			raise ValueError('Please enter an integer for number and autosave values')
		# check mass, energy, angle and corr are numbers
		for val in [mass, energy, angle, corr]:
			try:
				val = int(val)
			except ValueError:
				print('Please enter a number for mass, energy, angle and correction')
		# check numerical arguments are all positive
		if any(numarg <= 0 for numarg in [mass,energy,number,autosave]):
			raise ValueError('Only positive values accepted for ion parameters')

		self.makeBatch()
	def makeBatch(self):
		# Method writes .IN file for TRIM to run in batch mode

		###### Check target layers are ok ######
		# make sure that the layering order is sensical ie. layer keys proceed '1' to '# of layers'
		self._nolayers = len(self._layers.keys())
		for i in range(1,self._nolayers+1):
			if str(i) not in self._layers.keys():
				raise ValueError('Missing layers')
		
		###### create file to write to ######
		self._fnames.append(str(self.mass)+self.ion+str(self.energy)+'.txt')

		###### get target parameters ######
		# get atomic makeup of layers
		self._layermakeup = [] # list corresponding to number of atoms in each layer, in order
		for i in range(1,self._nolayers+1):
			if self._layers[str(i)]['Compound'] == False:
				# look up atom in atom dictionary
				for atnb, atdata in self._atoms.items():
					if atdata['Symbol'] == self._layers[str(i)]['Name']:
						self._layers[str(i)]['Atom List'] = [[int(atnb), 1.0]]
						if self._layers[str(i)]['Density'] == 0:
							if self._layers[str(i)]['Gas'] == True:
								self._layers[str(i)]['Density'] = atdata['GasDens']
							else:
								self._layers[str(i)]['Density'] = atdata['Density']
				self._layermakeup.append(1)
			else:
				# look up compound in compound dictionary
				self._layers[str(i)]['Atom List'] = self._compounds[self._layers[str(i)]['Name']]['Stoich']
				if self._layers[str(i)]['Density'] == 0:
					self._layers[str(i)]['Density'] = self._compounds[self._layers[str(i)]['Name']]['Density']
				self._layermakeup.append(len(self._layers[str(i)]['Atom List']))
			if self._layers[str(i)]['Pressure'] != 0:
				self._layers[str(i)]['Density'] *= self._layers[str(i)]['Pressure']/760
				self._layers[str(i)]['Pressure'] = 0 # set back to 0 so density is not scaled for future ions
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
		# write ion data and options as input by user below (some are hardcoded)
		# parameters have been checked during target and ion input methods, so we should end up with a 'good' batch file (can't account for ignorance)

		# create directories if they do not already exist
		savetodir = os.path.join(self._homedir,'TRIFIC','TRIMDATA',self.saveto)
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

	if saveto not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA')):
		raise ValueError('Given directory not found')

	for f in fs:
		if f not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'IN')):
			print(f,'not found in given directory')
		else:
        		filetosim = f
        		tocopy = os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'IN',filetosim)
        		topaste = os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013','TRIM.IN')
        		subprocess.call(['cp',tocopy,topaste])
        		subprocess.call(['wine','TRIM.exe'])
        		copyto = os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013','SRIM Outputs','COLLISON.txt')
       			pasteto = os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT',filetosim)
        		subprocess.call(['cp',copyto,pasteto])

def PIDPlot(saveto,fs,Xrange=0,Yrange=0,Xbins=50,Ybins=50):
	# Creates PID plots (using existing code) given a list of file names and a location where to look for them.
	# Takes up to 4 additional arguments to be passed to the plotter (args are checked to disallow potential shell insertion).
	# grids arg should be '12', '13', or '23' depending on how the anode signals in TRIFIC are collected.
	# bins arg determines how many bins exist in the x and y axes of the histogram. 50-100 is often a reasonable default.
	# Setting Xrange (Yrange) forces the x-axis (y-axis) range of the plot. 0 (default) lets the plotter pick a reasonable value given the range of the data.
	homedir = os.path.expanduser('~')
	if saveto not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA')):
		raise ValueError('Given directory not found')
	elif any(f not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT')) for f in fs):
		raise ValueError('File not found in given directory')
	elif any(isinstance(kwarg,int) is False for kwarg in [Xbins,Ybins,Xrange,Yrange]):
		raise ValueError('Plotter arguments (bins, ranges) must be integers')
	os.chdir(os.path.join(homedir,'TRIFIC'))
	toplot = []
	for f in fs:
		toplot.append(os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT',f))
	tocall12 = './TRIFICsim 12 '
	tocall13 = './TRIFICsim 13 '
	tocall23 = './TRIFICsim 23 '
	for f in toplot:
		tocall12 = tocall12+f+' '
		tocall13 = tocall13+f+' '
		tocall23 = tocall23+f+' '
	tocall12 = tocall12+'| ./csv2h2 -nx '+str(Xbins)+' -ny '+str(Ybins)+' -rx '+str(Xrange)+' -ry '+str(Yrange)+' -gn 12'
	tocall13 = tocall13+'| ./csv2h2 -nx '+str(Xbins)+' -ny '+str(Ybins)+' -rx '+str(Xrange)+' -ry '+str(Yrange)+' -gn 13'
	tocall23 = tocall23+'| ./csv2h2 -nx '+str(Xbins)+' -ny '+str(Ybins)+' -rx '+str(Xrange)+' -ry '+str(Yrange)+' -gn 23'
	subprocess.Popen(tocall12,shell=True)
	subprocess.Popen(tocall13,shell=True)
	subprocess.Popen(tocall23,shell=True)
	
	# block and then kill histograms if user did not close them properly
	input("Press Enter to quit...")
	subprocess.run("killall csv2h2",shell=True)

def getFiles(saveto):
	# returns names of files in existing simulation directory for ease of plotting already simulated ions
	homedir = os.path.expanduser('~')
	if saveto not in os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA')):
		raise ValueError('Given directory not found')
	return os.listdir(os.path.join(homedir,'TRIFIC','TRIMDATA',saveto,'OUT'))
