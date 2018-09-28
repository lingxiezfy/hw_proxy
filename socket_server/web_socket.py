# -*- coding: utf-8 -*-
# @Time    : 2018/9/28 11:42
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : web_socket
# @Software: PyCharm

import struct
import hashlib
import base64

from zope.interface import Attribute, Interface, implementer, provider
from twisted.internet import interfaces, protocol, address
from twisted.internet import error
from twisted.python import failure


@implementer(interfaces.ITransport)
class WebSocketProtocol(protocol.Protocol):
    is_handshake = False
    handshake_header = {}

    def connectionMade(self):
        print('WebSocket connect: %s.' % (self.getPeer(),))

    def dataReceived(self, data):
        if self.is_handshake:
            wsf = WebSocketFramer(data)
            result = wsf.unpack_framer()
            if result:
                if result == 8:
                    print("do Closing: %s." % (self.getPeer(),))
                    self.loseConnection()
                else:
                    print("received from %s : %s." % (self.getPeer(), result))
                    # do some thing ,hear do echo
                    self.sendResult(wsf.pack_framer(result))
        else:
            self._handshake(data)

    def connectionLost(self, reason):
        print("close WebSocket : %s." % (self.getPeer(),))
        self.is_handshake = None
        self.handshake_header = {}

    def sendResult(self, result):
        self.write(result)

    def write(self, data):
        self.transport.write(data)

    def writeSequence(self, iovec):
        self.transport.writeSequence(iovec)

    def getPeer(self):
        return self.transport.getPeer()

    def getHost(self):
        return self.transport.getHost()

    def loseConnection(self):
        return self.transport.loseConnection()

    def _generate_token(self, msg):
        key = msg + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key).digest()
        return base64.b64encode(ser_key)

    def _handshake(self, header):
        print("handshake with WebSocket: %s." % (self.getPeer(),))
        if header:
            h = header.rstrip(b"\0").rsplit(b"\r\n")
            if b"GET" in h[0]:
                for line in h:
                    if b":" in line:
                        name, val = line.split(b":", 1)
                        self.handshake_header[name] = val.strip(b" ")
                self.write(b"HTTP/1.1 101 WebSocket Protocol Hybi-10\r\nUpgrade: WebSocket\r\n"
                           b"Connection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n"
                           % self._generate_token(self.handshake_header[b'Sec-WebSocket-Key']))
                self.is_handshake = True
            else:
                self.connectionLost(failure.Failure(error.VerifyError))
        else:
            self.connectionLost(failure.Failure(error.VerifyError))


class WebSocketFramer(object):
    FIN = 1
    opcode = 1
    mask = 0
    payload_length = 0
    masking_key = ""
    payload_data = ""

    def __init__(self, framer):
        self.framer = framer

    def unpack_framer(self):
        if len(self.framer) == 0:
            print("null framer")
            return b""
        # print("unpack: %s " % self.framer)
        self.FIN = int(self.framer[0] >> 7)
        # print("FIN: %d " % self.FIN)
        self.opcode = int(self.framer[0] & 0x0F)
        # print("opcode: %d " % self.opcode)
        if self.opcode == 1 or self.opcode == 2:
            self.mask = int(self.framer[1] >> 7)
            # print("mask: %d " % self.mask)
            self.payload_length = int(self.framer[1] & 0x7F)
            i = 1
            if self.payload_length == 126:
                self.payload_length = 0
                while i <= 2:
                    self.payload_length += self.framer[i + 1] << (8 * (2 - i))
                    i += 1
            elif self.payload_length == 127:
                self.payload_length = 0
                while i <= 8:
                    self.payload_length += self.framer[i + 1] << (8 * (8 - i))
                    i += 1
            # print("length: %s " % self.payload_length)
            if self.mask == 1:
                self.masking_key = self.framer[i + 1:i + 5]
                # print(self.masking_key)
                i += 4
            i += 1
            self.payload_data = self.framer[i:i + self.payload_length]
            if self.mask == 1:
                j = 0
                temp_data = bytearray()
                # print(len(self.payload_data))
                while j < self.payload_length:
                    temp_data.append(self.payload_data[j] ^ self.masking_key[j % 4])
                    j += 1
                self.payload_data = temp_data
            i += self.payload_length
            # print(self.payload_data)
            self.payload_data = self.payload_data.decode()
            # print("data: %s " % self.payload_data)
            return self.payload_data
        elif self.opcode == 8:
            print("to close the webSocket")
            return 8
        else:
            print("data error")
            return None

    # no-mask
    def pack_framer(self, framer):
        l = len(framer)
        # print(l)
        f_fmt = "%ds" % l
        if l == 0:
            return struct.pack("Bb", 129, l)
        elif l <= 125:
            return struct.pack("Bb" + f_fmt, 129, l, framer.encode())
        elif l == 126:
            return struct.pack("BbH" + f_fmt, 129, 126, l, framer.encode())
        else:
            return struct.pack("BbQ" + f_fmt, 129, 127, l, framer.encode())
