import sys
sys.path.append('../source')
from SCPIDevice import *

myDevice = SCPIDevice()
measuredData = myDevice.Measure()
print(measuredData)
myDevice.Configure(10)

newData = myDevice.Measure()
fetchedData = myDevice.Fetch()
myDevice.closeDevice()
print(newData)
print(fetchedData)
type(newData)
