# CARDS BOT
import random
import discord
import asyncio

from abc import abstractmethod
from CardEval import evaluateHand, handType

DECK_CONST = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
              "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
              "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
              "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
              "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
              "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
              "deck/10D.png", "deck/10C.png", "deck/10H.png",
              "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png", "deck/QC.png",
              "deck/QH.png", "deck/QS.png",
              "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]

class Game:
    imageUrl = None

    def __init__(self, channel, ID):
        self.gameUnderway = False
        self.channel = channel
        self.gameEnded = False
        self.ID = ID
        self.players = []
        self.DECK = DECK_CONST
        self.playerHands = {}

    def checkEnded(self):
        return self.gameEnded

    def endGame(self):
        self.gameEnded = True

    def hasPlayer(self, user: discord.Member):
        if self.players.count(str(user.id)) > 0:
            return True
        return False

    @abstractmethod
    def deal(self, user: discord.Member, numCards: int):
        return

    @abstractmethod
    async def startGame(self):
        return

    @abstractmethod
    async def gameLoop(self):
        return


class TexasHoldEm(Game):
    imageUrl = "https://i.imgur.com/1DDTG0z.png"

    def __init__(self, channel, ID):
        super().__init__(channel, ID)
        self.pot = 0
        self.bets = {}
        self.maxBet = 0
        self.communityCards = []
        self.playerStatus = {}

    def deal(self, user: discord.Member, numCards: int):
        from main import loadHands, dumpHands
        if user.id == 716357127739801711:
            for i in range(0, numCards):
                selectCard = random.choice(self.DECK)
                self.communityCards.append(selectCard)
                self.DECK.remove(selectCard)
        else:
            loadHands()
            import main

            for i in range(0, numCards):
                selectCard = random.choice(self.DECK)
                self.playerHands[str(user.id)].append(selectCard)
                self.DECK.remove(selectCard)
            dumpHands()

    def updateStatus(self):
        for ID, bet in self.bets.items():
            if self.playerStatus[ID] == "Fold":
                continue
            if bet == self.maxBet:
                self.playerStatus[ID] = "Called"
            else:
                self.playerStatus[ID] = "Active"

    async def newHand(self):
        from main import loadData, loadHands, dumpEconomy, dumpHands, client, showHand
        import main
        self.gameEnded = False
        self.playerHands.clear()
        loadData()
        self.DECK = DECK_CONST
        self.pot = 0
        self.communityCards.clear()
        self.deal(client.get_user(716357127739801711), 3)
        await self.channel.send(
            "**------------------------------**\n**Starting new hand.**\n**------------------------------**\n")
        await self.channel.send("**Community Cards**",
                                file=showHand(client.get_user(716357127739801711), self.communityCards))
        for ID in self.players:
            self.playerHands.update({ID: []})
            self.playerStatus[ID] = "Active"
            if ID not in self.bets:
                self.bets.update({ID: 50})
            else:
                self.bets[ID] = 50
            if main.money[ID] < 50:
                await self.channel.send(client.get_user(int(ID)).mention + " you cannot afford to play a new hand.")
                self.players.remove(ID)

            self.maxBet = 50
            self.pot += 50
            self.deal(client.get_user(int(ID)), 2)
            main.money[ID] -= 50
            dumpEconomy()

    async def gameLoop(self):
        self.updateStatus()

        if len(self.players) == 0 and self.gameUnderway:
            await self.channel.send("No players left in game " + str(self.ID) + ". This game will now terminate.")
            import main
            main.gameList.remove(self)
            return

        if len(self.communityCards) == 5:
            self.endGame()

        if self.gameEnded:
            import main
            from main import loadData, dumpData, client, showHand
            loadData()
            await self.channel.send("Round finished. Revealing all players' hands...")
            score = {}
            overallMax = 0
            for ID in self.players:
                user = client.get_user(int(ID))
                maxScore = 0
                for i in range(0, 5):
                    for j in range(i + 1, 5):
                        for k in range(j + 1, 5):
                            cardVals = [self.playerHands[str(user.id)][0], self.playerHands[str(user.id)][1], self.communityCards[i], self.communityCards[j], self.communityCards[k]]
                            maxScore = max(maxScore, evaluateHand(cardVals))

                score.update({maxScore: ID})
                overallMax = max(maxScore, overallMax)
                await self.channel.send("**" + user.name + " has combo: " + handType(maxScore) + ".**", file=showHand(user, self.playerHands[ID]))

            await self.channel.send("The winner is " + client.get_user(int(score[overallMax])).mention + ", winning the pot of $" + str(self.pot))
            main.money[score[overallMax]] += self.pot
            dumpData()

            confirmEmoji = '👍'
            quitEmoji = '👎'
            msg = await self.channel.send("**Start next hand? Thumps up for yes, thumps down for no.**")
            rxn = None
            await msg.add_reaction(confirmEmoji)
            await msg.add_reaction(quitEmoji)

            def check(reaction, user):
                global rxn
                rxn = reaction
                return self.players.count(str(user.id)) > 0 and not user.bot

            try:
                rxn = await client.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await self.channel.send("Nobody chose in time. Game " + str(ID) + " terminated.")
                import main
                main.gameList.remove(self)
                return
            else:
                if str(rxn[0].emoji) == confirmEmoji:
                    await self.newHand()
                elif str(rxn[0].emoji) == quitEmoji:
                    await self.channel.send("Game " + str(self.ID) + " terminated.")
                    import main
                    main.gameList.remove(self)
                    return

    async def startGame(self):
        output = "Game started. Ante is $50\nIn this game:\n"
        self.gameUnderway = True
        await self.channel.send(output)
        await self.newHand()