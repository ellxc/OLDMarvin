
import defaultplugin
import re	
import random
import time
import traceback
import sys

class plugin(defaultplugin.plugin):

	pattern = re.compile(r"\%cd +[0-9]+(?:\.[0-9]*)? ?:( [0-9]+(?:\.[0-9]*)?){1,5}")
	gamepattern = re.compile(r"\%cdnewgame(?: (hard|easy|medium))?")
	answerpattern = re.compile(r"\%cdanswer [\(\)\*\+-\/0-9]+")
	calcpattern = re.compile(r"\%calc [\(\)\*\+-\/0-9%\.]+")
	viewpattern = re.compile(r"\%cdviewgame")
	giveuppattern = re.compile(r"\%cdgiveup")
	evalpattern = re.compile(r"\%eval( .+)+")
	
	difficulties ={'hard':3,'medium':2,'easy':1,None:2}
	
	current_running = 0
	
	enabled = True
	
	games = {}
	
	largenumbers = [25,50,75,100]
	largenumbershard = [12,37,62,87]
	smallnumbers = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10]
	
	
	commands = {"%cdnewgame" : (" <difficulty>","starts a medium difficulty game or a game with the specified dificulty"),
				"%cdanswer":(" <expression>","sumbit an answer for the current countdown game"),
				"%calc":(" <expression>","work out the expression given"),
				"%cdviewgame":("","show the current games information"),
				"%cd":(" <target>:<number> <number> ...","solve"),
				"%cdgiveup":("","end the current game and solve"),
				}
	
	def onMessage(self,bot,message):
		if self.pattern.match(message.text.lower()):
			if self.current_running < 2:
				self.current_running += 1
				try:
					target = message.text.split(":")[0].split(" ")[1]
					numbers = list(filter(bool, message.text.split(":")[1].split(" ")))
					if len(numbers) < 7:
						bot.spamsend(message.target,"looking for %s, with the numbers %s" % (target,numbers))
						bot.spamsend(message.target,self.workout(float(target),numbers,False))
					else:
						bot.spamsend(message.target,"too many numbers specified")
				except:
					bot.spamsend(message.target,"ERROR")
					traceback.print_exc(file=sys.stdout)
				self.current_running -= 1
			else:
				bot.spamsend(message.target,"maximum number of solvers are running, please try again when they have completed")
			
		elif self.gamepattern.match(message.text.lower()):
			if message.target in self.games:
				bot.spamsend(message.target,"game in progress. use %cdviewgame to see it or %cdgiveup to remove it before starting another")
			else:
				bot.spamsend(message.target,self.startgame(message.target,self.difficulties[self.gamepattern.match(message.text.lower()).group(1)])+" Please open this for added authenticity https://www.youtube.com/watch?v=M2dhD9zR6hk")

				
		elif self.answerpattern.match(message.text.lower()):
			if message.target in self.games:
				bot.spamsend(message.target,self.evaluateanswer(message.target," ".join(message.text.split(" ")[1:])))
			else:
				bot.spamsend(message.target,"no current game")
				
		elif self.calcpattern.match(message.text.lower()):
			bot.spamsend(message.target,str(eval(re.sub(r'(\d+(\.\d+)?)',r'float(\1)'," ".join(message.text.split(" ")[1:])))))
			
		elif self.viewpattern.match(message.text.lower()):
			if message.target in self.games:
				bot.spamsend(message.target,"target is %s, and the numbers are %s" % (self.games[message.target]["target"],self.games[message.target]["numbers"]))
			else:
				bot.spamsend(message.target,"no current game")
				
		elif self.giveuppattern.match(message.text.lower()):
			if message.target in self.games:
				bot.spamsend(message.target,"attempting to solve...")
				bot.spamsend(message.target,self.workout(float(self.games[message.target]["target"]),self.games[message.target]["numbers"],False))
				del self.games[message.target]
			else:
				bot.spamsend(message.target,"no current game")
			
			
	def evaluateanswer(self,channel,answer):
		numbersused = list(map(float, re.findall("[0-9]+",answer)))
		numbersvalid = set(numbersused).issubset(set(self.games[channel]["numbers"]))
		equals = eval(re.sub(r'(\d+)',r'float(\1)',answer))
		if equals == self.games[channel]["target"] and numbersvalid:
			del self.games[channel]
			return "correct! game over"
		elif numbersvalid:
			return "incorrect, your answer equals %s" % (equals)
		else:
			return "you did not use the correct numbers, please try again"

	def newgame(self,target,numbers):
		game = {"target":target,"numbers":numbers}
		return game
			
	def startgame(self,channel,difficulty=2,big=2,small=4):
		tempsmallnumbers = list(self.smallnumbers)
		
		if difficulty == 3:
			templargenumbers = list(self.largenumbershard)
			gametarget = random.randint(100,999)
		elif difficulty == 2:
			templargenumbers = list(self.largenumbers)
			gametarget = random.randint(100,999)
		elif difficulty == 1:
			templargenumbers = list(self.largenumbers)
			gametarget = random.choice([random.randint(4,39)*25,random.randint(10,99)*10])
		random.shuffle(templargenumbers)
		random.shuffle(tempsmallnumbers)
		gamenumbers = templargenumbers[:big] + tempsmallnumbers[:small]
		self.games[channel] = self.newgame(gametarget,gamenumbers)
		
		
		return "target is %s, and the numbers are %s" % (gametarget,gamenumbers)
		



	def workout(self,target,numbers,findBestAnswer):
		answers = []
		Numbers = []
		bestAnswer = "(" + str(numbers[0]) + ") = " + str(numbers[0])
		bestAnswervalue = float(numbers[0])
		found = False
		
		for number in numbers:
			Numbers.append(Number(float(number)))
		

		i = 0			
		while i in range(len(Numbers)) and (not found or findBestAnswer):
			if (Numbers[i].getValue() == target):
				answers.append("(" + Numbers[i].toString() + ") = " + str(target))
				found = True
			elif abs(target - Numbers[i].getValue()) < abs(target - bestAnswervalue) and not found:
				bestAnswer = "(" + Numbers[i].toString() + ") = " + Numbers[i].toString()
			i += 1

		i = 0			
		while i in range(len(Numbers)) and (not found or findBestAnswer):
			if Numbers[i].getUsed() == False:
				Numbers[i].setUsed(True);
				tempanswers,bestAnswervalue,bestAnswer,found = self.doMaths(Numbers[i].getValue(), target, Numbers, Numbers[i].toString(), findBestAnswer,False,Numbers[i].getValue(),bestAnswer)
				answers = list(set(answers) | set(tempanswers))
				Numbers[i].setUsed(False);
			i += 1
			
			
		if answers:
			return min(answers, key=len)
		else:
			return "best answer: " + bestAnswer

	def doMaths(self,lhv,target,Numbers,opSoFar,findBestAnswer,found,bestsofar,bestsofarstring):
		answers = []
		bestsofarl = bestsofar
		bestsofarstringl = bestsofarstring
		
		for i in range(len(Numbers)):
			if Numbers[i].getUsed() == False:
				currentno = float(Numbers[i].getValue())
				
				temp = lhv + Numbers[i].getValue()
				if temp == target and (not found or findBestAnswer):
					answers.append("("+opSoFar+"+"+Numbers[i].toString()+") = "+str(target))
					found = True
				elif abs(target - temp) < abs(target - bestsofarl) and not found:
					bestsofarstringl = "("+opSoFar+"+"+Numbers[i].toString()+") = " + str(temp)
					bestsofarl = temp
				
				temp = lhv - Numbers[i].getValue()
				if temp == target and (not found or findBestAnswer):
					answers.append("("+opSoFar+"-"+Numbers[i].toString()+") = "+str(target))
					found = True
				elif abs(target - temp) < abs(target - bestsofarl) and not found:
					bestsofarstringl = "("+opSoFar+"-"+Numbers[i].toString()+") = " + str(temp)
					bestsofarl = temp
				
				temp = lhv * Numbers[i].getValue()
				if temp == target and (not found or findBestAnswer):
					answers.append("("+opSoFar+"*"+Numbers[i].toString()+") = "+str(target))
					found = True
				elif abs(target - temp) < abs(target - bestsofarl) and not found:
					bestsofarstringl = "("+opSoFar+"*"+Numbers[i].toString()+") = " + str(temp)
					bestsofarl = temp
				
				temp = lhv / Numbers[i].getValue()
				if temp == target and (not found or findBestAnswer):
					answers.append("("+opSoFar+"/"+Numbers[i].toString()+") = "+str(target))
					found = True
				elif abs(target - temp) < abs(target - bestsofarl) and not found:
					bestsofarstringl = "("+opSoFar+"/"+Numbers[i].toString()+") = " + str(temp)
					bestsofarl = temp
		
		i = 0			
		while i in range(len(Numbers)) and (not found or findBestAnswer):
			if (Numbers[i].getUsed() == False):
				currentno = float(Numbers[i].getValue())
				
				Numbers[i].setUsed(True);
				tempanswers,bestsofarl,bestsofarstringl,found = self.doMaths(lhv+Numbers[i].getValue(),target,Numbers,"("+opSoFar+"+"+Numbers[i].toString()+")",findBestAnswer,found,bestsofarl,bestsofarstringl)
				answers = list(set(answers) | set(tempanswers))
				if not found or findBestAnswer:
					tempanswers,bestsofarl,bestsofarstringl,found = self.doMaths(lhv-Numbers[i].getValue(),target,Numbers,"("+opSoFar+"-"+Numbers[i].toString()+")",findBestAnswer,found,bestsofarl,bestsofarstringl)
					answers = list(set(answers) | set(tempanswers))
				if not found or findBestAnswer:
					tempanswers,bestsofarl,bestsofarstringl,found = self.doMaths(lhv*Numbers[i].getValue(),target,Numbers,"("+opSoFar+"*"+Numbers[i].toString()+")",findBestAnswer,found,bestsofarl,bestsofarstringl)
					answers = list(set(answers) | set(tempanswers))
				if not found or findBestAnswer:
					tempanswers,bestsofarl,bestsofarstringl,found = self.doMaths(lhv/Numbers[i].getValue(),target,Numbers,"("+opSoFar+"/"+Numbers[i].toString()+")",findBestAnswer,found,bestsofarl,bestsofarstringl)
					answers = list(set(answers) | set(tempanswers))
				Numbers[i].setUsed(False)
			i += 1
		return answers,bestsofarl,bestsofarstringl,found
		
class Number():
	def __init__(self,value):
		self.value = value
		self.used = False
	
	def toString(self):
		return str(self.value)

	def getValue(self):
		return self.value;

	def getUsed(self):
		return self.used;

	def setUsed(self,var):
		self.used = var
		

def delay( function , delay):
	count = 0
	while count < delay:
		time.sleep(1)
		count += 1
	function()

