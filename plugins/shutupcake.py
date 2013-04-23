
from . import defaultplugin
import re

class plugin(defaultplugin.plugin):
	response = "fuck off cake."
	pattern = re.compile("(?:.+): did you mean \'you\'\?")

	def onMessage(self,bot,message):
	    if self.pattern.match(message.text) and message.nick == "cake":
			bot.send(message.target,self.response)