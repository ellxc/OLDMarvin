import defaultplugin
import random

class plugin(defaultplugin.plugin):
	commands = {"%8ball":("<question>","using voodoo it will answer your question")}
	
	answers = ['Yes.',
	'no',
	'Outlook is not so good.',
	'All signs point to yes.',
	'All signs point to no.',
	'The answer is unclear.']
	
	def onMessage(self,bot,message):
		if message.text.lower().startswith("%8ball"):
			bot.send(message.target,message.nick +": " + self.answers[random.randint(0,len(self.answers)-1)])