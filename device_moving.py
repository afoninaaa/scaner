from flask import Flask,  request, redirect, url_for, session
import json

from command_sending.app_sending import update_data
from utils.modbus_utils import emergency_stop_event, time_sleep
# import focus
import os
from command_sending.modbus_commands import send_modbus_command

import execution
COMMAND_JSON_DIR = 'commands_json'  # Название папки с json файлами

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def run_file(client):
    session['log'] = "Starting command execution...\n"
    file_path = os.path.join(COMMAND_JSON_DIR, 'table_data.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
    except FileNotFoundError:
        return "JSON file not found.", False
    except json.JSONDecodeError:
        return "Error decoding JSON.", False
    except Exception as e:
        return str(e), False
    execution.execute_commands_run(client, table_data)
    return redirect(url_for('index'))


# def run_file():
#     slave = 1
#     axis = 1
#     steps = 0
#     point = 2
#     direct = 0
#     speed = 2000
#     slave = 2
#     focus.slave2_axis_run(client, slave,  axis, point=point, use_point_twice=use_point_twice,
#                           steps=steps, direct=direct, speed=speed)
#     slave = 1
#     axis = 1
#     steps = 0
#     point = 1
#     direct = 0
#     speed = 2000
#     slave = 2
#     focus.slave2_axis_run(client, slave,  axis, point=point, use_point_twice=use_point_twice,
#                            steps=steps, direct=direct, speed=speed)
#     return redirect(url_for('index'))


def load_and_run_from_file(client):
    session['log'] = "Starting to prepare device...\n"
    file_path = os.path.join(COMMAND_JSON_DIR, 'table_data.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
            print("file opened")
    except FileNotFoundError:
        return "JSON file not found.", False
    except json.JSONDecodeError:
        return "Error decoding JSON.", False
    except Exception as e:
        return str(e), False
    print("here")
    execution.execute_commands_prepare_dev(client, table_data)
    return redirect(url_for('index'))


def open_dev(client):
    global stop_event
    stop_event.clear()  # Сбрасываем флаг остановки
    file_path = os.path.join(COMMAND_JSON_DIR, 'open.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            table_data = json.load(f)
        update_data(table_data)
        form_data_comments = session.get('form_data_comments')
        count = request.form.get('count', '1')  # Получаем значение из формы, по умолчанию 1
        try:
            count = int(count)
        except ValueError:
            count = 1
        sorted_keys = sorted(form_data_comments.keys(), key=int)
        for i in range(count):
            if stop_event.is_set():
                session['log'] += "\nExecution stopped by user after current iteration.\n"
                break
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
                response = send_modbus_command(device_addr, command, register, value, client)
                log_message = f">> {command_info}\n<< Response: {response}\n"
                session['log'] += log_message
                time_sleep(client, delay)

                if stop_event.is_set():
                    session['log'] += "\nExecution stopped by user after current iteration.\n"
                    break
    except FileNotFoundError:
        session['log'] = "File open.json not found."
    except json.JSONDecodeError:
        session['log'] = "Error decoding JSON from open.json."
    except Exception as e:
        session['log'] = f"Failed to load or execute commands: {str(e)}"
    return redirect(url_for('index'))



