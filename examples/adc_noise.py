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

signalFrequency = 0.1 # kHz
startNoiseFrequency = 0.2 # kHz, this is after the roll-off of the 60Hz noise.
signalAmplitude = 1.5
stopNoiseFrequency = samplingFrequency/2
noiseBandwidth = (stopNoiseFrequency - startNoiseFrequency)
startNoiseBin = int(startNoiseFrequency / samplingFrequency * desiredMeasurements)

device = SCPIDevice()
device.Configure(desiredMeasurements)
data = device.Measure()
device.waitForMotor()
times = np.arange(0, desiredMeasurements / samplingFrequency, 1/samplingFrequency)
voltages = twosToVoltage(data)
dcOffset = np.mean(voltages)
print(f'Offset: {dcOffset:.3f} V')
voltagesOffset = voltages - dcOffset
voltagesTheoretical = signalAmplitude * np.cos(2*np.pi*signalFrequency * times)

#fig, ax = plt.subplots()
#ax.plot(voltagesTheoretical)
#ax.plot(voltages)
#plt.show()

hannWindow = windows.hann(desiredMeasurements) / np.sqrt(np.mean(np.square(windows.hann(desiredMeasurements))))
voltagesTheoretical *= hannWindow

# The single-sided voltage spectral power (rms, by definition)
voltageSpectralPower = np.square(np.abs(np.fft.fft(voltagesOffset*hannWindow/len(voltagesOffset))))[0:halfMeasurements]*2
voltageTheoreticalSpectralPower = np.square(np.abs(np.fft.fft(voltagesTheoretical/len(voltagesTheoretical))))[0:halfMeasurements]*2

voltageNoiseRMS = np.sqrt(np.sum(voltageSpectralPower[startNoiseBin:]) )
voltageNoisePSD = 1e9 * voltageNoiseRMS / np.sqrt(noiseBandwidth * 1e3) # in nV / rtHz
print(f'Voltage Noise ---\nRMS: {voltageNoiseRMS*1e6:.1f}uV, PSD: {voltageNoisePSD:.1f}nV/rtHz')

pdData = pd.DataFrame(data={'Time (ms)': times, 'Voltage (mV)': voltages})
pdData.to_csv('adc_data.csv', index=False)

fig, ax = plt.subplots()
ax.plot(times, voltagesOffset*1e3)
ax.set_xlabel('time (ms)')
ax.set_ylabel('Voltage (mV)')
ax.set_title('Time Domain Voltage')
prettifyPlot(ax, fig)
#plt.show()

fig, ax = plt.subplots()
ax.plot(frequencies, 10*np.log10(voltageSpectralPower))
#ax.plot(frequencies, 10*np.log10(voltageTheoreticalSpectralPower + np.square(260*1e-9)))
ax.legend(['Measured'])
ax.set_xlabel('f (kHz)')
ax.set_ylabel('dBVrms')
ax.set_title('Signal Spectral Power')
ax.set_ylim(-200, 0)
prettifyPlot(ax, fig)
plt.show()

