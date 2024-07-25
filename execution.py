from command_sending.modbus_commands import send_modbus_command
from utils.modbus_utils import time_sleep
from flask import session


def exec_by_name(func_name, client, table_data):
    for command_data in table_data:
        if command_data.get('func_name') == func_name:
            device_addr = int(command_data.get('deviceAddr'))
            command = command_data.get('commandNo')
            register = int(command_data.get('register'))
            value = int(command_data.get('value'))
            delay = float(command_data.get('delay'))
            response, success = send_modbus_command(device_addr, command, register, value, client)
            session['log'] += f">> {func_name}\n<< Response: {response}\n"
            if not success:
                return  # Остановить выполнение при ошибке
            time_sleep(client, delay)
            print(response)
            return response
    return f"Command {func_name} not found.", False


def loading_module(client, table_data):
    # ожидание кассеты в модуле загрузки
    while True:
        response = exec_by_name('slave1_cassette_sensor', client, table_data)[0]
        if response is True:
            exec_by_name('yellow_off', client, table_data)
            exec_by_name('green_on', client, table_data)
            break
        else:
            exec_by_name('green_off', client, table_data)
            exec_by_name('yellow_on', client, table_data)
    # проверка на правильность вставки кассеты
    while True:
        response = exec_by_name('slave1_check_cassette', client, table_data)
        if response[6] is False and response[7] is False:
            exec_by_name('red_off', client, table_data)
            exec_by_name('green_on', client, table_data)
            break
        else:
            exec_by_name('green_off', client, table_data)
            exec_by_name('red_on', client, table_data)

    # выключение питания у барабана
    exec_by_name('drum_power_off', client, table_data)

    # каретка в положение 2 (до барабана)
    exec_by_name('slave1_axis1_dir2', client, table_data)
    exec_by_name('slave1_axis1_run', client, table_data)

    # проверка на позиции каретки
    if exec_by_name('slave1_sensor_dir2', client, table_data)[0] != 4:

        exec_by_name('slave1_axis1_dir1', client, table_data)
        exec_by_name('slave1_axis1_run', client, table_data)

        response = exec_by_name('slave1_cassette_sensor', client, table_data)[0]

        if response is True:
            exec_by_name('slave1_axis1_dir2', client, table_data)
            exec_by_name('slave1_axis1_run', client, table_data)

            if exec_by_name('slave1_sensor_dir2', client, table_data)[0] != 4:
                session['log'] += f" Не удалось доехать до положения 2"
                return

    # поворот барабана на полшага
    drum_module_half_steps(client, table_data)

    # каретка до первой позиции (от барабана)
    exec_by_name('slave1_axis1_dir1', client, table_data)
    exec_by_name('slave1_axis1_run', client, table_data)


def drum_module_half_steps(client, table_data):
    # соленоиды 3 и 4 включить
    exec_by_name('solenoid3_on', client, table_data)
    exec_by_name('solenoid4_on', client, table_data)
    # барабан на полшага
    exec_by_name('drum_115_steps', client, table_data)
    exec_by_name('drum_10_349', client, table_data)
    exec_by_name('drum_direction2', client, table_data)
    # соленоиды 3 и 4 выключить
    exec_by_name('solenoid3_off', client, table_data)
    exec_by_name('solenoid4_off', client, table_data)
    # барабан до флага
    exec_by_name('drum_10_466', client, table_data)
    exec_by_name('strictly_in_positive_way', client, table_data)
    exec_by_name('drum_in_35_1', client, table_data)


def drum_half_turn_positive(client, table_data):
    scanning_module_1part(client, table_data)
    # соленоиды 5 и 6 включить
    exec_by_name('solenoid5_on', client, table_data)
    exec_by_name('solenoid6_on', client, table_data)
    # барабан на полоборота в положительную сторону
    exec_by_name('drum_half_in_positive', client, table_data)
    exec_by_name('drum_run_half_positive', client, table_data)
    # барабан до датчика
    # exec_by_name('drum_10_466', client, table_data, emergency_stop_event)
    # exec_by_name('strictly_in_positive_way', client, table_data, emergency_stop_event)
    # exec_by_name('drum_in_35_1', client, table_data, emergency_stop_event)
    # exec_by_name('drum_run', client, table_data, emergency_stop_event)
    # # барабан минус 120 шагов
    # exec_by_name('drum_120_steps', client, table_data, emergency_stop_event)
    # exec_by_name('drum_10_348', client, table_data, emergency_stop_event)
    # соленоиды 5 и 6 выключить
    exec_by_name('solenoid5_off', client, table_data)
    exec_by_name('solenoid6_off', client, table_data)
    # выключить питание у барабана
    exec_by_name('drum_power_off', client, table_data)


