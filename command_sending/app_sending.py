from flask import request, redirect, url_for, session, jsonify
import json
import time
from command_sending.modbus_commands import calculate_crc,  format_command_as_string, send_modbus_command
from utils.request import request_command, request_table
from utils.modbus_utils import time_sleep
from utils.state import state
from collections import OrderedDict
import os

COMMAND_JSON_DIR = 'commands_json'  # Название папки с json файлами


# Get available COM ports
command_history = []
prepared_commands = {}
saved_commands = {}
form_data_comments = {}
saved_data_file = 'saved_data.json'


def prepare_command():
    global prepared_commands, saved_commands
    device_addr, command_no, register, value = request_command()

    session['form_data_com'] = {'deviceAddr': device_addr, 'commandNo': command_no, 'register': register, 'value': value}
    if device_addr and command_no and register and value:
        try:
            message = [
                int(device_addr), int(command_no),
                int(register),
                int(value)
            ]
            data = [
                int(device_addr, 16),
                int(command_no, 16),
                int(register, 16) >> 8,
                int(register, 16) & 0xFF,
                int(value, 16) >> 8,
                int(value, 16) & 0xFF
            ]
            crc = calculate_crc(data)
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
                'deviceAddr': '',
                'register': '',
                'command': formatted_command,
                'value': '',
                'commandNo': ''}

            session['form_data_comments'] = form_data_comments

        except Exception as e:
            session['log'] = f"Failed to prepare command: {str(e)}"
    else:
        session['log'] = "Missing data"
    return redirect(url_for('index'))


def send_command():
    global prepared_commands, saved_commands
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
                delay = float(delay) if delay else 0
                prepared_command = saved_commands[idx]
                device_addr = prepared_command['device_addr']
                command = prepared_command['command']
                register = prepared_command['register']
                value = prepared_command['value']
                command_info = prepared_command['command_info']
                time_start = time.time()
                print("перед отправкой", state.client)
                response = send_modbus_command(device_addr, command, register, value, state.client)
                time_end = time.time()
                time_stamp = time_end-time_start
                session['log'] += f">>\n {command_info}\n<< Response: {response}\n << Time: {time_stamp}"
                print(">> ", command_info, "\n<< Response: ", response, "\n << Time: ", time_stamp)
                time_sleep(state.client, delay)

        except Exception as e:
            session['log'] = f"Failed to send command: {str(e)}"
    else:
        session['log'] = "Invalid command selected"
    return redirect(url_for('index'))


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
            with open('commands_json/table_data.json', 'w') as f:
                json.dump(table_data, f, indent=4)  # Dump the modified list back to JSON and save it
            return redirect(url_for('index'))
        except json.JSONDecodeError:
            return "Failed to decode JSON", 400
    return "No data provided", 400


def update_data(table_data):
    if table_data:
        form_data_comments = OrderedDict()
        for idx, command_data in enumerate(table_data):
            form_data_comments[idx] = {
                    'comment1': command_data.get('comment1', ''),
                    'comment2': command_data.get('comment2', ''),
                    'delay': command_data.get('delay', 0),
                    'color': command_data.get('color', ''),
                    'deviceAddr': command_data.get('deviceAddr', ''),
                    'register': command_data.get('register', ''),
                    'commandNo': command_data.get('commandNo', ''),
                    'command': command_data.get('command', ''),
                    'value': command_data.get('value', ''),
                    'func_name': command_data.get('func_name', '')
                }
        session['form_data_comments'] = form_data_comments
    else:
        session['log'] = 'No tableData provided'
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


def power_off(client):
    file_path = os.path.join(COMMAND_JSON_DIR, 'stop.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        table_data = json.load(f)
    update_data(table_data)
    form_data_comments = session.get('form_data_comments', {})
    sorted_keys = sorted(form_data_comments.keys(), key=int)
    for idx in sorted_keys:
        command_data = form_data_comments[idx]
        try:
            delay = command_data.get('delay', 0)
            delay = float(delay) if delay else 0
        except ValueError:
            session['log'] += f"Invalid delay value for command {idx}: {command_data.get('delay')}\n"
            continue
        device_addr = command_data['deviceAddr']
        command = command_data['commandNo']
        register = command_data['register']
        value = command_data['value']
        command_info = command_data['command']
        response = send_modbus_command(device_addr, command, register, value, state.client)
        log_message = f">> {command_info}\n<< Response: {response}\n"
        session['log'] += log_message
        time.sleep(delay)

