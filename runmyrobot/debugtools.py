import subprocess
import threading

class RemoteDebug(object):
    def __init__(self, api_client):
        self._api = api_client

        self._api.on('reverse_ssh_8872381747239', self.handle_start_reverse_ssh)
        self._api.on('end_reverse_ssh_8872381747239', self.handle_stop_reverse_ssh)

    
    def handle_start_reverse_ssh(self):
        self._api.emit("reverse_ssh_info", "starting")
        threading.Thread(target=self._start_reverse_ssh, args=(self.key_file, self.ssh_host,)).start()
        self._api.emit("reverse_ssh_info", "return code: " + str(returnCode))


    def handle_stop_reverse_ssh(self):
        threading.Thread(target=self._stop_reverse_ssh).start()

    def _start_reverse_ssh(self, ssh_key_file, ssh_host):
        return subprocess.call(["/usr/bin/ssh",
                                  "-X",
                                  "-i", ssh_key_file,
                                  "-N",
                                  "-R", "2222:localhost:22",
                                  ssh_host])

    def _stop_reverse_ssh(self):
        return subprocess.call(["killall", "ssh"])
