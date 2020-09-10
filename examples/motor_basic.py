import numpy as np
from DataAquisition import SCPIDevice, twosToVoltage
from Plotting import prettifyPlot, plt
import scipy.signal.windows as windows

device = SCPIDevice()
motorState = device.
times = np.arange(0, desiredMeasurements / samplingFrequency, 1/samplingFrequency)
voltages = twosToVoltage(data)
dcOffset = np.mean(voltages)
voltages -= dcOffset
voltagesTheoretical = signalAmplitude * np.cos(2*np.pi*signalFrequency * times)

#fig, ax = plt.subplots()
#ax.plot(voltagesTheoretical)
#ax.plot(voltages)
#plt.show()

hannWindow = windows.hann(desiredMeasurements) / np.mean(windows.hann(desiredMeasurements))
voltagesTheoretical *= hannWindow

# The single-sided voltage spectral power (rms, by definition)
voltageSpectralPower = np.square(np.abs(np.fft.fft(voltages*hannWindow/len(voltages))))[0:halfMeasurements]*2
voltageTheoreticalSpectralPower = np.square(np.abs(np.fft.fft(voltagesTheoretical/len(voltagesTheoretical))))[0:halfMeasurements]*2

voltageNoiseRMS = np.sqrt(np.sum(voltageSpectralPower[startNoiseBin:]) )
voltageNoisePSD = 1e9 * voltageNoiseRMS / np.sqrt(noiseBandwidth * 1e3) # in nV / rtHz
print(f'Voltage Noise ---\nRMS: {voltageNoiseRMS*1e6}uV, PSD: {voltageNoisePSD}nV/rtHz')

fig, ax = plt.subplots()
ax.plot(times, voltages*1e3)
ax.set_xlabel('time (ms)')
ax.set_ylabel('Voltage (mV)')
ax.set_title('Time Domain Voltage')
prettifyPlot(ax, fig)
plt.show()

fig, ax = plt.subplots()
ax.plot(frequencies, 10*np.log10(voltageSpectralPower))
ax.plot(frequencies, 10*np.log10(voltageTheoreticalSpectralPower))
ax.legend(['Measured', 'Theory'])
ax.set_xlabel('f (kHz)')
ax.set_ylabel('dBVrms')
ax.set_title('Signal Spectral Power')
ax.set_ylim(-200, 0)
prettifyPlot(ax, fig)
plt.show()

np.savetxt('aadc_data_raw_shorted_inputs.csv', data, delimiter=',')
