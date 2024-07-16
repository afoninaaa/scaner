def send_modbus_command(device_addr, command, register, value, client):
    command = int(command)
    response = MODBUS_COMMANDS[command-1](device_addr, register, value, client)
    return response


def read_coils(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    response = client.read_coils(address, count, slave).bits
    if response:
        success = True
    else:
        success = False
    return response, success


def read_discrete_inputs(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    response = client.read_discrete_inputs(address, count, slave).bits
    if response:
        success = True
    else:
        success = False
    return response, success


def read_holding_register(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    response = client.read_holding_registers(address, count, slave).registers
    if response:
        success = True
    else:
        success = False
    return response, success


def read_input_registers(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    response = client.read_input_registers(address, count, slave).registers
    if response:
        success = True
    else:
        success = False
    return response, success


def write_coils(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_coil(address, value, slave)
    if response:
        success = True
    else:
        success = False
    return response, success


def write_register(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_register(address, value, slave)
    if response:
        success = True
    else:
        success = False
    return response, success


def write_multiply_registers(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_registers(address, value, slave)
    if response:
        success = True
    else:
        success = False
    return response, success


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
                   read_input_registers, write_coils, write_register, write_multiply_registers]
