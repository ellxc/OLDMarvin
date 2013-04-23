#!/usr/bin/env python
# -*- coding: utf-8 -*-


import defaultplugin
import random
import re
import thread
import time

class plugin(defaultplugin.plugin):
	commands = {"%pet":("","")
				}
				
	pets = {}
	pattern1 = re.compile("""%createpet +(?:["']((?:\S+)(?: \S*)*)["']|(\S+))(?: +(\S+))?""")
	pattern2 = re.compile("""(?:%pet +|~)(?:["']((?:\S+)(?: +\S*)*)["']|(\S+))(?: +(\S+))?(?: +(\S+(?: +\S+)*))?""")
	
	class petbot
	
	
		
	def onAction(self,bot,message):
		print message.text
		print message.nick
	
	def onMessage(self,bot,message):
		
		xstr = lambda s: s or ""
		
		if self.pattern1.match(message.text):
			print self.pattern1.match(message.text).groups()
			name1,name2,owner = self.pattern1.match(message.text).groups()
			name = xstr(name1)+xstr(name2)
			if name not in self.pets.keys():
				self.pets[name] = pet(name,owner)
				bot.send(message.target,name +" has been born!")
			else:
				bot.send(message.target,message.nick+": "+ name +" already exists!")
		
		if self.pattern2.match(message.text):
			print self.pattern2.match(message.text).groups()
			name1,name2,command,params1 = self.pattern2.match(message.text).groups()
			name = xstr(name1)+xstr(name2)
			params = xstr(params1)
			if name in self.pets.keys():
				if (message.nick == self.pets[name].owner or self.pets[name].owner == None or bot.isadmin(message.nick)):
					if not self.pets[name].dead or command == "bury":
						if not self.pets[name].runaway or command == "bury":
							if command in self.actions.keys():
								bot.send(message.target,message.nick+": "+ self.actions[command](self,self.pets[name]))
							elif command == None:
								bot.send(message.target,message.nick+": "+ self.actions["check"](self,self.pets[name]))
							else:
								bot.send(message.target,message.nick+": "+ "unknown command!")
						else:
							bot.send(message.target,message.nick+": "+ "I am afraid that %s has died while trying to escape :(")
					else:
						bot.send(message.target,message.nick+": "+ "I am afraid that %s is dead :(" % (name))
				else:
					bot.send(message.target,message.nick+": "+ "you do not own this pet!")
			else:
				bot.send(message.target,message.nick+": "+ "that pet does not exist!")
				
	def onPrivateMessage(self,bot,message):
		self.onMessage(bot,message)
			
	def __init__(self):
		thread.start_new_thread(self.managepets,())
		
	def bury(self,pet):
		if pet.dead or pet.runaway:
			name = pet.name
			del self.pets[name]
			return "you have burried %s and put up a tombstone" % (name)
		else:
			return "you cannot bury %s! %s is still alive!" % (pet.name,pet.name)
		
	def managepets(self):
		try: 
			while True:
				for pet in self.pets.values():
					pet.tick()
				time.sleep(60*60)
		finally:
			print "KASJDNAS"
	
class pet():
	hunger = 50
	happiness = 50
	health = 50
	tickcount = 0
	
	sadticks = 0
	unhealthyticks = 0
	hungryticks = 0
	
	runaway = False
	dead = False
	
	def __init__(self,name,owner):
		self.name = name
		self.owner = owner
		
				

		
		
	def update(self):
		if self.hunger > 100:
			self.hunger = 100
		elif self.hunger < 0:
			self.hunger = 0
			
			
		if self.happiness > 100:
			self.happiness = 100
		elif self.happiness < 0:
			self.happiness = 0
			
		if self.health > 100:
			self.health = 100
		elif self.health < 0:
			self.health = 0 
		
	def tick(self):
		if self.tickcount < 25:
			self.tickcount += 1
		else: self.tickcount = 1
	
	
	
		
	
		self.hunger -= 2
		self.happiness -= 1
		
	
	

		if self.hunger > 100:
			self.hunger = 100
			self.hungryticks = 0
		elif self.hunger >= 20:
			self.hungryticks = 0
		elif self.hunger >= 0:
			self.hungryticks += 1
		elif self.hunger < 0:
			self.hungryticks += 1
			self.hunger = 0
			
			
		if self.happiness > 100:
			self.happiness = 100
			self.sadticks = 0
		elif self.happiness >= 20:
			self.sadticks = 0
		elif self.happiness >= 0:
			self.sadticks += 1
		elif self.happiness < 0:
			self.sadticks += 1
			self.happiness = 0
			
		if self.health > 100:
			self.health = 100
			self.unhealthyticks = 0
		elif self.health >= 20:
			self.unhealthyticks = 0
		elif self.health >= 0:
			self.unhealthyticks += 1
		elif self.health < 0:
			self.unhealthyticks += 1
			self.health = 0 
			
		if self.hungryticks > 5:
			self.health -= 10
			
		if self.hungryticks >= 40:
			if self.happiness >= 60 or self.health <= 20:
				self.dead = True
			else:
				self.runaway = True
		elif self.sadticks >= 40:
			self.runaway = True
		elif self.unhealthyticks >= 20:
			self.dead = True
		


class action():
	
	params = {
	"foodchange":0,
	"foodabove":0,
	"foodbelow":100,
	"healthchange":0,
	"healthabove":0,
	"healthbelow":100,
	"happinesschange":0,
	"happinessabove":0,
	"happinessbelow":100,
	"actionstrings":[""],
	"healthtoolow":[""],
	"healthtoohigh":[""],
	"foodtoolow":[""],
	"foodtoohigh":[""],
	"happinesstoolow":[""],
	"happinesstoohigh":[""]
	}
	
	
	def __init__(self,name,**kwargs):
		self.name = name
		for key, value in kwargs.iteritems():
			params[ket] = value
	
	def tryAction(self,pet):
		if pet.
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

		