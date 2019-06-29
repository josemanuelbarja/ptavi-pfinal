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

    def delUserTime(self):
        try:
            delete = []
            now = time.gmtime(time.time() + 3600)
            for usr in self.prjson.usr:
                if now >= time.strptime(self.prjson.usr[usr]['expires'],
                '%d/%m/%Y %H:%M:%S'):
                    delete.append(usr)
            for usr in delete:
                del self.prjson.usr[usr]
        except:
            pass

    def client2server(self, message, dst):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            try:
                port_dst= self.prjson.usr[dst]['serverport']
            except:
                self.wfile.write(bytes(cod['404'] + cab_proxy,'utf-8'))
                log.send(self.address,' '.join(cod['404'].split('\r\n')) + '\r\n')
                log.finishing()
                sys.exit('User ' + dst + ' not found')
            self.serv_addr = prip + ':' + port_dst
            my_socket.connect((prip, int(port_dst)))
            my_socket.send(bytes(message, 'utf-8'))
            try:
                self.reply = my_socket.recv(1024).decode('utf-8')
                log.send(self.serv_addr, ' '.join(message.split('\r\n')) + '\r\n')
            except:
                error = ('Connection refused: No server listening at ' +
                self.serv_addr)
                log.error(error + '\r\n')
                log.finishing()
                sys.exit(error)

    def handle(self):
        line = self.rfile.read()
        self.linedecod = line.decode('utf-8')
        self.message = self.linedecod.split('\r\n')
        self.prjson = JSONLoader(database)
        self.address = self.client_address[0] + ':'
        self.delUserTime()
        self.processSIP()

    def processRegister(self):
        user = self.message[0].split(":")[1]
        port = self.message[0].split(":")[2].split()[0]
        self.address += port
        expires = int(self.message[1].split(":")[1].split()[0])
        deadtime = time.gmtime(time.time()+ 3600 + int(expires))
        strdeadtime = time.strftime('%d/%m/%Y %H:%M:%S', deadtime)
        log.received(self.address,' '.join(self.message) + '\r\n')
        if user in self.prjson.usr:
            if expires == 0:
                del self.prjson.usr[user]
                self.wfile.write(bytes(cod['200'] + cab_proxy,'utf-8'))
                log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')
            else:
                self.prjson.usr[user]['expires'] = strdeadtime
                self.wfile.write(bytes(cod['200'] + cab_proxy,'utf-8'))
                log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')
        else:
            if expires == 0:
                self.wfile.write(bytes(cod['404'] + cab_proxy,'utf-8'))
                log.send(self.address,' '.join(cod['404'].split('\r\n')) + '\r\n')
                log.error('Not registered yet')
                print('Not registered yet')
            else:
                if user in self.prjson.passwd:
                    usrpasswd = self.prjson.passwd[user]['passwd']
                    if self.message[2] == '':
                        number = secrets.choice(range(000000000,999999999))
                        nonce[user] = number
                        message = 'WWW Authenticate: Digest nonce='+ str(number)
                        self.wfile.write(bytes(cod['401'],'utf-8'))
                        self.wfile.write(bytes(message + '\r\n' + cab_proxy,'utf-8'))
                        log.send(self.address,' '.join(cod['401'].split('\r\n')) + message + '\r\n')
                        print('Authorization Needed')
                    else:
                        dig_resp = self.message[2].split("=")[1]
                        h = hashlib.md5()
                        h.update(bytes(str(nonce[user]),'utf-8'))
                        h.update(bytes(usrpasswd,'utf-8'))
                        dig_compa = h.hexdigest()
                        if dig_resp == dig_compa:
                            user_data = {'serverport': port,
                                        'expires': strdeadtime}
                            self.prjson.usr[user] = user_data
                            self.wfile.write(bytes(cod['200'] + cab_proxy,'utf-8'))
                            log.send(self.address,' '.join(cod['200'].split('\r\n')) + '\r\n')
                            print("Registered completed")
                        else:
                            log.error('Authenticate failed')
                            print('Authenticate failed')
                else:
                    self.wfile.write(bytes(cod['404'] + cab_proxy, 'utf-8'))
                    log.send(self.address,' '.join(cod['404'].split('\r\n')) + '\r\n')
        self.prjson.register()

    def processInvite(self):
        sdp = self.message[3:8]
        orig = sdp[1].split()[0].split('=')[1]
        log.received(self.address,' '.join(self.message) + '\r\n')
        if orig in self.prjson.usr:
            port_orig = self.prjson.usr[orig]['serverport']
            self.address += port_orig
            dst = self.message[0].split(":")[1].split(" ")[0]
            if dst in self.prjson.usr:
                if dst != orig:
                    self.client2server(self.linedecod, dst)
                    received = self.reply.split('\r\n')
                    log.received(self.serv_addr,' '.join(received) + '\r\n')
                    self.wfile.write(bytes(self.reply + cab_proxy,'utf-8'))
                    log.send(self.address,' '.join(received) + '\r\n')
                else:
                    self.wfile.write(bytes(cod['400'] + cab_proxy,'utf-8'))
                    print('Same address')
                    log.error('Same address\r\n')
                    log.send(self.address,' '.join(cod['400'].split('\r\n')) + '\r\n')
            else:
                self.wfile.write(bytes(cod['404'] + cab_proxy,'utf-8'))
                print('user ' + dst + ' not found')
                log.send(self.address,' '.join(cod['404'].split('\r\n')) + '\r\n')
        else:
            self.wfile.write(bytes(cod['404'] + cab_proxy, 'utf-8'))
            print('user ' + orig + ' not found')
            log.send(self.address,' '.join(cod['404'].split('\r\n')) + '\r\n')

    def processBye(self):
        user = self.message[0].split(":")[1].split(" ")[0]
        log.received(self.address,self.linedecod)
        self.client2server(self.linedecod,user)
        self.wfile.write(bytes(self.reply + cab_proxy, 'utf-8'))


    def processSIP(self):
        method = self.message[0].split(' ')[0]
        if method == 'REGISTER':
            self.processRegister()
        elif method == 'INVITE':
            self.processInvite()
        elif method == 'ACK':
            user = self.message[0].split(":")[1].split(" ")[0]
            log.received(self.address,self.message[0] + '\r\n')
            self.client2server(self.linedecod,user)
        elif method == 'BYE':
            self.processBye()
        else:
            self.wfile.write(bytes(cod['405'] + cab_proxy, 'utf-8'))
            log.send(self.address,' '.join(cod['405'].split('\r\n')) + '\r\n')


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
    nonce = {}
    cab_proxy = ('Via: SIP/2.0/UDP ' + prip + ':'
                 + str(prport) + ';' + prname + '\r\n')
    log = Logger(fichlog)
    serve = socketserver.UDPServer((prip, prport),UDPHandler)
    print("Proxy listening at port " + str(prport))
    try:
        serve.serve_forever()
    except KeyboardInterrupt:
        log.finishing()
        sys.exit('Finalizando Servidor')
