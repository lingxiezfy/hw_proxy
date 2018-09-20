# -*- coding: utf-8 -*-
# @Time    : 2018/9/11 16:54
# @Author  : FrankZ
# @Email   : FrankZ981210@gmail.com
# @File    : reactor_client
# @Software: PyCharm
# from zope.interface import implementer
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientFactory,FileWrapper
from twisted.internet.interfaces import IFileDescriptor
from twisted.internet.interfaces import IReadDescriptor
from twisted.internet import main
from evdev import InputDevice
import util
import evdev


class ProxyProtocol(LineReceiver):
    def connectionMade(self):
        self.sendLine("I'm connecting!".encode())

    def send_some_thing(self):
        self.sendLine("I send number!".encode())


# @implementer(IFileDescriptor, IReadDescriptor)
class HidFile:
    dev = None
    fd = None
    key_recode = ""
    function_key = False

    def __init__(self, dev):
        # self.dev = InputDevice(dev)
        self.fd = open(dev, "r")
        from twisted.internet import reactor
        reactor.addReader(self)
        print(self.fileno())
        # print(self.dev.path)

    def doRead(self):
        try:
            result = self.fd.read()
            if isinstance(result, evdev.InputEvent):
                if result.type == evdev.ecodes.EV_KEY and result.value == 0x01:
                    print(str(evdev.ecodes.KEY[result.code])[4:])
                    # 分析键值（功能键，回车键，或普通键）
                    if result.code == 42 or result.code == 54:
                        self.function_key = True
                    elif result.code == 28:
                        print(self.key_recode)
                        # 向代理服务发送数据包
                        # packet = struct.pack("3s60s20s", "kbd".encode("utf-8"),
                        #                      self.path[19:].encode("utf-8"),
                        #                      key_str.encode("utf-8"))
                        # packet += "\r\n".encode("utf-8")
                        # s.send(packet)
                        # 置空键值缓存
                        self.key_recode = ""
                    else:
                        # 记录键值
                        self.key_recode += util.get_hid_print_key(self.function_key, result.code)
                        # 重置功能键
                        if self.function_key:
                            self.function_key = False
            else:
                print("no data")
                return main.error
        except Exception as e:
            print(e.__repr__())
            return main.error


    def fileno(self):
        if self.fd is None:
            return -1
        return self.fd

    def connectionLost(self,reason):
        # self.dev.close()
        print("已关闭： %s" % self.fd)


    def logPrefix(self):
        return 'hid_drives'



class SendClientFactory(ClientFactory):
    protocol = ProxyProtocol


def send_loop(factory):
    print("send")
    factory.proto.send_some_thing("I send number!")


def proxy_main():
    # 准备读取对象
    drives = []
    kbd_input_list = []

    # 初始化usb类键盘设备
    usb_temps = util.get_kbd_input_list()
    for u_t in usb_temps:
        if u_t not in kbd_input_list:
            print("新加入设备：%s" % u_t)
            drives.append(HidFile(util.get_kbd_input_dir() + "" + u_t))
            kbd_input_list.append(u_t)
    print(drives)
    # factory = SendClientFactory()
    from twisted.internet import reactor
    # reactor.connectTCP('192.168.1.139', 3390, factory)

    reactor.run()


if __name__ == "__main__":
    proxy_main()
