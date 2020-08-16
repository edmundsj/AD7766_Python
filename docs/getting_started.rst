Getting Started
==============================================
First, if you have not already done so, download the project repository from githib:

.. code-block:: bash
    git clone https://github.com/edmundsj/AD7766_Python.git

Next, navigate to the ``examples`` folder in the project directory. In that directory, there is a basic example (called ``basic.py``), which creates an SCPI device, performs a measurement, configures the device to measure more data, and then fetches that data. Finally, the device is "closed" (this is necessary for the ``pyvisa`` library used not to explode in horror). 

If you run this script you should see an output that looks something like this:
.. code-black:: bash

    Data from single measured data point: [167]
    Data from multiple measurements: [183 182 182 182 182 181 182 182 182 181]
    Same data, sent again from the Arduino: [183 182 182 182 182 181 182 182 182 181]

Debugging
-----------
If you do not see the data output, there are a couple potential reasons
**1. Device Not plugged in**
This is probably the most common, and I have errors that should tell you this

**2. Baud Rate is not correct**
Make sure the baud rate is the same on the Arduino and the python script. In the test script 'basic.py' it defaults to 115200, but if you call SCPIDevice() with no arguments, it will default to 115200.



* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
