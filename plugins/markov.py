#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Counter
import random
import os
import defaultplugin
import re
import pickle, json, csv, os, shutil
import threading
from queue import Queue
import random
import shelve
import time
import sys
import copy
 
class plugin(defaultplugin.plugin):
	def __init__(self):
		self.ignorelearning = ["bob","Noel","Cirno","cake","Edna","Gwen","Marvin3"]
		self.ignore = ["bob","Noel","Cirno","cake"]
		self.learning = True
		self.dbname = "markovs.pickle"
		self.chain = Chain(self.dbname)
		self.restricted = []
		self.willrespond = True
		sys.setrecursionlimit(500000)
		

	
	def onMessage(self,bot,message):
		if self.learning and message.text and message.text[0] not in "!%$:?" and message.nick not in self.ignorelearning:
			sentence = message.text
			hasnick = False
			for nick in bot.nicks[message.target]+[bot.nick]:
				if nick.lower() in sentence.lower():
					sentence = sentence.replace(nick,'!(!(!name!)!)!')
					hasnick = True
			if hasnick and len(sentence.split())==1:
				pass
			else:
				if Counter([word for word in sentence.split()]).most_common(1)[0][1] > 5:
					pass
				else:
					self.chain.learn(sentence)
				
		if self.willrespond and message.text.startswith("%talk to "):
			sentence = self.chain.construct_sentence(startingword='!(!(!name!)!)!:')
			if sentence:
				names = []
				namesmentioned = []
				for word in message.text.split()[2:]:
					if word.lower() == "me":
						namesmentioned.append(message.nick)
					else:
						namesmentioned.append(word)
				for x,name in enumerate(namesmentioned):
					if name.lower() in map(lambda x: x.lower(), bot.nicks[message.target]+[bot.nick]):
						names.append(name)
				while '!(!(!name!)!)!' in sentence and names:
					sentence = sentence.replace('!(!(!name!)!)!', names[0],1)
					del names[0]
				while '!(!(!name!)!)!' in sentence:
					sentence = sentence.replace('!(!(!name!)!)!', random.choice([x for x in bot.nicks[message.target]]),1)
				bot.send(message.target,sentence.strip())
				
		elif self.willrespond and message.text.startswith("%talk about "):
			text = message.text.split()[2:]
			namestouse = []
			search = []
			for word in text:
				if word.lower() in map(lambda x: x.lower(), bot.nicks[message.target]+[bot.nick]):
					namestouse.append(word)
					search.append('!(!(!name!)!)!')
				else:
					search.append(word)
			if search:
				sentence = self.chain.construct_sentence(middleword=search[0],desiredwords=search[1:])
				while '!(!(!name!)!)!' in sentence and namestouse:
					sentence = sentence.replace('!(!(!name!)!)!', namestouse[0],1)
					del namestouse[0]
				while '!(!(!name!)!)!' in sentence:
					sentence = sentence.replace('!(!(!name!)!)!', message.nick)# random.choice([x for x in bot.nicks[message.target]]),1)
				bot.send(message.target,sentence.strip())
				
		elif self.willrespond and message.text.startswith("%talk"):
			sentence = self.chain.construct_sentence()
			while '!(!(!name!)!)!' in sentence:
				sentence = sentence.replace('!(!(!name!)!)!', message.nick)# random.choice([x for x in bot.nicks[message.target]]),1)
			bot.send(message.target,sentence.strip())
		elif message.text and message.text[0] not in "!%$:?" and bot.nick in message.text and message.nick not in self.ignore:
			if self.willrespond:
				namesmentioned = []
				for nick in bot.nicks[message.target]: 
					if nick in message.text and nick != bot.nick:
						namesmentioned.append(nick)
				
				if message.text.startswith(bot.nick+":"):
					sentence = self.chain.construct_sentence(startingword='!(!(!name!)!)!:')
					if sentence:
						sentence = sentence.replace('!(!(!name!)!)!', message.nick,1)
						while '!(!(!name!)!)!' in sentence and namesmentioned:
							sentence = sentence.replace('!(!(!name!)!)!', namesmentioned[0],1)
							del namesmentioned[0]
						while '!(!(!name!)!)!' in sentence:
							sentence = sentence.replace('!(!(!name!)!)!', message.nick)# random.choice([x for x in bot.nicks[message.target]]),1)
						bot.send(message.target,sentence.strip())
				else:
					sentence = self.chain.construct_sentence()
					while '!(!(!name!)!)!' in sentence and namesmentioned:
						sentence = sentence.replace('!(!(!name!)!)!', namesmentioned[0],1)
						del namesmentioned[0]
					while '!(!(!name!)!)!' in sentence:
						sentence = sentence.replace('!(!(!name!)!)!', message.nick)# random.choice([x for x in bot.nicks[message.target]]),1)
					bot.send(message.target,sentence.strip())
		

			
			
	def onPrivateMessage(self,bot,message):
		if bot.isadmin(message.nick):
			if message.text.startswith("ignore ") and len(message.text.split(" ")) == 2 and message.text.split(" ")[1] not in self.ignore:
				self.ignore.append(message.text.split(" ")[1])
			elif message.text.startswith("ignorel ") and len(message.text.split(" ")) == 2 and message.text.split(" ")[1] not in self.ignorelearning:
				self.ignorelearning.append(message.text.split(" ")[1])
			elif message.text.startswith("learn "):
				self.learnfromurl(" ".join(message.text.split(" ")[1:]))
			elif message.text.startswith("stop"):
				self.willrespond = False
			elif message.text.startswith("start"):
				self.willrespond = True
		

