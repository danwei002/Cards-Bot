# CARDS BOT
import random
import discord

from abc import abstractmethod
from CardEval import evaluateHand, handType

class Game:
    def __init__(self, channel, ID):
        self.gameUnderway = False
        self.channel = channel
        self.gameEnded = False
        self.ID = ID
        self.players = []
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
    def __init__(self, channel, ID):
        super().__init__(channel, ID)
        self.pot = 0
        self.bets = {}
        self.maxBet = 0
        self.communityCards = []

    def deal(self, user: discord.Member, numCards: int):
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

    async def gameLoop(self):
        if len(self.communityCards) == 5:
            self.endGame()

        if self.gameEnded:
            import main
            from main import loadData, dumpData, client, showHand
            loadData()
            await self.channel.send("Game " + str(self.ID) + " ended. Revealing all players' hands...")
            score = {}
            overallMax = 0
            for ID in self.players:
                user = client.get_user(int(ID))
                maxScore = 0
                for i in range(0, 5):
                    for j in range(i + 1, 5):
                        for k in range(j + 1, 5):
                            cardVals = [main.hands[str(user.id)][0], main.hands[str(user.id)][1], self.communityCards[i], self.communityCards[j], self.communityCards[k]]
                            maxScore = max(maxScore, evaluateHand(cardVals))

                score.update({maxScore: ID})
                overallMax = max(maxScore, overallMax)
                await self.channel.send("**" + user.name + " has a " + handType(maxScore) + ". Score of " + str(maxScore) + "**", file=showHand(user, main.hands[str(ID)]))
                del main.hands[str(ID)]

            await self.channel.send("The winner is " + client.get_user(int(score[overallMax])).mention + ", winning the pot of $" + str(self.pot))
            main.money[score[overallMax]] += self.pot
            dumpData()
            main.gameList.remove(self)

    async def startGame(self):
        from main import loadData, dumpData, client, showHand
        loadData()
        output = "Game started. Ante is $50\nIn this game:\n"
        self.gameUnderway = True
        self.deal(client.get_user(716357127739801711), 3)
        self.maxBet = 50
        for ID in self.players:
            import main
            user = client.get_user(int(ID))
            output += user.mention + "\n"
            self.deal(user, 2)
            self.bets.update({ID: 50})
            main.money[ID] -= 50
            self.pot += 50

        await self.channel.send(output)
        await self.channel.send("**Community Cards**",
                                file=showHand(client.get_user(716357127739801711), self.communityCards))
        dumpData()





