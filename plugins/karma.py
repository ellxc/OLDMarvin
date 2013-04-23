

import defaultplugin
import re
import pickle
import os

class plugin(defaultplugin.plugin):
				
	karma = {}
				
	pattern = re.compile(".*?(?:\[([^\[\]]+)\]|(\S+))(\+\+|--)")
	pattern2 = re.compile("%k(?:arma)?(?: (?:\[([^\[\]]+)\]|(\S+)))?")
	
	def onMessage(self,bot,message):
		if self.pattern2.match(message.text):
			if self.pattern2.match(message.text).group(1) or self.pattern2.match(message.text).group(2):
				x = self.pattern2.match(message.text).group(1) or self.pattern2.match(message.text).group(2)
				if x.lower() in list(self.karma.keys()):
					bot.send(message.target,message.nick+": %s has %s karma." % (x,str(self.karma[x.lower()])))
				else:
					bot.send(message.target,message.nick+": %s has no karma." % (x)) 
			else:
				if message.nick.lower() in list(self.karma.keys()):
					bot.send(message.target,message.nick+": you have %s karma." % (str(self.karma[message.nick.lower()])))
				else:
					bot.send(message.target,message.nick+": you have no karma.") 
		elif self.pattern.match(message.text):
			x = self.pattern.match(message.text.lower()).group(1) or self.pattern.match(message.text.lower()).group(2)
			print(x)
			mod = self.pattern.match(message.text.lower()).group(3)
			if mod == "++":
				mod = 1
			else:
				mod = -1
			
			if x in list(self.karma.keys()) and x != message.nick.lower():
				self.karma[x] += mod
			elif x != message.nick.lower():
				self.karma[x] = mod
			elif x.lower() == message.nick.lower():
				self.karma[x] = 0
		
				
	def onLoad(self,bot):
		if os.path.exists(os.path.join(bot.dir, "karma.save")):
			self.karma = pickle.load( open( os.path.join(bot.dir, "karma.save"), "rb" ) )

	def onUnload(self,bot):
		pickle.dump( self.karma, open( os.path.join(bot.dir, "karma.save"), "wb" ) )