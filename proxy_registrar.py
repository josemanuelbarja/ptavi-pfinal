# /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import json
import secrets
import hashlib
import socket
import socketserver
from xml.sax import make_parser
from uaclient import ConfigHandler, Default, Logger, cod

atts = {'server': ['name', 'ip', 'puerto'],
       'database': ['path', 'passwdpath'],
       'log': ['path']}

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

    sesions = {}
    nonce = {}

    def expiresTime(self):
        try:
            user_del = []
            now = time.gmtime(time.time() + 3600)
            for usr in self.prjson.usr:
                if now >= time.strptime(self.prjson.usr[usr]['expires'],
                '%d/%m/%Y %H:%M:%S'):
                    user_del.append(usr)
            for usr in user_del:
                del self.prjson.usr[usr]
        except:
            pass

    def client2server(self, message, dst):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            port = self.prjson.usr[dst]['serverport']
            print(prip)
            print(port)
            self.serv_addr = prip + ':' + port
            my_socket.connect((prip, int(port)))
            my_socket.send(bytes(message, 'utf-8'))
            try:
                self.reply = my_socket.recv(1024).decode('utf-8')
                log.received(self.serv_addr, ' '.join(message.split('\r\n')) + '\r\n')
            except:
                # -- enviar error a cliente.
                # -- el servidor no se encuentra en ese .xml
                sys.exit('Connection refused')

    def handle(self):
        self.line = self.rfile.read()
        self.linedecod = self.line.decode('utf-8')
        self.message = self.linedecod.split('\r\n')
        self.prjson = JSONLoader(database)
        self.address = self.client_address[0] + ':'
        self.expiresTime()
        self.processSIP()

    def processRegister(self):
        user = self.message[0].split(":")[1]
        self.port = self.message[0].split(":")[2].split()[0]
        self.address += self.port
        self.expires = int(self.message[1].split(":")[1].split()[0])
        self.deadtime = time.gmtime(time.time()+ 3600 + int(self.expires))
        self.strdeadtime = time.strftime('%d/%m/%Y %H:%M:%S', self.deadtime)
        log.received(self.address,' '.join(self.message) + '\r\n')
        print(self.linedecod)
        print(user)
        if user in self.prjson.usr:
            if self.expires == 0:
                del self.prjson.usr[user]
                self.wfile.write(bytes(cod['200'],'utf-8'))
                log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')
                print("user is logging out")
            else:
                self.prjson.usr[user]['expires'] = self.strdeadtime
                self.wfile.write(bytes(cod['200'],'utf-8'))
                log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')
                print("user is already registered")
        else:
            if user in self.prjson.passwd:
                usrpasswd = self.prjson.passwd[user]['passwd']
                if self.message[2] == '':
                    nonce = secrets.choice(range(000000000,999999999))
                    self.nonce[user] = nonce
                    message = 'WWW Authenticate: Digest nonce='+ str(nonce)
                    self.wfile.write(bytes(cod['401'],'utf-8'))
                    self.wfile.write(bytes(message,'utf-8'))
                    log.send(self.address,' '.join(cod['401'].split('\r\n')) + message + '\r\n')
                    print('unauthorized')
                else:
                    print('nonce',self.nonce[user])
                    dig_resp = self.message[2].split("=")[1]
                    h = hashlib.md5()
                    h.update(bytes(str(self.nonce[user]),'utf-8'))
                    h.update(bytes(usrpasswd,'utf-8'))
                    dig_compa = h.hexdigest()
                    if dig_resp == dig_compa:
                        user_data = {'serverport': self.port,
                                    'expires': self.strdeadtime}
                        self.prjson.usr[user] = user_data
                        self.wfile.write(bytes(cod['200'],'utf-8'))
                        log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')
                        print("registered in json")
                    else:
                        print('Authenticate failed')
            else:
                self.wfile.write(bytes(cod['404'], 'utf-8'))
                log.send(self.address,' '.join(cod['404'].split('\r\n')) + '\r\n')
                print('user ' + user + ' not found')
        self.prjson.register()

    def processInvite(self):
        sdp = self.message[3:8]
        print(self.linedecod)
        log.received(self.address,' '.join(self.message) + '\r\n')
        orig = sdp[1].split()[0].split('=')[1]
        if orig in self.prjson.usr:
            dst = self.message[0].split(":")[1].split(" ")[0]
            if dst in self.prjson.usr:
                sesion = sdp[2].split('=')[1]
                self.sesions[sesion] = [orig, dst]
                self.client2server(self.linedecod, dst)
                print(self.linedecod)
                #log.send(self.serv_addr,self.linedecod)
                self.wfile.write(bytes(self.reply,'utf-8'))
                print(orig + ' starting sesion: ' + sesion)
                print(self.reply)

            else:
                self.wfile.write(bytes(cod['404'],'utf-8'))
                print('user ' + dst + ' not found')
        else:
            self.wfile.write(bytes(cod['404'], 'utf-8'))
            print('user ' + orig + ' not found')

    def processSIP(self):
        method = self.message[0].split(' ')[0]
        if method == 'REGISTER':
            self.processRegister()
        elif method == 'INVITE':
            self.processInvite()
        elif method == 'ACK':
            user = self.message[0].split(":")[1].split(" ")[0]
            print(self.message)
            self.client2server(self.linedecod,user)
        elif method == 'BYE':
            user = self.message[0].split(":")[1].split(" ")[0]
            self.client2server(self.linedecod,user)
            self.wfile.write(bytes(self.reply, 'utf-8'))
        else:
            self.wfile.write(bytes(cod['405'], 'utf-8'))


if __name__ == '__main__':
    try:
        CONFIG_FICH = sys.argv[1]
    except IndexError:
        sys.exit("Usage: python proxy_registrar.py config")
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
        log.finishing()
        sys.exit('Finalizando Servidor')
