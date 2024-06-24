from flask import Flask,  request, redirect, url_for, session, jsonify
import json
import serial.tools.list_ports
import time
from pymodbus.client import ModbusSerialClient as ModbusClient
from Modbus_comands import calculate_crc, send_modbus_command, format_command_as_string
from request import request_config, request_com, request_command, request_table
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get available COM ports
comports = [port.device for port in serial.tools.list_ports.comports()]
connected = False
command_history = []
prepared_commands = {}
saved_commands = {}
form_data_comments = {}
client = None
saved_data_file = 'saved_data.json'

def config():
    timeout, parity, stopbit, baudrate = request_config()

    parity_map = {'None': serial.PARITY_NONE, 'Odd': serial.PARITY_ODD}
    parity = parity_map.get(parity, serial.PARITY_NONE)
    stopbit_map = {1: serial.STOPBITS_ONE, 1.5: serial.STOPBITS_ONE_POINT_FIVE, 2: serial.STOPBITS_TWO}
    stopbit = stopbit_map.get(stopbit, serial.STOPBITS_ONE)
    session['form_data'] = {'baudrate': baudrate, 'parity': parity, 'stopbit': stopbit, 'timeout': timeout}
    return redirect(url_for('index'))

def toggle_connection():
    global connected, client
    form_data = session.get('form_data', {})
    comport_number = request.form.get('comportSelect')
    session['comport_number'] = comport_number
    if comport_number:
        try:
            if connected:
                client.close()
                connected = False
            else:
                client = ModbusClient(method='rtu', port=comport_number, baudrate=form_data['baudrate'],
                                      timeout=form_data['timeout'], parity=form_data['parity'],
                                      stopbits=form_data['stopbit'], bytesize=8)
                client.connect()
                connected = True
            session['connected'] = connected
        except Exception as e:
            session['log'] = f"Failed to connect: {str(e)}"
    else:
        session['log'] = "COM port not selected"
    print(f"Connected: {connected}")
    return redirect(url_for('index'))

def prepare_command():
    global prepared_commands, saved_commands
    device_addr, command_no, register, value = request_command()
    session['form_data_com'] = {'deviceAddr': device_addr, 'commandNo': command_no, 'register': register, 'value': value}
    if device_addr and command_no and register and value:
        try:
            message = [
                int(device_addr), int(command_no),
                int(register),
                int(value),
            ]
            crc = calculate_crc(message)
            message.extend([crc & 0xFF, crc >> 8])
            formatted_command = format_command_as_string(message)
            command_index = len(prepared_commands)
            prepared_commands[command_index] = formatted_command
            command_index = len(saved_commands)
            saved_commands[command_index] = {
                'command_info': formatted_command,
                'device_addr': device_addr,
                'command': command_no,
                'register': register,
                'value': value
            }

            if session.get('form_data_comments') is None:
                idx = 0
            else:
                idx = len(session.get('form_data_comments'))
            form_data_comments[idx] = {
                "comment1": '',
                "comment2": '',
                "delay": '',
                'deviceAddr':'',
                'register': '',
                'command': formatted_command,
                'value': '' ,
                'commandNo': ''}

            session['form_data_comments'] = form_data_comments

        except Exception as e:
            session['log'] = f"Failed to prepare command: {str(e)}"
    else:
        session['log'] = "Missing data"
    return redirect(url_for('index'))

def send_command():
    global client, prepared_commands, saved_commands
    for index in range(0, len(saved_commands)):
        saved_command_idx = saved_commands[index]
        prepared_command = saved_command_idx.get('command_info')
        value = saved_command_idx.get('value')
        deviceaddr = saved_command_idx.get('device_addr')
        register = saved_command_idx.get('register')
        commandno = saved_command_idx.get('command')
        comment1, comment2, delay, color = request_table(index)
        form_data_comments[index] = {
                "comment1": comment1, "comment2": comment2,
                "delay": delay, 'command': prepared_command,
                "value": value, "deviceAddr": deviceaddr,
                "register": register, "commandNo": commandno,
                "color": color
        }
    session['form_data_comments'] = form_data_comments

    command_index = request.form.get('command_row')
    if command_index is not None:
        try:
            for idx in saved_commands:
                delay = request.form.get(f'delay_{idx}')
                prepared_command = saved_commands[idx]
                device_addr = prepared_command['device_addr']
                command = prepared_command['command']
                register = prepared_command['register']
                value = prepared_command['value']
                command_info = prepared_command['command_info']
                response = send_modbus_command(device_addr, command, register, value, client)
                session['log'] += f">>\n {command_info}\n<< Response: {response}\n"
                time.sleep(int(delay))

        except Exception as e:
            session['log'] = f"Failed to send command: {str(e)}"
    else:
        session['log'] = "Invalid command selected"
    return redirect(url_for('index'))

@app.route('/delete_row', methods=['POST'])
def delete_row():
    try:
        data = request.json
        idx = data.get('idx')

        # Удаление строки по индексу из form_data_comments
        if idx in session['form_data_comments']:
            del session['form_data_comments'][idx]

        # Обновление сессии (опционально, в зависимости от вашей логики)
        session.modified = True

        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Failed to delete row: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

def save_table_data():
    table_data_json = request.form.get('tableData')
    if table_data_json:
        try:
            table_data = json.loads(table_data_json)  # Parse JSON into a Python list
            with open('table_data.json', 'w') as f:
                json.dump(table_data, f, indent=4)  # Dump the modified list back to JSON and save it
            return redirect(url_for('index'))
        except json.JSONDecodeError:
            return "Failed to decode JSON", 400
    return "No data provided", 400

def run_file():
    global client
    form_data_comments = session.get('form_data_comments', {})
    if not form_data_comments:
        session['log'] = "No commands to run."
        return redirect(url_for('index'))
    try:
        for idx, command_data in form_data_comments.items():
            try:
                delay = int(command_data.get('delay', 0))
            except ValueError:
                session['log'] += f"Invalid delay value for command {idx}: {command_data.get('delay')}\n"
                continue

            device_addr = command_data['deviceAddr']
            command = command_data['commandNo']
            register = command_data['register']
            value = command_data['value']
            command_info = command_data['command']

            response = send_modbus_command(device_addr, command, register, value, client)
            session['log'] += f">>\n {command_info}\n<< Response: {response}\n"

            time.sleep(delay)
    except Exception as e:
        session['log'] = f"Failed to send command: {str(e)}"

    return redirect(url_for('index'))

def clear_history():
    global prepared_commands, saved_commands
    prepared_commands.clear()
    form_data_comments.clear()
    saved_commands.clear()

    if 'form_data_comments' in session:
        session.pop('form_data_comments')
    if 'selected_command_idx' in session:
        session.pop('selected_command_idx')
    session['log'] = f""
    return redirect(url_for('index'))

def load_table_data():
    try:
        table_data = request.json.get('tableData')
        if table_data:
            session['form_data_comments'] = {}
            for idx, command_data in enumerate(table_data):
                session['form_data_comments'][str(idx)] = {
                    'comment1': command_data['comment1'],
                    'comment2': command_data['comment2'],
                    'delay': command_data['delay'],
                    'color': command_data['color'],
                    'deviceAddr': command_data['deviceAddr'],
                    'register': command_data['register'],
                    'commandNo': command_data['commandNo'],
                    'command': command_data['command'],
                    'value': command_data['value']
                }
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No tableData provided'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})