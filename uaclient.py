# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

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

class Default(dict):
     def __missing__(self, key):
         return key

class SendSip:

    def __init__(self, server, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.my_socket:
            self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.my_socket.connect((server, port))
            if METHOD == 'REGISTER':
                self.processRegister()
            elif METHOD == 'INVITE':
                self.processInvite()
            elif METHOD == 'BYE':
                self.processBye()
            data = self.my_socket.recv(1024)
            response = data.decode('utf-8').split("\r\n")
            print('Recibido --', data.decode('utf-8'))
            print("Terminando socket...")

    def processRegister(self):
        self.my_socket.send((bytes(MESSAGE.format_map(Default(name= user))
            + EXPIRES,'utf-8') + b'\r\n'))

    def processInvite(self):
        self.my_socket.send((bytes(MESSAGE.format_map(Default(name= OPTIONS))
            ,'utf-8')))
        self.my_socket.send(b'Content-type: application/sdp\r\n')
        self.my_socket.send(bytes('v=0\r\n' + 'o=' + usrname + " " + serverip
            + '\r\n' + 's=sipsesion\r\n' + 't=0\r\n' + 'm=audio ' + str(rtpport)
            + ' RTP\r\n','utf-8'))

    def processBye(self):
        self.my_socket.send((bytes(MESSAGE.format_map(Default(name= OPTIONS))
            ,'utf-8')))

if __name__ == '__main__':
    try:
        CONFIG_FICH = sys.argv[1]
        METHOD = str.upper(sys.argv[2])
        OPTIONS = sys.argv[3]
    except IndexError:
        sys.exit("Usage: python uaclient.py config method option")
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
    fichlog = values['log:path']
    audio = values['audio:path']
    MESSAGE = METHOD + ' sip: {name}' + ' SIP/2.0\r\n'
    EXPIRES = 'EXPIRES: ' + OPTIONS #  'Only used with REGISTER method'
    connect = SendSip(serverip, proxyport)
