"""
Measures the photocurrent spectra from 0.8um to 1.7um (the bandwidth of our InGaAs photodiode)
by taking the DFT of the measured voltages and extracting the first harmonic, then converting from the
harmonic component value to the square wave pk-pk value.

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

startWavelength = 950
stopWavelength = 955
stepWavelength = 5
wavelengthsToMeasure = np.arange(startWavelength, stopWavelength, stepWavelength)

fModulation = 1 # kHz
fSampling = 125 # kHz
correctionFactor = 0.86715082588 # Corrects for the conversion from sinusoidal component to pk-pk square wave value
Tmax = 250 # ms
samplesPerMeasurement = int(Tmax * fSampling)
signalBin = int(fModulation * Tmax)
device.Configure(samplesPerMeasurement)

TIAResistance = 4.7 # MOhms
totalTransimpedance = 2 * TIAResistance
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
    data = device.Measure()
    voltages = correctionFactor * twosToVoltage(data)
    voltagePowerSpectrum = np.square(np.abs(np.fft.fft(voltages/len(voltages))))
    # Multiply by 2 to convert to single-sided spectrum
    voltageSignalPower = voltagePowerSpectrum[signalBin] * 2
    # Multiply by 2 to convert from RMS power into amplitude
    voltageSignalAmplitude = np.sqrt(voltageSignalPower * 2)
    # Multiply by 2 to convert to uApp instead of uA amplitude
    currentSignalAmplitudeuApp = voltageSignalAmplitude / totalTransimpedance * 2
    currentSignalAmplitudenApp = currentSignalAmplitudeuApp * 1e3

    currents = np.append(currents, currentSignalAmplitudenApp)
    print(f'{wavelength} nm: {currentSignalAmplitudenApp:.2f}')

device.motorEnable = True
device.wavelength = startWavelength # set our device back to the original wavelength
device.waitForMotor()
device.motorEnable = False
device.closeDevice()

data = pd.DataFrame(data={'Wavelength (um)': wavelengthsToMeasure / 1000.0, 'Photocurrent (nApp)': currents})
data.to_csv('photocurrent_spectra.csv', index=False)
wavelengthsToMeasure = np.arange(startWavelength, stopWavelength, stepWavelength)
