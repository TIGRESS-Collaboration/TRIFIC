import os

def ionparse():
	homedir = os.path.expanduser('~')
	os.chdir(os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013','Data'))

	# copied binding energies (for calculating target damage) by hand
	# I couldn't find them in all the TRIM text files :(
	# BE[0] is H and BE[91] is U [0,1,2] is Displacement E, Lattice BE and Surface BE respectively
	BE =   [[10,3,2], # H
		[5,1,2],
		[25,3,1.67],
		[25,3,3,38],
		[25,3,5,73],
		[28,3,7.41],
		[28,3,2],
		[28,3,2],
		[25,3,2],
		[5,1,2],
		[25,3,1.12],
		[25,3,1.54],
		[25,3,3.36],
		[15,2,4.7],
		[25,3,3.27],
		[25,3,2.88],
		[25,3,2],
		[5,1,2],
		[25,3,0.93],
		[25,3,1.83],
		[25,3,3.49],
		[25,3,4.89],
		[25,3,5.33],
		[25,3,4.12], # Cr
		[25,3,2.98],
		[25,3,4.34],
		[25,3,4.43],
		[25,3,4.46],
		[25,3,3.52],
		[25,3,1.35],
		[25,3,2.82],
		[15,2,3.88],
		[25,3,1.26],
		[25,3,2.14],
		[25,3,2],
		[5,1,2],
		[25,3,0.86],
		[25,3,1.7],
		[25,3,4.24],
		[25,3,6.33],
		[25,3,7.59],
		[25,3,6.83],
		[25,3,2],
		[25,3,6.69],
		[25,3,5.78],
		[25,3,3.91],
		[25,3,2.97], # Ag
		[25,3,1.16],
		[25,3,2.49],
		[25,3,3.12],
		[25,3,2.72],
		[25,3,2.02],
		[25,3,2],
		[5,1,2],
		[25,3,0.81],
		[25,3,1.84],
		[25,3,4.42],
		[25,3,4.23],
		[25,3,3.71],
		[25,3,3.28],
		[25,3,2],
		[25,3,2.16],
		[25,3,1.85],
		[25,3,3.57],
		[25,3,3.81], # Tb
		[25,3,2.89],
		[25,3,3.05],
		[25,3,3.05],
		[25,3,2.52],
		[25,3,1.74],
		[25,3,4.29],
		[25,3,6.31],
		[25,3,8.1],
		[25,3,8.68],
		[25,3,8.09],
		[25,3,8.13],
		[25,3,6.9],
		[25,3,5.86],
		[25,3,3.8],
		[25,3,0.64], # Hg
		[25,3,1.88],
		[25,3,2.08],
		[25,3,2.17],
		[25,3,1.5],
		[25,3,2],
		[25,3,2],
		[25,3,2],
		[25,3,2],
		[25,3,2],
		[25,3,5.93],
		[25,3,2],
		[25,3,5.42]]

	f = open("ATOMDATA","r")
	f.readline()
	f.readline()
	# initialize a dictionary, keys will be atomic number
	atoms = {}
	for line in f:
		l = line.split()
		atoms[l[0]]={
				'Symbol':		l[1],
				'Name':			l[2],
				'MAI Mass':		int(l[3]),
				'MAI Weight':		float(l[4]),
				'Natural Weight':	float(l[5]),
				'Density (g/cm3)':	float(l[6]),
				'Atomic Density':	float(l[7]),
				'Fermi Vel.':		float(l[8]),
				'Heat Subl':		float(l[9]),
				'GasDens(g/cm3)':	float(l[10]),
				'Gas Density':		float(l[11]),
				'Disp':			BE[int(l[0])-1][0],
				'Latt':			BE[int(l[0])-1][1],
				'Surf':			BE[int(l[0])-1][2]
		     	}
		if int(l[0]) == 92:
			break
	f.close()
	return atoms
