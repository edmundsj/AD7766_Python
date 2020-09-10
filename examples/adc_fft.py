# NOTE: should be run from the main directory.
from DataAquisition import SCPIDevice
from DataAquisition import twosToVoltage
import time
import numpy as np
from matplotlib import pyplot as plt

desiredMeasurements = 100000
halfDesiredMeasurements = int(desiredMeasurements/2)
samplingFrequency = 125 # 125kHz is the actual measured sampling rate, correct within 1Hz.
samplingPeriod = 1 / samplingFrequency
averaged = False
window = 'hann' # hann or boxcar

signalAmplitudeVpp = 0.05 # Volts
signalFrequency = 1 # kHz

device = SCPIDevice()
device.Configure(desiredMeasurements)

startSystemTime = time.perf_counter()
rawData = device.Measure()
endSystemTime = time.perf_counter()
deltaSystemTime = endSystemTime - startSystemTime
voltages = twosToVoltage(rawData)

# Print byte rate / bit rate to the screen
numberBytes = len(rawData)
numberkB = numberBytes / 1e3
byteRatekB = numberkB / deltaSystemTime
byteRatekS = byteRatekB / 3
bitRatekb = byteRatekB * 8
print(f'Final byte count: {numberBytes}. Data rate of {byteRatekB} kBps / {bitRatekb} kbps / {byteRatekS} kSps')

# Set up our hanning / boxcar window
if window == 'hann':
    energyCorrectionFactor = 1.633156
    windowData = energyCorrectionFactor * scipy.signal.windows.hann(desiredMeasurements)

elif window == 'boxcar':
    energyCorrectionFactor = 1
    windowData = np.ones(desiredMeasurements)

dcOffset = np.mean(voltages)
voltages = voltages * windowData
voltages -= dcOffset
voltagesFFTPowerOneSidedVrms = np.square(np.abs(np.fft.fft(voltages)))[0:halfDesiredMeasurements]*2
frequencies = np.arange(0, samplingFrequency/2, samplingFrequency/2/halfDesiredMeasurements)

theoreticalData = np.sin(2*np.pi*signalFrequency)

fig, ax = plt.subplots()
ax.plot(frequencies, 10*np.log10(voltagesFFTPowerOneSidedVrms))
ax.set_xlabel('f (kHz)')
ax.set_ylabel('dBVrms')
ax.set_title('Spectral Power')
