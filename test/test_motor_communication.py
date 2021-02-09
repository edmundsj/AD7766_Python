import sys
import unittest
import time
sys.path.append('source')
from UnitTesting.shorthand import *
from AD7766_postprocessing import *
from DataAquisition import MCP3561

class TestArduinoADCSampling(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.device = MCP3561()

	def setUp(self):
		self.device.Reset()
		time.sleep(0.01)

	def testMotorPositionDefault(self):
		"""
		Check that the motor position defaults to its expected value (0)
		"""
		motorPositionDesired = 0
		motorPositionMeasured = self.device.motorPosition
		self.assertEqual(motorPositionMeasured, motorPositionDesired)
		"""
		Check that the motor direction defaults to 0 (whatever that means)
		"""
		motorDirectionDesired = 0
		motorDirectionMeasured = self.device.motorDirection
		self.assertEqual(motorDirectionMeasured, motorDirectionDesired)

		motorEnableDesired = False
		motorEnableMeasured = self.device.motorEnable
		self.assertEqual(motorEnableMeasured, motorEnableDesired)

	def testMotorPositionCommunication(self):
		"""
		Check that we can read and then write a motor position to the motor.
		"""
		motorPositionDesired = 100
		self.device.motorPosition = motorPositionDesired
		motorPositionMeasured = self.device.motorPosition
		self.assertEqual(motorPositionMeasured, motorPositionDesired)

	def testMotorRotatingDefault(self):
		"""
		Check that by default the motor does not think it is rotating
		"""
		motorRotatingDesired = False
		motorRotatingActual = self.device.motorRotating
		self.assertEqual(motorRotatingActual, motorRotatingDesired)

	#@unittest.skip('Do not want the motor to actually move')
	def testMotorRotation(self):
		"""
		Attempts to rotate the motor forward some, checks that the motor rotated, then attempts to rotate
		the motor backwards by some, and checks that it rotates. Also checks to see that the motor is in fact rotating
		after we give it the command.
		"""
		motorRotationDesired = 100
		motorPositionDesired = 0 + motorRotationDesired
		self.device.rotateMotor(motorRotationDesired)
		motorRotatingMeasured = self.device.motorRotating
		motorRotatingDesired = True
		self.assertEqual(motorRotatingMeasured, motorRotatingDesired) # check that the motor is actually rotating

		self.device.waitForMotor()
		motorPositionMeasured = self.device.motorPosition
		self.assertEqual(motorPositionMeasured, motorPositionDesired)

		motorRotationDesired = -100
		motorPositionDesired += motorRotationDesired
		self.device.rotateMotor(motorRotationDesired)
		self.device.waitForMotor()
		motorPositionMeasured = self.device.motorPosition
		self.assertEqual(motorPositionMeasured, motorPositionDesired)

	def testMotorAbortRotation(self):
		"""
		Checks that after sending a motor rotation command we can abort that rotation successfully prior to the completion
		of the rotation.
		"""
		motorRotation = 200
		self.device.rotateMotor(motorRotation)
		self.device.motorEnable = False
		time.sleep(0.05)
		motorRotatingMeasured = self.device.motorRotating # check that the motor is no longer rotating
		self.assertEqual(motorRotatingMeasured, False)

	def testMotorSpeedDefault(self):
		"""
		Check the default settings for motor speed.
		"""
		motorPeriodDesired = 2
		motorPeriodActual = self.device.motorPeriod
		self.assertEqual(motorPeriodActual, motorPeriodDesired)

	def testMotorSpeed(self):
		"""
		Check that we can successfully change the motor's period (and hence its speed)
		"""
		motorPeriodDesired = 5;
		self.device.motorPeriod = motorPeriodDesired
		motorPeriodActual = self.device.motorPeriod
		self.assertEqual(motorPeriodActual, motorPeriodDesired)

	def testMotorEnableDisableDefault(self):
		"""
		Check that the motor is enabled by default
		"""
		motorEnableDesired = False
		motorEnableActual = self.device.motorEnable
		self.assertEqual(motorEnableActual, motorEnableDesired)

	def testMotorEnableDisable(self):
		"""
		Test enabling and disabling of the motor
		"""
		motorEnableDesired = False
		self.device.motorEnable = motorEnableDesired
		motorEnableActual = self.device.motorEnable
		self.assertEqual(motorEnableActual, motorEnableDesired)

		motorEnableDesired = True
		self.device.motorEnable = motorEnableDesired
		motorEnableActual = self.device.motorEnable
		self.assertEqual(motorEnableActual, motorEnableDesired)

	def testCheckMotorRotating(self):
		"""
		Checks to see that we can find if the motor is currently rotating
		"""

	@classmethod
	def tearDownClass(cls):
		cls.device.motorEnable = False
		cls.device.Reset()
		cls.device.closeDevice()
