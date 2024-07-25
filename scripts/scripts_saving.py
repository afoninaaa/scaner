from flask import request, redirect, url_for, session, jsonify
import subprocess


def upload_py_file():
    if 'file' not in request.files:
        return jsonify(success=False, message='No file part in the request')

    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message='No selected file')

    if file and file.filename.endswith('.py'):
        filepath = f'scripts/user_code/{file.filename}'
        file.save(filepath)
        session['file_path'] = filepath
        return jsonify(success=True, message='File uploaded successfully')

    return jsonify(success=False, message='Invalid file type')


def save_code():
    data = request.get_json()
    code = data['code']
    with open('scripts/user_code/user_code.py', 'w') as f:
        f.write(code)
    return jsonify({'message': 'Code saved successfully!'})


def run_code():
    try:
        result = subprocess.run(['python', 'user_code/user_code.py'], capture_output=True, text=True, check=True)
        output = result.stdout + result.stderr
        log_message = f"Output: {output}"
        session['log'] += log_message
    except subprocess.CalledProcessError as e:
        output = e.output
        log_message = f"Output: {output}"
        session['log'] += log_message
    except Exception as e:
        output = str(e)
        log_message = f"Output: {output}"
        session['log'] += log_message
    return jsonify()
