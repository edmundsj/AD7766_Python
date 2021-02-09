import sys
import unittest
import numpy as np
sys.path.append('source')
from UnitTesting.shorthand import *
from AD7766_postprocessing import *
from DataAquisition import MCP3561
import matplotlib.pyplot as plt

class TestArduinoADCProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = MCP3561(sampling_frequency=9.76*1e3)

    def setUp(self):
        self.device.device.reset_input_buffer() # ONLY WORKS ON PYSERIAL

    def testNoiseSpectralDensity(self):
        """
        Check that the noise spectral density of our ADC is less than some desired threshold far away
        from the location of our signal (assumed here at 1kHz)
        """
        # First, disable the motor so that the associated noise (hopefully) goes away
        self.device.motorEnable = False

        desiredMeasurements = 10000
        halfMeasurements = int(desiredMeasurements/2)
        samplingFrequency = 4.68 # kHz
        frequencies = np.arange(0, samplingFrequency/2, samplingFrequency/desiredMeasurements)

        signalFrequency = 1 # kHz
        startNoiseFrequency = signalFrequency * 2
        stopNoiseFrequency = samplingFrequency/2
        noiseBandwidth = (stopNoiseFrequency - startNoiseFrequency)
        startNoiseBin = int(startNoiseFrequency / samplingFrequency * desiredMeasurements)

        self.device.Configure(desiredMeasurements)
        data = self.device.Measure()
        times = np.arange(0, desiredMeasurements / samplingFrequency, 1/samplingFrequency)
        voltages = twosToVoltage(data)
        dcOffset = np.mean(voltages)
        voltages -= dcOffset

        # The single-sided voltage spectral power (rms, by definition)
        voltageSpectralPower = np.square(np.abs(np.fft.fft(voltages/len(voltages))))[0:halfMeasurements]*2

        voltageNoiseRMS = np.sqrt(np.sum(voltageSpectralPower[startNoiseBin:]) )
        voltageNoisePSD = 1e9 * voltageNoiseRMS / np.sqrt(noiseBandwidth * 1e3) # in nV / rtHz

        noiseUpperBound = 400 # Differential converter: 120-150, TIA: 250, total ~300. 
        print(f'Noise PSD: {voltageNoisePSD}')
        self.assertLess(voltageNoisePSD, noiseUpperBound, msg=f'Noise PSD is {voltageNoisePSD} nV/rtHz, expected < {noiseUpperBound}nV/rtHz. RMS Integrated noise is {voltageNoiseRMS*1e6} uV')


    @classmethod
    def tearDownClass(cls):
        cls.device.closeDevice()
