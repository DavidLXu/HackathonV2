#!/usr/bin/env python3
"""
Script to find and test available serial ports
"""

import serial
import glob
import time

def get_available_serial_ports():
    """Get list of available serial ports"""
    ports = []
    patterns = ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/ttyAMA*', '/dev/ttyS*']
    
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    
    return sorted(ports)

def test_port(port_name, baudrate=115200):
    """Test if a serial port can be opened"""
    try:
        ser = serial.Serial(port_name, baudrate, timeout=1)
        ser.close()
        return True
    except:
        return False

def main():
    print("Available serial ports:")
    ports = get_available_serial_ports()
    
    if not ports:
        print("No serial ports found!")
        return
    
    for i, port in enumerate(ports, 1):
        test_result = "✓" if test_port(port) else "✗"
        print(f"{i}. {port} {test_result}")
    
    print("\nRecommended ports for ESP32:")
    print("- /dev/ttyAMA0: Hardware serial (GPIO 14/15)")
    print("- /dev/ttyUSB0: USB-to-serial adapter")
    print("- /dev/ttyACM0: Arduino/ESP32 via USB")
    
    print("\nTo use hardware serial (ttyAMA0), you may need to:")
    print("1. Disable Bluetooth: sudo raspi-config")
    print("2. Enable serial interface: sudo raspi-config")
    print("3. Disable serial console: sudo raspi-config")

if __name__ == "__main__":
    main() 