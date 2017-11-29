import os
import pickle
import re

homedir = os.path.expanduser('~')
os.chdir(os.path.join(homedir,'.wine','drive_c','Program Files (x86)','SRIM-2013','Data'))

f = open("Compound.dat","r",encoding='iso-8859-1')
f.readline()
f.readline()
# initialize a dictionary, keys will be compound names
compounds = {}
for line in f:
        # want lines beginning with names in quotations
	if line[0] == "\"":
		# name is in quotations
		m = re.search('(\".*\")',line)
		compname = m.group(0).strip('\"').strip('%')
		# rest of data is separated by commas
		# the if statement below fixes where TRIM misses a comma
		s = line[len(m.group(0)):].strip()
		if s[0] != ',':
			s = ","+s
		l = s.split(',')[1:]
		# value after name is density
		density = float(l[0])
		# next value is the number of elements
		Noe = int(l[1])
		# followed by Atomic No., Atom %, ...
		# create a list to hold the elements
		elements = []
		for i in range(0,2*Noe,2):
			elements.append([int(l[2+i]),float(l[3+i])])

		# normalize stoich to percentage
		totalelements = sum(x[1] for x in elements)
		for x in elements:
			x[1] /= totalelements
		compounds[compname] = {'Density': density, 'Stoich': elements}

###################################################
########## ADD ANY OTHER COMPOUNDS BELOW ##########
###################################################

# example adding CF4 (not included in TRIM's compound directory)
# The name should be the key, the density should be changed by the user when adding the layer
# and is pretty inconsequential. Stoich contains a list of pairs: [Atomic number,stoich fraction]
# i.e. [6,0.2] corresponds to Carbon, 1; [9,0.8] corresponds to Fluorine, 4
compounds['CF4'] = {'Density': 0.0003808, 'Stoich': [[6,0.2],[9,0.8]]}

###################################################
###################################################
###################################################

os.chdir(os.path.join(homedir,'TRIFIC','TRIMbatch'))
pickle.dump(compounds, open("compounds.p", "wb"))
f.close()

