from flask import request

def request_config():
    timeout = float(request.form.get('timeout'))
    parity = request.form.get('parity')
    stopbit = float(request.form.get('stopbit'))
    baudrate = int(request.form.get('baudrate'))
    return timeout, parity, stopbit, baudrate

def request_com():
    comport_number = request.form['comportSelect']
    return comport_number
    
def request_command():
    device_addr = request.form.get('deviceAddr')
    command_no = request.form.get('commandNo')
    register = request.form.get('register')
    value = request.form.get('value')
    return device_addr, command_no, register, value
    
def request_table(index):
    comment1 = request.form.get(f'comment1_{index}')
    comment2 = request.form.get(f'comment2_{index}')
    delay = request.form.get(f'delay_{index}')
    color = request.form.get(f'color_{index}')
    return comment1, comment2, delay, color

