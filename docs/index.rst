Python SCPI Interface for AD7766 ADC
==============================================
Documentation for a python library used to interface with SCPI instruments. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   test

Getting Started
==============================================
Before you are able to use the python interface, you will need to have uploaded compatible code to an Arduino, or be using an existing SCPI tool. For information on how to do that, see `the documentation on readthedocs
<https://pythonarduino-ad7766.readthedocs.io/en/latest/>`_.

If you have not already done so, download the project repository from githib:

.. code-block:: bash

   git clone https://github.com/edmundsj/AD7766_Python.git

Next, navigate to the ``examples`` folder in the project directory. In that directory, there is a basic example (called ``basic.py``), which creates an SCPI device, performs a measurement, configures the device to measure more data, and then fetches that data. Finally, the device is "closed" (this is necessary for the ``pyvisa`` library used not to explode in horror).

Hello World Example
---------------------
If you run this script you should see an output that looks something like this:

.. code-block:: bash

   Data from single measured data point: [167]
   Data from multiple measurements: [183 182 182 182 182 181 182 182 182 181]
   Same data, sent again from the Arduino: [183 182 182 182 182 181 182 182 182 181]


Running the Test Suite
--------------------------
To run the full test suite, which runs a stress test on the communication between the device and the python library, in addition to testing all the auxiliary and post-processing functions, run:

.. code-block:: bash
    
    python -m unittest discover



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
