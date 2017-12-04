from TRIMbatch.batch import *
import subprocess
import os

nameofexp = 'pyTEST'

batch = Batch(nameofexp,'Ga',80,381600,10)
batch.addTargetLayer(1,'Mylar',250000)
batch.addTargetLayer(2,'CF4',3000000000,0.0003808,gas=True)
batch.makeBatch()
batch.nextIon('Rb',80,308800,10)

Sim(nameofexp,batch.batchFiles())

#PIDPlot(nameofexp,batch.batchFiles())

