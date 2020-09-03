import sys
import unittest
sys.path.append('source')
from UnitTesting.shorthand import *
from AD7766_postprocessing import *
from DataAquisition import SCPIDevice

class TestArduinoADCSampling(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = SCPIDevice()

    def setUp(self):
        self.device.device.reset_input_buffer() # ONLY WORKS ON PYSERIAL

    def testIdentify(self):
        """
        Tests the Identify() function to check there are no more bytes than expected and to check that the ID
        does not change from initialization of the device
        """
        deviceIDActual = self.device.Identify()
        deviceIDDesired = self.device.deviceID
        self.assertEqual(deviceIDDesired, deviceIDActual)
        self.assertEqual(self.device.inWaiting(), 0) # Verify that there ore no bytes left to be read

    def testMeasure(self):
        """
        Asserts that the result of a measurement is a set of three bytes, and that no more than 3 bytes are returned
        """
        desiredMeasurements = 1
        measuredData = self.device.Measure()
        self.assertEqual(len(measuredData), 3)
        self.assertEqual(self.device.inWaiting(), 0) # Verify that there ore no bytes left to be read


    def testMeasureByteCount(self):
        """
        Asserts that the Configure() function can be used to measure between 1 and 100,000 measurements without
        dropping a single byte.
        """
        desiredMeasurementsList = [1, 10, 100, 1000, 10000, int(1e5)]

        for desiredMeasurements in desiredMeasurementsList:
            desiredBytes = desiredMeasurements * 3
            self.device.Configure(desiredMeasurements)
            data = self.device.Measure()
            actualBytes = len(data)
            self.assertEqual(actualBytes, desiredBytes,
                    msg=f'Received wrong number of bytes. Actual bytes: {actualBytes}.' + \
                    f'Desired bytes: {desiredBytes}' + \
                    f'attempt restart of the arduino.\n')

    @unittest.skip("Extremely large data transfer (long test)")
    def testMeasureLargeByteCount(self):
        """
        Asserts that we can measure very large numbers of measurements (1 million in this test) without dropping
        any bytes.
        """
        desiredMeasurements = int(1e6)
        desiredBytes = desiredMeasurements * 3
        self.device.Configure(desiredMeasurements)
        data = self.device.Measure()
        actualBytes = len(data)
        self.assertEqual(actualBytes, desiredBytes,
                    msg=f'Received wrong number of bytes. Actual bytes: {actualBytes}.' + \
                    f'Desired bytes: {desiredBytes}' + \
                    f'attempt restart of the arduino.\n')

    @classmethod
    def tearDownClass(cls):
        cls.device.closeDevice()
