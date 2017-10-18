import threading
import time
import subprocess
import signal

import runmyrobot.debugtools

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from socketIO_client import SocketIO, EngineIO, LoggingNamespace

class Client(object):
    """RunMyRobot main client"""
    def __init__(self, robot, chat_enabled=True, debug=True):
        self.robot = robot
        self.chat_enabled = chat_enabled
        self.exiting = False

        host = "https://letsrobot.tv"

        self._control = ControlClient(robot.id)
        self._chat = ChatClient(robot.id)
        self._api = ApiClient(robot.id)

        if debug:
            remote_debug = runmyrobot.debugtools.RemoteDebug(self._api)

    def connect(self):
        self._control.connect()
        self._chat.connect()
        self._api.connect()

    def identify_robot(self):
        print("identifying robot %s" % self.robot.id)
        self._api.emit('identify_robot_id', self.robot.id)
        if self.chat_enabled:
            print("chat enabled")
            self._chat.emit('identify_robot_id', self.robot.id)

    def update_ip_info(self):
        hostname_i = subprocess.check_output(["hostname", "-I"])
        self._api.emit('ip_information',
            {'ip': hostname_i, 'robot_id': self.robot.id})

    def send_charge_info(self, charge_data):
        charge_data = {
            'robot_id': self.robot.id,
            'charging': charge_data
        }
        self._api.emit('charge_state', charge_data)

    def _handle_command(self, args):
        self.robot.handle_command(args)

    def _handle_exclusive_control(self, args):
        self.robot.exclusive_control(args)

    def _handle_chat_message(self, args):
        if self.chat_enabled:
            self.robot.handle_chat_message(args)

    def _handle_interrupt(self, signal, frame):
        self.exiting=True
        print("Exiting...")
        exit(0)

    def _loop_func(self, f, *args):
        while not self.exiting:
            f(seconds=1)

    def run(self):
        self._control.on('command_to_robot', self._handle_command)
        self._api.on('exclusive_control', self._handle_exclusive_control)
        self._chat.on('chat_message_with_name', self._handle_chat_message)

        self.identify_robot()

        threads = [
            threading.Thread(target=self._loop_func, args=(self._control.wait,)),
            threading.Thread(target=self._loop_func, args=(self._api.wait,)),
            threading.Thread(target=self._loop_func, args=(self._chat.wait,)),
        ]

        signal.signal(signal.SIGINT, self._handle_interrupt)

        for t in threads:
            t.start()


class HttpClient(object):
    """Generic LetsRobot HTTP Client"""
    def __init__(self, host = "https://letsrobot.tv"):
        self.host = host

    def construct_url(self, path):
        return '%s/%s' % (self.host, path)    

    def get(self, method, args):
        url = self.construct_url("%s/%s" % (method, args))
        print(url)

        s = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504))

        adapter = HTTPAdapter(max_retries=retry)
        s.mount('http://', adapter)
        s.mount('https://', adapter)

        return s.get(url)


class WebSocketClient(SocketIO):
    """Generic WebSocket client"""
    def discover_endpoint(self, role, robot_id):
        http = HttpClient()
        resp = http.get("get_%s_host_port" % role, robot_id)
        data = resp.json()
        print("discovered endpoint for %s at %s:%s" % (role, data['host'], data['port']))
        return data


class ControlClient(WebSocketClient):
    """Control channel Client"""
    def __init__(self, robot):
        endpoint = self.discover_endpoint("control", robot)
        print(endpoint)
        super(self.__class__, self).__init__(endpoint["host"], endpoint["port"], LoggingNamespace)


class ChatClient(WebSocketClient):
    """Chat channel Client"""
    def __init__(self, robot):
        endpoint = self.discover_endpoint("chat", robot)
        print(endpoint)
        super(self.__class__, self).__init__(endpoint["host"], endpoint["port"], LoggingNamespace)


class ApiClient(WebSocketClient):
    """Api channel Client"""
    def __init__(self, robot):
        host = "letsrobot.tv"
        port = 8022
        super(self.__class__, self).__init__(host, port, LoggingNamespace)
