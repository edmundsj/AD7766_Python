"""
"""
import pyvisa
import numpy as np
import time
import serial
import serial.tools.list_ports as list_ports
import sys
import io
from DataAquisition.AD7766.python.source.AD7766_postprocessing import *

class DataError(Exception):
    pass

class DeviceNotFoundError(Exception):
    pass

class SCPIDevice:
    """SCPI Device base class, can be set up to use either pyserial or pyvisa"""
    def __init__(self, baudRate=115200, serialType='pyserial'):
        self.serialType = serialType
        self.numberMeasurements = 1
        self.numberBytes = self.numberMeasurements*3 + 1
        self.measurementRate = 125*1e3

        if serialType == 'pyvisa':
            resourceManager = pyvisa.ResourceManager()
            resourceList = resourceManager.list_resources()
            resourceIndex = 0
            numberResources = len(resourceList)
            if numberResources == 0:
                raise DeviceNotFoundError("ERROR: no devices found. Please make sure your arduino is plugged in.")

            self.device = resourceManager.open_resource(resourceList[resourceIndex])
            self.device.write_termination = '\n'
            self.device.read_termination = '\n'
            self.device.baud_rate = baudRate
            self.device.timeout = 2000
            time.sleep(3)
            self.deviceID = self.device.query('*IDN?')

        elif serialType == 'pyserial':
            serialPortsList = [port.device for port in list_ports.comports()]
            containsUSBModem = ['usbmodem' in x for x in serialPortsList]
            usbModemIndices = [i for i in range(len(serialPortsList)) if containsUSBModem[i] == True]

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
        if self.serialType == 'pyvisa':
            raise NotImplementedError
        else:
            return self.device.in_waiting

    def writeLine(self, stringToWrite):
        if self.serialType == 'pyvisa':
            raise NotImplementedException
        else:
            return self.device.write(bytes(stringToWrite + '\n', 'ascii'))

    def Configure(self, numberMeasurements):
        """ Configures the device for measurement """
        self.numberMeasurements = numberMeasurements
        self.numberBytes = numberMeasurements*3 + 1
        if self.serialType == 'pyvisa':
            self.configureVisa()
        else:
            self.configureSerial()

    def Measure(self):
        if self.serialType == 'pyvisa':
           return self.measureVisa()
        else:
           return self.measureSerial()

    def Fetch(self):
        if self.serialType == 'pyvisa':
            self.fetchVisa()
        else:
            self.fetchSerial()

    def Reset(self):
        self.numberMeasurements = 1
        self.numberBytes = self.numberMeasurements * 3 + 1
        if self.serialType == 'pyvisa':
            self.resetVisa()
        else:
            self.resetSerial()

    def Identify(self):
        if self.serialType == 'pyvisa':
            return self.identifyVisa()
        else:
            return self.identifySerial()

    def identifySerial(self):
        self.writeLine('*IDN?')
        deviceID = self.device.readline().decode('ascii')[:-2] # Discard carraige return
        return deviceID

    def resetSerial(self):
        self.writeLine('*RST')

        # For some reason, there may be extra bytes held by the OS that we only have access to after we
        # read the entirety of the current buffer, so for a real reset we need to read all of these.
        while(self.device.in_waiting > 0):
            self.device.reset_input_buffer()
            time.sleep(0.01)

    def measureSerial(self):
        timeoutOld = self.device.timeout
        if(self.numberMeasurements > 1e5):
            self.device.timeout = self.numberMeasurements / self.measurementRate + 1

        bytesWritten = self.writeLine('MEASURE?')
        measuredData = self.device.read(self.numberBytes)

        if len(measuredData) == 0:
            raise Exception(f"No data measured from device. Attempted to read {self.numberBytes} bytes. " + \
                    f"{bytesWritten} bytes successfully written")

        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8)
        #else:
        #    raise Exception("Data corrupted. Did not get # as first character.")

        if(self.numberMeasurements > 1e5):
            self.device.timeout = timeoutOld

        return measuredData

    def fetchSerial(self):
        self.device.write(toAscii('FETCH?'))
        measuredData = self.device.read(self.numberMeasurements)
        measuredData = np.frombuffer(measuredData[:-2], dtype=np.uint8)
        raise NotImplementedError

    def configureSerial(self):
        self.writeLine('CONFIGURE ' + str(self.numberMeasurements))

    def resetVisa(self):
        raise NotImplementedError

    def identifyVisa(self):
        raise NotImplementedError

    def configureVisa(self):
        """ Configures the device for measurement using the pyvisa library """
        configureString = f'CONFIGURE {self.numberMeasurements}'
        self.device.write(configureString)

    def fetchVisa(self):
        """ Performs a fetch query on the SCPI device (gets data that has already been measured)
        :return: data previously measured by the device"""
        self.device.write('FETCH?')
        measuredData = self.device.read_bytes(self.numberBytes + 1)
        if measuredData[0] != 35:
            raise DataException("Data not valid. Did not begin with start character #")
        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8)
        return measuredData

    def measureVisa(self):
        """ Performs a measure query on the SCPI device
        :return: data measured from the device
        """

        self.device.write('MEASURE?')
        measuredData = self.device.read_bytes(self.numberBytes)
        if measuredData[0] != 35:
            raise DataException("Data not valid. Did not begin with start character #. Actual data: " + \
                   str(measuredData) )
        measuredDat = np.frombuffer(measuredData[1:], dtype=np.uint8)

        return measuredData

    def closeDevice(self):
        """ Closes the connection to the Arduino. MUST be located in the script or pyVISA will have a heart
        attack"""
        self.device.close()
