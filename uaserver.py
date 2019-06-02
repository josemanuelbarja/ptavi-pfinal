# /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import ConfigHandler, Default, Logger

atts = {'account': ['username', 'passwd'],
        'uaserver': ['ip', 'puerto'],
        'rtpaudio': ['puerto'],
        'regproxy': ['ip', 'puerto'],
        'log': ['path'],
        'audio': ['path']}

class UDPHandler(socketserver.DatagramRequestHandler):

    def processResponse(self, line):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.connect((proxyip, int(proxyport)))
            my_socket.send(bytes(line, 'utf-8'))

    def handle(self):
        self.line = self.rfile.read()
        self.linedecod = self.line.decode('utf-8')
        self.address = self.client_address[0] + ':' + str(self.client_address[1])
        self.message = self.linedecod.split('\r\n')
        headsip = self.message[0]
        contspd = self.message[1]
        print(headsip)
        print(contspd)


if __name__ == '__main__':
    try:
        CONFIG_FICH = sys.argv[1]
    except IndexError:
        sys.exit("Usage: python uaserver.py config")
    parser = make_parser()
    xml = ConfigHandler(atts)
    parser.setContentHandler(xml)
    parser.parse(open(CONFIG_FICH))
    values = xml.get_tags()
    usrname = values['account:username']
    usrpasswd = values['account:passwd']
    serverip = values['uaserver:ip']
    serverport = int(values['uaserver:puerto'])
    user = usrname + ":" + str(serverport)
    rtpport = int(values['rtpaudio:puerto'])
    proxyip = values['regproxy:ip']
    proxyport = int(values['regproxy:puerto'])
    praddress = proxyip + ':' + str(proxyport)
    fichlog = values['log:path']
    audio = values['audio:path']
    serve = socketserver.UDPServer((serverip, serverport),UDPHandler)
    print(" listening at " + serverip + ":" + str(serverport))
    try:
        serve.serve_forever()
    except KeyboardInterrupt:
        sys.exit('Finalizando Servidor')