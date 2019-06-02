# /usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import socketserver
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import ConfigHandler, Default, Logger, cod

atts = {'account': ['username', 'passwd'],
        'uaserver': ['ip', 'puerto'],
        'rtpaudio': ['puerto'],
        'regproxy': ['ip', 'puerto'],
        'log': ['path'],
        'audio': ['path']}

class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        self.line = self.rfile.read()
        self.address = self.client_address[0] + ':' + str(self.client_address[1])
        self.linedecod = self.line.decode('utf-8')
        self.message = self.linedecod.split('\r\n')
        headsip = self.message[0]
        contsdp = self.message[2:7]
        version = contsdp[0].split("=")[1]
        fromdst = contsdp[1].split(" ")[0].split("=")[1]
        ipdst = contsdp[1].split(" ")[1]
        sesname = contsdp[2].split("=")[1]
        sestime = contsdp[3].split("=")[1]
        rtpdst = contsdp[4]
        rtptype = rtpdst.split(" ")[0].split("=")[1]
        rtpdstport = rtpdst.split(" ")[1]
        self.wfile.write(bytes(cod['100'], 'utf-8'))
        self.wfile.write(bytes(cod['180'], 'utf-8'))
        self.wfile.write(bytes(cod['200'], 'utf-8'))

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
    serve = socketserver.UDPServer((serverip, serverport),EchoHandler)
    print(" listening at " + serverip + ":" + str(serverport))
    try:
        serve.serve_forever()
    except KeyboardInterrupt:
        sys.exit('Finalizando Servidor')
