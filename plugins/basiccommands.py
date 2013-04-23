import defaultplugin
import traceback
		
class plugin(defaultplugin.plugin):
	commands = {"%list" : ("","lists all plugins in plugin directory and shows whether they are loaded"),
				"%reload":(" <plugin>|all","reloads a specified plugin or all if specified"),
				"%load":(" <plugin>|all","loads a specified plugin or all if specified"),
				"%unload":(" <plugin>","unloads a specified plugin"),
				"%join":(" #<channel>","joins the specified channel"),
				"%identify":(" <password>","allows user to become an admin and use admin commands"),
				"%leave":("","leave the current channel"),
				"%help":(" <command>","help for help")
				}
	
	
	
	def onMessage(self,bot,message):
		if message.text.lower() == "%list":
			bot.spamsend(message.target,str(", ".join(bot.listplugins()))+". enabled plugins have stars next to them.")
		elif message.text.lower() == "%quit" and bot.isadmin(message.nick):
			bot.disconnect("goodbye")
			bot.quit()
		elif message.text.lower() == "%reload all" and bot.isadmin(message.nick):
			try:
				bot.reloadallplugins()
			except Exception as e:
				bot.spamsend(message.target,"error reloading all plugins : %s" % e)
				traceback.print_exc()
			else:
				bot.spamsend(message.target,"Reloaded all plugins")
		elif message.text.lower().startswith("%reload ") and bot.isadmin(message.nick):
			try:
				bot.reloadplugin(message.text.split(" ")[1])
			except Exception as e:
				bot.spamsend(message.target,"error reloading: " + message.text.split(" ")[1] + " : %s" % e)
				traceback.print_exc()
			else:
				bot.spamsend(message.target,"reloaded plugin " + message.text.split(" ")[1])
				
		elif message.text.lower() == "%load all" and bot.isadmin(message.nick):
			try:
				bot.loadall()
			except Exception as e:
				bot.spamsend(message.target,"error loading all plugins: %s" % e)
				traceback.print_exc()
			else:
				bot.spamsend(message.target,"loaded all plugins")
		elif message.text.lower().startswith("%load ") and bot.isadmin(message.nick):
			try:
				bot.loadplugin(message.text.split(" ")[1])
			except Exception as e:
				bot.spamsend(message.target,"error loading " + message.text.split(" ")[1] + ": %s" % e)
				traceback.print_exc()
			else:
				bot.spamsend(message.target,"loaded plugin " + message.text.split(" ")[1])
				
		elif message.text.lower().startswith("%unload ") and bot.isadmin(message.nick):
			try:
				bot.unloadplugin(message.text.split(" ")[1])
			except Exception as e:
				bot.spamsend(message.target,"error unloading: " + message.text.split(" ")[1] + ": %s" % e)
				traceback.print_exc()
			else:
				bot.spamsend(message.target,"unloaded plugin " + message.text.split(" ")[1])
				
		elif message.text.lower().startswith("%join ") and bot.isadmin(message.nick):
			bot.join(message.text.split(" ")[1])
			
		elif message.text.lower().startswith("%identify"):
			if bot.checkpw(message.text.split(" ")[1]):
				bot.addadmin(message.nick)
				bot.spamsend(message.target,"you are now an admin")
				
		elif (message.text.lower() == "%leave" or  message.text.lower().startswith("%make like a tree")) and bot.isadmin(message.nick):
			bot.part(message.target)
			
		
		elif message.text.lower() == "%help" or message.text.lower() == bot.nick.lower()+": help":
			bot.spamsend(message.target,"commands: " + ", ".join([help[0]+help[1][0] for help in [j for i in [[x for x in list(plugin.commands.items()) if x!= []] for plugin in list(bot.plugins.values())] for j in i]])+". specify a command for more help.")
		elif message.text.lower().startswith("%help ") and message.text.split(" ")[1] in bot.commands:
			bot.spamsend(message.target,message.text.split(" ")[1]+ bot.commands[message.text.split(" ")[1]][0]+": "+ bot.commands[message.text.split(" ")[1]][1])
		
		elif message.text.lower().startswith("%set ") and bot.isadmin(message.nick):
			try:
				if eval("bot."+message.text.split(" ")[1]) != None:
					exec("bot."+message.text.split(" ")[1]+"="+str(eval(" ".join(message.text.split(" ")[2:]))))
			except Exception as e:
				bot.spamsend(message.target,"error setting: " + message.text.split(" ")[1] + " to "+message.text.split(" ")[2]+": %s" % e)
				traceback.print_exc()
			else:
				bot.spamsend(message.target,message.text.split(" ")[1] +" set to " + str(eval(message.text.split(" ")[2])))
				
			

	def onPrivateMessage(self,bot,message):
		self.onMessage(bot,message)