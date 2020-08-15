import numpy as np

def twosToInteger(twosBytes, firstByte='msb'):
    numberBytes = len(twosBytes)
    number = 0.0
    if(firstByte == 'msb'):
        for i in range(numberBytes):
            number += pow(256, numberBytes - 1 - i) * twosBytes[i]

        isNegative = bool(twosBytes[0] & 0b10000000) # checks the MSB of the twos complement number
        if isNegative:
            number -= pow(2, 8*numberBytes)
    elif(firstByte == 'lsb'):
        for i in range(numberBytes):
            number += pow(256, i) * twosBytes[i]

        isNegative = bool(twosBytes[-1] & 0b10000000)
        if isNegative:
            number -= pow(2, 8*numberBytes)

    return number


def countToVoltage(data, numberBits=24, maxVoltage=5):
    conversionFactor = maxVoltage / pow(2.0, numberBits)
    return np.multiply(data, conversionFactor)

