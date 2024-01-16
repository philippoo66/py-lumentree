import serial  # Du wirst vielleicht pyserial installieren müssen: pip install pyserial
import argparse
import binascii
import sys
import time

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')

def read_register(register, length):
    # Modbus RTU-Adresse des Slaves (kann angepasst werden)
    slave_address = 1

    # Funktionscode für das Lesen von Registern
    function_code = 0x03

    # Datenpaket erstellen (Adresse, Funktionscode, Register und Länge)
    data = bytearray([slave_address, function_code, (register >> 8) & 0xFF, register & 0xFF, (length >> 8) & 0xFF, length & 0xFF])

    # CRC berechnen und dem Datenpaket hinzufügen
    crc_bytes = calculate_crc(data)
    data.extend(crc_bytes)

    return bytes(data)

def write_register():  #(register, length):
    # Modbus RTU-Adresse des Slaves (kann angepasst werden)
    slave_address = 1

    # Funktionscode für das Schreiben von Registern
    function_code = 0x10

    # Datenpaket erstellen (Adresse, Funktionscode, Register und Länge)
#    data = bytearray([slave_address, function_code, (register >> 8) & 0xFF, register & 0xFF, (length >> 8) & 0xFF, length & 0xFF])
    data = bytearray([slave_address, function_code, 0x00, 0x28, 0x02, 0x00, 0xC8])

    # CRC berechnen und dem Datenpaket hinzufügen
    crc_bytes = calculate_crc(data)
    data.extend(crc_bytes)

    return bytes(data)



def extract_decimal_from_response(response):
    # Überprüfen, ob die Antwort mindestens ausreichend Bytes hat
    if len(response) < 5:
        print("Ungültige Antwort. Nicht genügend Datenbytes.")
        return None

    # Datenlänge
    dlen = response[2]
    #print(dlen)

    # Datenbytes extrahieren
    data_bytes = response[3:-3]
    print(dlen, binascii.hexlify(data_bytes).decode('utf-8'))

    # Jedes Wertepaar in zwei Bytes aufteilen
    #value_pairs = [data_bytes[i:i+2] for i in range(0, len(data_bytes), 2)]
    value_pairs = [data_bytes[i:i+2] for i in range(0, dlen, 2)]

    # Bytes in Dezimalzahl konvertieren und in einer Liste speichern
    decimal_values = [int.from_bytes(pair, byteorder='big', signed=True) for pair in value_pairs]

    return decimal_values

'''
# Beispielverwendung
example_response = bytes.fromhex("01 03 04 01 02 03 04 3A B9")  # Beispielantwort mit 4 Datenbytes
decimal_values = extract_decimal_from_response(example_response)

print("Dezimalwerte:", decimal_values)
'''

def send_modbus_request(request, port='COM1', baudrate=9600):
    with serial.Serial(port, baudrate, timeout=1) as ser:
        ser.write(request)
        response = ser.readall()
    return response


def do_read(register_to_read:int, read_length:int = 1):
    port_name = 'COM4'  # Ersetze dies durch den tatsächlichen COM-Port-Namen, den du verwendest

    modbus_request = read_register(register_to_read, read_length)
    response = send_modbus_request(modbus_request, port=port_name)
    print(register_to_read, "Modbus Antwort:", bbbstr(response)) #response.hex().upper())

    decimal_values = extract_decimal_from_response(response)
    print(register_to_read, "Dezimalwerte:", decimal_values)


def do_write():  #(register_to_read:int, read_length:int = 1):
    port_name = 'COM4'  # Ersetze dies durch den tatsächlichen COM-Port-Namen, den du verwendest

    #temp
    register_to_read = 40

    modbus_request = write_register()  #(register_to_read, read_length)
    print (bbbstr(modbus_request))

    response = send_modbus_request(modbus_request, port=port_name)
    print(register_to_read, "Modbus Antwort:", bbbstr(response)) #response.hex().upper())

    # decimal_values = extract_decimal_from_response(response)
    # print(register_to_read, "Dezimalwerte:", decimal_values)


def bbbstr(data_buffer):
    return ' '.join([format(byte, '02X') for byte in data_buffer])

#if __name__ == "__main__":
# Überprüfen, ob genügend Befehlszeilenargumente vorhanden sind
if len(sys.argv) != 4:
    print("Verwendung: python script.py arg1 arg2 arg3")
    sys.exit() #(1)  # Beende das Skript mit einem Fehlercode
    

# Die Befehlszeilenargumente erfassen
arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]
'''
# Jetzt kannst du mit den erfassten Argumenten arbeiten
print("Argument 1:", arg1)
print("Argument 2:", arg2)
print("Argument 3:", arg3)
'''

if (arg1 == "s"):
    for i in range(int(arg2), int(arg3)):
        do_read(i)
#        time.sleep(1)
        print()

elif (arg1 == "r"):
    do_read(int(arg2), int(arg3))

elif (arg1 == "w"):
    do_write()

else:
    print("bad command:", arg1)
    








