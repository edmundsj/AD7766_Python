"""
Measures the photocurrent spectra from 0.8um to 1.7um (the bandwidth of our InGaAs photodiode)
using previously-developed software for communicating with the AD7766 ADC and controlling a stepper motor

Considerations:
    - The motor is the dominant source of delay in the system, so I will want to measure the photocurrent spectra
    - If I want the actual pk-pk current and not the sinusoidal component, I need to add a correction factor. This is the case for optical chopping but is not the case for sinusoidal modulation.
"""
import numpy as np
import pandas as pd
from DataAquisition import SCPIDevice, twosToVoltage, twosToInteger
from Plotting import prettifyPlot, plt
import time

device = SCPIDevice()

startWavelength = 1050
stopWavelength = 1055
stepWavelength = 5
wavelengthsToMeasure = np.arange(startWavelength, stopWavelength, stepWavelength)

fModulation = 1 # kHz
fSampling = 125 # kHz
Tmax = 1000 # ms
samplesPerMeasurement = int(Tmax * fSampling)
signalBin = int(fModulation * Tmax)
device.Configure(samplesPerMeasurement)

TIAResistance = 1 # MOhms
totalTransimpedance = 2 * TIAResistance
deltaRMax = 3e-4 # maximum expected change in reflectance
photocurrentMax = 150 *1e3 # peak photocurrent with R=1 (pA)
expectedPhotocurrentAmplitude = photocurrentMax * deltaRMax
currents = np.array([])

# Set the current wavelength to 800nm, wait for the motor to stop rotating, and then turn it off to tamp down the noise.

device.motorEnable = True
device.wavelength = startWavelength
device.waitForMotor()

for wavelength in wavelengthsToMeasure:
    device.motorEnable = True # Enable the motor for movement
    device.wavelength = wavelength
    device.waitForMotor()
    device.motorEnable = False
    time.sleep(1) # The motor is generating hella noise (I think)
    data = device.Measure()
    voltages = twosToVoltage(data)
    syncPulseLocations = twosToInteger(device.getSyncData())
    voltagePowerSpectrum = np.square(np.abs(np.fft.fft(voltages/len(voltages))))
    # Multiply by 2 to convert to single-sided spectrum
    voltageSignalPower = voltagePowerSpectrum[signalBin] * 2
    # Multiply by 2 to convert from RMS power into amplitude
    voltageSignalAmplitude = np.sqrt(voltageSignalPower * 2)
    # Multiply by 2 to convert to uApp instead of uA amplitude
    currentSignalAmplitudeuApp = voltageSignalAmplitude / totalTransimpedance * 2
    currentSignalAmplitudepApp = currentSignalAmplitudeuApp * 1e6

    currents = np.append(currents, currentSignalAmplitudepApp)
    print(f'{wavelength} nm: {currentSignalAmplitudepApp:.2f} / {expectedPhotocurrentAmplitude:.2f} pApp')

    #syncPulseTimes = syncPulseLocations / fSampling
    #fig, ax = plt.subplots()
    #ax.plot(times, voltages - np.mean(voltages))
    #ax.plot(syncPulseTimes, 0.0*np.ones(len(syncPulseTimes)), marker='o') # show the synchronization markers
    #plt.show()

device.motorEnable = True
device.wavelength = startWavelength # set our device back to the original wavelength
device.closeDevice()

data = pd.DataFrame(data={'Wavelength (um)': wavelengthsToMeasure / 1000.0, 'Photocurrent (pApp)': currents})
data.to_csv('photocurrent_modulation_spectra.csv', index=False)
wavelengthsToMeasure = np.arange(startWavelength, stopWavelength, stepWavelength)
