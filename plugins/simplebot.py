import socket
import _thread

class Message():
	nick = ""
	login = ""
	hostname = ""
	target = ""
	text = ""
	command = ""
	target = ""

class bot():
	admins = []
	adminpw = "password"

	run = True
	
	def __init__(self,nick):
		self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.nick = nick
		
	def connect(self,host,port):
		self.irc.connect ( ( host, port ) )
		print(self.irc.recv ( 4096 ))
		self.irc.send( 'NICK '+self.nick+'\r\n' )
		self.irc.send( 'USER '+(self.nick+' ')*3+'Python IRC\r\n' )
		
	def join(self,channel):
		self.irc.send ( 'JOIN '+channel+'\r\n' )

	def send(self,target,message):
	    self.irc.send( 'PRIVMSG '+target+' :'+message+'\r\n')

	def do(self,target,action):
		self.irc.send( 'PRIVMSG '+target+' :\001ACTION '+action+'\r\n' )

	def part(self,channel):
		self.irc.send ( 'PART '+channel+'\r\n' )

	def addadmin(self,nick):
		self.admins.append(nick)

	def isadmin(self,nick):
		return nick in self.admins

	def checkpw(self,pw):
		return pw == self.adminpw

	def disconnect(self,message=""):
		self.irc.send( 'QUIT '+message+'\r\n' )

	def notice(self,target,text):
	    self.irc.send( 'NOTICE '+target+' :'+text+'\r\n' )
		
	def run(self):
		try:
			while self.run:
				lines = self.irc.recv ( 4096 ).strip().split("\r\n")
				for line in lines:
					print(line)
					_thread.start_new_thread(lambda line: self.handleline(line.strip()),(line,))
		finally:
			self.quit()
			
	def quit(self):
		self.run = False
		self.irc.close()
			
	def handleline(self,line):
		message = Message()
		if line.startswith("PING "):
			self.irc.send( 'PONG ' + " ".join(line.split()[1:]) + '\r\n' )
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


		if message.command == "PRIVMSG":
			message.text = " ".join(line.split(" ")[3:])[1:].strip()
			if message.target[0] not in "#&+!":
				message.target = message.nick
				if message.text.startswith("\001ACTION"):
					message.text = message.text[8:]
					try: pass # onPrivateAction(message)
					except: traceback.print_exc(file=sys.stdout)
				else:
					try: pass # onPrivateMessage(message)
					except: traceback.print_exc(file=sys.stdout)
			else:
				if message.text.startswith("\001ACTION"):
					message.text = message.text[8:]
					try: pass # onAction(message)
					except: traceback.print_exc(file=sys.stdout)
				else:
					try: pass # onMessage(message)
					except: traceback.print_exc(file=sys.stdout)
		elif message.command == "JOIN":
			try: pass # onJoin(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "PART":
			try: pass # onPart(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "NICK":
			try: pass # onNick(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "NOTICE":
			try: pass # onNotice(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "QUIT":
			try: pass # onQuit(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "KICK":
			try: pass # onKick(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "MODE":
			try: pass # onMode(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "TOPIC":
			try: pass # onTopic(message)
			except: traceback.print_exc(file=sys.stdout)
		elif message.command == "INVITE":
			try: pass # onInvite(message)
			except: traceback.print_exc(file=sys.stdout)
			
	
	def onMessage(self,message):
		if message.text.startswith(":d "):
			print(" ".join(message.text.split(" ")[1:]))
				
if __name__=="__main__":
	network = 'irc.compsoc.kent.ac.uk'
	port = 6667
	nick = 'simplebot'
	channels = ['#bottesting']
	admins = []

	ircbot = bot(nick)
	ircbot.connect(network,port)
	for channel in channels:
		ircbot.join(channel)


	for admin in admins:
		ircbot.addadmin(admin)

	ircbot.run()
	
	