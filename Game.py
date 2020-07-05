# CARDS BOT
import random
import discord
import asyncio
import itertools

from abc import abstractmethod
from DBConnection import DBConnection
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
    gameName = None

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
    gameName = "Texas Hold 'Em"

    def __init__(self, channel, ID):
        super().__init__(channel, ID)
        self.pot = 0
        self.bets = {}
        self.maxBet = 0
        self.communityCards = []
        self.playerStatus = {}

    def deal(self, user: discord.Member, numCards: int):
        if user.id == 716357127739801711:
            for i in range(0, numCards):
                selectCard = random.choice(self.DECK)
                self.communityCards.append(selectCard)
                self.DECK.remove(selectCard)
        else:
            for i in range(0, numCards):
                selectCard = random.choice(self.DECK)
                self.playerHands[str(user.id)].append(selectCard)
                self.DECK.remove(selectCard)

    def updateStatus(self):
        for ID, bet in self.bets.items():
            if self.playerStatus[ID] == "Fold":
                continue
            if bet == self.maxBet:
                self.playerStatus[ID] = "Called"
            else:
                self.playerStatus[ID] = "Active"

    async def newHand(self):
        from main import client, showHand

        self.gameEnded = False
        self.playerHands.clear()

        self.DECK = DECK_CONST
        self.pot = 0
        self.communityCards.clear()
        self.deal(client.get_user(716357127739801711), 3)

        embed = discord.Embed(title="Texas Hold 'Em", description="Starting new hand. Ante is $50", colour=0x00ff00)
        embed.set_thumbnail(url=TexasHoldEm.imageUrl)
        embed.set_footer(text="Use %leave to leave this game.")
        file = showHand(client.get_user(716357127739801711), self.communityCards)
        embed.set_image(url="attachment://hand.png")

        playerList = ""
        for ID in self.players:
            self.playerHands.update({ID: []})
            self.playerStatus[ID] = "Active"
            userMoney = DBConnection.fetchUserData("userBalance", ID)
            if ID not in self.bets:
                self.bets.update({ID: 50})
            else:
                self.bets[ID] = 50
            if userMoney < 50:
                await self.channel.send(client.get_user(int(ID)).mention + " you cannot afford to play a new hand.")
                self.players.remove(ID)
                continue

            user = client.get_user(int(ID))
            playerList += user.name + "\n"
            self.maxBet = 50
            self.pot += 50
            self.deal(client.get_user(int(ID)), 2)

            userMoney -= 50
            DBConnection.updateUserBalance(ID, userMoney)

        embed.add_field(name="Players", value=playerList)
        embed.add_field(name="Pot", value="$" + str(self.pot))
        embed.add_field(name="Game ID", value=str(self.ID))
        embed.add_field(name="Community Cards", value="Cards Dealt: " + str(len(self.communityCards)), inline=False)

        await self.channel.send(file=file, embed=embed)

    async def gameLoop(self):
        self.updateStatus()
        if len(self.players) == 0 and self.gameUnderway:
            embed = discord.Embed(title="Texas Hold 'Em", description="No players left in game. This game will now terminate.", colour=0x00ff00)
            embed.add_field(name="Game ID", value=str(self.ID))
            embed.set_thumbnail(url=TexasHoldEm.imageUrl)
            await self.channel.send(embed=embed)
            import main
            main.gameList.remove(self)
            return

        if len(self.communityCards) == 5:
            self.endGame()

        if self.gameEnded:
            embed = discord.Embed(title="Texas Hold 'Em", colour=0x00ff00)
            embed.add_field(name="Game ID", value=str(self.ID))
            embed.set_thumbnail(url=TexasHoldEm.imageUrl)

            import main
            from main import client, showHand

            score = {}
            overallMax = 0
            embed.add_field(name="Combo", value="value")
            for ID in self.players:
                user = client.get_user(int(ID))
                embed.title = user.name + "'s Hand"

                if self.playerStatus[ID] == "Fold":
                    embed.description = "Folded"
                    embed.set_field_at(1, name="Combo", value="None")
                    await self.channel.send(embed=embed)
                    continue

                maxScore = 0
                cardChoices = [self.communityCards[0], self.communityCards[1], self.communityCards[2], self.communityCards[3], self.communityCards[4], self.playerHands[str(user.id)][0], self.playerHands[str(user.id)][1]]
                combos = list(itertools.combinations(cardChoices, 5))
                for combo in combos:
                    maxScore = max(maxScore, evaluateHand(combo))

                score.update({maxScore: ID})
                overallMax = max(maxScore, overallMax)
                file = showHand(user, self.playerHands[ID])
                embed.set_image(url="attachment://hand.png")
                embed.set_field_at(1, name="Combo", value=handType(maxScore))
                await self.channel.send(file=file, embed=embed)

            winners = []
            for userScore, userID in score.items():
                if userScore == overallMax:
                    print(client.get_user(int(userID)).name)
                    winners.append(userID)

            if len(winners) == 1:
                winner = client.get_user(int(score[overallMax]))

                embed.title = "Texas Hold 'Em"
                embed.description = "The winner is " + winner.name + ", winning the pot of $" + str(self.pot) + ".\n\nStart next hand? Thumps up for yes, thumbs down for no."
                embed.set_thumbnail(url=winner.avatar_url)
                embed.set_footer(text="Use %leave to leave this game.")

                userMoney = DBConnection.fetchUserData("userBalance", score[overallMax])
                userMoney += self.pot
                DBConnection.updateUserBalance(score[overallMax], userMoney)
            else:
                payout = self.pot / len(winners)
                embed.title = "Texas Hold 'Em"
                desc = "The winners are "
                for winnerID in winners:
                    winner = client.get_user(int(winnerID))
                    desc += winner.name + " "
                    userMoney = DBConnection.fetchUserData("userBalance", winnerID)
                    userMoney += payout
                    DBConnection.updateUserBalance(winnerID, userMoney)

                desc += ", splitting the pot of $" + str(self.pot) + ".\n\nStart next hand? Thumbs up for yes, thumbs down for no."
                embed.description = desc
                embed.set_thumbnail(url=TexasHoldEm.imageUrl)
                embed.set_footer(text="Use %leave to leave this game.")

            confirmEmoji = '👍'
            quitEmoji = '👎'

            embed.remove_field(0)
            embed.remove_field(0)
            msg = await self.channel.send(embed=embed)
            embed.set_thumbnail(url=TexasHoldEm.imageUrl)

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
                embed.description = "Nobody chose in time. Game terminated."
                embed.add_field(name="Game ID", value=str(self.ID))
                await self.channel.send(embed=embed)

                import main
                main.gameList.remove(self)
                return
            else:
                if str(rxn[0].emoji) == confirmEmoji:
                    await self.newHand()
                elif str(rxn[0].emoji) == quitEmoji:
                    embed.description = "Game terminated."
                    embed.add_field(name="Game ID", value=str(self.ID))
                    await self.channel.send(embed=embed)

                    import main
                    main.gameList.remove(self)
                    return

    async def startGame(self):
        self.gameUnderway = True
        await self.newHand()
