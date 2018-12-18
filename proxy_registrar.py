# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import secrets
import socket
import socketserver
from xml.sax import make_parser
from uaclient import ConfigHandler, Default

CONFIG_FICH = sys.argv[1]
atts = {'server': ['name', 'ip', 'puerto'],
       'database': ['path', 'passwdpath'],
       'log': ['path']}

cod = {'100': 'SIP/2.0 100 Trying\r\n\r\n',
        '180': 'SIP/2.0 180 Ringing\r\n\r\n',
        '200': 'SIP/2.0 200 OK\r\n\r\n',
        '400': 'SIP/2.0 400 Bad Request\r\n\r\n',
        '401': 'SIP/2.0 401 Unauthorized\r\n\r\n',
        '404': 'SIP/2.0 404 User Not Found\r\n\r\n',
        '405': 'SIP/2.0 405 Method Not Allowed\r\n\r\n'}

class UDPHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        self.line = self.rfile.read()
        self.message = self.line.decode('utf-8').split('\r\n')
        print(self.message)
        self.processSIP()

    def processRegister(self):
        nonce = secrets.choice(range(000000000,999999999))
        if self.message[2] == '':
            print(nonce)
            self.wfile.write(bytes(cod['401'],'utf-8'))
            self.wfile.write((bytes('WWW Authenticate: Digest nonce='
            + str(nonce),'utf-8')))
            print('unauthorized')
        else:
            print("registered")

    def processSIP(self):
        self.method = self.message[0].split(' ')[0]
        if self.method == 'REGISTER':
            self.processRegister()

if __name__ == '__main__':

    parser = make_parser()
    xml = ConfigHandler(atts)
    parser.setContentHandler(xml)
    parser.parse(open(CONFIG_FICH))
    values = xml.get_tags()
    prname = values['server:name']
    prip = values['server:ip']
    prport = int(values['server:puerto'])
    database = values['database:path']
    datapasswd = values['database:passwdpath']
    fichlog = values['log:path']
    serve = socketserver.UDPServer((prip, prport),UDPHandler)
    print("Server " + prname + " listening at port " + str(prport))
    try:
        serve.serve_forever()
    except KeyboardInterrupt:
        sys.exit('Finalizando Servidor')
