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
        self.hasTrueValue = -1
        self.players[index] = -1
        self.turn = 0
        
        self.round = 1
        self.count = 0
        
        self.game += 1
        self.shouldBid = True
        self.prevBid = 0
        self.nonNPC = []
        self.differenceObserved = False
        self.teamReports = {}
        self.teamReportCount = 0
        self.hasFakeTrueValue = -1
        
        if self.ph2:
            self.ownTeam = [self.index]
        
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        # PHASE 1
        if not self.ph2:
            if not (self.index in self.ownTeam):
                self.ownTeam.append(self.index)
            
            # print(self.turn)
            
            # In first two turns of auction recieve signals from non bots saying they're on same team
            if howMuch % 13 == 1 and self.round <= 2 and self.game == 1:
                self.players[whoMadeBid] += 1
                if self.players[whoMadeBid] == 2:
                    self.ownTeam.append(whoMadeBid)

            # First turn each auction recieve signal from bot with true value
            if howMuch % 17 == 1 and howMuch % 13 == 1 and self.round == 1:
                if not (whoMadeBid in self.ownTeam):
                    self.ownTeam.append(whoMadeBid)
                self.hasTrueValue = whoMadeBid
            
            # Receive true value from plauer with true value
            if self.round == 2 and whoMadeBid == self.hasTrueValue:
                self.sharedTrueValue = howMuch + (self.mean - self.stddev)
            
            # set to stop bidding if there's a larger non-true value player on same team
            if self.round >=3 and self.sharedTrueValue > 0 and self.shouldBid:
                if self.index < max(filter(lambda x : not x == self.hasTrueValue, self.ownTeam)):
                    self.shouldBid = False
            
            if not self.ph2:
                # Bid made is greater than what npc bot would make
                if self.prevBid and howMuch > (self.prevBid + self.minp + 2):
                    if whoMadeBid not in self.nonNPC and whoMadeBid not in self.ownTeam:
                        self.nonNPC.append(whoMadeBid)
        
        # PHASE 2
        elif self.ph2:
            # first two rounds, identify team members
            if howMuch % 13 == 1 and self.round <= 2:
                self.players[whoMadeBid] += 1
                if self.players[whoMadeBid] == 2:
                    self.ownTeam.append(whoMadeBid)
            
            # third round, start storing reports from team members
            if self.round >= 3 and not self.differenceObserved and whoMadeBid in self.ownTeam:

                # add report to dictionary holding players: [reported values]
                if not (whoMadeBid in self.teamReports.keys()):
                    self.teamReports[whoMadeBid] = [howMuch % 10]
                else:
                    self.teamReports[whoMadeBid].append(howMuch % 10)

                self.teamReportCount += 1
                
                # if a round of reporting has been done, deduce player 
                # with fake value if possible
                if self.teamReportCount != 0 and self.teamReportCount % 3 == 0:
                    
                    # compare, identify who has the true value
                    values = [self.teamReports[x][-1] for x in self.ownTeam]
                    fakeValue = min(values, key=values.count)

                    if values.count(fakeValue) < 3:

                        for player, report in self.teamReports.items():
                            if report[-1] == fakeValue:
                                self.hasFakeTrueValue = player

                        self.differenceObserved = True

            # if the true value has been broadcast, set it
            elif self.round >= 3 and self.differenceObserved and whoMadeBid in self.ownTeam:
                if whoMadeBid != self.hasFakeTrueValue:
                    self.sharedTrueValue = howMuch + (self.mean - self.stddev) - self.prevBid

            # if we know the true value, stop bidding
            if self.sharedTrueValue == self.trueValue:
                self.shouldBid = False
            

        # print(self.ph2)
        # print(self.ownTeam, self.index)

        self.prevBid = howMuch
        self.count += 1
        if self.count % 12 == 0:
            self.round += 1
    

    def onMyTurn(self,lastBid):
        # lastBid is the last bid that was made
        self.turn += 1
        if not self.shouldBid:
            return

        # PHASE 1: only act in round 1
        if not self.ph2:
            
            # game 1: we don't know which bots belong to which team
            if self.game == 1:
                
                # non-true value teammates established by bidding 1 mod 13 on turns 1,2
                if self.trueValue == -1 and self.turn <= 2:
                    # set bidvalue as remainder 1 modulo 13
                    bidValue = lastBid + 11
                    dif = 14 - (bidValue % 13)
                    bidValue += dif
                    
                    # correction in case of 1 mod 17 
                    # (would result in two reports for having the true value)
                    if bidValue % 17 == 1:
                        bidValue += 13
                    
                    print(self.index, bidValue)
                    self.engine.makeBid(bidValue)
                    return

                # true value teammate bids 1 mod 13, 1 mod 17 on turn 1, 
                #   then sends true value
                elif self.trueValue > 0:
                    
                    # bid 1 mod 13, 1 mod 17
                    if self.turn == 1:
                        bidValue = lastBid + 11
                        dif = 14 - (bidValue % 13)
                        bidValue += dif
                        while bidValue % 17 != 1:
                            bidValue += 13
                        
                        self.engine.makeBid(bidValue)
                        return

                    # send bid value
                    elif self.turn == 2:
                        # TODO: are we guaranteed this to be greater than the current bid?
                        bidValue = self.trueValue - (self.mean - self.stddev)
                        self.engine.makeBid(bidValue)
                        self.shouldBid = False
                        return


            #games following game 1
            else:
                # bot with true value must bid 1 mod 13, 1 mod 17 (others must not)
                #   then sends true value on turn 2
                if self.trueValue > 0:
                    if self.turn == 1:
                        bidValue = lastBid + 11
                        dif = 14 - (bidValue % 13)
                        bidValue += dif
                        while bidValue % 17 != 1:
                            bidValue += 13
                        
                        self.engine.makeBid(bidValue)
                        return
                    
                    elif self.turn == 2:
                        bidValue = self.trueValue - (self.mean - self.stddev)
                        self.engine.makeBid(bidValue)
                        self.shouldBid = False
                        return

                # if turn > 2 is team rep then fall to the case of bidding as NPC.
                # otherwise just bid +11.
                # TODO: (randomly in future maybe)
                elif self.trueValue == -1 and self.turn <= 2:
                    self.engine.makeBid(lastBid + 11)

        # PHASE 2
        elif self.ph2:
            # bid 1 mod 13 first two rounds to indicate team
            if self.turn <= 2:
                # set bidvalue as remainder 1 modulo 13
                bidValue = lastBid + 11
                dif = 14 - (bidValue % 13)
                bidValue += dif
        
                self.engine.makeBid(bidValue)
                return
        
            # have last digit of bid match the last digit of believed 'true value'
            elif not self.differenceObserved:
                bidValue = lastBid + 21
        
                # determine which digit to communicate (last, second last, etc)
                positionToCommunicateFromBack = self.turn - 3
                digitToCommunicate = int(str(self.trueValue)[-1 + positionToCommunicateFromBack])
        
                bidValue = bidValue - (bidValue % 10) + digitToCommunicate
                self.engine.makeBid(bidValue)
                return
        
            # communicate true value
            elif not self.sharedTrueValue and self.index != self.hasFakeTrueValue:
                # this could lead to problems
                bidValue = lastBid + (self.trueValue - (self.mean - self.stddev))
                self.engine.makeBid(bidValue)
                self.shouldBid = False
                return


        # Knows true value
        if self.sharedTrueValue > 0:
            if lastBid + self.minp < self.sharedTrueValue:
                value = self.engine.math.floor(
                    lastBid+(self.minp*(1+2*self.engine.random.random())))
                if value > self.sharedTrueValue:
                    self.engine.makeBid(min(self.sharedTrueValue, lastBid + 8))
                else:
                    self.engine.makeBid(value)
            return
        # if self.engine.random.random() < pr:
        #     if not self.ph2:
        #         self.engine.makeBid(self.engine.math.floor(
        #             lastBid+(self.minp*(1+2*self.engine.random.random()))))
        #     else:
        #         self.engine.makeBid(lastBid + int((1+7 * self.linterp(self.NPCnormalY2,self.NPCnormalX, self.engine.random.random())) * self.minp))
        return


    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        if self.game == 1:
            for player in self.ownTeam:
                if player in self.nonNPC:
                    self.nonNPC.remove(player)
        
        if self.ph2:
            if self.hasFakeTrueValue != -1:
                self.hasTrueValuels = [self.hasFakeTrueValue]
        else:
            if self.hasTrueValue != -1:
                self.hasTrueValuels = [self.hasTrueValue]
        
        self.engine.reportTeams(self.ownTeam, self.nonNPC, self.hasTrueValuels)
        return

if __name__ == "__main__":
    bot = CompetitorInstance()
    pass
