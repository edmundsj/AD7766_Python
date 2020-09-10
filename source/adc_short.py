# NOTE: should be run from the main directory.
from DataAquisition import SCPIDevice
#from DataAquisition import AD7766_postprocessing
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal.windows

desiredMeasurements = 10000
samplingFrequency = 125 # 125kHz is the actual measured sampling rate, correct within 1Hz.
samplingPeriod = 1 / samplingFrequency
averaged = False

startSystemTime = time.perf_counter()
device = SCPIDevice()
device.Configure(desiredMeasurements)
rawData = device.Measure()
endSystemTime = time.perf_counter()
deltaSystemTime = endSystemTime - startSystemTime

# Print byte rate / bit rate to the screen
numberBytes = len(dataBuffer)
byteRate = maxBytes / deltaSystemTime
bitRate = byteRate * 8
print(f'Final byte count: {numberBytes}. Data rate of {byteRate} MBps / {bitRate} Mbps')


numberSamples = len(adcValues)
samplingTimes = samplingPeriod * np.arange(0, numberSamples, 1)
frequencies = samplingFrequency / numberSamples * np.arange(0, numberSamples, 1)

zeroMeanData = adcValues - np.mean(adcValues)
fftData = 10*np.log10(np.square(np.abs(np.fft.fft(zeroMeanData*2/numberSamples))))
fftDataRMS = fftData - 3 # subtract 3dB, or a factor of 2 in power
signalAmplitudeVpp = 0.05
signalFrequency = 1
hanningCorrectionFactor = 1.633

hanningWindow = hanningCorrectionFactor * scipy.signal.windows.hann(numberSamples)
hanningFilteredData = zeroMeanData * hanningWindow
hanningFFTDataPower = np.square(np.abs(np.fft.fft(hanningFilteredData*2/numberSamples)))
hanningFFTDataPowerRMS = hanningFFTDataPower / 2
convolutionKernel = np.ones(500)/500.0
hanningFFTDataPowerAverage = np.convolve(hanningFFTDataPowerRMS, convolutionKernel, mode='same')
hanningFFTDataPowerAveragedBV = 10*np.log10(hanningFFTDataPowerAverage)
hanningFFTDataPowerdBV = 10*np.log10(hanningFFTDataPowerRMS)

np.savetxt('data/arduino_raw_data.csv', dataBuffer, delimiter=',')
np.savetxt('data/adc_values.csv', adcValues, delimiter=',')

samplingWindow = samplingPeriod * numberSamples
#theoreticalPSD = np.square(signalAmplitudeVpp/2*np.sinc((frequencies-signalFrequency)* samplingWindow)) / 2
theoreticalData = hanningWindow * signalAmplitudeVpp / 2 * np.cos(2*np.pi * signalFrequency * samplingTimes)
theoreticalPSD = np.square(np.abs(np.fft.fft(theoreticalData*2/numberSamples))) / 2 # The 2 converts from amplitude to RMS
if(averaged):
    theoreticalPSD = np.convolve(theoreticalPSD, convolutionKernel, mode='same')

theoreticalPSD = 10*np.log10(theoreticalPSD)

fig, axes = plt.subplots(1, 2)
axes[0].plot(samplingTimes, 1000*zeroMeanData)
axes[0].set_xlabel('time (ms)')
axes[0].set_ylabel('voltage (mV)')
axes[0].set_xlim(0, 5)

if(averaged):
    axes[1].plot(frequencies[1:], hanningFFTDataPowerAveragedBV[1:], 'b')
else:
    axes[1].plot(frequencies[1:], hanningFFTDataPowerdBV[1:], 'b')
    #axes[1].plot(frequencies[1:], fftDataRMS[1:], 'b')
axes[1].set_xlabel('frequency (kHz)')
axes[1].set_ylabel('dBV rms')
axes[1].set_ylim(-180, 0)
axes[1].set_xlim(0.0, 62.5)
axes[1].plot(frequencies[1:], theoreticalPSD[1:], 'g', linestyle='dashed')

#print(noiseAverage)
plt.show()
