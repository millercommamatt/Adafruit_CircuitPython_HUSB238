# SPDX-FileCopyrightText: Copyright (c) 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# Written by ladyada (Adafruit Industries) and Liz Clark (Adafruit Industries)
# with OpenAI ChatGPT v4 September 25, 2023 build
# https://help.openai.com/en/articles/6825453-chatgpt-release-notes

# https://chat.openai.com/share/67b3bd79-ddc0-471b-91e9-9b15342fa62b
# https://chat.openai.com/share/653e461a-ec7a-4a03-93ee-db2ee3ebdb74
"""
`adafruit_husb238`
================================================================================

CircuitPython helper library for the HUSB238 Type C Power Delivery Dummy Breakout


* Author(s): Liz Clark

Implementation Notes
--------------------

**Hardware:**

* `Adafruit USB Type C PD Breakout - HUSB238 <https://www.adafruit.com/product/5807>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import time
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bit import ROBit
from adafruit_register.i2c_bits import ROBits, RWBits
from adafruit_register.i2c_struct import UnaryStruct

try:
    import typing  # pylint: disable=unused-import
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HUSB238.git"

_I2CADDR_DEFAULT = const(0x08)

_PD_STATUS0 = const(0x00)
_PD_STATUS1 = const(0x01)
_SRC_PDO_5V = const(0x02)
_SRC_PDO_9V = const(0x03)
_SRC_PDO_12V = const(0x04)
_SRC_PDO_15V = const(0x05)
_SRC_PDO_18V = const(0x06)
_SRC_PDO_20V = const(0x07)
_SRC_PDO = const(0x08)
_GO_COMMAND = const(0x09)


class Adafruit_HUSB238:
    """
    Instantiates a new HUSB238 class.
    This constructor initializes a new instance of the HUSB238 class.
    """

    cc_direction = ROBit(_PD_STATUS1, 7)
    attachment_status = ROBit(_PD_STATUS1, 6)
    pd_response = ROBits(3, _PD_STATUS1, 3)
    contract_v_5v = ROBit(_PD_STATUS1, 2)
    contract_a_5v = ROBits(2, _PD_STATUS1, 0)
    pd_src_voltage = ROBits(4, _PD_STATUS0, 4)
    pd_src_current = ROBits(4, _PD_STATUS0, 0)
    voltage_detected_5v = ROBit(_SRC_PDO_5V, 7)
    voltage_detected_9v = ROBit(_SRC_PDO_9V, 7)
    voltage_detected_12v = ROBit(_SRC_PDO_12V, 7)
    voltage_detected_15v = ROBit(_SRC_PDO_15V, 7)
    voltage_detected_18v = ROBit(_SRC_PDO_18V, 7)
    voltage_detected_20v = ROBit(_SRC_PDO_20V, 7)
    current_detected_5v = ROBits(4, _SRC_PDO_5V, 0)
    current_detected_9v = ROBits(4, _SRC_PDO_9V, 0)
    current_detected_12v = ROBits(4, _SRC_PDO_12V, 0)
    current_detected_15v = ROBits(4, _SRC_PDO_15V, 0)
    current_detected_18v = ROBits(4, _SRC_PDO_18V, 0)
    current_detected_20v = ROBits(4, _SRC_PDO_20V, 0)
    selected_pd = RWBits(4, _SRC_PDO, 4)
    _go_command = UnaryStruct(_GO_COMMAND, "<B")
    _src_pdo = UnaryStruct(_SRC_PDO, "<B")

    # Voltage to PDO mapping
    VOLTAGE_TO_PDO = {
        5: 0b0001,  # 5V
        9: 0b0010,  # 9V
        12: 0b0011,  # 12V
        15: 0b1000,  # 15V
        18: 0b1001,  # 18V
        20: 0b1010,  # 20V
    }
    # PDO to voltage mapping
    PDO_TO_VOLTAGE = {
        0b0000: "UNATTACHED",
        0b0001: 5,  # 5V
        0b0010: 9,  # 9V
        0b0011: 12,  # 12V
        0b0100: 15,  # 15V
        0b0101: 18,  # 18V
        0b0110: 20,  # 20V
    }
    # PDO to current mapping
    PDO_TO_CURRENT = {
        0b0000: "0.5A",
        0b0001: "0.7A",  # 0.7A
        0b0010: "1.0A",  # 1.0A
        0b0011: "1.25A",  # 1.25A
        0b0100: "1.5A",  # 1.5A
        0b0101: "1.75A",  # 1.75A
        0b0110: "2.0A",  # 2.0A
        0b0111: "2.0A",  # 2.0A
        0b1000: "2.50A",  # 2.50A
        0b1001: "2.75A",  # 2.75A
        0b1010: "3.0A",  # 3.0A
        0b1011: "3.25A",  # 3.25A
        0b1100: "3.5A",  # 3.5A
        0b1101: "4.0A",  # 4.0A
        0b1110: "4.5A",  # 4.5A
        0b1111: "5.0A",  # 5.0A
    }
    # PDO response codes
    PDO_RESPONSE_CODES = {
        0b000: "NO RESPONSE",
        0b001: "SUCCESS",
        0b011: "INVALID COMMAND OR ARGUMENT",
        0b100: "COMMAND NOT SUPPORTED",
        0b101: "TRANSACTION FAILED, NO GOOD CRC",
    }

    def __init__(
        self, i2c: typing.Type[I2C], i2c_address: int = _I2CADDR_DEFAULT
    ) -> None:
        """
        Sets up the I2C connection and tests that the sensor was found.

        :param i2c: The I2C device we'll use to communicate.
        :type i2c: Type[I2C]
        :param i2c_address: The 7-bit I2C address of the HUSB238, defaults to 0x40.
        :type i2c_address: int

        This function initializes the I2C communication with the HUSB238 device.
        It uses the provided I2C device and address for communication.
        """
        self.i2c_device = I2CDevice(i2c, i2c_address)

    def available_voltages(self) -> typing.List[int]:
        """
        Checks if specific voltages are detected and returns a list of available voltages.

        This function checks if specific voltages are detected based on the PD selection.
        It reads the 7th bit of the corresponding register to determine the status.

        :return: List of available voltages.
        :rtype: List[int]
        """
        _available_voltages = []
        print("The following voltages are available:")

        for voltage, detected in [
            (5, self.voltage_detected_5v),
            (9, self.voltage_detected_9v),
            (12, self.voltage_detected_12v),
            (15, self.voltage_detected_15v),
            (18, self.voltage_detected_18v),
            (20, self.voltage_detected_20v),
        ]:
            print(f"{voltage}V:", end=" ")
            if detected:
                print("Available")
                _available_voltages.append(voltage)
            else:
                print("Unavailable")

        return _available_voltages

    @property
    def get_5v_contract_amps(self) -> int:
        """
        Reads the 5V contract current from the HUSB238 device.

        This function reads the bottom two bits (0-1) of the HUSB238_PD_STATUS1 register
        to get the 5V contract current. It returns the current as an integer.

        :return: The 5V contract current.
        :rtype: int
        """
        amps = self.contract_a_5v
        return amps

    @property
    def get_5v_contract_volts(self) -> bool:
        """
        Reads the 5V contract voltage status from the HUSB238 device.

        This function reads the 2nd bit of the HUSB238_PD_STATUS1 register
        to get the 5V contract voltage status.
        It returns true if the 5V contract voltage bit is set.

        :return: The 5V contract voltage status.
        :rtype: bool
        """
        volts = self.contract_v_5v
        return volts

    @property
    def get_cc_direction(self) -> bool:
        """
        Reads the CC direction from the HUSB238 device.

        This function reads the 7th bit of the HUSB238_PD_STATUS1 register to get the CC direction.
        It prints "CC2 connected" if true and "CC1 connected" if false.

        :return: The CC status as a boolean value - false is CC1 connected, true is CC2 connected.
        :rtype: bool
        """
        direction = self.cc_direction
        if direction:
            print("CC2 connected")
        else:
            print("CC1 connected")
        return direction

    @property
    def get_response(self) -> str:
        """
        Reads the PD response from the HUSB238 device.

        This function reads bits 3-5 of the HUSB238_PD_STATUS1 register to get the PD response.
        It returns the response as a string corresponding to the HUSB238_ResponseCodes enum value.

        :return: The PD response.
        :rtype: str
        """
        pd_msg = self.PDO_RESPONSE_CODES[self.pd_response]
        return pd_msg

    @property
    def get_source_capabilities(self) -> int:
        """
        Retrieves the source capabilities of the HUSB238 device.

        This function writes to the GO_COMMAND register to send out a Get_SRC_Cap command.
        Specifically, it writes 0b00100 to the bottom 5 bits of the GO_COMMAND register.

        See: GO_COMMAND register in HUSB238 Register Information (Page 7)
        """
        self._go_command = 0x02
        time.sleep(0.01)  # 10 milliseconds delay
        return self._src_pdo

    @property
    def is_attached(self) -> bool:
        """
        Reads the attachment status from the HUSB238 device.

        This function reads the 6th bit of the HUSB238_PD_STATUS1 register
        to get the attachment status.
        It returns true if the attachment status bit is set.

        :return: The attachment status as a boolean value.
        :rtype: bool
        """
        status = self.attachment_status
        return status

    @property
    def read_current(self) -> typing.Union[int, str]:
        """
        Reads the source current from the HUSB238 device.

        This function reads the bottom four bits (0-3) of the HUSB238_PD_STATUS0 register
        to get the source current. It returns the current as an integer
        or a string if unable to read.

        :return: The source current or a string indicating an error.
        :rtype: Union[int, str]
        """
        if self.pd_src_current in self.PDO_TO_CURRENT:
            pdo_value = self.PDO_TO_CURRENT[self.pd_src_current]
        else:
            pdo_value = "Unable to read current"
        return pdo_value

    @property
    def read_voltage(self) -> typing.Union[int, str]:
        """
        Reads the source voltage from the HUSB238 device.

        This function reads bits 4-7 of the HUSB238_PD_STATUS0 register to get the source voltage.
        It returns the voltage as an integer or a string if unable to read.

        :return: The source voltage or a string indicating an error.
        :rtype: Union[int, str]
        """
        time.sleep(0.01)  # 10 milliseconds delay
        if self.pd_src_voltage in self.PDO_TO_VOLTAGE:
            pdo_value = self.PDO_TO_VOLTAGE[self.pd_src_voltage]
        else:
            pdo_value = "Unable to read voltage"
        return pdo_value

    def reset(self) -> None:
        """
        Resets the HUSB238 device.

        This function sends a reset command to the HUSB238 device.
        """
        self._go_command = 0x01

    def set_value(self) -> None:
        """
        Requests Power Delivery (PD) from the HUSB238 device.

        This function writes to the GO_COMMAND register to request a PD contract.
        Specifically, it writes 0b00001 to bits 0-1 of the GO_COMMAND register.

        See: GO_COMMAND register in HUSB238 Register Information (Page 7)
        """
        self._go_command = 0b00001

    @property
    def value(self) -> int:
        """
        Selects a PD output.

        :param voltage: The PD selection as an integer voltage value.
        :type voltage: int

        This function writes to bits 4-7 of the SRC_PDO register to select a PD.
        """
        return self.value

    @value.setter
    def value(self, voltage: int) -> None:
        if voltage not in self.VOLTAGE_TO_PDO:
            raise ValueError(f"Invalid voltage: {voltage}V")
        pdo_value = self.VOLTAGE_TO_PDO[voltage]
        self.selected_pd = pdo_value
