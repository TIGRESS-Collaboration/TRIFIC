from TRIMbatch.batch import *

nameofexp = 'IRIS-2017-09-29' # name of file we will use to store TRIM inputs and outputs

# Create a Batch object that will save to our file. Begin with 20 atoms of 80Ga @ 5.91MeV/u.
batch = Batch(nameofexp,'Ga',80,472800,20)
# Our first layer is a 25 micron thick mylar window. We will use TRIM's default density since we know it's accurate.
batch.addTargetLayer(1,'Mylar',width=25,unit='um',gas=False)
# Our second layer is a 30cm long gas chamber filled with CF4 at 80 Torr.
# We defined this layer at the bottom of the compound parser, so we know its density at STP to be accurate.
batch.addTargetLayer(2,'CF4',width=30,unit='cm',pressure=80,gas=True)
# We can now generate a TRIM input file.
batch.makeBatch()
# We would also like to simulate 20 atoms of 80Se @ 5.65MeV/u through the same layers.
batch.nextIon('Se',80,452000,20)
# Repeat with 80Kr @ 5.47 MeV/u.
batch.nextIon('Kr',80,437600,20)
# Repeat with 80Rb @ 5.37 MeV/u.
batch.nextIon('Rb',80,429600,20)

# Simulate all of the input files our object created.
Sim(nameofexp,batch.batchFiles())

# Generate PID plots for TRIFIC for the simulations. Will block until user input and close generated histograms responsibly.
PIDPlot(nameofexp,batch.batchFiles(),Xrange=200,Yrange=200,Xbins=100,Ybins=100)

# Show all files we just created/simulated/processed.
print("Files generated:")
for f in getFiles(nameofexp):
	print(f)
