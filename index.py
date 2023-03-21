import asyncio
import json
import os
import socket
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import kasa

plug = {
    "ip": os.environ['PLUG_IP'],
    "name": os.environ['PLUG_NAME']
}
server = {
    "hostName": "0.0.0.0",
    "port": os.getenv('LISTEN_PORT', 8001)
}
ha_ip = os.environ['HA_IP']
ha_port = os.getenv('HA_PORT', 8123)
kuma_monitor_name = os.environ['MONITOR_NAME']


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == "/down":
            print("Triggered.")

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            json_post = json.loads(post_data.decode('utf8'))
            if json_post['monitor']['name'] == kuma_monitor_name:
                if json_post['heartbeat']['status'] == 0:
                    asyncio.run(self.do_thing())
                    return
                else:
                    print("Ignoring status update as status is not 'down'")
            else:
                print(f"Ignoring status update as monitor name {json_post['monitor']['name']} does not match expected {kuma_monitor_name}")

        self.send_response(404)
        self.end_headers()

        return

    async def do_thing(self):
        if is_up():
            self.send_response(302)
            self.end_headers()
            print("Home assistant is not down")
            return

            # Now, HA is down. Let's see about that plug
        try:
            plug = await self.server.get_plug()
        except SmartplugDoesNotMatchException as e:
            self.send_response(412)
            print(f"Smartplug name {e.actual_name} does not match expected name {e.expected_name}")
            self.end_headers()
            return

        await plug.turn_off()
        time.sleep(0.5)
        await plug.turn_on()

        # Respond with the file contents.
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()


def is_up():
    """Method that checks if home-assistant can be connected to."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((ha_ip, ha_port))
        if result == 0:
            return True
    except socket.timeout:
        return False
    return False


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    def __init__(self, server_address: tuple[str, int], request_handler_class,
                 bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, request_handler_class, bind_and_activate)
        self.plug = None

    async def get_plug(self):
        """Method to fetch a plug from the given IP.
            Note: I couldn't get autodetection working. That's something for future me to figure out
        :return: A Kasa Smartplug object
        """
        if self.plug is None:
            p = kasa.SmartPlug(plug['ip'])
            await p.update()

            print(p.alias)
            if p.alias != plug['name']:
                raise SmartplugDoesNotMatchException(plug['name'], p.alias)
            self.plug = p
        return self.plug


class SmartplugDoesNotMatchException(Exception):
    """Exception raised when smartplug does not match the given name

    Attributes:
        expected_name -- The name that was expected
        actual_name -- The name that the plug has
    """

    def __init__(self, expected_name, actual_name):
        self.expected_name = expected_name
        self.actual_name = actual_name
        super().__init__(f"Smartplug name {actual_name} does not match expected name {expected_name}")


if __name__ == "__main__":

    webServer = ThreadedHTTPServer((server['hostName'], server['port']), Handler)
    print("Server started http://%s:%s" % (server['hostName'], server['port']))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
