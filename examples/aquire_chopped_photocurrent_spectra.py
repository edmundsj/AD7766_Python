"""
Measures the photocurrent spectra from 0.8um to 1.7um (the bandwidth of our InGaAs photodiode)
using previously-developed software for communicating with the AD7766 ADC and controlling a stepper motor

Considerations:
    The motor is the dominant source of delay in the system, so I will want to measure the photocurrent spectra
"""
import numpy as np
import pandas as pd
from DataAquisition import SCPIDevice, twosToVoltage, twosToInteger
from Plotting import prettifyPlot, plt

device = SCPIDevice()

startWavelength = 800
stopWavelength = 1700
stepWavelength = 5
wavelengthsToMeasure = np.arange(startWavelength, stopWavelength, stepWavelength)

fModulation = 1 # kHz
fSampling = 125 # kHz
samplesPerPeriod = fSampling / fModulation
modulationPeriodsPerMeasurement = 50 # average the pk-pk photocurrent measurements from ~20ms of data.
samplesPerMeasurement = int(modulationPeriodsPerMeasurement * fSampling / fModulation)
device.Configure(samplesPerMeasurement)

voltageMaximaDelayms = 0.312-0.543
voltageMinimaDelayms = voltageMaximaDelayms + 0.5 # The voltage minima is 0.05s delayed compared to the synchronization pulse
voltageMaximaDelaySamples = int(fSampling * voltageMaximaDelayms)
voltageMinimaDelaySamples = int(fSampling * voltageMinimaDelayms)

TIAResistance = 1e6 # Ohms
currents = np.array([])

# Set the current wavelength to 800nm, wait for the motor to stop rotating, and then turn it off to tamp down the noise.

device.motorEnable = True
device.wavelength = startWavelength
device.waitForMotor()
times = np.linspace(0, modulationPeriodsPerMeasurement / fModulation, samplesPerMeasurement) # ms

for wavelength in wavelengthsToMeasure:
    device.motorEnable = True # Enable the motor for movement
    device.wavelength = wavelength
    device.waitForMotor()
    device.motorEnable = False
    data = device.Measure()
    voltages = twosToVoltage(data)
    syncPulseLocations = twosToInteger(device.getSyncData())
    maximaSampleLocations = np.array(syncPulseLocations + voltageMaximaDelaySamples, dtype=np.int)[0:-3]
    minimaSampleLocations = np.array(syncPulseLocations + voltageMinimaDelaySamples, dtype=np.int)[0:-3]
    maxima = voltages[maximaSampleLocations]
    minima = voltages[minimaSampleLocations]
    Vpps = maxima - minima
    averageVpp = np.mean(Vpps)
    current = averageVpp / TIAResistance * 1e9 /2 # current in nA, need the 2 because we have gain now.
    currents = np.append(currents, current)
    print(f'l: {wavelength}nm: {current:.2f}nApp')

    #maximaTimes = maximaSampleLocations / fSampling
    #fig, ax = plt.subplots()
    #ax.plot(times, 1e3*(voltages - np.mean(voltages)))
    # show where the maxima locations should be
    #ax.plot(maximaTimes, 0.0*np.ones(len(maximaTimes)), marker='o')
    #ax.set_xlabel('time (ms)')
    #ax.set_ylabel('mV / nA')
    #plt.show()

device.motorEnable = True
device.wavelength = startWavelength # set our device back to the original wavelength
device.closeDevice()
data = pd.DataFrame(data={'Wavelength (um)': wavelengthsToMeasure / 1000.0, 'Photocurrent (nApp)': currents})
data.to_csv('photocurrent_spectra.csv', index=False)
wavelengthsToMeasure = np.arange(startWavelength, stopWavelength, stepWavelength)
