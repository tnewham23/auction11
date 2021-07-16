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
        self.minp = gameParameters["minimumBid"]
        self.ph2 = gameParameters["phase"] == "phase_2"
        self.players = [0]*gameParameters["numPlayers"]

        self.hasTrueValuels = []


    
    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value 
        self.trueValue = trueValue
        self.index = index
        self.players[index] = -1
        self.turn = 1
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        if self.players[whoMadeBid] == -1:
            return

        if howMuch % 13 == 1 and (howMuch % 5 == 1 or howMuch % 17 == 1):
            self.players[whoMadeBid] += 1
            if howMuch % 17 == 1:
                self.players[whoMadeBid] += 1
                self.hasTrueValuels.append(whoMadeBid)
        pass

    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        # On first turn establish who else is on team
        if self.turn == 1 or (self.turn == 2 and self.trueValue == -1):
            self.turn += 1
            bidValue = lastBid + 8
            # set bidvalue as remainder 1 modulo 13
            dif = 14 - (bidValue % 13)
            bidValue += dif
            if self.trueValue == -1:
                # Edge case where bidvalue would fit criteria for index with bid
                while bidValue % 5 != 1 and bidValue % 17 == 1:
                    bidValue += 13
            else:
                # set bidvalue as both remainder 13 and 23
                while bidValue % 17 != 1:
                    bidValue += 13
            self.engine.makeBid(bidValue)
            return
        
        if self.turn == 2 and self.trueValue > 0:
            # give value as difference from mean
            self.turn += 1
        
        pr=32/50
        if lastBid>self.mean/4:
            pr=16/100
        if lastBid>self.mean/2:
            pr=8/100
        if lastBid>self.mean*3/4:
            pr=2/50
        # Knows true value
        if self.trueValue > 0:
            # Bidding 50 won't cause the bidder to lost money
            knowledgePenalty = self.gameParameters["knowledgePenalty"]
            if lastBid + knowledgePenalty < self.trueValue:
                self.engine.makeBid(11+(knowledgePenalty-8)*self.engine.random.random())
            return
        if self.engine.random.random() < pr:
            if not self.ph2:
                self.engine.makeBid(self.engine.math.floor(
                    lastBid+(self.minp*(1+2*self.engine.random.random()))))
            else:
                self.engine.makeBid(lastBid + int((1+7 * self.linterp(self.NPCnormalY2,self.NPCnormalX, self.engine.random.random())) * self.minp))
                
        #if (lastBid < self.gameParameters["meanTrueValue"]):
            # But don't bid too high!
        #    self.engine.makeBid(lastBid+11)
        #pass

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        ownTeamList = []
        for index, value in enumerate(self.players):
            if index == self.index:
                continue
            if value > 1:
                ownTeamList.append(index)

        self.engine.reportTeams(ownTeamList, [], self.hasTrueValuels)
        return