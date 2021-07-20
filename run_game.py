from gameEngine import GameEngine, NPCRandomBot
import importlib

# List your bots here
botsToRun = {
    "examples.randomBidder":3,
    "examples.randomAccuser":3,
    "examples.randomSwapper":3,
    "NPC": 3
}

engine = GameEngine()

for b in botsToRun:
    for i in range(botsToRun[b]):
        if b=="NPC":
            engine.registerBot(NPCRandomBot(),team="NPC")
        else:
            botClass = importlib.import_module(b)
            engine.registerBot(botClass.CompetitorInstance(),team=b)
engine.runGame()