# Work with Python 3.6
# USED IMPORTS
import random
from random import randrange
import asyncio
import discord
from discord.ext import commands
import discord.ext.commands
from main import *
from CardEval import num_pairs, get_pair, hasTriple

def keyByValue(value, d):
    for key, val in d.items():
        if val == value:
            return key

def convertToNumerical(cards):
    cardVals = []
    conversion = {'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15}
    for card in cards:
        if len(card) == 11:
            if card[5] == 'J' or card[5] == 'Q' or card[5] == 'K' or card[5] == 'A' or card[5] == '2':
                cardVals.append(conversion[card[5]])
            else:
                cardVals.append(int(card[5]))
        else:
            cardVals.append(10)

    return cardVals

def evaluatePlay(cards):
    noneValue = ("None", -1)
    if len(cards) > 5 or len(cards) == 0:
        return noneValue

    cards.sort()
    if len(cards) == 5:
        if cards[0] == cards[1] - 1 == cards[2] - 2 == cards[3] - 3 == cards[4] - 4:
            return "Straight", cards[4]

        occ = {}
        for card in cards:
            if card not in occ:
                occ.update({card: 1})
            else:
                occ[card] += 1

        sortedOcc = list(occ.values())
        sortedOcc.sort()
        if sortedOcc == [2, 3]:
            return "Full House", keyByValue(3, occ)
        elif sortedOcc == [1, 4]:
            return "Quad", keyByValue(4, occ)

        return noneValue

    if len(cards) == 4:
        if cards[0] == cards[1] == cards[2] == cards[3]:
            return "Quad", cards[0]
        return noneValue

    if len(cards) == 3:
        if cards[0] == cards[1] == cards[2]:
            return "Triple", cards[0]
        return noneValue

    if len(cards) == 2:
        if cards[0] == cards[1]:
            return "Pair", cards[0]
        return noneValue

    if len(cards) == 1:
        return "Single", cards[0]

class Pres(commands.Cog):
    @commands.command(description="Play cards by the index displayed underneath them.",
                      help="Play cards from your hand in a game of President. Specify which cards you wish to play using their indices displayed beneath them in your hand.\n "
                           "Indices must be non-negative integers and not outside the range of your hand.",
                      pass_context=True)
    async def play(self, ctx, *args: int):
        embed = discord.Embed(colour=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in any games."
            embed.set_footer(text="Use %join <game ID> to join an existing game.")
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        if not isinstance(GAME, President):
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "You are not in a President game."
            await ctx.send(embed=embed)
            return

        embed.set_thumbnail(url=President.imageUrl)
        embed.title = "President"
        embed.add_field(name="Game ID", value=str(GAME.ID))

        if not GAME.gameUnderway:
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        if ctx.author != GAME.currentPlayer:
            embed.description = "It is not your turn!"
            await ctx.send(embed=embed)
            return

        if len(args) > 5 or len(args) < 1:
            embed.description = "You have provided an invalid number of arguments!"
            await ctx.send(embed=embed)
            return

        cardsToPlay = []
        for arg in args:
            card = GAME.playerHands[str(ctx.author.id)][arg]
            cardsToPlay.append(card)

        file = None
        playerPlay = evaluatePlay(convertToNumerical(cardsToPlay))

        if playerPlay[1] == -1:
            embed.description = "That is an invalid card combo."
            await ctx.send(embed=embed)
            return

        if len(GAME.cardsToBeat) == 0:
            file = showHand(ctx.author, cardsToPlay)
            embed.set_image(url="attachment://hand.png")
        else:
            toBeatPlay = evaluatePlay(convertToNumerical(GAME.cardsToBeat))
            if playerPlay[0] == "Quad":
                if toBeatPlay[0] == "Quad" and playerPlay[1] <= toBeatPlay[1]:
                    embed.description = "That does not beat the current cards."
                    await ctx.send(embed=embed)
                    return
                else:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")
            elif playerPlay[0] != toBeatPlay[0]:
                embed.description = "That is an invalid card combo. You need to pass or play a " + toBeatPlay[0] + "."
                await ctx.send(embed=embed)
                return
            else:
                if playerPlay[1] <= toBeatPlay[1]:
                    embed.description = "That does not beat the current cards."
                    await ctx.send(embed=embed)
                    return
                else:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")

        GAME.cardsToBeat = cardsToPlay
        GAME.turnIndex += 1
        GAME.numPasses = 0

        for card in cardsToPlay:
            GAME.playerHands[str(ctx.author.id)].remove(card)

        embed.description = "Card(s) played."
        if len(GAME.playerHands[str(ctx.author.id)]) == 0:
            embed.description += "\n\nYou finished!"
            GAME.finished.append(str(ctx.author.id))
            GAME.activePlayers.remove(str(ctx.author.id))

        await ctx.send(file=file, embed=embed)
        await GAME.nextTurn()

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Command Error", description="Invalid arguments detected for command 'play'. Check %help play for more details.", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            from main import client
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            await ctx.send(embed=embed)

    @commands.command(description="Pass your turn.",
                      help="If you choose not to play a card, or cannot play a card in a game of President, use this command to pass.",
                      name="pass",
                      pass_context=True)
    async def __pass(self, ctx):
        embed = discord.Embed(colour=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in any games."
            embed.set_footer(text="Use %join <game ID> to join an existing game.")
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        if not isinstance(GAME, President):
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "You are not in a President game."
            await ctx.send(embed=embed)
            return

        embed.set_thumbnail(url=President.imageUrl)
        embed.title = "President"

        if not GAME.gameUnderway:
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        if ctx.author != GAME.currentPlayer:
            embed.description = "It is not your turn!"
            await ctx.send(embed=embed)
            return

        if len(GAME.cardsToBeat) == 0:
            embed.description = "You have a free turn, don't give it up!"
            await ctx.send(embed=embed)
            return

        embed.description = "You have passed."
        GAME.numPasses += 1
        GAME.turnIndex += 1
        await ctx.send(embed=embed)
        await GAME.nextTurn()

    @commands.command(description="Check what cards you need to beat.",
                      help="Check the most recently played cards that you need to beat, assuming you aren't the one who played them.",
                      pass_context=True)
    async def ctb(self, ctx):
        embed = discord.Embed(colour=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in any games."
            embed.set_footer(text="Use %join <game ID> to join an existing game.")
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        if not isinstance(GAME, President):
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "You are not in a President game."
            await ctx.send(embed=embed)
            return

        embed.set_thumbnail(url=President.imageUrl)
        embed.title = "President"

        if not GAME.gameUnderway:
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        from main import showHand
        file = showHand(ctx.author, GAME.cardsToBeat)
        embed.set_image(url="attachment://hand.png")
        embed.description = "Here are the cards to beat."
        embed.add_field(name="Game ID", value=str(GAME.ID))
        await ctx.send(file=file, embed=embed)

def setup(bot):
    bot.add_cog(Pres(bot))
