import time
def send_modbus_command(device_addr, command, register, value, client):
    command = int(command)
    response = MODBUS_COMMANDS[command-1](device_addr, register, value, client)
    return response

# def solenoid12_1(client):
#     response = []
#     result = client.write_coil(1, 1, 1)
#     response += result
#     result = client.write_coil(2, 1, 1)
#     response += result
#     return response
# def solenoid12_0(client):
#     response = []
#     result = client.write_coil(1, 0, 1)
#     response += result
#     result = client.write_coil(2, 0, 1)
#     response += result
#     return response
#
# def solenoid34_1(client):
#     response = []
#     result = client.write_coil(3, 1, 1)
#     response += result
#     result = client.write_coil(4, 1, 1)
#     response += result
#     return response
# def solenoid34_0(client):
#     response = []
#     result = client.write_coil(3, 0, 1)
#     response += result
#     result = client.write_coil(4, 0, 1)
#     response += result
#     return response
#
# def solenoid56_1(client):
#     response = []
#     result = client.write_coil(5, 1, 1)
#     response += result
#     result = client.write_coil(6, 1, 1)
#     response += result
#     return response
# def solenoid56_0(client):
#     response = []
#     result = client.write_coil(5, 0, 1)
#     response += result
#     result = client.write_coil(6, 0, 1)
#     response += result
#     return response
#
#
# def s1_to1point(client):
#     response = []
#     result = client.write_register(4, 1, 1)
#     response += result
#     result = client.write_register(5, 221, 1)
#     response += result
#     return response
# def s1_to2point(client):
#     response = []
#     result = client.write_register(4, 2, 1)
#     response += result
#     result = client.write_register(5, 221, 1)
#     response += result
#     return response
#
# def s2_to1point(client):
#     response = []
#     result = client.write_register(4, 1, 2)
#     response += result
#     result = client.write_register(5, 221, 2)
#     response += result
#     return response
#
# def s2_to2point(client):
#     response = []
#     result = client.write_register(4, 2, 2)
#     response += result
#     result = client.write_register(5, 221, 2)
#     response += result
#     return response
# def alignment_drum(client):
#     response =[]
#     result = client.write_register(10, 210, 1)
#     response += result
#     result = client.write_coil(32,1,1)
#     response += result
#     result = client.write_coil(35, 1, 1)
#     response += result
#     time.sleep(0.5)
#     result = client.write_register(7, 79, 1)
#     response += result
#     result = client.write_register(10, 92, 1)
#     response += result
#     return response
#
# def turn180(client):
#     response = []
#     result = client.write_register(7, 3520, 1)
#     response += result
#     result = client.write_register(10, 93, 1)
#     response += result
#     return result
# def s2_up(client):
#     response = []
#     result = client.write_register(12, 8000, 2)
#     response += result
#     result = client.wrte_register(15, 93, 2)
#     response += result
#     return response
# def s2_str(client):
#     response = []
#     result = client.write_register(7, 1000, 2)
#     response += result
#     result = client. write_register(10, 93, 2)
#     response += result
#     return response
# def s2_back(client):
#     response =[]
#     result = client.write_register(7, 1000, 2)
#     response += result
#     result = client.write_register(10, 92, 2)
#     response += result
#     return response
# def s2_down(client):
#     response = []
#     result = client.write_register(14, 1, 2)
#     response += result
#     result = client.write_register(15, 221, 2)
#     response += result
#     return response

def read_coils(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_coils(address, count, slave)
    response = result.bits
    return response

def read_discrete_inputs(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_discrete_inputs(address, count, slave)
    response = result.bits
    return response

def read_holding_register(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_holding_registers(address, count, slave)
    response = result.registers
    return response

# def check_cassette(result, exp_value):
#     # Проверка наличия кассеты
#     if result[] == exp_value:
#         return True
#     else:
#         return False
#
#
# if check_cassette(result, exp_value):
#     response = result.registers
# else:
#     time.sleep(3)
#     while True:
#         result =
#         if check_cassette(data, command["expected_value"]):
#             response = result.registers
#             break
#         else:
#             time.sleep(3)


def read_input_registers(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    count = int(value)
    result = client.read_input_registers(address, count, slave)
    response = result.registers
    return response

def write_coils(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_coils(address, value, slave)
    return response

def  write_registers(device_addr, register, value, client):
    address = int(register)
    slave = int(device_addr)
    value = int(value)
    response = client.write_registers(address, value, slave)
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

# command_mapping = {
#     "solenoid12_1": solenoid12_1,
#     "solenoid12_0": solenoid12_0,
#     "solenoid34_1": solenoid34_1,
#     "solenoid34_0": solenoid34_0,
#     "solenoid56_1": solenoid56_1,
#     "solenoid56_0": solenoid56_0,
#     "s1_to1point": s1_to1point,
#     "s1_to2point": s1_to2point,
#     "s2_to1point": s2_to1point,
#     "s2_to2point": s2_to2point,
#     "alignment_drum": alignment_drum,
#     "turn180": turn180,
#     "s2_up": s2_up,
#     "s2_str": s2_str,
#     "s2_back": s2_back,
#     "s2_down": s2_down,
# }


MODBUS_COMMANDS = [read_coils, read_discrete_inputs, read_holding_register,
                  read_input_registers, write_coils, write_registers]