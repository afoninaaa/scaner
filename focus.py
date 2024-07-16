import time
from pymodbus.client import ModbusSerialClient as ModbusClient


# client = ModbusClient(method='rtu', port=comport_number, baudrate=form_data['baudrate'],
#                                       timeout=form_data['timeout'], parity=form_data['parity'],
#                                       stopbits=form_data['stopbit'], bytesize=8)
# client.connect()

def slave2_axis_run(client, slave, axis, point=None, steps=None, direct=None,
                    speed=None, micro_steps=None, speed_profile=None):

    if micro_steps and speed_profile:
        run_config(client, slave, axis, micro_steps, speed_profile)

    check_parameters(axis, slave, point, steps, direct, speed)

    use_steps = 1
    use_point = 0
    register = 0
    direction = 0
    registers = [0, 1, 0, 0]

    if point is not None:
        registers[2] = point
        use_point = 1
    if (steps is not None) and (steps >= 0):
        registers[0] = steps
    if direct is not None:
        direction = direct
    if speed is not None:
        registers[1] = speed

    register = register | (1 << 3) | (1 << 4) | (direction << 0) | (use_steps << 6) | (use_point << 7) | (1 << 8)
    registers[3] = register

    address_first = 2 + (axis - 1) * 5
    address_time2complete = 16 * axis + 6
    address_state = 16 * axis + 2

    response = client.write_registers(address_first, registers, slave)
    print(response)
    state = client.read_input_registers(address_state, 1, slave).registers[0] & 1
    while state != 0:
        time2complete = client.read_input_registers(address_time2complete, 1, slave).registers[0]
        time.sleep(time2complete/1000)
        state = client.read_input_registers(address_state, 1, slave).registers[0] & 1
        print(time2complete)


def run_config(client, slave,  axis, micro_steps, speed_profile):
    address_micro_steps = 16 + (axis - 1) * 16 + 3
    if micro_steps is not None:
        client.write_registers(address_micro_steps, micro_steps, slave)
    address_speed_profile = 16 + (axis - 1) * 16 + 15
    if speed_profile is not None:
        client.write_registers(address_speed_profile, speed_profile, slave)


def check_parameters(slave, axis, point, steps, direct, speed):
    if slave not in [1, 2]:
        raise ValueError("Parameter 'slave' can only take values 1 or 2.")
    if axis not in [1, 2, 3]:
        raise ValueError("Parameter 'axis' can only take values 1, 2, or 3.")
    if point is not None and point not in [0, 1, 2]:
        raise ValueError("Parameter 'point' can only take values 1 or 2.")
    if steps is not None and steps < 0:
        raise ValueError("Parameter 'steps' must be a positive value.")
    if direct is not None and direct not in [0, 1]:
        raise ValueError("Parameter 'direct' can only take values 0 or 1.")
    if speed is not None and speed <= 0:
        raise ValueError("Parameter 'speed' must be a positive value.")