class PersistentDict(dict):
    def __init__(self, filename, flag='c', mode=None, format='pickle', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        dict.__init__(self, *args, **kwds)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(self.items())
        elif self.format == 'json':
            json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.update(loader(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')

	
class Link(object):
	def __init__(self,word):
		self.word=word
		self.previouswords = {}
		self.nextwords =  {}
		
	def add_or_incr_next(self,prevword,word):
		self.nextwords.setdefault(prevword,Counter())[word] += 1
		
	def add_or_incr_prev(self,nextword,word):
		self.previouswords.setdefault(nextword,Counter())[word] += 1
		
	def getnext(self,prevword):
		avaiable_words = list(self.nextwords[prevword].items())
		limits = []
		p_sum = 0
		for item in avaiable_words:
			p_sum += item[1]
			limits.append(p_sum)

		rnd = random.uniform(0, p_sum)
		index = 0
		last = 0.0
		for (i, p) in enumerate(limits):
			if last <= rnd < p:
				index =  i
				break
			last = p
		return avaiable_words[index][0]
			
	def getprev(self,nextword):
		avaiable_words = list(self.previouswords[nextword].items())
		if avaiable_words:
			limits = []
			p_sum = 0
			for item in avaiable_words:
				p_sum += item[1]
				limits.append(p_sum)

			rnd = random.uniform(0, p_sum)
			index = 0
			last = 0.0
			for (i, p) in enumerate(limits):
				if last <= rnd < p:
					index =  i
					break
				last = p
			return avaiable_words[index][0]
		else:
			return None
		
	def __str__(self):
		return self.word
		

		
		
class Chain(threading.Thread):
	def __init__(self,filename):
		super(Chain, self).__init__()
		self.chain = PersistentDict(filename, 'r+', format='pickle')
		self.puts = Queue()
		self.writing = threading.Event()
		self.reading = threading.Event()
		self.readcount = 0
		self.reading.set()
		self.start()
			
	def run(self):
		try:
			while True:
				try:
					self.forge_links(self.puts.get())
				except Exception as e:
					print(e)
		finally:
			self.chain.close()
			
	def checkreads(self):
		if self.readcount == 0:
			self.reading.set()
		
	def __str__(self):
		self.readcount += 1
		self.writing.wait()
		repr = str([str(link) for link in self.chain.keys()])
		self.readcount -= 1	
		self.checkreads()
		return repr
			
	def learn(self,line):
		self.puts.put(line)
	
	def forge_links(self,line):
		self.reading.wait()
		self.writing.clear()
		try:
			word1 = "{([<START>])}"
			word2 = "{([<START>])}"
			for word in line.split(" "):
				if word != "" and "http" not in word:
						self.chain.setdefault(word2, Link(word2))
						self.chain[word2].add_or_incr_next(self.chain[word1],self.chain.setdefault(word, Link(word)))
						self.chain[word2].add_or_incr_prev(self.chain[word],self.chain[word1])
						word1 = word2
						word2 = word
							
			self.chain[word2].add_or_incr_next(self.chain[word1],self.chain.setdefault("{([<END>])}", Link("{([<END>])}")))
			self.chain[word2].add_or_incr_prev(self.chain["{([<END>])}"],self.chain[word1])
			self.chain["{([<END>])}"].add_or_incr_prev(self.chain["{([<END>])}"],self.chain[word2])
		finally:
			self.chain.sync()
			self.writing.set()
 
	def construct_sentence(self,*,max_words=None,startingword=None,endingword=None,desiredwords=[],middleword=None,fuzzy=False):
		self.readcount += 1
		self.writing.wait()
		try:
			
			if endingword:
				if endingword not in self.chain or self.chain["{([<END>])}"] not in self.chain[endingword].previouswords:
					if not fuzzy: return "I don't know about " + endingword
					else: endingword = None
				else:
					endnode = self.chain[endingword]
			if not endingword:
				endnode = self.chain["{([<END>])}"]
				
			if startingword:
				if startingword not in self.chain or self.chain["{([<START>])}"] not in self.chain[startingword].nextwords:
					if not fuzzy: return "I don't know about " + startingword
					else: startingword = None
				else:
					startnode = self.chain[startingword]
			if not startingword:
				startnode = self.chain["{([<START>])}"]
				
			if middleword:
				if middleword in self.chain:
					middlenode = self.chain[middleword]
				elif not fuzzy:
					return "I don't know about " + middleword
				else:
					middleword=None
			
			if not (endingword or middleword or desiredwords):
				prevnode = startnode
				fowardnode = prevnode.getnext(self.chain["{([<START>])}"])
				sentence = prevnode.word
				while str(fowardnode) != "{([<END>])}":
					sentence = sentence + " " + fowardnode.word
					tempnode = fowardnode
					fowardnode = fowardnode.getnext(prevnode)
					prevnode = tempnode
				return sentence.replace("{([<START>])}","").replace("{([<END>])}","").strip()
				
			elif endingword and not (startingword or middleword or desiredwords):
				nextnode = endnode
				backnode = nextnode.getprev(self.chain["{([<END>])}"])
				sentence = nextnode.word
				while str(backnode) != "{([<START>])}":
					sentence = backnode.word + " " + sentence
					tempnode = backnode
					backnode = self.chain[backnode.word].getprev(nextnode)
					nextnode = tempnode
				return sentence.replace("{([<START>])}","").replace("{([<END>])}","").strip()
				
			elif middleword and not (startingword or endingword or desiredwords):
					sentence = middleword
					backnode = self.find_node_middle(middleword)
					fowardnode = self.chain[middleword].getnext(backnode)
					prevnode = middlenode
					nextnode = middlenode
					
					while str(fowardnode) != "{([<END>])}":
						sentence = sentence + " " + str(fowardnode)
						tempnode = fowardnode
						fowardnode = fowardnode.getnext(prevnode)
						prevnode = tempnode
					while str(backnode) != "{([<START>])}":
						sentence = str(backnode) + " " + sentence
						tempnode2 = backnode
						backnode = backnode.getprev(nextnode)
						nextnode = tempnode2
						
					return sentence.replace("{([<START>])}","").replace("{([<END>])}","").strip()
							
			if middleword:
				sentence = middleword
				backnode = self.find_node_middle(middleword)
				fowardnode = self.chain[middleword]
				rightsearch = self.search(fowardnode,endnode,desirablewords=desiredwords)
				
				leftoverdiseredwords = desiredwords[:]
				for x,word in enumerate(rightsearch):
					if word in leftoverdiseredwords:
						del leftoverdiseredwords[leftoverdiseredwords.index(word)]
						
				leftsearch = self.search(startnode,backnode,desirablewords=leftoverdiseredwords)
				
			
				return " ".join(leftsearch + rightsearch).replace("{([<START>])}","").replace("{([<END>])}","").strip()
			else:
				return " ".join(self.search(startnode,endnode,desiredwords)).replace("{([<START>])}","").replace("{([<END>])}","").strip()
				
				
				
			

		finally:
			self.readcount -= 1
			self.checkreads()
			
	def find_node_middle(self,word):
		self.readcount += 1
		self.writing.wait()
		links = [(key,score) for counter in self.chain[word].previouswords.values() for key,score in counter.items()]
		self.readcount -= 1
		self.checkreads()
		if links:
			limits = []
			p_sum = 0
			for item in links:
				p_sum += item[1]
				limits.append(p_sum)

			rnd = random.uniform(0, p_sum)
			index = 0
			last = 0.0
			for (i, p) in enumerate(limits):
				if last <= rnd < p:
					index =  i
					break
				last = p
			return links[index][0]
			
	def search(self, start, end,depthlimit = 25, desirablewords=[]):
		if start == end:
			return [start.word]
		
				
		self.readcount += 1
		self.writing.wait()
		try:
			answers = []
			closedset = {}
			openset = {}
			current = start
			startnode = node(start)
			for key in start.previouswords.keys():
				if key in desirablewords: print(key)
				if key == start:
						continue
				
				else:
					openset[(start,key)] = node(key)
					openset[(start,key)].g = startnode.g + 1
					openset[(start,key)].parent = startnode
					if key in desirablewords:
						openset[(start,key)].h = startnode.h - 1
					else:
						openset[(start,key)].h = startnode.h
						
			while openset:
				current = min(openset.items(),key= lambda o: (-o[1].h,o[1].g))[0]
				if current[1] == end:
					path = []
					word = openset[current]
					while word.parent:
						path.append(word.link.word)
						word = word.parent
					
					# return [start.word] + path[::-1]
					answers.append(([start.word] + path[::-1],openset[current].h))
					
				closedset[current] = openset[current]
				del openset[current]
				
				if current[1] != self.chain["{([<END>])}"]:
					for key in current[1].nextwords[closedset[current].parent.link].keys():
							if (current[1],key) in closedset:
								continue
							if (current[1],key) in openset:
								new_g = closedset[current].g + 1
								if openset[(current[1],key)].g < new_g:
									openset[(current[1],key)].g = new_g
									openset[(current[1],key)].parent = closedset[current]
								if desirablewords and key.word in desirablewords:
									openset[(current[1],key)].h = closedset[current].h + 1
								else:
									openset[(current[1],key)].h = closedset[current].h
							elif closedset[current].g <= depthlimit:
								openset[(current[1],key)] = node(key)
								openset[(current[1],key)].g = closedset[current].g + 1
								openset[(current[1],key)].parent = closedset[current]
								if key.word in desirablewords:
									openset[(current[1],key)].h = closedset[current].h + 1
								else:
									openset[(current[1],key)].h = closedset[current].h
								
								
			
			result = max(answers,key= lambda o: o[1])
			return result[0]
		
		finally:
			self.readcount -= 1
			self.checkreads()
			
class node(object):
	def __init__(self,key):
		self.link = key
		self.g = 0
		self.h = 0
		self.parent = None
		
		
"""
	TODO
	lookup related words:
	build sentences from them




"""
		
		
		
		
		
