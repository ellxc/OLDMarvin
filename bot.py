

import socket
import os
import sys
import types
import imp
import re
import traceback
import _thread
import time
from collections import deque




class Message():
	nick = ""
	login = ""
	hostname = ""
	target = ""
	text = ""
	command = ""
	target = ""

class bot():
	plugins = {}
	admins = []
	adminpw = "newpassword"
	nicks = {}
	
	commands = {}

	run = True
	
	spams = {}
	
	spamtime = 10
	spamlimit = 5
	spamwait = 20

	def __init__(self,nick):
		self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.nick = nick
		self.dir = os.path.dirname(os.path.abspath(__file__))

	def join(self,channel):
		self.irc.send ( ('JOIN '+channel+'\r\n').encode() )

	def send(self,target,message):
		for line in message.split('\n'):
			if line:
				self.irc.send( ('PRIVMSG '+target+' :'+line+'\r\n').encode())

	def do(self,target,action):
		self.irc.send( ('PRIVMSG '+target+' :\001ACTION '+action+'\001\r\n').encode() )

	def part(self,channel):
		self.irc.send ( ('PART '+channel+'\r\n').encode() )

	def addadmin(self,nick):
		self.admins.append(nick)

	def isadmin(self,nick):
		return nick in self.admins

	def checkpw(self,pw):
		return pw == self.adminpw

	def disconnect(self,message=""):
		self.irc.send( ('QUIT '+message+'\r\n').encode() )

	def notice(self,target,text):
	    self.irc.send( ('NOTICE '+target+' :'+text+'\r\n').encode() )

	def spamsend(self,to,message):
		t = time.time()
		
		if to not in list(self.spams.keys()):
			self.spams[to] = [deque([],self.spamlimit),t]
		elif self.spams[to][0].maxlen != self.spamlimit:
			self.spams[to][0] = deque([],self.spamlimit)
			
		if len(self.spams[to][0]) == self.spamlimit:
			if t - self.spams[to][0][0] < self.spamtime and t >= self.spams[to][1]:
				self.do(to,"stops spamming for %s seconds." % (self.spamwait))
				self.spams[to] = [deque([],self.spamlimit),t+self.spamwait]
			elif t >= self.spams[to][1]:
				self.send(to,message)
				self.spams[to][0].append(t)
		elif t >= self.spams[to][1]:
			self.send(to,message)
			self.spams[to][0].append(t)

	def spamsdo(self,to,message):
		t = time.time()
		
		if to not in list(self.spams.keys()):
			self.spams[to] = [deque([],self.spamlimit),t]
		elif self.spams[to][0].maxlen != self.spamlimit:
			self.spams[to][0] = deque([],self.spamlimit)
				
		if len(self.spams[to][0]) == self.spamlimit:
			if t - self.spams[to][0][0] < self.spamtime and t >= self.spams[to][1]:
				self.do(to,"stops spamming for %s seconds." % (self.spamwait))
				self.spams[to] = [deque([],self.spamlimit),t+self.spamwait]
			elif t >= self.spams[to][1]:
				self.do(to,message)
				self.spams[to][0].append(t)
		elif t >= self.spams[to][1]:
			self.do(to,message)
			self.spams[to][0].append(t)
			
		
			
	def run(self):
		try:
			while self.run:
				lines = self.irc.recv ( 4096 ).decode().strip().split("\r\n")
				for line in lines:
					try:
						print(line)
						_thread.start_new_thread(lambda line: self.handleline(line.strip()),(line,))
					except:
						pass
		finally:
			self.quit()

	def handleline(self,line):
		message = Message()
		if line.startswith("PING "):
			self.irc.send( ('PONG ' + " ".join(line.split()[1:]) + '\r\n').encode() )
			return

		senderinfo = line.split(" ")[0]
		message.command = line.split(" ")[1]

		exclamation = senderinfo.find("!")
		at = senderinfo.find("@")
		if senderinfo.startswith(":"):
			if exclamation > 0 and at > 0 and exclamation < at:
				message.nick = senderinfo[1:exclamation]
				message.login = senderinfo[exclamation+ 1:at]
				message.hostname = senderinfo[at+1:]

		message.target = line.split(" ")[2]
		
		if message.target.startswith(":"):
			message.target = message.target[1:]

		if message.command == "PRIVMSG":
			message.text = " ".join(line.split(" ")[3:])[1:].strip()
			if message.target[0] not in "#&+!":
				message.target = message.nick
				if message.text.startswith("\001ACTION"):
					message.text = message.text[8:]
					for plugin in list(self.plugins.values()):
						try: plugin.onPrivateAction(self,message)
						except: traceback.print_exc(file=sys.stdout)
				else:
					for plugin in list(self.plugins.values()):
						try: plugin.onPrivateMessage(self,message)
						except: traceback.print_exc(file=sys.stdout)
			else:
				if message.text.startswith("\001ACTION"):
					message.text = message.text[8:]
					for plugin in list(self.plugins.values()):
						try: plugin.onAction(self,message)
						except: traceback.print_exc(file=sys.stdout)
				else:
					for plugin in list(self.plugins.values()):
						try: plugin.onMessage(self,message)
						except: traceback.print_exc(file=sys.stdout)
		elif message.command == "JOIN":
			#self.nicks.setdefault(message.target,[]).append(message.nick)
			for plugin in list(self.plugins.values()):
				try: plugin.onJoin(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "PART":
			del self.nicks[message.target][self.nicks[message.target].index(message.nick)]
			for plugin in list(self.plugins.values()):
				try: plugin.onPart(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "NICK":
			for plugin in list(self.plugins.values()):
				try: plugin.onNick(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "NOTICE":
			for plugin in list(self.plugins.values()):
				try: plugin.onNotice(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "QUIT":
			del self.nicks[message.target][self.nicks[message.target].index(message.nick)]
			for plugin in list(self.plugins.values()):
				try: plugin.onQuit(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "KICK":
			del self.nicks[message.target][self.nicks[message.target].index(message.nick)]
			for plugin in list(self.plugins.values()):
				try: plugin.onKick(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "MODE":
			for plugin in list(self.plugins.values()):
				try: plugin.onMode(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "TOPIC":
			for plugin in list(self.plugins.values()):
				try: plugin.onTopic(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "INVITE":
			for plugin in list(self.plugins.values()):
				try: plugin.onInvite(self,message)
				except: traceback.print_exc(file=sys.stdout)
		elif message.command == "353":
			if line.split(" ")[4] in self.nicks:
				self.nicks[line.split(" ")[4]] += [x if x[0] not in "@+" else x[1:] for x in line.split(":")[2].split(" ")]
			else:
				self.nicks[line.split(" ")[4]] = []
				for name in line.split(":")[2].split(" "):
					self.nicks[line.split(" ")[4]].append(name if name[0] not in "@+" else name[1:])
			
			for channel in self.nicks.keys():
				if self.nick in self.nicks[channel]:
					del self.nicks[channel][self.nicks[channel].index(self.nick)]
		else:
			pass


	def setplugindir(self,dir):
		self.pluginsdir = dir

	def quit(self,message=""):

		for plugin in list(self.plugins.values()):
			plugin.onUnload(self)
		self.run = False
		self.irc.close()


	def connect(self,host,port):
		self.irc.connect ( ( host, port ) )
		print(self.irc.recv ( 4096 ).decode())
		self.irc.send( ('NICK '+self.nick+'\r\n').encode() )
		self.irc.send( ('USER '+(self.nick+' ')*3+'Python IRC\r\n').encode() )



	def loadall(self):
		for name in os.listdir(self.pluginsdir):
			if name.endswith(".py") and not name.startswith("__") and name[:-3] not in list(self.plugins.keys()):
				path = os.path.join(self.pluginsdir, name)
				module = imp.load_source(name[:-3],path)
				self.plugins[name[:-3]] = getattr(module, "plugin")()
				for command in list(self.plugins[name[:-3]].commands.items()):
					self.commands[command[0]] = command[1]
				self.plugins[name[:-3]].onload(self)

	def reloadallplugins(self):
		for plugin in list(self.plugins.keys()):
			self.plugins[plugin].onUnload(self)

			for command in list(self.plugins[plugin].commands.keys()):
				if command in self.commands:
					del self.commands[command]

			del self.plugins[plugin]
			path = os.path.join(self.pluginsdir, plugin+".py")
			module = imp.load_source(plugin,path)
			self.plugins[plugin] = getattr(module, "plugin")()
			self.plugins[plugin].onLoad(self)
			for command in list(self.plugins[plugin].commands.items()):
				self.commands[command[0]] = command[1]

	def reloadplugin(self,plugin):
		if plugin in list(self.plugins.keys()):
			self.plugins[plugin].onUnload(self)

			for command in list(self.plugins[plugin].commands.keys()):
				if command in self.commands:
					del self.commands[command]

			del self.plugins[plugin]
			path = os.path.join(self.pluginsdir, plugin+".py")
			module = imp.load_source(plugin,path)
			self.plugins[plugin] = getattr(module, "plugin")()
			self.plugins[plugin].onLoad(self)

			for command in list(self.plugins[plugin].commands.items()):
				self.commands[command[0]] = command[1]

		else:
			raise Exception('not loaded')

	def unloadplugin(self,plugin):
		if plugin in list(self.plugins.keys()):
			self.plugins[plugin].onUnload(self)
			for command in list(self.plugins[plugin].commands.keys()):
				if command in self.commands:
					del self.commands[command]

			del self.plugins[plugin]

		else:
			raise Exception('not loaded')


	def loadplugin(self,plugin):
		if plugin not in list(self.plugins.keys()):
		
					
				
			path = os.path.join(self.pluginsdir, plugin+".py")
			module = imp.load_source(plugin,path)
			
			for command in list(getattr(module, "plugin")().commands.items()):
				if command[0] not in list(self.commands.keys()):
					self.commands[command[0]] = command[1]
				else:
					raise Exception('command overlap')
					
			self.plugins[plugin] = getattr(module, "plugin")()

			self.plugins[plugin].onLoad(self)
		else:
			raise Exception('already loaded')

	def listplugins(self):
		list = []
		for plugin in list(self.plugins.keys()):
				list.append(plugin+"*")
		for name in os.listdir(self.pluginsdir):
			if name.endswith(".py") and not name.startswith("__") and name[:-3] not in list(self.plugins.keys()):
				list.append(name[:-3])
		return list

	def directloadplugin(self,plugin,name):
		if name not in list(self.plugins.keys()):
			for command in list(plugin.commands.items()):
				if command[0] not in list(self.commands.keys()):
					self.commands[command[0]] = command[1]
				else:
					raise Exception('command overlap')
			self.plugins[name] = plugin
		else:
			print(list(self.plugins.keys()))
			raise Exception('already loaded')
			



if __name__=="__main__":
	plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
	network = 'irc.compsoc.kent.ac.uk'
	port = 6667
	nick = 'Marvin4'
	channels = ['#bottesting','#pokertest']
	plugins = ["defaultplugin","basiccommands","countdown","translate","8ball","rtd","karma","eval","markov","remind"]
	admins = ["Penguin"]

	marvin = bot(nick)
	marvin.connect(network,port)
	for channel in channels:
		marvin.join(channel)

	marvin.setplugindir(plugins_dir)
	for plugin in plugins:
		marvin.loadplugin(plugin)

	for admin in admins:
		marvin.addadmin(admin)

	marvin.run()