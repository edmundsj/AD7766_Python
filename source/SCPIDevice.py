import pyvisa
import numpy as np
import time
class DataError(Exception):
    pass

class DeviceNotFoundError(Exception):
    pass

class SCPIDevice:
    """This is another class. Is it visible?"""
    def __init__(self, baudRate=115200):
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
        self.numberBytes = 1
        time.sleep(2)
        self.deviceID = self.device.query('*IDN?')

    def Configure(self, numberMeasurements):
        """ Configures the device for measurement """
        configureString = f'configure {numberMeasurements}'
        self.numberBytes = numberMeasurements
        self.device.write(configureString)

    def Measure(self):
        """ Performs a measure query on the SCPI device
        :return: data measured from the device
        """
        self.device.write('measure?')
        measuredData = self.device.read_bytes(self.numberBytes + 1)
        if measuredData[0] != 35:
            raise DataException("Data not valid. Did not begin with start character #")
        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8)

        return measuredData

    def Fetch(self):
        """ Performs a fetch query on the SCPI device (gets data that has already been measured)
        :return: data previously measured by the device"""
        self.device.write('fetch?')
        measuredData = self.device.read_bytes(self.numberBytes + 1)
        if measuredData[0] != 35:
            raise DataException("Data not valid. Did not begin with start character #")
        measuredData = np.frombuffer(measuredData[1:], dtype=np.uint8)
        return measuredData

    def closeDevice(self):
        """ Closes the connection to the Arduino. MUST be located in the script or pyVISA will have a heart
        attack"""
        self.device.close()