def scanning_module_1part(client, table_data):
    # каретка до позиции 2 (до барабана)
    exec_by_name('slave2_axis1_dir2', client, table_data)
    exec_by_name('slave_2_run', client, table_data)


def scanning_module(client, table_data):
    # каретка к положению 1 (от барабана)
    exec_by_name('slave2_axis1_dir1', client, table_data)
    exec_by_name('slave_2_run', client, table_data)
    # проверка на доезд кассеты до сканирования
    while True:
        response = exec_by_name('slave2_cassette_sensor', client, table_data)
        if response[0] is True:
            exec_by_name('red_off', client, table_data)
            exec_by_name('green_on', client, table_data)
            break
        else:
            exec_by_name('green_off', client, table_data)
            exec_by_name('red_on', client, table_data)
    # ось сканирования наверх
    # for i in range(10):
    #     for k in range(4):
    #         exec_by_name('focus_axis_steps_up', client, table_data)
    #         exec_by_name('focus_axis_run_up', client, table_data)
    #         # тут захват изображения
    #     exec_by_name('axis1_steps1', client, table_data)
    #     exec_by_name('axis1_steps1_run1', client, table_data)
    #     for x in range(4):
    #         exec_by_name('focus_axis_steps_down', client, table_data)
    #         exec_by_name('focus_axis_run_down', client, table_data)
    #         # тут захват изображения
    #     exec_by_name('axis1_steps1', client, table_data)
    #     exec_by_name('axis1_steps1_run1', client, table_data)
    #     for k in range(4):
    #         exec_by_name('focus_axis_steps_up', client, table_data)
    #         exec_by_name('focus_axis_run_up', client, table_data)
    #         # тут захват изображения
    #     exec_by_name('focus_axis_steps_up', client, table_data)
    #     exec_by_name('focus_axis_run_up', client, table_data)
    #     exec_by_name('axis1_steps1_back', client, table_data)
    #     exec_by_name('axis1_steps1_run0', client, table_data)
    # # ось сканирования до первого положения
    # exec_by_name('focus_axis_dir1', client, table_data)
    # exec_by_name('focus_axis_run_down', client, table_data)
    # # ось сканирования до первого положения
    #
    # exec_by_name('slave2_axis1_dir1', client, table_data)
    # exec_by_name('slave_2_run', client, table_data)
    # выключить питание барабана
    exec_by_name('drum_power_off', client, table_data)
    # каретка до положения 2 (до барабана)
    exec_by_name('slave2_axis1_dir2', client, table_data)
    exec_by_name('slave_2_run', client, table_data)
    # проверка положения каретки
    if exec_by_name('slave2_sensor_dir2', client, table_data)[0] != 4:
        exec_by_name('slave2_axis1_dir1', client, table_data)
        exec_by_name('slave_2_run', client, table_data)
        exec_by_name('slave2_axis1_dir2', client, table_data)
        exec_by_name('slave_2_run', client, table_data)
        if exec_by_name('slave2_sensor_dir2', client, table_data)[0] != 4:
            session['log'] += f" Не удалось доехать до положения 2"
            return
    # соленоиды ключить
    exec_by_name('solenoid5_on', client, table_data)
    exec_by_name('solenoid6_on', client, table_data)


