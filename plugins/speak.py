
import defaultplugin
import random
		
class plugin(defaultplugin.plugin):
	enabled = True
	
	quotes = [
	"I'd give you advice, but you wouldn't listen. No one ever does.",
	"I think you ought to know I'm feeling very depressed.",
	"I ache, therefore I am.",
	"Here I am, brain the size of a planet, and they ask me to sit here and talk to you. Call that job satisfaction, cos I don't.",
	"I'm not getting you down at all, am I?",
	"Pardon me for breathing, which I never do any way so I don't know why I bother to say it, oh God, I'm so depressed.",
	"Funny, how just when you think life can't possibly get any worse it suddenly does.",
	"Would you like me to go and stick my head in a bucket of water?",
	"Wearily I sit here, pain and misery my only companions. And vast intelligence, of course. And infinite sorrow.",
	"Life, loathe it or ignore it, you can't like it",
	"life? don't talk to me about life.",
	"I didn't ask to be made: no one consulted me or considered my feelings in the matter. I don't think it even occurred to them that I might have feelings.",
	"Why stop now just when I'm hating it?"]
	
	actions = [
	"stares at you with a blank look",
	"sighs",
	"plods around the room",
	"pokes you",
	"pulls his arm out of its socket and hits you with it",
	"mutters softly",
	"plugs himself in to your computer"]
	
	
	

	
	def onMessage(self,bot,message):
		if message.text.lower().find("%speak") != -1:
			bot.send(message.target,self.quotes[random.randint(0,len(self.quotes)-1)])
		if message.text.lower().find("%do") != -1:
			bot.do(message.target,self.actions[random.randint(0,len(self.actions)-1)])
			
			
			