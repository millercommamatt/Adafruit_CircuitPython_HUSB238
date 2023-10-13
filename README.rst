Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-husb238/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/husb238/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_HUSB238/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_HUSB238/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

CircuitPython helper library for the HUSB238 Type C Power Delivery Dummy Breakout


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


The HUSB238 USB PD sink chip is neat in that you can either use jumpers (really, resistor selection) to set the desired power delivery voltage and current or you can use I2C for dynamic querying and setting.

We've built a nice Adafruit USB Type C Power Delivery Dummy Breakout board around the HUSB238 to make it very easy to configure and integrate without having to solder any tiny resistors.

`Purchase one from the Adafruit shop <http://www.adafruit.com/products/5807>`_

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-husb238/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-husb238

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-husb238

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install adafruit-circuitpython-husb238

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_husb238

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

    import time
    import board
    import adafruit_husb238

    i2c = board.I2C()

    # Initialize HUSB238
    pd = adafruit_husb238.Adafruit_HUSB238(i2c)
    voltages = pd.available_voltages()

    v = 0

    while True:
        if pd.is_attached():
            print(f"Setting to {voltages[v]}V!")
            pd.value = voltages[v]
            pd.set_value()
            current = pd.read_current()
            volts = pd.read_voltage()
            response = pd.get_response()
            print(f"The PD chip returned a response of: {response}")
            print(f"It is set to {volts}V/{current}")
            print()
            v = (v + 1) % len(voltages)
            time.sleep(2)

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/husb238/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_HUSB238/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
