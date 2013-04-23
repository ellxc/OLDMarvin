

from . import defaultplugin
import re
import pickle
import os
import random
import collections
import itertools

class Hist(dict):
    """A map from each item (x) to its frequency."""

    def __init__(self, seq=[]):
        "Creates a new histogram starting with the items in seq."
        for x in seq:
            self.count(x)

    def count(self, x, f=1):
        "Increments the counter associated with item x."
        self[x] = self.get(x, 0) + f
        if self[x] == 0:
            del self[x]


class Card(object):
    """Represents a standard playing card.
    
    Attributes:
      suit: integer 0-3
      rank: integer 1-13
    """

    suit_names = ["Clubs", "Diamonds", "Hearts", "Spades"]
    rank_names = [None, "Ace", "2", "3", "4", "5", "6", "7", 
              "8", "9", "10", "Jack", "Queen", "King"]

    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        """Returns a human-readable string representation."""
        return '%s of %s' % (Card.rank_names[self.rank],
                             Card.suit_names[self.suit])

    def __cmp__(self, other):
        """Compares this card to other, first by suit, then rank.

        Returns a positive number if this > other; negative if other > this;
        and 0 if they are equivalent.
        """
        t1 = self.suit, self.rank
        t2 = other.suit, other.rank
        return cmp(t1, t2)
		


class deck():
	def __init__(self):
		self.cards = [Card(suit,value) for suit in range(4) for value in range(1,14)]
		
	def deal(self):
		return self.cards.pop()
		
	def shuffle(self):
		random.shuffle(self.cards)
		
	def returndeck(self):
		self.cards = [Card(suit,value) for suit in range(4) for value in range(14)]
		
class Hand():
    """Represents a hand of playing cards."""
    
    def __init__(self, label=''):
        self.cards = []
        self.label = label

		
class PokerHand(object):
	"""Represents a poker hand."""
	all_labels = ['straightflush', 'fourkind', 'fullhouse', 'flush',
                  'straight', 'threekind', 'twopair', 'pair', 'highcard']
	
	
	def __cmp__(self,other):
		if all_labels.index(self.labels[0]) > all_labels.index(other.labels[0]): return 1
		if all_labels.index(self.labels[0]) < all_labels.index(other.labels[0]): return -1
		#if self.cards[-1].rank 
				  
	def __init__(self,cards):
		self.cards = cards
		self.classify()

	def make_histograms(self):
		"""Computes histograms for suits and hands.

		Creates attributes:

		  suits: a histogram of the suits in the hand.
		  ranks: a histogram of the ranks.
		  sets: a sorted list of the rank sets in the hand.
		"""
		self.suits = Hist()
		self.ranks = Hist()

		for c in self.cards:
			self.suits.count(c.suit)
			self.ranks.count(c.rank)

		self.sets = list(self.ranks.values())
		self.sets.sort(reverse=True)

		print(self.ranks)
 
	def has_highcard(self):
		"""Returns True if this hand has a high card."""
		return len(self.cards)
        
	def check_sets(self, *t):
		"""Checks whether self.sets contains sets that are
		at least as big as the requirements in t.

		t: list of int
		"""
		values = []
		for need, have in zip(t, self.sets):
			if need > have: return False
			#if need == have: values.append
		return True

	def has_pair(self):
		"""Checks whether this hand has a pair."""
		return self.check_sets(2)
        
	def has_twopair(self):
		"""Checks whether this hand has two pair."""
		return self.check_sets(2, 2)
        
	def has_threekind(self):
		"""Checks whether this hand has three of a kind."""
		return self.check_sets(3)
        
	def has_fourkind(self):
		"""Checks whether this hand has four of a kind."""
		return self.check_sets(4)

	def has_fullhouse(self):
		"""Checks whether this hand has a full house."""
		return self.check_sets(3, 2)

	def has_flush(self):
		"""Checks whether this hand has a flush."""
		for val in list(self.suits.values()):
			if val >= 5:
				return True
		return False

	def has_straight(self):
		"""Checks whether this hand has a straight."""
		# make a copy of the rank histogram before we mess with it
		ranks = self.ranks.copy()
		ranks[14] = ranks.get(1, 0)

		# see if we have 5 in a row
		return self.in_a_row(ranks, 5)

	def in_a_row(self, ranks, n):
		"""Checks whether the histogram has n ranks in a row.

		hist: map from rank to frequency
		n: number we need to get to
		"""
		count = 0
		for i in range(1, 15):
			if ranks.get(i, 0):
				count += 1
				if count == 5: return True
			else:
				count = 0
		return False
    
	def has_straightflush(self):
		"""Checks whether this hand has a straight flush.

		Clumsy algorithm.
		"""
		# make a set of the (rank, suit) pairs we have
		s = set()
		for c in self.cards:
			s.add((c.rank, c.suit))
			if c.rank == 1:
				s.add((14, c.suit))

		# iterate through the suits and ranks and see if we
		# get to 5 in a row
		for suit in range(4):
			count = 0
			for rank in range(1, 15):
				if (rank, suit) in s:
					count += 1
					if count == 5: return True
				else:
					count = 0
		return False
                



	def classify(self):
		"""Classifies this hand.

		Creates attributes:
		  labels:
		"""
		self.make_histograms()

		self.labels = []
		for label in PokerHand.all_labels:
			f = getattr(self, 'has_' + label)
			if f():
				self.labels.append(label)

		
	
		
