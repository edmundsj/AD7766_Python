# NOTE: should be run from the main directory.
from DataAquisition import SCPIDevice
import time

desiredMeasurements = 1000000
samplingFrequency = 125 # 125kHz is the actual measured sampling rate, correct within 1Hz.
samplingPeriod = 1 / samplingFrequency
averaged = False

device = SCPIDevice()
device.Configure(desiredMeasurements)

startSystemTime = time.perf_counter()
rawData = device.Measure()
endSystemTime = time.perf_counter()
deltaSystemTime = endSystemTime - startSystemTime

# Print byte rate / bit rate to the screen
numberBytes = len(rawData)
numberkB = numberBytes / 1e3
byteRatekB = numberkB / deltaSystemTime
byteRatekS = byteRatekB / 3
bitRatekb = byteRatekB * 8
print(f'Final byte count: {numberBytes}. Data rate of {byteRatekB} kBps / {bitRatekb} kbps / {byteRatekS} kSps')