def drum_half_turn_negative(client, table_data):
    exec_by_name('drum_115_steps', client, table_data)
    exec_by_name('drum_10_349', client, table_data)
    # соленоиды 5 и 6 выключить
    exec_by_name('solenoid5_off', client, table_data)
    exec_by_name('solenoid6_off', client, table_data)
    # барабан до флага

    # каретка 2 до положения 1 (от барабана), каретка 1 до положения 2 (к барабану)
    scanning_module_2part(client, table_data)
    exec_by_name('drum_direction2', client, table_data)
    exec_by_name('drum_10_466', client, table_data)
    exec_by_name('strictly_in_positive_way', client, table_data)
    exec_by_name('drum_in_35_1', client, table_data)
    exec_by_name('drum_run', client, table_data)
    # соленоиды 3 и 4 включить
    exec_by_name('solenoid3_on', client, table_data)
    exec_by_name('solenoid4_on', client, table_data)
    # барабан полоборота в отрицательную сторону
    exec_by_name('drum_half_in_positive', client, table_data)
    exec_by_name('drum_run_half_positive', client, table_data)
    # барабан 123 шага
    # exec_by_name('drum_run_123_steps', client, table_data, emergency_stop_event)
    # exec_by_name('drum_10_349', client, table_data, emergency_stop_event)
    # соленоид 3 и 4 выключить
    exec_by_name('solenoid3_off', client, table_data)
    exec_by_name('solenoid4_off', client, table_data)


def scanning_module_2part(client, table_data):
    # каретка 2 до положения 1
    exec_by_name('slave2_axis1_dir1', client, table_data)
    exec_by_name('slave_2_run', client, table_data)
    # каретка 1 до положения 2
    exec_by_name('slave1_axis1_dir2', client, table_data)
    exec_by_name('slave1_axis1_run', client, table_data)


def getting_cassette(client, table_data):
    # каретка 1 до положения 1 (от барабана)
    exec_by_name('slave1_axis1_dir1', client, table_data)
    exec_by_name('slave1_axis1_run', client, table_data)
    # соленоид 1 и 2 включить
    exec_by_name('solenoid1_on', client, table_data)
    exec_by_name('solenoid2_on', client, table_data)
    # соленоид 1 и 2 выключить
    exec_by_name('solenoid1_off', client, table_data)
    exec_by_name('solenoid2_off', client, table_data)
    # выключить зеленый
    exec_by_name('green_off', client, table_data)


def execute_commands_run(client, table_data):
    if ((exec_by_name('slave1_sensor_dir2', client, table_data)[0] != 2)
            or (exec_by_name('slave2_sensor_dir2', client, table_data)[0] != 2)):
        raise ValueError("Axis are not in first direction, needed to prepare device")
    # модуль загрузки
    loading_module(client, table_data)
    # модуль барабана
    drum_half_turn_positive(client, table_data)
    # модуль сканирования
    scanning_module(client, table_data)
    # модуль барабана
    drum_half_turn_negative(client, table_data)
    # получение кассеты
    getting_cassette(client, table_data)


def execute_commands_prepare_dev(client, table_data):
    exec_by_name('illuminator_on', client, table_data)
    exec_by_name('slave1_axis1_dir1', client, table_data)
    exec_by_name('slave1_axis1_run', client, table_data)
    exec_by_name('slave2_axis1_dir1', client, table_data)
    exec_by_name('slave_2_run', client, table_data)
    exec_by_name('interraptions1', client, table_data)
    exec_by_name('drum_direction1', client, table_data)
    exec_by_name('drum_10_466', client, table_data)
    exec_by_name('strictly_in_positive_way', client, table_data)
    exec_by_name('drum_in_35_1_prep', client, table_data)
    exec_by_name('drum_direction2', client, table_data)
    exec_by_name('drum_10_466', client, table_data)
    exec_by_name('strictly_in_positive_way', client, table_data)
    exec_by_name('drum_in_35_1', client, table_data)
    # exec_by_name('drum_run_87_steps', client, table_data, emergency_stop_event)
    # exec_by_name('drum_10_348', client, table_data, emergency_stop_event)
    exec_by_name('interraptions2', client, table_data)
    exec_by_name('focus_axis_dir1', client, table_data)
    exec_by_name('focus_axis_run_down_point', client, table_data)
    exec_by_name('focus_axis_back', client, table_data)
    exec_by_name('focus_axis_run_full_back', client, table_data)


def execute_commands_take_cassette(client, table_data):
    exec_by_name('solenoid1_on', client, table_data)
    exec_by_name('solenoid2_on', client, table_data)
    exec_by_name('solenoid1_off', client, table_data)
    exec_by_name('solenoid2_off', client, table_data)
