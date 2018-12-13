# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
import socketserver
from xml.sax import make_parser
from uaclient import ConfigHandler

CONFIG_FICH = sys.argv[1]
atts = {'server': ['name', 'ip', 'puerto'],
       'database': ['path', 'passwdpath'],
       'log': ['path']}

class UDPHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        line = self.rfile.read()
        print("El cliente nos manda " + line.decode('utf-8'))

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
