#!/usr/bin/env python
# -*- coding: utf-8 -*-

import defaultplugin


import pickle
import os
import urllib.request, urllib.error, urllib.parse

class plugin(defaultplugin.plugin):

	counter = 0

	def onMessage(self,bot,message):
		if message.text.startswith("%test "):
			response = urllib.request.urlopen(" ".join(message.text.split(" ")[1:]))
			html = response.read()
			print(html)

		



	"""	def onAction(self,ubot,message):
			print message.text
			print "floods "+message.target+" with kittens"
			if message.text.find("floods "+message.target+" with kittens") != -1:
				for i in range(1,20):
					tempbot = bot.bot("kitten"+str(i))
					tempbot.connect("irc.compsoc.kent.ac.uk",6667)
					thread.start_new_thread(tempbot.run,())
					tempbot.send(message.target,"meow")
					#tempbot.disconnect()
					#tempbot.quit()"""


		
	def onLoad(self,bot):
		try:
			self.counter = pickle.load( open( os.path.join(bot.dir, "test.save"), "rb" ) )
		except Exception as e:
			print("error loading saved data: %s" % e)
		print("LOADED")

	def onUnload(self,bot):
		try:
			pickle.dump( self.counter, open( os.path.join(bot.dir, "test.save"), "wb" ) )
		except Exception as e:
			print("error saving data: %s" % e)
		print("UNLOADED")


