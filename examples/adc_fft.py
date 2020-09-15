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
dcOffset = np.mean(voltages)

# Set up our hanning / boxcar window
if window == 'hann':
    energyCorrectionFactor = 1.633156
    windowData = energyCorrectionFactor * scipy.signal.windows.hann(desiredMeasurements)

elif window == 'boxcar':
    energyCorrectionFactor = 1
    windowData = np.ones(desiredMeasurements)

voltagesFFTPowerOneSidedVrms = 4*np.square(np.abs(np.fft.fft((voltages-dcOffset)*windowData)))[0:halfDesiredMeasurements]
frequencies = np.arange(0, samplingFrequency/2, samplingFrequency/2/halfDesiredMeasurements)

theoreticalData = np.sin(2*np.pi*signalFrequency)

fig, ax = plt.subplots()
ax.plot(frequencies, 10*np.log10(voltagesFFTPowerOneSidedVrms))
ax.set_xlabel('f (kHz)')
ax.set_ylabel('dBVrms')
ax.set_title('Spectral Power')
