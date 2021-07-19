class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        # line i added to see if git is working
        pass

    def linterp(self, x,y,x1):
        for i,xn in enumerate(x):
            if x1<xn:
                if (i==0):
                    return y[0]
                else:
                    return y[i-1] + (y[i]-y[i-1]) * (x1-x[i-1]) / (xn - x[i-1])
        return y[len(y)-1]
    
    def onGameStart(self, engine, gameParameters):
        # engine: an instance of the game engine with functions as outlined in the documentation.
        self.engine=engine
        self.NPCnormalX = list(map(lambda x: x/50, range(0,214)))
        NPCnormalY = list(map(lambda x: (self.engine.math.e **(-x**2/2))/self.engine.math.sqrt(2*self.engine.math.pi), self.NPCnormalX))
        _sum=0
        NPCnormalY2=[]
        for y in NPCnormalY:
            NPCnormalY2.append(_sum)
            _sum+=y
        self.NPCnormalY2 = list(map(lambda x: x/_sum, NPCnormalY2))
        # gameParameters: A dictionary containing a variety of game parameters
        self.gameParameters = gameParameters
        self.mean = gameParameters["meanTrueValue"]
        self.stddev = gameParameters["stddevTrueValue"]
        self.minp = gameParameters["minimumBid"]
        self.ph2 = gameParameters["phase"] == "phase_2"

        self.game = 0
        self.ownTeam = []


    
    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value 
        self.trueValue = trueValue
        self.sharedTrueValue = 0
        self.index = index
        self.players = [0]*self.gameParameters["numPlayers"]
        self.hasTrueValuels = []
        self.players[index] = -1
        self.turn = 0
        self.game += 1
        self.shouldBid = True
        self.prevBid = 0
        self.nonNPC = []
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        # person who made bid is the bot itself
        if self.players[whoMadeBid] == -1:
            return

        if not self.ph2:
            # Bid made is greater than what npc bot would make
            if self.prevBid and howMuch > (self.prevBid + self.minp + 2):
                if whoMadeBid not in self.nonNPC:
                    self.nonNPC.append(whoMadeBid)

        # In first two turns of auction recieve signals from non bots saying they're on same team
        if howMuch % 13 == 1 and self.turn < 3 and self.game == 1: # and (howMuch % 5 == 1 or howMuch % 17 == 1):
            self.players[whoMadeBid] += 1
            if self.players[whoMadeBid] == 2:
                self.ownTeam.append(whoMadeBid)

        # First turn each auction recieve signal from bot with true value (if they have it)
        if howMuch % 17 == 1 and howMuch % 13 == 1 and self.turn < 2:
            self.players[whoMadeBid] += 1
            if self.players[whoMadeBid] == 2:
                self.ownTeam.append(whoMadeBid)
            self.hasTrueValuels.append(whoMadeBid)
        
        # Receive true value from plauer with true value
        if self.turn < 3 and self.hasTrueValuels and whoMadeBid == self.hasTrueValuels[0]:
            self.sharedTrueValue = howMuch + (self.mean - self.stddev)
            if len(self.ownTeam) > 1:
                # Only continue bidding with bot that has largest index and wasn't given the true value
                if self.ownTeam[0] == whoMadeBid:
                    if self.ownTeam[1] < self.index:
                        self.shouldBid = False
                else:
                    if self.ownTeam[0] < self.index:
                        self.shouldBid = False
    

    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        self.turn += 1
        if not self.shouldBid:
            return
        # On first turn establish who else is on team
        if (self.turn == 1 and (self.game == 1 or self.trueValue > 0)) or (self.turn == 2 and self.trueValue == -1):
            bidValue = lastBid + 11
            # set bidvalue as remainder 1 modulo 13
            dif = 14 - (bidValue % 13)
            bidValue += dif
            if self.trueValue == -1:
                # Edge case where bidvalue would fit criteria for index with bid
                if bidValue % 17 == 1:
                    # bidValue % 5 != 1 and
                    bidValue += 13
            else:
                # set bidvalue as both remainder 13 and 23
                while bidValue % 17 != 1:
                    bidValue += 13
            self.engine.makeBid(bidValue)
            return
        
        
        if self.turn == 2 and self.trueValue > 0:
            # give value as difference from mean
            bidValue = self.trueValue - (self.mean - self.stddev)
            self.engine.makeBid(bidValue)
            self.shouldBid = False
            return
        
        pr=32/50
        if lastBid>self.mean/4:
            pr=16/100
        if lastBid>self.mean*3/4:
            pr=2/50
        # Knows true value
        if self.sharedTrueValue > 0 and self.trueValue < 0:
            # Bidding 50 won't cause the bidder to lost money
            knowledgePenalty = self.gameParameters["knowledgePenalty"]
            if lastBid + knowledgePenalty - self.minp < self.sharedTrueValue:
                self.engine.makeBid(self.minp(1+int(2*self.engine.random.random()) ) )
            return
        if self.engine.random.random() < pr:
            if not self.ph2:
                self.engine.makeBid(self.engine.math.floor(
                    lastBid+(self.minp*(1+2*self.engine.random.random()))))
            else:
                self.engine.makeBid(lastBid + int((1+7 * self.linterp(self.NPCnormalY2,self.NPCnormalX, self.engine.random.random())) * self.minp))
        return
        #if (lastBid < self.gameParameters["meanTrueValue"]):
            # But don't bid too high!
        #    self.engine.makeBid(lastBid+11)
        #pass

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.engine.reportTeams(self.ownTeam, self.nonNPC, self.hasTrueValuels)
        return

if __name__ == "__main__":
    bot = CompetitorInstance()
    pass