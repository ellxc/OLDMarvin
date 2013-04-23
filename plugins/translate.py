
import defaultplugin
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
try: import simplejson
except ImportError: import json as simplejson
import re

class plugin(defaultplugin.plugin):

	pattern = re.compile("\%t(?: +([\w]+)?[:>]([\w]+)?)?((?: \S+)+)")

	commands = {"%t":(" <lang>:<lang> <text>","translate text to language etc"),
				"%morse":(" <text>","blah"),
				"%unmorse":(" <text>","blah")
				}

	langauges = {
		"afrikaans" : "af",
		"albanian" : "sq",
		"arabic" : "ar",
		"armenian" : "hy",
		"azerbaijani" : "az",
		"basque" : "eu",
		"belarusian" : "be",
		"bengali" : "bn",
		"bulgarian" : "bg",
		"catalan" : "ca",
		"chinese" : "zh-CN",
		"croatian" : "hr",
		"czech" : "cs",
		"danish" : "da",
		"dutch" : "nl",
		"english" : "en",
		"estonian" : "et",
		"esperanto" : "eo",
		"filipino" : "tl",
		"finnish" : "fi",
		"french" : "fr",
		"galician" : "gl",
		"georgian" : "ka",
		"german" : "de",
		"greek" : "el",
		"gujarati" : "gu",
		"hebrew" : "iw",
		"hindi" : "hi",
		"hungarian" : "hu",
		"icelandic" : "is",
		"indonesian" : "id",
		"irish" : "ga",
		"italian" : "it",
		"japanese" : "ja",
		"korean" : "ko",
		"latin" : "la",
		"latvian" : "lv",
		"lithuanian" : "lt",
		"macedonian" : "mk",
		"malay" : "ms",
		"maltese" : "mt",
		"norwegian" : "no",
		"persian" : "fa",
		"polish" : "pl",
		"portuguese" : "pt",
		"romanian" : "ro",
		"russian" : "ru",
		"serbian" : "sr",
		"slovak" : "sk",
		"slovenian" : "sl",
		"spanish" : "es",
		"swahili" : "sw",
		"swedish" : "sv",
		"thai" : "th",
		"turkish" : "tr",
		"ukrainian" : "uk",
		"vietnamese" : "vi",
		"welsh" : "cy",
		"yiddish" : "yi",
		"xhosa" : "xh"}

	unlanguage = dict((value,key) for (key, value) in list(langauges.items()))

	morse = {
		"a" : ".-",
		"b" : "-...",
		"c" : "-.-.",
		"d" : "-..",
		"e" : ".",
		"f" : "..-.",
		"g" : "--.",
		"h" : "....",
		"i" : "..",
		"j" : ".---",
		"k" : "-.-",
		"l" : ".-..",
		"m" : "--",
		"n" : "-.",
		"o" : "---",
		"p" : ".--.",
		"q" : "--.-",
		"r" : ".-.",
		"s" : "...",
		"t" : "-",
		"u" : "..-",
		"v" : "...-",
		"w" : ".--",
		"x" : "-..-",
		"y" : "-.--",
		"z" : "--..",
		"0" : "-----",
		"1" : ".----",
		"2" : "..---",
		"3" : "...--",
		"4" : "....-",
		"5" : ".....",
		"6" : "-....",
		"7" : "--...",
		"8" : "---..",
		"9" : "----.",
		"." : ".-.-.-",
		"," : "--..--",
		"?" : "..--..",
		"'" : ".----.",
		"!" : "-.-.--",
		"/" : "-..-.",
		"(" : "-.--.",
		")" : "-.--.-",
		"&" : ".-...",
		":" : "---...",
		";" : "-.-.-.",
		"=" : "-...-",
		"+" : ".-.-.",
		"-" : "-....-",
		"_" : "..--.-",
		'"' : ".-..-.",
		"$" : "...-..-",
		"@" : ".--.-.",
		" " : "/"}

	unmorse = dict([(value,key) for (key, value) in list(morse.items())])



	def onMessage(self,bot,message):
		if self.pattern.match(message.text):
			bot.spamsend(message.target,message.nick +": "+ self.translate(message.text))

		elif message.text.startswith("%morse"):
			bot.spamsend(message.target,message.nick +": "+ self.translatetomorse(" ".join(message.text.split(" ")[1:])))
		elif message.text.startswith("%unmorse"):
			bot.spamsend(message.target,message.nick +": "+ self.translatefrommorse(" ".join(message.text.split(" ")[1:])))



	def translate(self,message):

		sourcelangkey,targetlangkey,text = self.pattern.match(message).groups()


		if sourcelangkey == None:
			sourcelang = "auto"
		elif sourcelangkey.lower() not in self.langauges:
			return "language: %s was not found" % (sourcelangkey)
		else:
			sourcelang = self.langauges[sourcelangkey.lower()]

		if targetlangkey == None:
			targetlang = "en"
		elif targetlangkey.lower() not in self.langauges:
			return "language: %s was not found" % (targetlangkey)
		else:
			targetlang = self.langauges[targetlangkey.lower()]

		return self.translate_language(text,sourcelang,targetlang)



	def translate_language(self,text, source_lang="auto", dest_lang="en"):
		translate_params = {"client":"xxxxxxx","text":text,"hl":"en","sl":source_lang,"tl":dest_lang,"ie":"UTF-8","oe":"UTF-8"}
		url_translate = "http://translate.google.com/translate_a/t?"
		headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
		url = url_translate + urllib.parse.urlencode(translate_params)
		req = urllib.request.Request(url, None, headers)
		response = eval(urllib.request.urlopen(req).read().decode())
		lang = self.unlanguage[response["src"]] if response["src"] in self.unlanguage else response["src"]
		lang = lang + " to " +  self.unlanguage[dest_lang] + ": "

		

		if "dict" in response and len(response["dict"][0]["terms"]) >  1:
			return lang + '"' + '", "'.join(response["dict"][0]["terms"][:-1]) + '" or "' + response["dict"][0]["terms"][-1] + '"'
		else:
			return lang + response["sentences"][0]["trans"]

	def translatetomorse(self,text):
		ret = []
		for char in text:
			if char in self.morse:
				ret.append(self.morse[char])
		return " ".join(ret)

	def translatefrommorse(self,text):
		ret = []
		textl = text.split(" ")
		for char in textl:
			if char in self.unmorse:
				ret.append(self.unmorse[char])

		return "".join(ret)



