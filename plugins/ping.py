
from . import defaultplugin

class plugin(defaultplugin.plugin):
	def onMessage(self,bot,message):
	    if message.text.lower() == "%ping":
			bot.send(message.target,"pong")