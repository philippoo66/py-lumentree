import serial  # Du wirst vielleicht pyserial installieren müssen: pip install pyserial
import sys
import time


# utils
def bbbstr(data_buffer):
    return ' '.join([format(byte, '02X') for byte in data_buffer])


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
    #print(dlen, binascii.hexlify(data_bytes).decode('utf-8'))

    # Jedes Wertepaar in zwei Bytes aufteilen
    #value_pairs = [data_bytes[i:i+2] for i in range(0, len(data_bytes), 2)]
    value_pairs = [data_bytes[i:i+2] for i in range(0, dlen, 2)]

    # Bytes in Dezimalzahl konvertieren und in einer Liste speichern
    decimal_values = [int.from_bytes(pair, byteorder='big', signed=True) for pair in value_pairs]

    return decimal_values


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


def send_modbus_request(request):
    # HIER Einstellungen ggf. anpassen!
    port='COM1'
    baudrate=9600
    timeout=0.5
    with serial.Serial(port, baudrate=baudrate, timeout=timeout) as ser:
        ser.write(request)
        response = ser.readall()
    return response


def get_read_request(register, length):
    # Modbus RTU-Adresse des Slaves (kann angepasst werden)
    slave_address = 1

    # Funktionscode für das Lesen von Registern
    function_code = 0x03

    # Datenpaket erstellen (Adresse, Funktionscode, Register und Länge)
    data = bytearray([slave_address, 
                      function_code, 
                      (register >> 8) & 0xFF, 
                      register & 0xFF, 
                      (length >> 8) & 0xFF, 
                      length & 0xFF])

    # CRC berechnen und dem Datenpaket hinzufügen
    crc_bytes = calculate_crc(data)
    data.extend(crc_bytes)

    return bytes(data)


def get_write_request_40_20h():  # nur Test
    # Modbus RTU-Adresse des Slaves (kann angepasst werden)
    slave_address = 1

    # Funktionscode für das Lesen von Registern
    function_code = 0x10

    # Datenpaket erstellen (Adresse, Funktionscode, Register und Länge)

    # Slave_Addr
    # Fct_Code
    # Reg_Start_Addr_Hi
    # Reg_Start_Addr_Lo
    # Anzahl_Reg_Hi
    # Anzahl_Reg_Lo
    # Anzahl_Bytes (n*2)
    # Reg0_Wert_Hi
    # Reg0_Wert_Lo
    #[Reg1_Wert_Hi
    # Reg1_Wert_Lo
    # ...]
    # CRC_0
    # CRC_1

#    data = bytearray([slave_address, function_code, (register >> 8) & 0xFF, register & 0xFF, (length >> 8) & 0xFF, length & 0xFF])
    # 40 schreiben auf 32 (dez)
    data = bytearray([slave_address, function_code, 0x00, 0x28, 0x00, 0x01, 0x02, 0x00, 0x20])

    # CRC berechnen und dem Datenpaket hinzufügen
    crc_bytes = calculate_crc(data)
    data.extend(crc_bytes)

    return bytes(data)

def get_write_request(register:int, value:int):
    # Modbus RTU-Adresse des Slaves (kann angepasst werden)
    slave_address = 1

    # Funktionscode für das Schreiben von Registern
    function_code = 0x10

    # Datenpaket erstellen (Adresse, Funktionscode, Register und Länge)

    # Slave_Addr
    # Fct_Code
    # Reg_Start_Addr_Hi
    # Reg_Start_Addr_Lo
    # Anzahl_Reg_Hi
    # Anzahl_Reg_Lo
    # Anzahl_Bytes (n*2)
    # Reg0_Wert_Hi
    # Reg0_Wert_Lo
    #[Reg1_Wert_Hi
    # Reg1_Wert_Lo
    # ...]
    # CRC_0
    # CRC_1

    # wir schreiben hier nur 1 einziges Register!
    length = 1

    data = bytearray([slave_address, 
                      function_code, 
                      (register >> 8) & 0xFF, 
                      register & 0xFF, 
                      (length >> 8) & 0xFF, 
                      length & 0xFF, 
                      length * 2,
                      (value >> 8) & 0xFF, 
                      value & 0xFF])
 
    # CRC berechnen und dem Datenpaket hinzufügen
    crc_bytes = calculate_crc(data)
    data.extend(crc_bytes)

    return bytes(data)


def do_read(register_to_read:int, read_length:int = 1):
    modbus_request = get_read_request(register_to_read, read_length)
    print(register_to_read, "modbus_request:", bbbstr(modbus_request))
 
    response = send_modbus_request(modbus_request)
    print(register_to_read, "Modbus_Antwort:", bbbstr(response)) 

    decimal_values = extract_decimal_from_response(response)
    print(register_to_read, "Dezimalwerte:", decimal_values)


def do_write(register_to_write:int, value:int):
    modbus_request = get_write_request(register_to_write, value)
    print(register_to_write, "modbus_request:", bbbstr(modbus_request))
 
    response = send_modbus_request(modbus_request)
    print(register_to_write, "Modbus Antwort:", bbbstr(response)) 



# main ------------
def main():
    # Überprüfen, ob genügend Befehlszeilenargumente vorhanden sind
    if len(sys.argv) != 4:
        print("Verwendung: python script.py arg1 arg2 arg3")
        sys.exit() #(1)  # Beende das Skript mit einem Fehlercode
        
    # Die Befehlszeilenargumente erfassen
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]

    if (arg1 == "s"):
        for i in range(int(arg2), int(arg3)+1):
            do_read(i)
    #        time.sleep(1)
            print()

    elif (arg1 == "r"):
        do_read(int(arg2), int(arg3))

    elif (arg1 == "w"):
       do_write(int(arg2), int(arg3))

    elif (arg1 == "c"):  # cyclic
        try:
            while(True):
                do_read(int(arg2))
                time.sleep(float(arg3))
        except Exception as e:
            print(e)
        return

    elif (arg1 == "t"): # test
        mybytes = get_write_request(40,32)
        print(bbbstr(mybytes))  

    else:
        print("bad command:", arg1)


main()