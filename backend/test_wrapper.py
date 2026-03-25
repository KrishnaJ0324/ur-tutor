import subprocess

try:
    out = subprocess.check_output([r".\venv\Scripts\python.exe", "test_agent.py"], stderr=subprocess.STDOUT)
    print(out.decode('utf-8'))
except subprocess.CalledProcessError as e:
    print(e.output.decode('utf-8'))
