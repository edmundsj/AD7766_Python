import serial
import numpy as np

def getADCBytes(maxBytes=90000, port='/dev/cu.usbmodem14141', baudrate=7372800):
    arduino = serial.Serial()
    arduino.port = port
    arduino.baudrate = baudrate
    randomString=b'ENDTRANSACTION';
    arduino.open()

    byteCounter = 0
    bytesWritten = arduino.write(b'y') # tell the Arduino to get us some data.
    dataBuffer = np.zeros(maxBytes + 1020, dtype='uint8')

    while byteCounter < maxBytes-1: # HACK HACK THIS IS A HACK THE -1 SHOULD NOT BE HERE.
        bytesAvailable = arduino.in_waiting
        dataBuffer[byteCounter:byteCounter+bytesAvailable] = \
                np.frombuffer(arduino.read_until(randomString, size=bytesAvailable), dtype='uint8')
        byteCounter += bytesAvailable
        print(byteCounter)
    # THIS WILL NOT WORK 100% OF THE TIME.
    if(byteCounter == 90000):
        return dataBuffer[0:byteCounter]
    elif(byteCounter == 89999):
        return dataBuffer[2:byteCounter]
    elif(byteCounter == 89998):
        return dataBuffer[1:byteCounter]
