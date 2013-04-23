import bisect
import datetime
import time
import re
import sys
import os
import defaultplugin
import pickle
import _thread
from collections import deque

import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dateutil import parser

class plugin(defaultplugin.plugin):
	reminders = []
	
	pattern = re.compile("%remind(?: +(\S+))? +(?:in +(.+?)|(?:on|at) +(.+?))(?: *(?:>) ?(.*))?$")
	"""%remind(?: +(\S+))? +(?:in +((?:\d+(?:\.\d*)? +\w+|(?!and|nd|d)\w+ +\w+)(?: +(?:and +|, +)?(?:\d+(?:\.\d*)? +\w+|(?!and|nd|d)\w+ +\w+))*)|(?:on|at) +(.+?))(?: *> ?(.*))?$"""
	
	units = {
	"year" : 31536000,
	"years" : 31536000,
	"fortnight" : 1209600,
	"fortnights" : 1209600,
	"week" : 604800,
	"weeks" : 604800,
	"day" : 86400,
	"days" : 86400,
	"hour" : 3600,
	"hours" : 3600,
	"min" : 60,
	"mins" : 60,
	"minute" : 60,
	"minutes" : 60,
	"second" : 1,
	"seconds" : 1,
	"sec" : 1,
	"secs" : 1,
	"moment" : 90,
	"moments" : 90,
	"milliseconds" : 0.0001,
	"ms" : 0.0001}
	
	quants = {
		"a" : 1,
		"an" : 1,
		"one" : 1,
		"two" : 2,
		"couple" : 2,
		"three" : 3,
		"few" : 3,
		"four" : 4,
		"five" : 5,
		"six" : 6,
		"seven" : 7 ,
		"eight" : 8,
		"nine" : 9,
		"ten" : 10,
		"eleven" : 11,
		"twelve" : 12,
		"dozen" : 12,
		"thirteen" : 13,
		"fourteen" : 14,
		"fifteen" : 15,
		"sixteen" : 16,
		"seventeen" : 17,
		"eighteen" : 18,
		"nineteen" : 19,
		"twenty" : 20,
		"thirty" : 30,
		"fourty" : 40,
		"fifty" : 50,
		"sixty" : 60,
		"seventy" : 70,
		"eighty" : 80,
		"ninety" : 90,
		"hundred" : 100,
		"thousand" : 1000,
		"million" : 1000000,
		"billion" : 1000000000,
		"trillion" : 1000000000000,
		}
		
	fractions = {
		"tenth" : 0.1,
		"quarter" : 0.25,
		"half" : 0.5,
		"tenths" : 0.1,
		"quarters" : 0.25,
		"halfs" : 0.5,
		}

	def isquant(self,string):
		return string in list(self.quants.keys()) or string in list(self.fractions.keys()) or self.is_number(string)
		
	def isfraction(self,string):
		return string in list(self.fractions.keys())
		
	def isunit(self,string):
		return string in list(self.units.keys())

	def onLoad(self,bot):
		self.ticking = True
		
		if os.path.exists(os.path.join(bot.dir, "reminders.save")):
			self.reminders = pickle.load( open( os.path.join(bot.dir, "reminders.save"), "rb" ) )
		_thread.start_new_thread(lambda self,bot: self.tick(bot),(self,bot))

	def onUnload(self,bot):
		pickle.dump( self.reminders, open( os.path.join(bot.dir, "reminders.save"), "wb" ) )
		self.ticking = False
		
	def split_by_units(self,message):
		temp = message
		quants_units = []
		while len(temp) > 0:
			pair,temp = self.split_by_unit(temp)
			if pair: quants_units.append(pair)
			else:
				if message[-1] not in list(self.units.keys()):
					if message[-1] in list(self.quants.keys()):
						raise Exception("No units detected")
					else:
						raise Exception("Unknown unit: " + message[-1])
				
		
		return quants_units
					
	def split_by_unit(self,message):
		temp = message
		quants_unit = None
		for word in temp:
			if word in list(self.units.keys()):
				quants = []
				for x in range(temp.index(word)):
					quants.append(temp[0])
					del temp[0]
				unit = temp[0]
				del temp[0]
				quants_unit = quants,unit
				break
		return quants_unit , temp
		
	def getvalue(self,val):
		if val in list(self.quants.keys()):
			return self.quants[val]
		elif val in list(self.fractions.keys()):
			return self.fractions[val]
		elif self.is_number(val):
			return float(val)
		else: 
			return False
		
	def parsequantity(self,array):
		print(array)
		operators = {
		"and" : "+",
		"," : "+",
		"+" : "+",
		"of" : "*",
		"*" : "*",
		"/" : "/",
		"**" : "**",
		"-" : "-",
		"(" : "(",
		")" : ")",
		}
		string = "("
		for i in range(len(array)):
			print(string)
			if len(array) == 1:
				if self.isquant(array[i]):
					string += str(self.getvalue(array[i]))
				elif array[i] in list(operators.keys()):
					raise Exception("no quantity specified")
				else:
					try: 
						eval(array[i])
						string += str(eval(array[i]))
					except:
						raise Exception("Unknown quantity: " + array[i])
			else:
				if self.isquant(array[i]):
					if i < len(array)-1 and i != 0 and self.getvalue(array[i-1]):
						if self.getvalue(array[i-1]) > self.getvalue(array[i]):
							if self.getvalue(array[i+1]) > self.getvalue(array[i])  and self.getvalue(array[i]) >= 1:# and array[i-1] not in ["a","an"]:
								string += "+"
							#elif array[i-1] not in ["a","an"]:
							#	string += "+"
							else:
								string += "*"
						elif array[i-1] not in list(operators.keys()):
							string+= "*"
					elif i != 0 and self.getvalue(array[i]):
						if self.getvalue(array[i-1]) > self.getvalue(array[i]) and self.getvalue(array[i]) >= 1:# and array[i] not in ["a","an"]:
							if array[i-1] not in ["a","an"]:
								string += "+"
							else:
								string += "*"
						elif array[i-1] not in list(operators.keys()):
							string+= "*"
					string += str(self.getvalue(array[i]))
					if i > 2 and array[i-2] in ["and"] and array[i-1] in ["a","an"]:
						print("derp")
						x = string.rfind("+")
						x2 = string[:x].rfind("+") + 1
						if array[i-2] == "of": string = string[:x] +"*"+ string[x+1:]
						string = string[:x2] + "(" + string[x2:] +")"
				elif array[i] in list(operators.keys()):
					string += str(operators[array[i]])
				else:
					try: 
						eval(array[i])
						string += str(eval(array[i]))
					except:
						raise Exception("Unknown quantity: " + array[i])
				
		string += ")"
		try:
			print(eval(string))
			return eval(string)
		except Exception as e:
			traceback.print_exc()
			raise Exception("Parse fail: " +str( "".join(traceback.format_exception_only(type(e),e))))
		
		

	def onMessage(self,bot,message):
		if message.text.startswith("%testdate "):
			try:
				bot.send(message.target,parser.parse(" ".join(message.text.split(" ")[1:])).strftime("%c"))
			except:
				bot.send(message.target,"Unknown format used!")
				
		if message.text.startswith("%unitsplit "):
			bot.send(message.target,str(self.split_by_units(message.text.split(" ")[1:])))
			
		if message.text.startswith("%testtime "):
			try:
				seconds = 0
				temp = self.split_by_units(message.text.split(" ")[1:])
				if temp:
					for x,y in temp:
						seconds += self.parsequantity(x) * self.units[y]
					bot.send(message.target,message.nick + ": " + str(int(seconds)) + " seconds : " + datetime.datetime.fromtimestamp(time.time()+(int(seconds))).strftime("%c"))
				else:
					bot.send(message.target,message.nick + ": No quantity detected")
			except Exception as e:
				traceback.print_exc()
				bot.send(message.target,message.nick + ": Error parsing: " + str(e))
					
				
		if self.pattern.match(message.text.strip()):
			try:
				args = [x for x in self.pattern.match(message.text).groups()]
				if args[0] == "me":
					args[0] = message.nick
					
				if args[1]:
					seconds = 0
					temp = self.split_by_units(args[1].split(" "))
					if temp:
						for x,y in temp:
							seconds += self.parsequantity(x) * self.units[y]
						bisect.insort(self.reminders , reminder(message.nick,args[0],datetime.datetime.today(),datetime.datetime.fromtimestamp(time.time()+int(seconds)), args[3] or "",message.target))
						bot.send(message.target,message.nick + ": reminder set for " + datetime.datetime.fromtimestamp(time.time()+(int(seconds))).strftime("%c"))
					else:
						bot.send(message.target,message.nick + ": No quantity detected")
				
							
							
				elif args[2]:
					bisect.insort(self.reminders , reminder(message.nick,args[0],datetime.datetime.today(),parser.parse(args[2]), args[3] or "",message.target))
					bot.send(message.target,message.nick + ": reminder set for " + parser.parse(args[2]).strftime("%c"))
			except Exception as e:
				traceback.print_exc()
				bot.send(message.target,message.nick + ": Error parsing: " + str(e))
				
		elif message.text.startswith("%remind"):
			bot.send(message.target,message.nick + ": failed to parse.")
			
	def parsenumber(self,text):
		pass
	
	def is_number(self,s):
		try:
			float(s)
			return True
		except ValueError:
			return False
	
	def tick(self,bot):
		while self.ticking:
			if self.reminders and self.reminders[0].due_time <= datetime.datetime.today():
				if self.reminders[0].set_for == self.reminders[0].set_by:
					bot.send(self.reminders[0].channel,self.reminders[0].set_for + ": reminder: " + self.reminders[0].message)
				else:
					bot.send(self.reminders[0].channel,self.reminders[0].set_for + ": "+self.reminders[0].set_by+" reminds you: " + self.reminders[0].message)
				del self.reminders[0]
			else:
				time.sleep(1)

	def getHelp(self,bot,message):
		pass
		
	def onPrivateMessage(self,bot,message):
		self.onMessage(bot,message)
		
class reminder:

	def __init__(self,set_by,set_for,set_time,due_time,message,channel):
		self.set_by = set_by
		self.set_for = set_for
		self.set_time = set_time
		self.due_time = due_time
		self.message = message
		self.channel = channel
	
	def __lt__(self,other):
		try:
			return not other.due_time<self.due_time
		except:
			pass
		return 0
	
	
	
	
	
	
	
	

