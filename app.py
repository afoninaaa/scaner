from flask import Flask, render_template, session
import json
import os
import serial.tools.list_ports
from funcs import (config, toggle_connection, prepare_command, send_command, save_table_data,
                   run_file, clear_history, delete_row, stop_file, load_and_run_from_file, upload_py_file,
                   stop_execution, open_dev, run_code, save_code)
from collections import OrderedDict
from threading import Event
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get available COM ports
comports = [port.device for port in serial.tools.list_ports.comports()]
stop_event = Event()
emergency_stop_event = Event()
connected = False
command_history = []
prepared_commands = {}
saved_commands = {}
form_data_comments = {}
client = None

saved_data_file = 'commands_json/table_data.json'
if not os.path.exists(saved_data_file):
    with open(saved_data_file, 'w') as f:
        json.dump({"form_data_comments": {}}, f)


@app.route('/')
def index():
    form_data = session.get('form_data', {})
    form_data_com = session.get('form_data_com', {})
    form_data_comments = session.get('form_data_comments',OrderedDict())
    sorted_comments = OrderedDict(sorted(form_data_comments.items(), key=lambda x: int(x[0])))
    selected_command_idx = session.get('selected_command_idx')
    connected = session.get('connected')
    return render_template('index.html', comports=comports, client=client, connected=connected,
                           log=session.get('log', ''), form_data=form_data, saved_commands=saved_commands,
                           prepared_commands=prepared_commands, form_data_com=form_data_com,
                           command_history=command_history, comport_number=session.get('comport_number'),
                           selected_command_idx=selected_command_idx, form_data_comments=sorted_comments)


@app.route('/config', methods=['POST'])
def handle_config():
    return config()


@app.route('/toggle_connection', methods=['POST'])
def handle_toggle_connection():
    return toggle_connection()


@app.route('/prepare_command', methods=['POST'])
def handle_prepare_command():
    return prepare_command()


@app.route('/send_command', methods=['POST','GET'])
def handle_send_command():
    return send_command()


@app.route('/delete_row', methods=['POST'])
def handle_delete_row():
    return delete_row()


@app.route('/save_table_data', methods=['POST'])
def handle_save_table_data():
    return save_table_data()


@app.route('/run_file', methods=['POST'])
def handle_run_file():
    return run_file()


@app.route('/stop_file', methods=['POST'])
def handle_stop_file():
    return stop_file()


@app.route('/clear_history', methods=['POST'])
def handle_clear_history():
    return clear_history()


@app.route('/upload_py_file', methods=['POST'])
def handle_upload_py_file():
    return upload_py_file()


@app.route('/load_and_run_from_file', methods=['POST'])
def load_and_run_from_file_route():
    return load_and_run_from_file()


@app.route('/stop_execution', methods=['POST'])
def handle_stop_execution():
    return stop_execution()


@app.route('/open', methods=['POST'])
def handle_open():
    return open_dev()


@app.route('/save_code', methods=['POST'])
def handle_save_code():
    return save_code()


@app.route('/run_code', methods=['POST'])
def handle_run_code():
    return run_code()
# @app.route('/upload_py_file', methods=['POST'])
# def handle_upload_py_file():
#     return handle_upload_py_file()

if __name__ == '__main__':
    app.run(debug=True)
