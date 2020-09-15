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

    def __init__(self, baudRate=115200, serialType='pyserial'):
        self.serialType = serialType
        self.numberMeasurements = 1
        self.numberBytes = self.numberMeasurements*3 + 1
        self.numberSynchronizationPulses = 0
        self.measurementRate = 125*1e3
        self.microstepsPerNanometer = 30.3716*1.011 # calibrated from 800nm - 1700nm. Optimized for 5nm steps.
        self.microstepsCorrection = 6.17*1e-6

        with open('device_settings.txt', 'r') as settingsFile:
            data = json.load(settingsFile)
            self.currentWavelength = data['currentWavelength']

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
            #print(f'Found Device with name: {self.deviceID}')

    def inWaiting(self):
        """
        Get the number of bytes in the read buffer that have not yet been read
        """
        if self.serialType == 'pyvisa':
            raise NotImplementedError
        else:
            return self.device.in_waiting

    def writeLine(self, stringToWrite):
        """
        Wrapper function that writes a set of bytes ending in a newline character.

        :param stringToWrite: The variable arguments are used for
        :returns: Number of bytes written
        """
        if self.serialType == 'pyvisa':
            raise NotImplementedException
        else:
            return self.device.write(bytes(stringToWrite + '\n', 'ascii'))

    def readLine(self):
        """
        Wrapper function that writes a set of bytes ending in a newline character.

        :param stringToWrite: The variable arguments are used for
        :returns: Number of bytes written
        """
        if self.serialType == 'pyvisa':
            raise NotImplementedException
        else:
            return self.device.readline().decode('ascii').rstrip('\n\r')

    def Configure(self, numberMeasurements):
        """ Configures the number of measuremets for the device to send back

        :param numberMeasurements: The number of measurements to request from the ADC.
        """
        self.numberMeasurements = numberMeasurements
        self.numberBytes = numberMeasurements*3 + 1
        if self.serialType == 'pyvisa':
            self.configureVisa()
        else:
            self.configureSerial()

    def Measure(self):
        """
        Measures data from the ADC based on the number of measurements configured.

        :returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
        """
        if self.serialType == 'pyvisa':
           return self.measureVisa()
        else:
           return self.measureSerial()

    def Fetch(self):
        """
        Fetches previously-measured data to ensure data integrity.

        :returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
        """
        if self.serialType == 'pyvisa':
            self.fetchVisa()
        else:
            self.fetchSerial()

    def Reset(self):
        """
        Sends SCPI reset command to device flushes serial buffer, and sets default configuration for emasurement.
        """
        self.numberMeasurements = 1
        self.numberBytes = self.numberMeasurements * 3 + 1
        if self.serialType == 'pyvisa':
            self.resetVisa()
        else:
            self.resetSerial()

    def Identify(self):
        """
        Requests device's identifier string.

        :return: Newline-stripped string containing the device name
        """
        if self.serialType == 'pyvisa':
            return self.identifyVisa()
        else:
            return self.identifySerial()

    def getSyncPoints(self):
        """
        Get the number of points we will use for synchronization and subsequent sampling

        :return syncPoints: The number of pulses measured from the signal generator
        """
        self.writeLine('SYNC:NUMPOINTS?')
        return int(self.readLine())

    syncPoints = property(getSyncPoints)

    def getSyncData(self):
        """
        Get the measurement numbers that each synchronization pulse corresponds to.

        :returns data: an array of integers corresponding to the measurement indices of the synchronization point events.

        """
        self.writeLine('SYNC:DATA?')
        measuredData = self.device.read(self.numberBytes)
        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8) # Discard the leading #
        return measuredData


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
        while(self.motorRotating == True):
            time.sleep(0.05)

    def rotateMotor(self, rotationSteps):
        """
        Rotates the stepper motor by some integer number of steps.

        :param rotationSteps: The number of stepper motor steps to take. Positive = clockwise, negative = counterclockwise.
        """
        if(rotationSteps < 0):
            self.motorDirection = 1
        else:
            self.motorDirection = 0

        self.writeLine('MOTOR:ROTATE ' + str(rotationSteps))

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

    """
    This should really be changed so that I can choose my wavelength
    """
    def setWavelength(self, wavelength):
        self.increaseWavelength(wavelength - self.wavelength)
        self.currentWavelength = wavelength

        with open('device_settings.txt', 'w') as settingsFile:
            json.dump({'currentWavelength': float(self.currentWavelength)}, settingsFile)


    def getWavelength(self):
        return self.currentWavelength

    wavelength = property(getWavelength, setWavelength)

    def increaseWavelength(self, nm):
        integerSteps = int((self.microstepsPerNanometer * nm)*(1 + self.microstepsCorrection * nm))
        self.rotateMotor(integerSteps)
        self.currentWavelength += integerSteps / self.microstepsPerNanometer

    def identifySerial(self):
        """
        Identify() function implemented using the pyserial library

        :returns: Device identifier string
        """
        self.writeLine('*IDN?')
        deviceID = self.device.readline().decode('ascii')[:-2] # Discard carraige return
        return deviceID

    def resetSerial(self):
        """
        Reset() function implemented using the pyserial library
        """
        self.writeLine('*RST')

        # For some reason, there may be extra bytes held by the OS that we only have access to after we
        # read the entirety of the current buffer, so for a real reset we need to read all of these.
        while(self.device.in_waiting > 0):
            self.device.reset_input_buffer()
            time.sleep(0.01)

    def measureSerial(self):
        """
        Measure() function implemented with pyserial library.

        :returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
        """
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
        """
        Measure() function implemented with pyserial library.

        :returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
        """
        self.device.write(toAscii('FETCH?'))
        measuredData = self.device.read(self.numberMeasurements)
        measuredData = np.frombuffer(measuredData[:-2], dtype=np.uint8)
        raise NotImplementedError

    def configureSerial(self):
        """
        Configure() function implemented with the pyserial library
        """
        self.writeLine('CONFIGURE ' + str(self.numberMeasurements))

    def resetVisa(self):
        """
        Reset() function implemented using the pyvisa library.
        """
        raise NotImplementedError

    def identifyVisa(self):
        """
        Identify() function implemented using the pyvisa library
        """
        raise NotImplementedError

    def configureVisa(self):
        """ Configures the device for measurement using the pyvisa library """
        configureString = f'CONFIGURE {self.numberMeasurements}'
        self.device.write(configureString)

    def fetchVisa(self):
        """
        Fetch() function implemented using the pyvisa library

        :returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
        """
        self.device.write('FETCH?')
        measuredData = self.device.read_bytes(self.numberBytes + 1)
        if measuredData[0] != 35:
            raise DataException("Data not valid. Did not begin with start character #")
        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8)
        return measuredData

    def measureVisa(self):
        """
        Measure() function implemented using the pyvisa library.

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
        """
        Closes the connection to the Arduino. MUST be located in the script or pyVISA will have a heart
        attack. Also save the wavelength.
        """
        self.device.close()
        with open('device_settings.txt', 'w') as settingsFile:
            json.dump({'currentWavelength': float(self.currentWavelength)}, settingsFile)
