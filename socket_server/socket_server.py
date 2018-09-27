# -*- coding: utf-8 -*-
# @Time    : 2018/9/26 17:05
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : socket_server
# @Software: PyCharm


import hashlib
import base64
import struct
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 7777))
s.listen(1)

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
                    self.payload_length += self.framer[i+1] << (8*(2-i))
                    i += 1
            elif self.payload_length == 127:
                self.payload_length = 0
                while i <= 8:
                    self.payload_length += self.framer[i+1] << (8*(8-i))
                    i += 1
            # print("length: %s " % self.payload_length)
            if self.mask == 1:
                self.masking_key = self.framer[i+1:i+5]
                # print(self.masking_key)
                i += 4
            i += 1
            self.payload_data = self.framer[i:i+self.payload_length]
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
        else:
            print("data error")
            return b""

    # no-mask
    def pack_framer(self, framer):
        l = len(framer)
        # print(l)
        f_fmt = "%ds" % l
        if l == 0:
            return struct.pack("Bb", 129, l)
        elif l <= 125:
            return struct.pack("Bb"+f_fmt, 129, l, framer.encode())
        elif l == 126:
            return struct.pack("BbH"+f_fmt, 129, 126, l, framer.encode())
        else:
            return struct.pack("BbQ"+f_fmt, 129, 127, l, framer.encode())


def generate_token(msg):
    key = msg + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    ser_key = hashlib.sha1(key).digest()
    return base64.b64encode(ser_key)


def handle_request(client):
    buf = client.recv(1024)
    d = buf.rstrip(b"\0").rsplit(b"\r\n")
    header = {}
    for line in d:
        if b":" in line:
            name, val = line.split(b":", 1)

            header[name] = val.strip(b" ")
    client.send(b"HTTP/1.1 101 WebSocket Protocol Hybi-10\r\nUpgrade: WebSocket\r\nConnection: Upgrade\r\n"
                b"Sec-WebSocket-Accept: %s\r\n\r\n" % generate_token(header[b'Sec-WebSocket-Key']))
    print(header[b'Sec-WebSocket-Key'])
    while True:
        buf = client.recv(1024*2)
        wsf = WebSocketFramer(buf)
        client.send(wsf.pack_framer(wsf.unpack_framer()))
        pass

    # client.send(b"I'm Coming")

while True:
    so, addr = s.accept()
    handle_request(so)
    # so.close()

