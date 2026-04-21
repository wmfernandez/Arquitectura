import paramiko
import sys
import time

def run_ssh_command(host, user, password, commands):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password, timeout=10)

        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8', errors='ignore').strip()
            err = stderr.read().decode('utf-8', errors='ignore').strip()
            print(f"--- CMD: {cmd} ---")
            if out:
                print(out.encode('ascii', errors='replace').decode('ascii'))
            if err:
                print(f"ERR: {err.encode('ascii', errors='replace').decode('ascii')}", file=sys.stderr)
            
        client.close()
    except Exception as e:
        print(f"SSH Exception: {e}")

if __name__ == "__main__":
    commands = [
        "cd /opt/contenedores/Arquitectura/ && git pull",
        "cd /opt/contenedores/Arquitectura/ && docker compose restart frontend_portal",
        "sleep 5",
        "docker exec frontend_portal wget -qO- http://localhost:5173/api/profesiones/"
    ]
    run_ssh_command("192.168.1.208", "wmfernandez", "Winston-2010", commands)
