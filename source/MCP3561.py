from .SCPIDevice import SCPIDevice
import serial
import json
import os
import numpy as np

class MCP3561(SCPIDevice):
    def __init__(self, baudRate=115200, sampling_frequency=9.76*1e3, device_type='usbmodem'):
        SCPIDevice.__init__(self, baudRate=baudRate, device_type=device_type)

        self.numberMeasurements = 1
        self.numberBytes = self.numberMeasurements*3 + 1
        self.numberSynchronizationPulses = 0
        self.measurementRate = sampling_frequency
        self.microstepsPerNanometer = 30.3716*1.011 # calibrated from 800nm - 1700nm. Optimized for 5nm steps.
        self.microstepsCorrection = -6.17*1e-6

        if(os.path.isfile('device_settings.txt')):
            with open('device_settings.txt', 'r') as settingsFile:
                data = json.load(settingsFile)
                self._wavelength = data['wavelength']

    def setWavelength(self, wavelength):
        self.increaseWavelength(wavelength - self.wavelength)

        with open('device_settings.txt', 'w') as settingsFile:
            json.dump({'wavelength': float(self._wavelength)}, settingsFile)

    def getWavelength(self):
        return self._wavelength

    wavelength = property(getWavelength, setWavelength)

    def increaseWavelength(self, nm):
        integerSteps = int(np.round((self.microstepsPerNanometer * nm)*(1 + self.microstepsCorrection * nm)))
        self.rotateMotor(integerSteps)
        self._wavelength += integerSteps / self.microstepsPerNanometer

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
        number_points = self.getSyncPoints()
        self.writeLine('SYNC:DATA?')
        number_bytes = number_points*3 +1
        measuredData = self.device.read(number_bytes)
        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8) # Discard the leading # and the newline at the end
        return measuredData

    def closeDevice(self):
        self.device.close()
        with open('device_settings.txt', 'w') as settingsFile:
            json.dump({'wavelength': float(self._wavelength)}, settingsFile)

    def Configure(self, numberMeasurements):
        """ Configures the number of measuremets for the device to send back

        :param numberMeasurements: The number of measurements to request from the ADC.
        """
        if numberMeasurements > 500000:
            print("TEENSY CANNOT DO MORE THAN 600K MEASUREMENTS. SETTING TO 500K")
            numberMeasurements = 500000

        self.numberMeasurements = int(numberMeasurements)
        self.numberBytes = int(numberMeasurements)*3 + 1
        self.writeLine('CONFIGURE ' + str(self.numberMeasurements))

    def Measure(self):
        """
        Measures data from the ADC based on the number of measurements configured.

        :returns: Array of 8-bit integers starting with the most significant byte of the first measurement.
        """
        timeoutOld = self.device.timeout
        if(self.numberMeasurements / self.measurementRate > self.device.timeout - 0.1):
            self.device.timeout = self.numberMeasurements / self.measurementRate * 1.2 # Give some wiggle room.

        bytesWritten = self.writeLine('MEASURE?')
        measuredData = self.device.read(self.numberBytes)

        if len(measuredData) == 0:
            raise Exception(f"No data measured from device. Attempted to read {self.numberBytes} bytes. " + \
                    f"{bytesWritten} bytes successfully written")

        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8)
        #else:
        #    raise Exception("Data corrupted. Did not get # as first character.")

        if(self.numberMeasurements / self.measurementRate > self.device.timeout - 0.1):
            self.device.timeout = timeoutOld

        return measuredData
