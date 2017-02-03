import socket
import re

import time

'''
class SenseMeFan:
This class provides UDP access to Haiku SenseMe capable fans.
Based on work from Bruce at http://bruce.pennypacker.org/tag/senseme-plugin/
https://github.com/bpennypacker/SenseME-Indigo-Plugin
'''

class SenseMeFan:

    def __init__(self, ip='', name=''):
        self.PORT = 31415

        if not ip or not name:
            self.discover()
        else:
            self.ip = ip
            self.name = name
            self.mac = ''
            self.details = ''
            self.series = ''

        self.light = {'brightness': None, 'status': None}
        self.fan = {'speed': None, 'status': None}

        #self.getstate()

    def __sendcommand__(self, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg.encode('utf-8'), (self.ip, self.PORT))
        return

    def __query__(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, 31415))
        sock.send(msg.encode('utf-8'))

        try:
            status = sock.recv(1048).decode('utf-8')
	    print('Status: ' + status)
        except socket.timeout:
            print('Socket Timed Out')
        else:
            sock.close()
            print(str(status))
            matchObj = re.match('\(.*;([^;]+)\)', status)
            if matchObj:
                return matchObj.group(1)
            else:
                return False

    def setspeed(self, speed):
        if speed > 7: # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0: # 0 also sets fan to off automatically
            speed = 0
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):
        	self.__sendcommand__('<%s;FAN;SPD;SET;%s>' % (self.name, speed))
        	return
	else:
		print('Device Not Supported Yet')

    def incspeed(self, incspeed = 1):
        self.getfan()
        self.setspeed(int(self.fan['speed']) + incspeed)
        return


    def decspeed(self, decspeed = 1):
        self.getfan()
        self.setspeed(int(self.fan['speed']) - decspeed)
        return

    def setlight(self, light):
        if light > 16: # max light level, if receiving > 16 fan auto changes to 16
            light = 16
        elif light < 0: # light 0 also automatically sets pwr = off
            light = 0
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):
        	self.__sendcommand__('<%s;LIGHT;LEVEL;SET;%s>' % (self.name, light))
        	return
	else:
		print('Device Not Supported Yet')

    def inclight(self, incbright = 1):
        self.getlight()
        self.setlight(int(self.light['brightness']) + incbright)
        return

    def declight(self, decbright = 1):
        self.getlight()
        self.setlight(int(self.light['brightness']) - decbright)
        return

    def fanoff(self):
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):	
        	self.__sendcommand__('<%s;FAN;PWR;OFF>' % self.name)
        	return
	else:
		print('Device Not Supported Yet')

    def fanon(self):
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):
       		self.__sendcommand__('<%s;FAN;PWR;ON>' % self.name)
        	return
	else:
		print('Device Not Supported Yet')

    def fantoggle(self):
        self.getfan()
        if self.fan['status'] == 'ON':
            self.fanoff()
            return 'OFF'
        else:
            self.fanon()
            return 'ON'

    def lightoff(self):
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):
        	self.__sendcommand__('<%s;LIGHT;PWR;OFF>' % self.name)
        	return
	else:
		print('Device Not Supported Yet')

    def lighton(self):
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):
        	self.__sendcommand__('<%s;LIGHT;PWR;ON>' % self.name)
        	return
	else:
		print('Device Not Supported Yet')

    def lighttoggle(self):
        self.getlight()
        if self.light['status'] == 'ON':
            self.lightoff()
            return 'OFF'
        else:
            self.lighton()
            return 'ON'

    def getlight(self):
	# Commands for LSERIES fan only 
	if ( self.model == 'FAN' and self.series == 'LSERIES' ):
        	self.light['brightness'] = self.__query__('<%s;LIGHT;LEVEL;GET;ACTUAL>' % self.name)
        	self.light['status'] = self.__query__('<%s;LIGHT;PWR;GET>' % self.name)
        	return self.light
	else:
		print('Device Not Supported Yet')

    def getfan(self):
	# Commands for LSERIES fan only
        if ( self.model == 'FAN' and self.series == 'LSERIES' ):
        	self.fan['speed'] = self.__query__('<%s;FAN;SPD;GET;ACTUAL>' % self.name)
        	self.fan['status'] = self.__query__('<%s;FAN;PWR;GET>' % self.name)
        	return self.fan
	else:
		print('Device Not Supported Yet')

    def getstate(self):
        self.getfan()
        self.getlight()

    @property
    def fan_speed(self):
        return self.getfan()

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 31415))
        for x in range(1, 30):
            m = sock.recvfrom(1024)
            #print(m)

    def discover(self):
        data = '<ALL;DEVICE;ID;GET>'.encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        res = s.sendto(data, ('<broadcast>', self.PORT))
        print(res)
        print('sent broadcast')

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 31415))
        m = s.recvfrom(2048)
        print(m)
        if not m:
            pass
        else:
            self.details = m[0].decode('utf-8') 
            res = re.match('\((.*);DEVICE;ID;(.*);(.*),(.*)\)',self.details)
            self.name = res.group(1)
            self.mac = res.group(2)
            self.model = res.group(3)
            self.series = res.group(4)
            self.ip = m[1][0]
            # print('ip: ' + self.ip)
            # print('details: ' + self.details)
            # print(self.name)
        pass
