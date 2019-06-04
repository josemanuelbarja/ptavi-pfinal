# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
import hashlib
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


atts = {'account': ['username', 'passwd'],
        'uaserver': ['ip', 'puerto'],
        'rtpaudio': ['puerto'],
        'regproxy': ['ip', 'puerto'],
        'log': ['path'],
        'audio': ['path']}

cod = {'100': 'SIP/2.0 100 Trying\r\n\r\n',
        '180': 'SIP/2.0 180 Ringing\r\n\r\n',
        '200': 'SIP/2.0 200 OK\r\n\r\n',
        '400': 'SIP/2.0 400 Bad Request\r\n\r\n',
        '401': 'SIP/2.0 401 Unauthorized\r\n\r\n',
        '404': 'SIP/2.0 404 User Not Found\r\n\r\n',
        '405': 'SIP/2.0 405 Method Not Allowed\r\n\r\n'}


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

class Logger:

    def __init__(self,fich):
        if not os.path.exists(fich):
            self.log = open(fich, 'w')
        self.fich = fich
        self.log = open(self.fich, 'a')
        self.log.write(time.strftime('%Y%m%d%H%M%S') + ' Starting...\r\n')
        self.log.close()

    def send(self,address,message):
        self.log = open(self.fich, 'a')
        self.log.write((time.strftime('%Y%m%d%H%M%S') + ' Sent to ' + address +
            ': ' + message))
        self.log.close()

    def received(self,address,message):
        self.log = self.log = open(self.fich, 'a')
        self.log.write((time.strftime('%Y%m%d%H%M%S') + ' Received from ' +
            address + ': ' + message))
        self.log.close()

    def error(self, message):
        self.log = self.log = open(self.fich, 'a')
        self.log.write((time.strftime('%Y%m%d%H%M%S') + ' Error: '
            + message))
        self.log.close()

    def finishing(self):
        self.log = open(self.fich, 'a')
        self.log.write(time.strftime('%Y%m%d%H%M%S') + ' Finishing.\r\n')
        self.log.close()

class SendSip:


    def __init__(self, server, port):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.sock:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.connect((server, port))
                if METHOD == 'REGISTER':
                    self.processRegister()
                elif METHOD == 'INVITE':
                    self.processInvite()
                elif METHOD == 'BYE':
                    self.processBye()
                try:
                    data = self.sock.recv(1024)
                    self.response = data.decode('utf-8').split("\r\n")
                    print(' '.join(self.response))
                    log.received(praddress, ' '.join(self.response) + '\r\n')
                    self.processResponse()
                except:
                    message = ('No server listening at ' + proxyip + ' port '
                        + str(proxyport))
                    log.error(message + '\r\n')
                    log.finishing()
                    sys.exit(message)


    def processRegister(self):
        self.sock.send((bytes(MESSAGE.format_map(Default(name= user))
            + '\r\n' + EXPIRES + '\r\n','utf-8')))
        log.send(praddress, MESSAGE.format_map(Default(name= user))+ EXPIRES +
        '\r\n')

    def processInvite(self):
        headersdp = ('Content-type: application/sdp\r\n\r\n' + 'v=0\r\n' + 'o=' +
            usrname + " " + serverip + '\r\n' + 's=sipsesion\r\n' + 't=0\r\n' +
             'm=audio ' + str(rtpport) + ' RTP\r\n')
        self.sock.send((bytes(MESSAGE.format_map(Default(name= OPTIONS))
            + '\r\n' + headersdp,'utf-8')))
        log.send(praddress, MESSAGE.format_map(Default(name= OPTIONS)))

    def processBye(self):
        self.sock.send((bytes(MESSAGE.format_map(Default(name= OPTIONS))
            + '\r\n','utf-8')))
        log.send(praddress, MESSAGE.format_map(Default(name= OPTIONS)))

    def processResponse(self):
        if '401' in self.response[0]:
            h = hashlib.md5()
            nonce = self.response[2].split("nonce=")[1]
            h.update(bytes(nonce,'utf-8'))
            h.update(bytes(usrpasswd,'utf-8'))
            authen = 'Authorization: Digest response=' + h.hexdigest() + '\r\n'
            self.sock.send((bytes(MESSAGE.format_map(Default(name= user))
                + '\r\n' + EXPIRES + '\r\n' + authen,'utf-8')))
            log.send(praddress, MESSAGE.format_map(Default(name= user)) +
            EXPIRES + ' ' + authen)
            try:
                data = self.sock.recv(1024)
                self.response = data.decode('utf-8').split("\r\n")
                print(' '.join(self.response))
                log.received(praddress, ' '.join(self.response) + '\r\n')
            except:
                message = ('No server listening at ' + proxyip + ' port '
                    + str(proxyport))
                log.error(message + '\r\n')
                log.finishing()
                sys.exit(message)
        elif ('100' in self.response[0] and '180' in self.response[2]
        and '200' in self.response[4]) and 'sdp' in self.response[6]:
            self.sock.send(bytes('ACK' + ' sip:' + OPTIONS + ' SIP/2.0 \r\n', 'utf-8'))
            log.send(praddress,'ACK' + ' sip:' + OPTIONS + ' SIP/2.0 \r\n')
            dstport = self.response[12].split(" ")[1]
            mp32rtp = './mp32rtp i- ' + serverip + ' p ' + dstport + ' < ' + audio
            os.system(mp32rtp)
            #dst_addr = serverip + ":" + dstport


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
    praddress = proxyip + ':' + str(proxyport)
    fichlog = values['log:path']
    audio = values['audio:path']
    MESSAGE = METHOD + ' sip:{name}' + ' SIP/2.0 '
    EXPIRES = 'EXPIRES: ' + OPTIONS  #  'Only used in REGISTER method'
    log = Logger(fichlog)
    connect = SendSip(proxyip, proxyport)
    log.finishing()
