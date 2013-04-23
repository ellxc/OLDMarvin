

import defaultplugin

import traceback

class plugin(defaultplugin.plugin):
	commands = {"%eval":("","returns an eval() of the message")
				}
	
	def onMessage(self,bot,message):
		if message.text.lower().startswith("%eval") and bot.isadmin(message.nick):
			try:
				bot.send(message.target,str(eval(" ".join(message.text.split(" ")[1:]))))
			except Exception as e:
				bot.send(message.target,"error: %s" % e)
				traceback.print_exc()
		if message.text.lower().startswith("%exec") and bot.isadmin(message.nick):
			try:
				exec(" ".join(message.text.split(" ")[1:]))
			except Exception as e:
				bot.send(message.target,"error: %s" % e)
				traceback.print_exc()
				
	def onPrivateMessage(self,bot,message):
		self.onMessage(bot,message)