# CARDS BOT
import random
import requests
import json
import asyncio
import discord.ext.commands
import discord
import re
import sys
import io

from CardEval import evaluateHand, handType
from sortingOrders import order, presOrder, pokerOrder, suitOrder
from io import BytesIO
from discord.ext.commands import Bot, has_permissions, CheckFailure
from discord.ext.tasks import loop
from PIL import Image, ImageDraw, ImageColor, ImageFont
from discord.ext import tasks
from random import randrange
from discord.ext import commands

class Game:
    def __init__(self, gameType, channel, ID):
        from main import deck
        self.gameUnderway = False
        self.ID = ID
        self.gameType = gameType
        self.gameEnded = False
        self.communityCards = []
        self.players = []
        self.bets = {}
        self.maxBet = 0
        self.pot = 0
        self.DECK = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
                     "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
                     "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
                     "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
                     "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
                     "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
                     "deck/10D.png", "deck/10C.png", "deck/10H.png",
                     "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png", "deck/QC.png",
                     "deck/QH.png", "deck/QS.png",
                     "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]
        self.channel = channel

    def checkEnded(self):
        return self.gameEnded

    def endGame(self):
        self.gameEnded = True

    def hasPlayer(self, user: discord.Member):
        if self.players.count(str(user.id)) > 0:
            return True
        return False

    def gameDraw(self, user: discord.Member, numCards: int):
        from main import loadData, dumpData
        if user.id == 716357127739801711:
            for i in range(0, numCards):
                selectCard = random.choice(self.DECK)
                self.communityCards.append(selectCard)
                self.DECK.remove(selectCard)
        else:
            loadData()
            import main
            if str(user.id) not in main.hands:
                main.hands.update({str(user.id): []})
            for i in range(0, numCards):

                selectCard = random.choice(self.DECK)
                main.hands[str(user.id)].append(selectCard)
                self.DECK.remove(selectCard)
            dumpData()

    async def startGame(self):
        from main import loadData, dumpData, client, showHand
        loadData()
        if self.gameType == "Texas Hold 'Em":
            loadData()
            output = "Game started. Ante is $50\nIn this game:\n"
            self.gameUnderway = True
            self.gameDraw(client.get_user(716357127739801711), 3)
            self.maxBet = 50
            for ID in self.players:
                import main
                user = client.get_user(int(ID))
                output += user.mention + "\n"
                self.gameDraw(user, 2)
                self.bets.update({ID: 50})
                main.money[ID] -= 50
                self.pot += 50

            await self.channel.send(output)
            await self.channel.send("**Community Cards**", file=showHand(client.get_user(716357127739801711), self.communityCards))
            dumpData()
