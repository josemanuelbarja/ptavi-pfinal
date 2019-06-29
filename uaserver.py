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
        self.address = self.client_address[0] + ':' + str(proxyport)
        self.linedecod = self.line.decode('utf-8')
        self.message = self.linedecod.split('\r\n')
        log.received(self.address,' '.join(self.message) + '\r\n')
        method = self.message[0].split(" ")[0]
        if method == 'INVITE':
            contsdp = self.message[3:8]
            version = contsdp[0].split("=")[1]
            fromdst = contsdp[1].split(" ")[0].split("=")[1]
            ipdst = contsdp[1].split(" ")[1]
            sesname = contsdp[2].split("=")[1]
            sestime = contsdp[3].split("=")[1]
            rtpdst = contsdp[4]
            rtptype = rtpdst.split(" ")[0].split("=")[1]
            rtpdstport.append(rtpdst.split(" ")[1])
            self.process_Call()
        elif method == 'ACK':
            mp32rtp = ('./mp32rtp -i ' + self.client_address[0] +
            ' -p ' + rtpdstport[0] + ' < ' + audio)
            print('running: ' + mp32rtp)
            os.system(mp32rtp)
        elif method == 'BYE':
            print('Bye Received')
            self.wfile.write(bytes(cod['200'],'utf-8'))
            log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')

    def process_Call(self):

        headersdp = ('Content-type: application/sdp\r\n\r\n' + 'v=0\r\n' + 'o='
        + usrname + " " + serverip + '\r\n' + 's=sipsesion\r\n' + 't=0\r\n' +
        'm=audio ' + str(rtpport) + ' RTP\r\n')
        self.wfile.write(bytes(cod['100'], 'utf-8'))
        self.wfile.write(bytes(cod['180'], 'utf-8'))
        self.wfile.write(bytes(cod['200'] + headersdp, 'utf-8'))
        log.send(self.address,' '.join(cod['100'].split('\r\n')) + '\r\n')
        log.send(self.address,' '.join(cod['180'].split('\r\n')) + '\r\n')
        log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')

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
    serverip = values['uaserver:ip']
    serverport = int(values['uaserver:puerto'])
    rtpport = int(values['rtpaudio:puerto'])
    rtpdstport = []
    proxyport = int(values['regproxy:puerto'])
    fichlog = values['log:path']
    audio = values['audio:path']
    serve = socketserver.UDPServer((serverip, serverport),EchoHandler)
    print("Server listening at " + serverip + ":" + str(serverport))
    log = Logger(fichlog)
    try:
        serve.serve_forever()
    except KeyboardInterrupt:
        log.finishing()
        sys.exit('Finalizando Servidor')
