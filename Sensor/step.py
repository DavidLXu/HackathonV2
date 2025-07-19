import serial
import time
import struct
import glob
import os

def get_available_serial_ports():
    """
    Get list of available serial ports
    
    Returns:
        list: List of available serial port paths
    """
    ports = []
    
    # Common serial port patterns
    patterns = ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/ttyAMA*', '/dev/ttyS*']
    
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    
    return sorted(ports)

class ESP32SerialCommunicator:
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200):
        """
        Initialize serial communication with ESP32
        
        Args:
            port (str): Serial port (default: /dev/ttyAMA0 for Raspberry Pi)
            baudrate (int): Baud rate (default: 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        
    def connect(self):
        """Establish serial connection with ESP32"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            print(f"Connected to ESP32 on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to ESP32: {e}")
            print(f"Available ports: {get_available_serial_ports()}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from ESP32")
    
    def distance_to_hex(self, distance):
        """
        Convert distance (0-100) to 4-digit hexadecimal
        
        Args:
            distance (int): Distance value (0-100)
            
        Returns:
            str: 4-digit hexadecimal string
        """
        if not 0 <= distance <= 100:
            raise ValueError("Distance must be between 0 and 100")
        
        # Convert to 4-digit hex (0x0000 to 0x0064)
        hex_value = format(distance, '04x').upper()
        return hex_value
    
    def send_distance(self, distance):
        """
        Send distance value in FE____0E format
        
        Args:
            distance (int): Distance value (0-100)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            print("Serial connection not established")
            return False
        
        try:
            # Convert distance to 4-digit hex
            hex_distance = self.distance_to_hex(distance)
            
            # Create message in FE____0E format
            message = f"FE{hex_distance}0E"
            
            # Convert string to bytes and send
            message_bytes = message.encode('utf-8')
            self.serial_connection.write(message_bytes)
            
            print(f"Sent: {message} (distance: {distance})")
            return True
            
        except Exception as e:
            print(f"Error sending distance: {e}")
            return False
    
    def read_response(self, timeout=1):
        """
        Read response from ESP32
        
        Args:
            timeout (int): Timeout in seconds
            
        Returns:
            str: Response from ESP32 or None if timeout
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            return None
        
        try:
            self.serial_connection.timeout = timeout
            response = self.serial_connection.readline()
            if response:
                return response.decode('utf-8').strip()
            return None
        except Exception as e:
            print(f"Error reading response: {e}")
            return None

def main():
    """Example usage of ESP32SerialCommunicator"""
    
    # Initialize communicator
    # You may need to change the port based on your setup
    # Common ports: /dev/ttyUSB0, /dev/ttyACM0, /dev/ttyS0
    communicator = ESP32SerialCommunicator(port='/dev/ttyAMA0', baudrate=115200)
    
    # Connect to ESP32
    if not communicator.connect():
        print("Failed to connect to ESP32")
        return
    
    try:
        # Example: Send different distance values
        test_distances = [0, 25, 50, 75, 100]
        
        for distance in test_distances:
            # Send distance
            if communicator.send_distance(distance):
                # Wait a bit for ESP32 to process
                time.sleep(0.5)
                
                # Try to read response
                response = communicator.read_response()
                if response:
                    print(f"Received: {response}")
                else:
                    print("No response received")
            
            # Wait between sends
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        # Clean up
        communicator.disconnect()

if __name__ == "__main__":
    main()
