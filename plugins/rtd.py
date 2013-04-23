import defaultplugin
import random
import re

class plugin(defaultplugin.plugin):
	pattern = re.compile("%roll(?: (?:(\d*)#)?(\d*)d(\d*)(?:\+(\d*)|\-(\d*))?)?")
	
	
	commands = {"%roll":("","<number of rolls>#<number of dice>d<sides on dice>+/-<modifier>")}

	def onMessage(self,bot,message):
		if self.pattern.match(message.text):
			answers = []
			vars = self.getvars(self.pattern.match(message.text).groups())
			total = ""
			for i in range(0,vars[0]):
				answers.append(str(self.roll(vars[1],vars[2],vars[3])))
			
			if len(answers) > 1:
				total = " with a total of: " + str(sum([int(x) for x in answers]))
			bot.send(message.target,message.nick + ": " + ", ".join(answers) + total)
				
			
	def roll(self,number,max,offset):
		return (random.randint(1,max) * number) + offset
		
	def getvars(self,vars):
		individualrolls = vars[0]
		if individualrolls in (None,""):
			individualrolls = 1
		
		dicerolls = vars[1]
		if dicerolls in (None,""):
			dicerolls = 1
		
		dicemax = vars[2]
		if dicemax in (None,""):
			dicemax = 6
			
		posoffset = vars[3]
		if posoffset in (None,""):
			posoffset = 0
			
		negoffset = vars[4]
		if negoffset in (None,""):
			negoffset = 0
		
		return int(individualrolls),int(dicerolls),int(dicemax),int(posoffset)-int(negoffset)
		

