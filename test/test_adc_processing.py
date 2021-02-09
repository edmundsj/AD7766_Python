import sys
import unittest
sys.path.append('source')
from AD7766_postprocessing import *
from UnitTesting.shorthand import *

class TestADCProcessing(unittest.TestCase):
    """
    Tests ADC post-processing functions, including converting from a set of 8-bit arrays of integers that contain
    raw twos complement data to voltages.
    """

    def testTwosToInteger(self):
        """
        Check that this function converts a set of three bytes in twos complement to a signed integer. Checks
        two 3-byte arrays and one 6-byte array.
        """
        testBytes = np.array([255, 255, 255]) # check for proper sign conversion
        desiredInteger = -1
        actualInteger = twosToInteger(testBytes)
        self.assertEqual(desiredInteger, actualInteger)

        testBytes = np.array([100, 255, 255])
        desiredInteger = 6619135
        actualInteger = twosToInteger(testBytes)
        self.assertEqual(desiredInteger, actualInteger)

        testBytes = np.array([255, 255, 255, 100, 255, 255])
        desiredIntegers = np.array([-1, 6619135])
        actualIntegers = twosToInteger(testBytes)
        assertAlmostEqual(desiredIntegers, actualIntegers)


    def testCountToVoltage(self):
        """
        Test converting a raw ADC count into a voltage
        """
        desiredValue = 5.0
        actualCount = pow(2, 23)
        actualValue = countToVoltage(actualCount, maxVoltage=5)
        assertAlmostEqual(desiredValue, actualValue)

    def testTwosToVoltage(self):
        desiredVoltage = np.array([5.0])
        testBytes = np.array([127, 255, 255])
        actualVoltage = twosToVoltage(testBytes, maxVoltage=5, differential=True)
        assertAlmostEqual(desiredVoltage, actualVoltage, absoluteTolerance = 1e-5)

if __name__ == '__main__':
    unittest.main()
