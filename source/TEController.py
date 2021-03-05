from .SCPIDevice import SCPIDevice
import serial
import json
import numpy as np

class TEController(SCPIDevice):
	def __init__(self, baudRate=115200, sampling_frequency=9.76*1e3):
		SCPIDevice.__init__(self, baudRate=baudRate, device_type='usbserial')
		self.remote_enabled = False

	def remoteEnable(self):
		if self.remote_enabled == False:
			self.writeLine('CONFIGURE:REMOTE 1')
			self.remote_enabled = True

	def remoteDisable(self):
		if self.remote_enabled == True:
			self.writeLine('CONIFUGER:REMOTE 0')
			self.remote_enabled = False

	def Fetch(self):
		self.writeLine("FETCH?")
		data = self.readLine()
		temp = None
		if data[0] == '#' and data[-1] == '$':
			temp = float(data[1:-1])
		return temp

	def setTemperature(self, temp):
		self.writeLine("CONFIGURE:TEMPERATURE " + str(temp))
