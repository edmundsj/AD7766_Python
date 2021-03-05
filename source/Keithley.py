from .SCPIDevice import SCPIDevice
import serial
import json
import numpy as np
import time
import re
from math import ceil

class Keithley(SCPIDevice):
	def __init__(self):
		SCPIDevice.__init__(self, baudRate=9600)
		self._set_voltage = 0
		self._set_current = 0
		self._output = False
		self._mode = 'voltage'

	def setVoltageMode(self):
		if self._mode != 'voltage':
			self.writeLine('source:function voltage')
			self._mode = 'voltage'

	def setCurrentMode(self):
		if self._mode != 'current':
			self.writeLine('source:function current')
			self._mode = 'current'

	def setVoltage(self, voltage):
		self.setVoltageMode()
		if self._set_voltage != voltage:
			self.writeLine('source:voltage:level ' + str(voltage))
			self._set_voltage = voltage

	def setCurrent(self, current):
		self.setCurrentMode()
		if self._set_current != current:
			self.writeLine('source:current:level ' + str(current))
			self._set_current = current

	def outputToggle(self):
		if self._output == True:
			self.writeLine('output:state: off')
		if self_output == False:
			self.writeLine('output:state: on')
		self._output = not(self._output)

	def outputOn(self):
		self.writeLine('output:state on')
		self._output = True

	def outputOff(self):
		self.writeLine('output:state off')
		self._output = False

	def setCurrentCompliance(self, current):
		self.writeLine('sense:current:protection:level ' + str(current))

	def setVoltageCompliance(self, voltage):
		self.writeLine('sense:voltage:protection:level ' + str(voltage))

	def applyVoltageMeasureCurrent(self, voltages, delay=0.5):
		if(delay < 0.25):
			print("WARNING: COMMUNICATION OVERFLOW WILL BE CAUSED. DELAY CANNOT BE LESS THAN 0.2s. SWITCHING TO 0.2s")
			delay = 0.25
		if self._output == False:
			self.setVoltage(0)
			self.outputOn()
		measured_currents = np.array([])
		measured_voltages = np.array([])
		if isinstance(voltages, (np.ndarray, list, tuple)):
			if len(voltages) > 200:
				segments = ceil(len(voltages) / 200)
				voltage_container = np.array_split(voltages, segments)
			else:
				voltage_container = np.array([voltages])
			for voltages in voltage_container:
				for voltage in voltages:
					self.setVoltage(voltage)
					time.sleep(delay/2) # Wait 500ms for the device [HACK - NEED TO FIX THIS ]
					self.writeLine('measure:current?')
					time.sleep(delay/2)
				data = self.readLine()
				data = np.array(re.split(',|\r', data), dtype=np.float64)
				data = data.reshape(len(voltages), 5)
				measured_voltages = np.append(measured_voltages, data[:,0])
				measured_currents = np.append(measured_currents, data[:,1])

		else:
			self.setVoltage(voltages)
			self.writeLine('read?')
			data = self.readLine().split(',')
			measured_voltages = float(data[0])
			measured_currents = float(data[1])

		self.setVoltage(0)
		self.outputOff()
		return (measured_voltages, measured_currents)
