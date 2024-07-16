import time
from flask import session
from Modbus_comands import send_modbus_command  # Импорт вашей библиотеки Modbus
import funcs
from flask import redirect, url_for, session


def exec_by_name(func_name, client, table_data, emergency_stop_event):
    for command_data in table_data:
        if emergency_stop_event.is_set():
            session['log'] += "\nEmergency stop activated. Execution stopped immediately.\n"
            funcs.power_off()
            return redirect(url_for('index'))
        if command_data.get('func_name') == func_name:
            device_addr = int(command_data.get('deviceAddr'))
            command = command_data.get('commandNo')
            register = int(command_data.get('register'))
            value = int(command_data.get('value'))
            delay = int(command_data.get('delay'))
            response, success = send_modbus_command(device_addr, command, register, value, client)
            session['log'] += f">> {func_name}\n<< Response: {response}\n"
            if not success:
                return  # Остановить выполнение при ошибке
            time.sleep(delay)
            return response
    return f"Command {func_name} not found.", False


def execute_commands_run(emergency_stop_event, client, table_data):
    exec_by_name('illuminator_on', client, table_data, emergency_stop_event)

    if ((exec_by_name('slave1_sensor_dir2', client, table_data, emergency_stop_event)[0] != 2)
            or (exec_by_name('slave2_sensor_dir2', client, table_data, emergency_stop_event)[0] != 2)):

        raise ValueError("Axis are not in first direction, needed to prepare device")

    while True:
        response = exec_by_name('slave1_cassette_sensor', client, table_data, emergency_stop_event)[0]
        if response is True:  # Если первое значение в response True
            exec_by_name('red_off', client, table_data, emergency_stop_event)
            exec_by_name('green_on', client, table_data, emergency_stop_event)
            break  # Выход из цикла, если условие выполнено
        else:
            exec_by_name('green_off', client, table_data, emergency_stop_event)
            exec_by_name('red_on', client, table_data, emergency_stop_event)

    while True:
        response = exec_by_name('slave1_check_cassette', client, table_data, emergency_stop_event)

        if response[6] is False and response[7] is False:
            exec_by_name('red_off', client, table_data, emergency_stop_event)
            exec_by_name('green_on', client, table_data, emergency_stop_event)
            break  # Выход из цикла, если условие выполнено
        else:
            exec_by_name('green_off', client, table_data, emergency_stop_event)
            exec_by_name('red_on', client, table_data, emergency_stop_event)
    exec_by_name('drum_power_off', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_dir2', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    # if exec_by_name('slave1_sensor_dir2', client, table_data, emergency_stop_event)[0] != 4:
    #     exec_by_name('slave1_axis1_dir1', client, table_data, emergency_stop_event)
    #     exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    #     exec_by_name('slave1_axis1_dir2', client, table_data, emergency_stop_event)
    #     exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    #     if exec_by_name('slave1_sensor_dir2', client, table_data, emergency_stop_event)[0] != 4:
    #         session['log'] += f" Не удалось доехать до положения 2"
    #         return
    exec_by_name('solenoid3_on', client, table_data, emergency_stop_event)
    exec_by_name('solenoid4_on', client, table_data, emergency_stop_event)
    exec_by_name('drum_115_steps', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_349', client, table_data, emergency_stop_event)
    exec_by_name('solenoid3_off', client, table_data, emergency_stop_event)
    exec_by_name('solenoid4_off', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_dir1', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_210', client, table_data, emergency_stop_event)
    exec_by_name('strictly_in_positive_way', client, table_data, emergency_stop_event)
    exec_by_name('drum_in_35_1', client, table_data, emergency_stop_event)
    exec_by_name('drum_run', client, table_data, emergency_stop_event)
    exec_by_name('slave2_axis1_dir2', client, table_data, emergency_stop_event)
    exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    exec_by_name('solenoid5_on', client, table_data, emergency_stop_event)
    exec_by_name('solenoid6_on', client, table_data, emergency_stop_event)
    exec_by_name('drum_half_in_positive', client, table_data, emergency_stop_event)
    exec_by_name('drum_run_half_positive', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_210', client, table_data, emergency_stop_event)
    exec_by_name('strictly_in_positive_way', client, table_data, emergency_stop_event)
    exec_by_name('drum_in_35_1', client, table_data, emergency_stop_event)
    exec_by_name('drum_run', client, table_data, emergency_stop_event)
    exec_by_name('drum_120_steps', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_348', client, table_data, emergency_stop_event)
    exec_by_name('solenoid5_off', client, table_data, emergency_stop_event)
    exec_by_name('solenoid6_off', client, table_data, emergency_stop_event)
    exec_by_name('drum_power_off', client, table_data, emergency_stop_event)
    exec_by_name('slave2_axis1_dir1', client, table_data, emergency_stop_event)
    exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    while True:
        response = exec_by_name('slave2_cassette_sensor', client, table_data, emergency_stop_event)
        if response[0] is True:  # Если первое значение в response True
            exec_by_name('red_off', client, table_data, emergency_stop_event)
            exec_by_name('green_on', client, table_data, emergency_stop_event)
            break
        else:
            exec_by_name('green_off', client, table_data, emergency_stop_event)
            exec_by_name('red_on', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_steps_up', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_run_up', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_steps_straight', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_run_straight', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_steps_back', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_run_back', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_dir1', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_run_down', client, table_data, emergency_stop_event)
    exec_by_name('drum_power_off', client, table_data, emergency_stop_event)
    exec_by_name('slave2_axis1_dir2', client, table_data, emergency_stop_event)
    exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    # if exec_by_name('slave2_sensor_dir2', client, table_data, emergency_stop_event)[0] != 4:
    #     exec_by_name('slave2_axis1_dir1', client, table_data, emergency_stop_event)
    #     exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    #     exec_by_name('slave2_axis1_dir2', client, table_data, emergency_stop_event)
    #     exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    #     if exec_by_name('slave2_sensor_dir2', client, table_data, emergency_stop_event)[0] != 4:
    #         session['log'] += f" Не удалось доехать до положения 2"
    #         return
    exec_by_name('solenoid5_on', client, table_data, emergency_stop_event)
    exec_by_name('solenoid6_on', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_210', client, table_data, emergency_stop_event)
    exec_by_name('strictly_in_positive_way', client, table_data, emergency_stop_event)
    exec_by_name('drum_in_35_1', client, table_data, emergency_stop_event)
    exec_by_name('drum_run', client, table_data, emergency_stop_event)
    exec_by_name('solenoid5_off', client, table_data, emergency_stop_event)
    exec_by_name('solenoid6_off', client, table_data, emergency_stop_event)
    exec_by_name('slave2_axis1_dir1', client, table_data, emergency_stop_event)
    exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_dir2', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    exec_by_name('solenoid3_on', client, table_data, emergency_stop_event)
    exec_by_name('solenoid4_on', client, table_data, emergency_stop_event)
    exec_by_name('drum_half_in_negative_way', client, table_data, emergency_stop_event)
    exec_by_name('drum_run_half_negative', client, table_data, emergency_stop_event)
    exec_by_name('drum_run_123_steps', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_349', client, table_data, emergency_stop_event)
    exec_by_name('solenoid3_off', client, table_data, emergency_stop_event)
    exec_by_name('solenoid4_off', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_dir1', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    exec_by_name('solenoid1_on', client, table_data, emergency_stop_event)
    exec_by_name('solenoid2_on', client, table_data, emergency_stop_event)
    exec_by_name('solenoid1_off', client, table_data, emergency_stop_event)
    exec_by_name('solenoid2_off', client, table_data, emergency_stop_event)
    exec_by_name('green_off', client, table_data, emergency_stop_event)


def execute_commands_prepare_dev(client, table_data, emergency_stop_event):
    exec_by_name('illuminator_on', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_dir1', client, table_data, emergency_stop_event)
    exec_by_name('slave1_axis1_run', client, table_data, emergency_stop_event)
    exec_by_name('slave2_axis1_dir1', client, table_data, emergency_stop_event)
    exec_by_name('slave_2_run', client, table_data, emergency_stop_event)
    exec_by_name('interraptions1', client, table_data, emergency_stop_event)
    exec_by_name('drum_direction', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_210', client, table_data, emergency_stop_event)
    exec_by_name('strictly_in_positive_way', client, table_data, emergency_stop_event)
    exec_by_name('drum_in_35_1', client, table_data, emergency_stop_event)
    exec_by_name('drum_run_87_steps', client, table_data, emergency_stop_event)
    exec_by_name('drum_10_348', client, table_data, emergency_stop_event)
    exec_by_name('interraptions2', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_dir1', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_run_down', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_back', client, table_data, emergency_stop_event)
    exec_by_name('focus_axis_run_full_back', client, table_data, emergency_stop_event)














