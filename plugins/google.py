

import defaultplugin
import urllib.request, urllib.parse, urllib.error

class plugin(defaultplugin.plugin):
	commands = {"%g":(" <query>","returns a google link"),
				"%l":(" <query>","returns a LMGTFY link")
				}
				
	lmgtfy = "http://lmgtfy.com/?"
	google = "https://www.google.com/search?"
	
	def onMessage(self,bot,message):
		if message.text.lower().startswith("%l "):
			temp = {"q" : " ".join(message.text.split(" ")[1:])}
			url = self.lmgtfy + urllib.parse.urlencode(temp)
			bot.send(message.target,url)
		elif message.text.lower().startswith("%g "):
			temp = {"q" : " ".join(message.text.split(" ")[1:])}
			url = self.google + urllib.parse.urlencode(temp)
			bot.send(message.target,url)

