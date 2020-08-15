import sys
import unittest
sys.path.append('source')
from adc_processing import *
from UnitTesting.shorthand import *


class TestADCProcessing(unittest.TestCase):

    def testTwosToInteger(self):
        testBytes = [255, 255, 255] # check for proper sign conversion
        desiredInteger = -1
        actualInteger = twosToInteger(testBytes)
        self.assertEqual(desiredInteger, actualInteger)

        testBytes = [100, 255, 255]
        desiredInteger = 6619135
        actualInteger = twosToInteger(testBytes)
        self.assertEqual(desiredInteger, actualInteger)

    def testaCountToVoltage(self):
        desiredValue = 2.5
        actualCount = pow(2, 23)
        actualValue = countToVoltage(actualCount)
        assertAlmostEqual(desiredValue, actualValue)


if __name__ == '__main__':
    unittest.main()
