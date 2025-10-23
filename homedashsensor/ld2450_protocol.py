"""
HLK-LD2450 24GHz mmWave Radar Sensor Protocol Implementation

This module provides a Python interface for communicating with the HLK-LD2450 radar sensor.
The protocol implementation is based on the official Hi-Link documentation and community 
reverse engineering efforts.

Original protocol reverse engineering and implementation credits:
- Hi-Link Electronic Co., Ltd. - Official LD2450 documentation
- Community contributors who documented the serial protocol
- Various GitHub repositories that helped decode the binary protocol

This implementation extends and adapts the original work for use in proximity detection
applications with advanced filtering and Python integration.

Author: edizaziz-dev
License: MIT
"""

import serial

COMMAND_HEADER = bytes.fromhex('FD FC FB FA')
COMMAND_TAIL = bytes.fromhex('04 03 02 01')

REPORT_HEADER = bytes.fromhex('AA FF 03 00')
REPORT_TAIL = bytes.fromhex('55 CC')

def _send_command(ser: serial.Serial, 
                 intra_frame_length: bytes,
                 command_word: bytes, 
                 command_value: bytes) -> bytes:
    '''
    Send a command to the radar (see docs 2.1.2)
    Parameters:
    - ser (serial.Serial): the serial port object
    - intra_frame_length (bytes): the intra frame length
    - command_word (bytes): the command word
    - command_value (bytes): the command value
    Returns:
    - response (bytes): the response from the radar
    '''
    # Create the command
    command = COMMAND_HEADER + intra_frame_length + command_word + command_value + COMMAND_TAIL
    ser.write(command)
    response = ser.read_until(COMMAND_TAIL)
    return response

def _get_command_success(response: bytes) -> bool:
    '''
    Check if the command was sent successfully
    Parameters:
    - response (bytes): the response from the radar
    Returns:
    - success (bool): True if the command was sent successfully, False otherwise
    ''' 
    success_int = int.from_bytes(response[8:10], byteorder='little', signed=True)
    if success_int == 0:
        return True
    else:
        return False

def enable_configuration_mode(ser: serial.Serial) -> bool:
    '''
    Set the radar to configuration mode (see docs 2.2.1)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the configuration mode was successfully enabled, False otherwise
    '''
    intra_frame_length = int(4).to_bytes(2, byteorder='little', signed=True)
    command_word = bytes.fromhex('FF 00')
    command_value = bytes.fromhex('01 00')

    response = _send_command(ser, intra_frame_length, command_word, command_value)
    command_successful = _get_command_success(response)
    if command_successful:
        print('Configuration mode enabled')
    else:
        print('Configuration enable failed')
    return command_successful

def end_configuration_mode(ser: serial.Serial) -> bool:
    '''
    End the configuration mode (see docs 2.2.2)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the configuration mode was successfully ended, False otherwise
    '''
    intra_frame_length = int(2).to_bytes(2, byteorder='little', signed=False)
    command_word = bytes.fromhex('FE 00')
    command_value = bytes.fromhex('')

    response = _send_command(ser, intra_frame_length, command_word, command_value)
    command_successful = _get_command_success(response)
    if command_successful:
        print('Configuration mode disabled')
    else:
        print('Configuration disable failed')
    return command_successful

def single_target_tracking(ser: serial.Serial) -> bool:
    '''
    Set the radar to single target tracking mode (see docs 2.2.3)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the single target tracking mode was successfully enabled, False otherwise
    '''
    intra_frame_length = int(2).to_bytes(2, byteorder='little', signed=True)
    command_word = bytes.fromhex('80 00')
    command_value = bytes.fromhex('')

    response = _send_command(ser, intra_frame_length, command_word, command_value)
    command_successful = _get_command_success(response)
    if command_successful:
        print('Single target tracking mode enabled')
    else:
        print('Single target tracking mode enable failed')
    return command_successful

def multi_target_tracking(ser: serial.Serial) -> bool:
    '''
    Set the radar to multi target tracking mode (see docs 2.2.4)
    Parameters:
    - ser (serial.Serial): the serial port object
    Returns:
    - success (bool): True if the multiple target tracking mode was successfully enabled, False otherwise
    '''
    intra_frame_length = int(2).to_bytes(2, byteorder='little', signed=True)
    command_word = bytes.fromhex('90 00')
    command_value = bytes.fromhex('')

    response = _send_command(ser, intra_frame_length, command_word, command_value)
    command_successful = _get_command_success(response)
    if command_successful:
        print('Multi target tracking mode enabled')
    else:
        print('Multi target tracking mode enable failed')
    return command_successful

