"""
Note - it is very important that we grab exactly 1 second of data. If we do this, and we have an integer
number of periods, then we don't have to worry about the effects of the window.
We should be able to resolve signals about 10 times smaller than our expected signal (3e-4) before we hit
the noise floor.
"""
import numpy as np
import Plotting
plt = Plotting.plt
cmap = Plotting.cmap
from DataAquisition import SCPIDevice, twosToVoltage, twosToInteger

Tmax = 1000 # ms
binBandwidth = 1/Tmax # kHz
fSample = 125 # kHz
Npoints = Tmax*fSample
fSignal = 1
signalBin = int(np.round(Tmax * fSignal))
times = np.arange(0, Tmax, Tmax/Npoints)
noiseStd = 125e-6 # Integrated Noise (Voltage) from TIA (~500nV/rtHz)

deltaRMax = 3e-4 # maximum expected change in reflectance
photocurrentMax = 0.150 # peak photocurrent with R=1 (uA)
TIAGain = 1 # TIA gain (MOhm)
signalAmplitude = photocurrentMax * TIAGain * deltaRMax

signalTheoretical = signalAmplitude * np.sin(fSignal * 2*np.pi * times)
noiseTheoretical = np.random.normal(scale=noiseStd, size=Npoints)
totalTheoretical = signalTheoretical + noiseTheoretical
totalTheoreticalPowerSpectrum = np.square(np.abs(np.fft.fft(totalTheoretical/Npoints)))
totalTheoreticalPowerFiltered = totalTheoreticalPowerSpectrum[signalBin]

averageNoiseSpectralDensity = np.sum(np.square(np.abs(np.fft.fft(noiseTheoretical/Npoints)))) / (fSample ) # V^2 / kHz
expectedNoisePower = averageNoiseSpectralDensity * binBandwidth
expectedSNR = totalTheoreticalPowerFiltered / expectedNoisePower
relativeSensitivity = 1 / expectedSNR
print(relativeSensitivity)
