"""
"""
import pyvisa
import numpy as np
import time
import serial
import serial.tools.list_ports as list_ports
import sys
import io
import json
from DataAquisition.AD7766.python.source.AD7766_postprocessing import *

class DataError(Exception):
	pass

class DeviceNotFoundError(Exception):
	pass

class SCPIDevice:
	"""SCPI Device base class which serves as a wrapper for the pyserial or pyvisa interface and implemets
	basic SCPI functions, such as Identify, Reset, Measure, Fetch, and others."""

	def __init__(self, baudRate=9600):
		serialPortsList = [port.device for port in list_ports.comports()]
		containsUSBModem = ['usbmodem' in x for x in serialPortsList]
		containsUSBSerial = ['usbserial' in x for x in serialPortsList]
		usbModemIndices = [i for i in range(len(serialPortsList)) \
			if containsUSBModem[i] == True or containsUSBSerial[i] == True]

		if len(usbModemIndices) == 0:
			raise Exception("No USB devices found. Check device is plugged in and try again.")

		self.device = serial.Serial(serialPortsList[usbModemIndices[0]])
		self.device.timeout = 3 # MAY NEED TO CHANGE FOR LARGER DATA STREAMS
		self.device.baudrate = baudRate
		self.Reset()
		time.sleep(1) # Wait for arduino/Teensy initialization
		self.deviceID = self.Identify()
		print(f'Found Device with name: {self.deviceID}')

	def inWaiting(self):
		"""
		Get the number of bytes in the read buffer that have not yet been read
		"""
		return self.device.in_waiting

	def writeLine(self, stringToWrite):
		"""
		Wrapper function that writes a set of bytes ending in a newline character.

		:param stringToWrite: The variable arguments are used for
		:returns: Number of bytes written
		"""
		return self.device.write(bytes(stringToWrite + '\n', 'ascii'))

	def readLine(self):
		"""
		Wrapper function that writes a set of bytes ending in a newline character.

		:param stringToWrite: The variable arguments are used for
		:returns: Number of bytes written
		"""
		return self.device.readline().decode('ascii').rstrip('\n\r')

	def Fetch(self):
		"""
		Fetches previously-measured data to ensure data integrity.

		:returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
		"""
		self.fetchSerial()

	def Reset(self):
		"""
		Sends SCPI reset command to device flushes serial buffer, and sets default configuration for emasurement.
		"""
		self.numberMeasurements = 1
		self.numberBytes = self.numberMeasurements * 3 + 1
		self.writeLine('*RST')
		# For some reason, there may be extra bytes held by the OS that we only have access to after we
		# read the entirety of the current buffer, so for a real reset we need to read all of these.
		while(self.device.in_waiting > 0):
			self.device.reset_input_buffer()
			time.sleep(0.01)

	def Identify(self):
		"""
		Requests device's identifier string.

		:return: Newline-stripped string containing the device name
		"""
		self.writeLine('*IDN?')
		deviceID = self.device.readline().decode('ascii')[:-2] # Discard carraige return
		return deviceID

	def setMotorPosition(self, motorPosition):
		"""
		Sets the motor position to a desired value.

		:param motorPosition: Integer value of number of steps motor has taken
		"""
		self.writeLine('MOTOR:POSITION ' + str(motorPosition))

	def getMotorPosition(self):
		"""
		Gets the motor position from the Teensy

		:returns motorPosition: Integer value of number of steps motor has taken
		"""
		self.writeLine('MOTOR:POSITION?')
		position = int(self.readLine())
		return position

	motorPosition = property(getMotorPosition, setMotorPosition)

	def setMotorDirection(self, motorDirection):
		"""
		Sets the direction of the motor to 0 (clockwise) or 1 (counterclockwise)

		:param motorDirection: A boolean or 0/1 valued integer with the direction of the motor
		"""
		self.writeLine('MOTOR:DIRECTION ' + str(int(bool(motorDirection))))

	def getMotorDirection(self):
		"""
		Gets the motor direction of the motor.

		:returns motorDirection: The direction of the motor, either 0 (clockwise) or 1 (counterclockwise)
		"""
		self.writeLine('MOTOR:DIRECTION?')
		direction = int(self.readLine())
		return direction

	def getMotorRotating(self):
		"""
		Checks whether the motor is currently rotating or not.

		:returns rotation: boolean value of whether the motor is currently rotating or not
		"""
		self.writeLine('MOTOR:ROTATE?')
		rotation = bool(int(self.readLine()))
		return rotation

	motorRotating = property(getMotorRotating)
	motorDirection = property(getMotorDirection, setMotorDirection)

	def waitForMotor(self):
		time.sleep(0.05)
		while(self.motorRotating == True):
			time.sleep(0.05)

	def rotateMotor(self, rotationSteps):
		"""
		Rotates the stepper motor by some integer number of steps.

		:param rotationSteps: The number of stepper motor steps to take. Positive = clockwise, negative = counterclockwise.
		"""
		if self.motorEnable == False:
			self.motorEnable = True
			time.sleep(0.01)
		if(rotationSteps < 0):
			self.motorDirection = 1
		else:
			self.motorDirection = 0

		self.writeLine('MOTOR:ROTATE ' + str(rotationSteps))
		self.waitForMotor() # Not having this here was causing endless headaches. Better to just make this a blocking event.

	def setMotorEnable(self, motorEnable):
		if motorEnable == True:
			self.writeLine('MOTOR:ENABLE')
		elif motorEnable == False:
			self.writeLine('MOTOR:DISABLE')

	def getMotorEnable(self):
		self.writeLine('MOTOR:ENABLED?')
		enabled = bool(int(self.readLine()))
		return enabled

	motorEnable = property(getMotorEnable, setMotorEnable)

	def setMotorPeriod(self, motorPeriod):
		self.writeLine('MOTOR:PERIOD ' + str(int(motorPeriod)))

	def getMotorPeriod(self):
		self.writeLine('MOTOR:PERIOD?')
		motorPeriod = int(self.readLine())
		return motorPeriod

	motorPeriod = property(getMotorPeriod, setMotorPeriod)

	def closeDevice(self):
		"""
		Closes the connection to the Arduino. MUST be located in the script or pyVISA will have a heart
		attack. Also save the wavelength.
		"""
		self.device.close()
