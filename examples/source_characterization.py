"""
Uses a Hann window and plots the PSD and recorded time-domain voltage to screen.
"""
import numpy as np
import pandas as pd
from DataAquisition import SCPIDevice, twosToVoltage
from Plotting import prettifyPlot, plt
import scipy.signal.windows as windows
import time

desiredMeasurements = 4800 # This ensures each frequency bin is 1Hz wide.
halfMeasurements = int(desiredMeasurements/2)
samplingFrequency = 9.76 # kHz
frequencies = np.arange(0, samplingFrequency/2, samplingFrequency/desiredMeasurements)
wavelengths = np.arange(850, 1700, 5)

startNoiseFrequency = 0.2 # kHz, this is after the roll-off of the 60Hz noise.
signalAmplitude = 1.5
stopNoiseFrequency = samplingFrequency/2
noiseBandwidth = (stopNoiseFrequency - startNoiseFrequency)
startNoiseBin = int(startNoiseFrequency / samplingFrequency * desiredMeasurements)

device = SCPIDevice()
device.Configure(desiredMeasurements)
device.wavelength = wavelengths[0]

times = np.arange(0, desiredMeasurements / samplingFrequency, 1/samplingFrequency)
currents = np.array([])
noises = np.array([])
for wavelength in wavelengths:
	device.wavelength = wavelength
	device.motorEnable = False
	time.sleep(0.1)
	data = device.Measure()
	voltages = twosToVoltage(data)
	dcOffset = np.mean(voltages)
	dcCurrent = abs(dcOffset - 1.678)*1000 # units of nA
	currents =np.append(currents, dcCurrent)

	voltagesOffset = voltages - dcOffset
	hannWindow = windows.hann(desiredMeasurements) / np.sqrt(np.mean(np.square(windows.hann(desiredMeasurements))))
	voltageSpectralPower = np.square(np.abs(np.fft.fft(voltagesOffset*hannWindow/len(voltagesOffset))))[0:halfMeasurements]*2
	voltageNoiseRMS = np.sqrt(np.sum(voltageSpectralPower[startNoiseBin:]) )
	voltageNoisePSD = 1e9 * voltageNoiseRMS / np.sqrt(noiseBandwidth * 1e3) # in nV / rtHz, or fA/rtHz
	noises = np.append(noises, voltageNoisePSD)
	print(f'Current: {dcCurrent:.3f} nA')
	print(f'Noise: RMS: {voltageNoiseRMS*1e6:.1f}uV, PSD: {voltageNoisePSD:.1f}nV/rtHz')

# The single-sided voltage spectral power (rms, by definition)

device.wavelength = wavelengths[0]
device.motorEnable = False

pdData = pd.DataFrame(data={'Wavelength (nm)': wavelengths, 'Current (nA)': currents, 'Noise (fA/rtHz):': noises})
pdData.to_csv('source_data.csv', index=False)

fig, ax = plt.subplots()
ax.plot(wavelengths , currents)
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Current (nA)')
ax.set_title('Current Spectra')
prettifyPlot(ax, fig)
plt.show()