class globalplayer():
	def __init__(self,name,chips):
		self.name = name
		self.chips = chips

class Player():
	folded = False
	inround = False
	hadturn = False
	handvalue = 0
	def __init__(self,name,chips):
		self.name = name
		self.chips = chips
		self.hand = []
		self.currentbet = 0
		
	def addtohand(self,card):
		self.hand.append(card)
		
	def clearhand(self):
		self.hand = []
		
	def __cmp__(self,other):
		pass
		
class pokertable():
	
	
	bettinground = False
	
	pool = 0
	roundmaxbet = 0
	
	handsdealt = False
	flop = False
	turn = False
	river = False
	showdown = False
	
	
	gamerunning = False
	
	
	suits = {
				"H" : "HEARTS",
				"D" : "DIAMONDS",
				"C" : "CLUBS",
				"S" : "SPADES"
			}
	
	values= {
				"2" : "TWO",
				"3" : "THREE",
				"4" : "FOUR",
				"5" : "FIVE",
				"6" : "SIX",
				"7" : "SEVEN",
				"8" : "EIGHT",
				"9" : "NINE",
				"10" : "TEN",
				"J" : "JACK",
				"Q" : "QUEEN",
				"K" : "KING",
				"A" : "ACE"
			}
			
	values2= {
				"2" : 2,
				"3" : 3,
				"4" : 4,
				"5" : 5,
				"6" : 6,
				"7" : 7,
				"8" : 8,
				"9" : 9,
				"10" : 10,
				"J" : 11,
				"Q" : 12,
				"K" : 13,
				"A" : 14
			}
	
	def __init__(self,bot,globalplayers,channel,buyin,minbet=2,maxbet=50):
		self.bot = bot
		self.globalplayers = globalplayers
		self.channel = channel
		self.buyin = buyin
		self.minbet = minbet
		self.maxbet = maxbet
		
		self.deck = deck()
		self.players = collections.OrderedDict([])
		self.tablecards = []
		self.currentplayer = ""
		
	def handlemessage(self,message):
		if message.text == "%join":
			if message.nick not in list(self.players.keys()):
				if message.nick not in list(self.globalplayers.keys()):
					self.globalplayers[message.nick] = globalplayer(message.nick,500)
					self.bot.send(message.nick,"New player detected, allocating you %s chips." % (500))
				
				if self.globalplayers[message.nick].chips >= self.buyin:
					self.bot.send(self.channel,"%s joined the table with %s chips" % (message.nick,self.buyin))
					self.players[message.nick] = Player(message.nick,self.buyin)
					self.globalplayers[message.nick].chips -= self.buyin
					
				else:
					self.bot.send(message.nick,"I am sorry, you do not have the required \x02%s\x02 chips to buyin to this table." % (self.buyin))
			else:
				self.bot.send(message.nick,"you have already joined the table in %s." % (self.channel))
				
		if message.text == "%start":
			if len(list(self.players.values())) >= 2:
				if not self.gamerunning:
					self.gamestart()
				else:
					self.bot.send(self.channel,"Game running.")
			else:
				self.bot.send(self.channel,"not enough players. %s" % (len(list(self.players.values()))))
		
		elif self.bettinground and message.nick == self.currentplayer:
			if message.text.startswith("%raise") and self.players[message.nick].hadturn == False:
				a = int(message.text.split(" ")[1])
				self.roundmaxbet += a
				self.players[message.nick].chips -= (self.roundmaxbet - self.players[message.nick].currentbet)
				self.pool += (self.roundmaxbet - self.players[message.nick].currentbet)
				self.players[message.nick].currentbet = self.roundmaxbet
				self.players[message.nick].hadturn = True
				self.bot.send(self.channel,"%s has \x02raised\x02 the bet by \x02%s\x02. The current bet for this round is \x02%s\x02. %s." % (message.nick,a,self.roundmaxbet,self.nextplayer()))
				if not self.bettinground: self.gamenext()
			if message.text.startswith("%call"):
				temp = self.roundmaxbet - self.players[message.nick].currentbet
				self.players[message.nick].chips -= temp
				self.pool += temp
				self.players[message.nick].currentbet = self.roundmaxbet
				self.players[message.nick].hadturn = True
				self.bot.send(self.channel,"%s has \x02called\x02 the raise of %s. The current bet for this round is \x02%s\x02. %s." % (message.nick,temp,self.roundmaxbet,self.nextplayer()))
				if not self.bettinground: self.gamenext()
			if message.text.startswith("%check") and self.players[message.nick].hadturn == False:
				if self.roundmaxbet == self.players[message.nick].currentbet:
					self.bot.send(self.channel,"%s has \x02checked\x02. The current bet for this round is \x02%s\x02. %s." % (message.nick,self.roundmaxbet,self.nextplayer()))
					self.players[message.nick].hadturn = True
					if not self.bettinground: self.gamenext()
			if message.text.startswith("%fold"):
				self.players[message.nick].folded = True
				if not self.checkfoldwin():
					self.bot.send(self.channel,"%s has \x02folded\x02. %s." % (message.nick,self.nextplayer()))
					if not self.bettinground: self.gamenext()
				else:
					self.bot.send(self.channel,"%s has \x02folded\x02. which means that:" % (message.nick))
					self.bot.notice(self.channel,"%s is the winner, adding %s to thier pile." % (self.findfirstplayer(),self.pool))
					self.players[self.findfirstplayer()].chips += self.pool
					x,y =   self.players.popitem(last=True)
					self.players[x] = y
					self.gamerunning = False
					handsdealt = False
					flop = False
					turn = False
					river = False
					showdown = False
					self.resetturns()
					self.resetbets()
					
				
				
	def nextplayer(self):
		playerstemp = list(self.players.values())[list(self.players.keys()).index(self.currentplayer)+1:] + list(self.players.values())[:list(self.players.keys()).index(self.currentplayer)]
		playertemp = None
		
		for player in playerstemp:
			if not player.folded and player.inround and (player.currentbet < self.roundmaxbet or not player.hadturn):
				playertemp = player
				break
			
			
		if not playertemp:
			self.bettinground = False
			self.currentplayer = self.findfirstplayer()
			self.resetbets()
			self.roundmaxbet = 0
			return "Betting round over"
		else:
			self.currentplayer = playertemp.name
			if self.players[self.currentplayer].currentbet < self.roundmaxbet:
				if self.players[self.currentplayer].hadturn:
					validmoves = "call or fold"
				else:
					validmoves = "call, raise or fold"
			else:
				validmoves = "check, raise or fold"
			return "It is now %s's turn. %s must " % (self.currentplayer,self.currentplayer) +validmoves
			
	def findfirstplayer(self):
		for player in list(self.players.values()):
			if not player.folded and player.inround:
				return player.name
				
	def resetturns(self):
		for player in list(self.players.values()):
			player.hadturn = False
			
	def resetbets(self):
		for player in list(self.players.values()):
			player.currentbet = 0
		
	def gamestart(self):
		for player in list(self.players.values()):
			player.inround = True
			player.folded = False
		self.gamerunning = True
		self.deck.returndeck()
		self.deck.shuffle()
		self.tablecards = []
		self.bot.do(self.channel,"shuffles the deck")
		if not self.currentplayer:
			self.currentplayer = list(self.players.values())[0].name
		self.players[self.currentplayer].chips -= self.minbet/2
		self.pool += self.minbet/2
		self.players[self.currentplayer].currentbet = self.minbet/2
		self.bot.send(self.channel,"%s has placed the small blind of \x02%s\x02 for this round." % (self.currentplayer,self.minbet/2))
		self.nextplayer()
		self.roundmaxbet = self.minbet
		self.players[self.currentplayer].chips -= self.minbet
		self.pool += self.minbet
		self.players[self.currentplayer].currentbet = self.minbet
		self.bot.send(self.channel,"%s has placed the big blind of \x02%s\x02 for this round. The cards will now be dealt." % (self.currentplayer,self.roundmaxbet))
		self.nextplayer()
		self.gamenext()
		
	def gamenext(self):
		if not self.handsdealt:
			self.bot.do(self.channel,"deals each player thier hand")
			for Player in list(self.players.values()):
				Player.hand = [self.deck.deal(),self.deck.deal()]
				self.bot.send(Player.name,"your hand is: " + " , ".join([str(card) for card in Player.hand]))
			self.bot.send(self.channel,"It is now %s's turn to bet. %s must either call, raise or fold." % (self.currentplayer,self.currentplayer))
			self.bettinground = True
			self.handsdealt = True
			
		elif not self.flop:
			self.bot.do(self.channel,"deals three cards to the table.")
			for i in range(3):
				self.tablecards.append(self.deck.deal())
			self.bot.notice(self.channel,"\x02The community cards are: " + " , ".join([str(card) for card in self.tablecards]))
			self.bot.send(self.channel,"It is now %s's turn to bet. %s must either check, raise or fold." % (self.currentplayer,self.currentplayer))
			self.resetturns()
			self.bettinground = True
			self.flop = True
		elif not self.turn:
			self.bot.do(self.channel,"deals another card to the table.")
			self.tablecards.append(self.deck.deal())
			self.bot.notice(self.channel,"\x02The community cards are now: " + " , ".join([str(card) for card in self.tablecards]))
			self.bot.send(self.channel,"It is now %s's turn to bet. %s must either check, raise or fold." % (self.currentplayer,self.currentplayer))
			self.resetturns()
			self.bettinground = True
			self.turn = True
		elif not self.river:
			self.bot.do(self.channel,"deals another card to the table.")
			self.tablecards.append(self.deck.deal())
			self.bot.notice(self.channel,"\x02The community cards are now: " + " , ".join([str(card) for card in self.tablecards]))
			self.bot.send(self.channel,"It is now %s's turn to bet. %s must either check, raise or fold." % (self.currentplayer,self.currentplayer))
			self.resetturns()
			self.bettinground = True
			self.river = True
		elif not self.showdown:
			for player in list(self.players.values()):
				self.gethandscore(player.hand,self.tablecards)
			
			
			self.bot.send(self.channel,"SHOWDOWN not done yet")
			self.bot.notice(self.channel,"%s is the winner, adding %s to thier pile." % (self.currentplayer,self.pool))
			self.players[self.currentplayer].chips += self.pool
			x,y =   self.players.popitem(last=True)
			self.players[x] = y
			self.gamerunning = False
			handsdealt = False
			flop = False
			turn = False
			river = False
			showdown = False
			self.resetturns()
			self.resetbets()
			
	def checkfoldwin(self):
		playertemp = []
		
		for player in list(self.players.values()):
			if not player.folded and player.inround:
				playertemp.append(player)
		
		print(playertemp)
		
		if len(playertemp) == 1:
			return True
		else:
			return False
			
			
			
		
		
		
	def gameend(self):
		self.bot.send(self.channel,"\x02The game has ended, your chips have been added to your stash.\x02")
		for player in list(self.players.values()):
			self.globalplayers[player.name].chips += player.chips
			self.bot.send(player.name,"You recieved %s chips into your stash. It now has %s chips in." % (player.chips,self.globalplayers[player.name].chips))
		
		handsdealt = False
		flop = False
		turn = False
		river = False
		showdown = False
		
	def gethandscore(self,hand,tablecards):
		temp = sorted(hand+tablecards)
		for subhand in itertools.combinations(temp, 5):
			temphand = PokerHand(subhand)
		
			
	

class plugin(defaultplugin.plugin):
				
	globalplayers = {}
	games = {}
	
				
	def onMessage(self,bot,message):
		if message.text.lower()=="%poker":
			if message.target not in list(self.games.keys()):
				self.games[message.target] = pokertable(bot,self.globalplayers,message.target,50)
				bot.send(message.target,"A poker table has been set up. players join with %join.")
			else:
				bot.send(message.target,"A table already exists in this channel. join with %join.")
			
		elif message.target in list(self.games.keys()):
			self.games[message.target].handlemessage(message)
			
				
	def onLoad(self,bot):
		if os.path.exists(os.path.join(bot.dir, "pokerplayers.save")):
			self.globalplayers = pickle.load( open( os.path.join(bot.dir, "pokerplayers.save"), "rb" ) )
			self.globalplayers = pickle.load( open( os.path.join(bot.dir, "pokerplayers.save"), "rb" ) )
		print("LOADED")

	def onUnload(self,bot):
		pickle.dump( self.globalplayers, open( os.path.join(bot.dir, "pokerplayers.save"), "wb" ) )
		
		print("UNLOADED")
		
