import serial
import serial.tools.list_ports
import time
import sys

HEADER = 0xFE
TAIL = 0x0E

def list_ports():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No available serial ports found.")
        return None

    print("Available serial ports:")
    for i, p in enumerate(ports):
        print(f"{i + 1}. {p.device} - {p.description}")
    return ports

def choose_port(ports):
    while True:
        try:
            choice = int(input("Please choose a port by number: "))
            if 1 <= choice <= len(ports):
                return ports[choice - 1].device
            else:
                print("Invalid choice. Please select a valid port number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def find_available_port():
    ports = list_ports()
    if not ports:
        return None

    chosen_port = choose_port(ports)
    try:
        ser = serial.Serial(chosen_port, baudrate=9600, timeout=1)
        print(f"Successfully connected to {chosen_port}")
        return ser
    except Exception as e:
        print(f"Unable to connect to {chosen_port}: {e}")
        return None

def encode_distance_packet(distance_mm):
    # Limit the distance to be within 0-65535
    distance = max(0, min(65535, int(distance_mm)))
    high = (distance >> 8) & 0xFF
    low = distance & 0xFF
    return bytes([HEADER, high, low, TAIL])

def main():
    ser = find_available_port()
    if not ser:
        sys.exit(1)

    while True:
        try:
            user_input = input("Enter the target distance in mm (enter 'q' to quit): ").strip()
            if user_input.lower() == 'q':
                print("Exiting the program.")
                break

            if not user_input.isdigit():
                print("Invalid input. Please enter a valid number.")
                continue

            distance = int(user_input)
            packet = encode_distance_packet(distance)
            ser.write(packet)
            print(f"Sent: {packet.hex().upper()}")

            time.sleep(0.1)  # Wait for response
            while ser.in_waiting:
                response = ser.readline().decode(errors='ignore').strip()
                print(f"Response: {response}")

        except KeyboardInterrupt:
            print("\nManual interrupt. Exiting the program.")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

    ser.close()

if __name__ == "__main__":
    main()
