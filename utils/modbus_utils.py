import serial
from flask import redirect, url_for, session, jsonify
from pymodbus.client import ModbusSerialClient as ModbusClient
from utils.request import request_config, request_com
from utils.state import state
import time
from command_sending.modbus_commands import send_modbus_command
from threading import Event

stop_event = Event()
emergency_stop_event = Event()


def config():
    timeout, parity, stopbit, baudrate = request_config()
    parity_map = {'None': serial.PARITY_NONE, 'Odd': serial.PARITY_ODD}
    parity = parity_map.get(parity, serial.PARITY_NONE)
    stopbit_map = {1: serial.STOPBITS_ONE, 1.5: serial.STOPBITS_ONE_POINT_FIVE, 2: serial.STOPBITS_TWO}
    stopbit = stopbit_map.get(stopbit, serial.STOPBITS_ONE)
    session['form_data'] = {'baudrate': baudrate, 'parity': parity, 'stopbit': stopbit, 'timeout': timeout}
    return redirect(url_for('index'))


def toggle_connection():
    form_data = session.get('form_data', {})
    comport_number = request_com()
    session['comport_number'] = comport_number
    if comport_number:
        try:
            if state.connected:
                state.client.close()
                state.connected = False
            else:
                state.client = ModbusClient(method='rtu', port=comport_number, baudrate=form_data['baudrate'],
                                            timeout=form_data['timeout'], parity=form_data['parity'],
                                            stopbits=form_data['stopbit'], bytesize=8)
                state.client.connect()
                state.connected = True
            session['connected'] = state.connected
        except Exception as e:
            session['log'] = f"Failed to connect: {str(e)}"
    else:
        session['log'] = "COM port not selected"
    print(f"Connected: {state.connected}")
    return redirect(url_for('index'))


def stop_execution():
    global stop_event
    stop_event.set()  # Устанавливаем флаг остановки
    session['log'] += "\nRunning will stop after this iteration.\n"
    return jsonify({'success': True})


def stop_file():
    global emergency_stop_event
    emergency_stop_event.set()  # Устанавливаем флаг экстренной остановки
    session['log'] += "\nEmergency stop command received.\n"
    return redirect(url_for('index'))


def time_sleep(client, delay):
    delay_devider = delay/10
    for i in range(1, 10):
        time.sleep(delay_devider)
        if emergency_stop_event.is_set():
            session['log'] += "\nEmergency stop activated. Execution stopped immediately.\n"
            send_modbus_command(1, 6, 10, 0, client)
            send_modbus_command(2, 6, 10, 0, client)
            return redirect(url_for('index'))
