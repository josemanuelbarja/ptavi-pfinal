# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import json
import secrets
import socket
import socketserver
from xml.sax import make_parser
from uaclient import ConfigHandler, Default, Logger

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

class JSONLoader:

    usr = {}
    passwd = {}

    def __init__(self, filejson):
        try:
            with open(database, 'r') as filejson:
                self.usr = json.load(filejson)
            with open(datapasswd, 'r') as filejson:
                self.passwd = json.load(filejson)
            #tiempo de expiracion
        except:
            pass

    def register(self):
        with open(database, 'w') as filejson:
            json.dump(self.usr, filejson, indent = 4)
        with open(datapasswd, 'w') as filejson:
            json.dump(self.passwd, filejson, indent = 4)



class UDPHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        line = self.rfile.read()
        self.message = line.decode('utf-8').split('\r\n')
        self.usr = self.message[0].split(":")[1]
        self.port = self.message[0].split(":")[2].split()[0]
        self.expires = int(self.message[1].split(":")[1].split()[0])
        self.deadtime = time.gmtime(time.time()+ 3600 + int(self.expires))
        self.deadtime = time.strftime('%d/%m/%Y %H:%M:%S', self.deadtime)
        self.address = self.client_address[0] + ':' + str(self.client_address[1])
        print(self.deadtime)
        #print(self.line.decode('utf-8'))
        self.processSIP()

    def processRegister(self):
        if self.usr in self.prjson.usr:
            if self.expires == 0:
                del self.prjson.usr[self.usr]
                self.wfile.write(bytes(cod['200'],'utf-8'))
                print("user is logging out")
            else:
                self.prjson.usr[self.usr]['expires'] = self.deadtime
                self.wfile.write(bytes(cod['200'],'utf-8'))
                print("user are already registered")
        else:
            nonce = secrets.choice(range(000000000,999999999))
            if self.message[2] == '':
                self.wfile.write(bytes(cod['401'],'utf-8'))
                self.wfile.write((bytes('WWW Authenticate: Digest nonce='
                + str(nonce),'utf-8')))
                print('unauthorized')
            else:
                user_data = {'serverport': self.port,
                            'expires': self.deadtime}
                self.prjson.usr[self.usr] = user_data
                self.wfile.write(bytes(cod['200'],'utf-8'))
                print("registered in json")
        self.prjson.register()

    def processSIP(self):
        self.prjson = JSONLoader(database)
        method = self.message[0].split(' ')[0]
        if method == 'REGISTER':
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
    log = Logger(fichlog)
    serve = socketserver.UDPServer((prip, prport),UDPHandler)
    print("Server " + prname + " listening at port " + str(prport))
    try:
        serve.serve_forever()
    except KeyboardInterrupt:
        sys.exit('Finalizando Servidor')
