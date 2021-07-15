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


    
    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value 
        self.trueValue = trueValue
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was
        pass

    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        pr=32/50
        if lastBid>self.mean/4:
            pr=16/100
        if lastBid>self.mean*3/4:
            pr=2/50
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
        pass