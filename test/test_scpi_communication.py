import sys
import unittest
sys.path.append('source')
from UnitTesting.shorthand import *
from adc_processing import *
from SCPIDevice import *

class TestArduinoADCSampling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arduino = SCPIDevice(baudRate=115200)

    def testMeasureByteCount(self):
        desiredBytesList = [1, 10, 100, 1000]
        for desiredBytes in desiredBytesList:
            self.arduino.Configure(desiredBytes)
            data = self.arduino.Measure()
            actualBytes = len(data)
            self.assertEqual(actualBytes, desiredBytes,
                    msg=f'Received too many bytes. Actual bytes: {actualBytes}. Desired bytes: {desiredBytes}' + \
                            f'attempt restart of the arduino.\n')

    @classmethod
    def tearDownClass(cls):
        cls.arduino.closeDevice()