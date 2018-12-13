# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

CONFIG_FICH = sys.argv[1]
atts = {'account': ['username', 'passwd'],
        'uaserver': ['ip', 'puerto'],
        'rtpaudio': ['puerto'],
        'regproxy': ['ip', 'puerto'],
        'log': ['path'],
        'audio': ['path']}

class ConfigHandler(ContentHandler):

    def __init__(self, att):
        self.dicc = {}
        self.atts = att

    def startElement(self, name, attrs):
        if name in self.atts:
            for atts in self.atts[name]:
                self.dicc[name + ":" + atts] = attrs.get(atts, '')

    def get_tags(self):
        return self.dicc

def connect(server, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((server, port))
        my_socket.send(bytes('HOLA', 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)
        response = data.decode('utf-8').split("\r\n")
        print('Recibido --', data.decode('utf-8'))
        print("Terminando socket...")

if __name__ == '__main__':

    parser = make_parser()
    xml = ConfigHandler(atts)
    parser.setContentHandler(xml)
    parser.parse(open(CONFIG_FICH))
    values = xml.get_tags()
    usrname = values['account:username']
    usrpasswd = values['account:passwd']
    serverip = values['uaserver:ip']
    serverport = int(values['uaserver:puerto'])
    rtpport = int(values['rtpaudio:puerto'])
    proxyip = values['regproxy:ip']
    proxyport = int(values['regproxy:puerto'])
    fichlog = values['log:path']
    audio = values['audio:path']
    connect(serverip, serverport)
