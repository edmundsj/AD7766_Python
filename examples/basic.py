import sys
from DataAquisition import SCPIDevice

baudRate = 115200
myDevice = SCPIDevice(baudRate=baudRate, serialType='pyserial')
measuredData = myDevice.Measure()
print(f'Data from single measured data point: {measuredData}')
myDevice.Configure(10) # Configures the SCPI device to take 10 measurements

newData = myDevice.Measure() # Performs a measurement
myDevice.closeDevice()
print(f'Data from multiple measurements: {newData}')
