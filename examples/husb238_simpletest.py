# SPDX-FileCopyrightText: Copyright (c) 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
Simple test for the HUSB238.
Reads available voltages and then sets each available voltage.
Reads the response, voltage and current from the attached PD power supply.
"""
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
