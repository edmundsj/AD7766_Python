import sys
sys.path.append('../source')
from SCPIDevice import *

baudRate = 115200
myDevice = SCPIDevice(baudRate=baudRate)
measuredData = myDevice.Measure()
print(f'Data from single measured data point: {measuredData}')
myDevice.Configure(10) # Configures the SCPI device to take 10 measurements

newData = myDevice.Measure() # Performs a measurement
fetchedData = myDevice.Fetch()
myDevice.closeDevice()
print(f'Data from multiple measurements: {newData}')
print(f'Same data, sent again from the Arduino: {fetchedData}')
