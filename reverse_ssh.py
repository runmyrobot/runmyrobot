from __future__  import print_function
import os
import json
import subprocess
try:
    import websocket
    import psutil
except:
    os.system("pip install wheel websocket-client psutil")
    import websocket
    import psutil
try:
    import thread
except ImportError:
    import _thread as thread
import time
FNULL = open(os.devnull, 'w')

def on_message(ws, message):
    #print(message)
    try:
        data = json.loads(message)
    except:
        return
    print(data)
    if "e" in data:
        if data["e"] == "start_rssh":
            v = data["d"]
            start_rssh(v["ip"], v["port"], v["rport"], v["username"], v["password"])
        elif data["e"] == "stop_rssh":
            stop_rssh()
        elif data["e"] == "reboot":
            os.system("sudo reboot")

ssh_process = False
ssh_string = 'n/a'

def stop_rssh():
    global ssh_string
    subprocess.call(["killall", "ssh", "sshpass"])
    ssh_string = 'n/a'

def start_rssh(ssh_ip, ssh_port, rssh_port, username, password):
    global ssh_process
    global ssh_string
    stop_rssh()
    try:
        subprocess.call(["sshpass"], stdout=FNULL)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            os.system("sudo apt-get update")
            os.system("sudo apt install sshpass")
    cmd = ['sshpass', '-p', password, 'ssh', '-t', '-t', '-R', str(rssh_port) + ':localhost:' + str(ssh_port), '-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=5', username+'@'+ssh_ip, '-p', str(ssh_port)]
    ssh_process = subprocess.Popen(cmd, stdout=FNULL)
    ssh_string = ssh_ip + ':' + str(ssh_port) + '('+str(rssh_port)+')'
    #print(cmd)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### websocket closed ###")

def on_open(ws):
    print("### websocket opened ###")
    def run(*args):
        ws.send(json.dumps({"e": "identify", "d": robot_id}))
    thread.start_new_thread(run, ())

robot_id = 'Not Found'

def locate_robot_id():
    global robot_id
    found = False
    for process in psutil.process_iter():
        cmdline = process.cmdline()
        if "controller.py" in cmdline:
            if len(cmdline) > 2:
                found = True
                if robot_id != cmdline[2]:
                    robot_id = cmdline[2]
                    try:
                        ws.send(json.dumps({"e": "identify", "d": robot_id}))
                    except:
                        pass
    if robot_id != 'Not Found' and found == False: 
        robot_id = 'Not Found'
        try:
            ws.send(json.dumps({"e": "identify", "d": robot_id}))
        except:
            pass

def locate_loop(*args):
    while True:
        try:
            time.sleep(30)
            locate_robot_id() # attempt to locate controller.py and scrape robot id
        except Exception as e:
            print(e)

def status_loop(*args):
    global ssh_process
    global ssh_string
    while True:
        try:
            time.sleep(5)
            ok = False
            if ssh_process != False:
                if ssh_process.poll() == None: # None if process is still running
                    ok = True
                else:
                    ssh_process = False
                    ssh_string = 'n/a'
            ws.send(json.dumps({"e": "status", "d": {"ok": ok, "ssh_string": ssh_string, "cpu": psutil.cpu_percent()}}))
        except Exception as e:
            print(e)

if __name__ == "__main__":
    try:
        locate_robot_id()
    except Exception as e:
        print(e)
    thread.start_new_thread(locate_loop, ())
    thread.start_new_thread(status_loop, ())

    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://rssh.letsrobot.tv:1500/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    while True:
        try:
            ws.run_forever()
            time.sleep(5)
        except KeyboardInterrupt:
            exit()
        except:
            pass