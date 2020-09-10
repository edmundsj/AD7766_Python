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

    def testMeasureSynchronizationPoints(self):
        """
        Confirm that we get the expected number of data synchronization events when we sample in a given time period.
        Assumes an external 1kHz square wave is being applied to pin 20 on the Teensy.
        """
        fMeasure = 125000
        fSync = 1000
        desiredSynchronizationEvents = 8
        numberMeasurements = int(fMeasure/fSync * desiredSynchronizationEvents)
        self.device.Configure(numberMeasurements)
        self.device.Measure()
        actualSynchronizationEvents = self.device.syncPoints
        self.assertEqual(actualSynchronizationEvents, desiredSynchronizationEvents, msg='Failed to synchronize to external function generator. Is it turned on?')

    def testMeasureSynchronizationData(self):
        """
        Verify that the synchronization data we get is "reasonable" - that is that points are separated by very close
        to their expected frequency of 1kHz. This assumes there is a square wave at 1kHz sending data to the Teensy.
        """
        fMeasure = 125000
        fSync = 1000
        desiredSynchronizationEvents = 3
        numberMeasurements = int(fMeasure/fSync * desiredSynchronizationEvents)
        self.device.Configure(numberMeasurements)
        self.device.Measure()
        actualSynchronizationEvents = self.device.syncPoints
        syncData = self.device.getSyncData()
        bytesPerDataPoint = 3
        desiredSyncBytes = bytesPerDataPoint * desiredSynchronizationEvents

        # check that the data has the right number of bytes in it
        self.assertEqual(len(syncData), desiredSyncBytes)
        measurementPoints = twosToInteger(syncData)
        measurementDeltas = np.diff(measurementPoints)
        timeDeltas = 1 / fMeasure * measurementDeltas
        approxFrequencies = np.reciprocal(timeDeltas)
        assertAlmostEqual(approxFrequencies[0], fSync)
        assertAlmostEqual(approxFrequencies[1], fSync)

    @classmethod
    def tearDownClass(cls):
        cls.device.closeDevice()
