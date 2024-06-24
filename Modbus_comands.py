
def send_modbus_command(device_addr, command, register, value, client):
    command = int(command)
    response = MODBUS_COMMANDS[command-1](device_addr, register, value, client)
    return response


def read_coils(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_coils(address, count, slave)
    response = result.bits
    print(response)
    return response

def read_discrete_inputs(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_discrete_inputs(address, count, slave)
    response = result.registers
    return response

def read_holding_register(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_holding_registers(address, count, slave)
    response = result.registers
    return response

def read_input_registers(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_input_registers(address, count, slave)
    response = result.registers
    return response

def write_coil(device_addr, register, value, client):
    print("ну вызвалась же че за хуйня")
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_coil(address, value, slave)
    print(response)
    return response

def  write_register(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_register(address, value, slave)
    return response



def format_command_as_string(message):
    return ' '.join(format(x, '02X') for x in message)

def calculate_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

MODBUS_COMMANDS = [read_coils, read_discrete_inputs, read_holding_register,
                  read_input_registers, write_coil, write_register]