#!/usr/bin/env python3
"""
Simple example of sending a distance value to ESP32 via serial and receiving data
"""

from step import ESP32SerialCommunicator
import time

def send_single_distance(distance_value):
    """
    Send a single distance value to ESP32
    
    Args:
        distance_value (int): Distance value (0-100)
    """
    # Initialize communicator
    # Change port if needed: /dev/ttyAMA0, /dev/ttyUSB0, /dev/ttyACM0, /dev/ttyS0
    communicator = ESP32SerialCommunicator(port='/dev/ttyAMA0', baudrate=9600)
    
    # Connect to ESP32
    if not communicator.connect():
        print("Failed to connect to ESP32")
        return False
    
    try:
        # Send the distance value
        success = communicator.send_distance(distance_value)
        
        if success:
            print(f"Successfully sent distance {distance_value}")
            
            # Wait for potential response
            time.sleep(0.5)
            response = communicator.read_response()
            if response:
                print(f"ESP32 response: {response}")
        else:
            print(f"Failed to send distance {distance_value}")
            
        return success
        
    finally:
        # Clean up
        communicator.disconnect()

def receive_serial_data(duration=10):
    """
    Receive data from serial port for a specified duration
    
    Args:
        duration (int): How long to receive data in seconds
    """
    # Initialize communicator
    communicator = ESP32SerialCommunicator(port='/dev/ttyAMA0', baudrate=9600)
    
    # Connect to ESP32
    if not communicator.connect():
        print("Failed to connect to ESP32")
        return False
    
    print(f"Receiving data for {duration} seconds... (Press Ctrl+C to stop early)")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Read any available data
            data = communicator.read_response()
            if data:
                print(f"[{time.strftime('%H:%M:%S')}] Received: {data}")
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping data reception...")
    finally:
        # Clean up
        communicator.disconnect()
        print("Serial connection closed.")

def send_and_receive(distance_value, receive_duration=5):
    """
    Send a distance value and then receive data for a specified duration
    
    Args:
        distance_value (int): Distance value to send (0-100)
        receive_duration (int): How long to receive data after sending
    """
    # Initialize communicator
    communicator = ESP32SerialCommunicator(port='/dev/ttyAMA0', baudrate=9600)
    
    # Connect to ESP32
    if not communicator.connect():
        print("Failed to connect to ESP32")
        return False
    
    try:
        # Send the distance value
        success = communicator.send_distance(distance_value)
        
        if success:
            print(f"Successfully sent distance {distance_value}")
            
            # Wait a moment for processing
            time.sleep(0.5)
            
            # Now receive data for specified duration
            print(f"\nReceiving data for {receive_duration} seconds...")
            print("-" * 50)
            
            start_time = time.time()
            while time.time() - start_time < receive_duration:
                data = communicator.read_response()
                if data:
                    print(f"[{time.strftime('%H:%M:%S')}] Received: {data}")
                time.sleep(0.1)
                
        else:
            print(f"Failed to send distance {distance_value}")
            
        return success
        
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Clean up
        communicator.disconnect()
        print("Serial connection closed.")

if __name__ == "__main__":
    # Example: Send distance value 75 and then receive data
    distance = 75
    print(f"Sending distance value: {distance}")
    print(f"This will send: FE{format(distance, '04x').upper()}0E")
    print()
    
    # Option 1: Send and receive in one function
    send_and_receive(distance, receive_duration=10)
    
    # Option 2: Uncomment below to just receive data
    # print("\n" + "="*50)
    # print("Just receiving data...")
    # receive_serial_data(duration=10) 