def read_radar_data(serial_port_line: bytes) -> tuple:
    '''
    Read the basic mode data from the serial port line (see docs 2.3)
    Parameters:
    - serial_port_line (bytes): the serial port line
    Returns:
    - radar_data (tuple[12]): the radar data
        - [0-3] x, y, speed, distance_resolution of target 1
        - [4-7] x, y, speed, distance_resolution of target 2
        - [8-11] x, y, speed, distance_resolution of target 3
    '''
    # Check if the frame header and tail are present
    if REPORT_HEADER in serial_port_line and REPORT_TAIL in serial_port_line:
        # Interpret the target data
        if len(serial_port_line) == 30:
            target1_bytes = serial_port_line[4:12]
            target2_bytes = serial_port_line[12:20]
            target3_bytes = serial_port_line[20:28]

            all_targets_bytes = [target1_bytes, target2_bytes, target3_bytes]
            all_targets_data = []

            for target_bytes in all_targets_bytes:
                x = int.from_bytes(target_bytes[0:2], byteorder='little', signed=True)
                y = int.from_bytes(target_bytes[2:4], byteorder='little', signed=True)     
                speed = int.from_bytes(target_bytes[4:6], byteorder='little', signed=True)
                distance_resolution = int.from_bytes(target_bytes[6:8], byteorder='little', signed=False)
    
                # substract 2^15 depending if negative or positive
                x = x if x >= 0 else -2**15 - x
                y = y if y >= 0 else -2**15 - y
                speed = speed if speed >= 0 else -2**15 - speed

                # append target data to the list and flatten
                all_targets_data.extend([x, y, speed, distance_resolution])
            
            return tuple(all_targets_data)
        # if the target data is not 30 bytes long the line is corrupted
        else:
            print("Serial port line corrupted - not 30 bytes long")
            return None
    # if the header and tail are not present the line is corrupted
    else: 
        print("Serial port line corrupted - header or tail not present")
        return None

class LD2450:
    """
    A Python class for interfacing with the HLK-LD2450 24 GHz Radar Sensor
    """
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 256000, timeout: float = 1.0):
        """
        Initialize the LD2450 sensor
        
        Args:
            port (str): Serial port path (e.g., '/dev/ttyUSB0' on Linux)
            baudrate (int): Serial communication speed (default: 256000)
            timeout (float): Serial read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to the LD2450 sensor
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to LD2450 sensor: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Disconnect from the LD2450 sensor
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
    
    def read_targets(self) -> dict:
        """
        Read target data from the sensor
        
        Returns:
            dict: Dictionary containing target information, or None if read failed
        """
        if not self.connected or not self.serial:
            print("Sensor not connected")
            return None
            
        try:
            # Read a line from the serial port
            serial_port_line = self.serial.read_until(REPORT_TAIL)
            
            # Parse the radar data
            all_target_values = read_radar_data(serial_port_line)
            
            if all_target_values is None:
                return None
            
            # Unpack the values for easier access
            target1_x, target1_y, target1_speed, target1_distance_res, \
            target2_x, target2_y, target2_speed, target2_distance_res, \
            target3_x, target3_y, target3_speed, target3_distance_res = all_target_values
            
            return {
                'target1': {
                    'x': target1_x,          # mm
                    'y': target1_y,          # mm  
                    'speed': target1_speed,  # cm/s
                    'distance_resolution': target1_distance_res  # mm
                },
                'target2': {
                    'x': target2_x,          # mm
                    'y': target2_y,          # mm
                    'speed': target2_speed,  # cm/s
                    'distance_resolution': target2_distance_res  # mm
                },
                'target3': {
                    'x': target3_x,          # mm
                    'y': target3_y,          # mm
                    'speed': target3_speed,  # cm/s
                    'distance_resolution': target3_distance_res  # mm
                }
            }
        except Exception as e:
            print(f"Error reading from sensor: {e}")
            return None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()