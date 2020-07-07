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


# Return the value of the cards in the pair if they are one, -1 if they are not
def isPair(cardVals):
    if len(cardVals) != 2:
        return -1

    if cardVals[0] == cardVals[1]:
        return cardVals[0]
    return -1

# Return the value of the cards in the triple if they are one, -1 if they are not
def isTriple(cardVals):
    if len(cardVals) != 3:
        return -1

    if cardVals[0] == cardVals[1] == cardVals[2]:
        return cardVals[0]
    return -1

# Return the value of the triple in a full house if it exists, -1 if there is no full house
def isFullHouse(cardVals):
    if len(cardVals) != 5:
        return -1

    if hasTriple(cardVals) and num_pairs(cardVals) == 4:
        value = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value]
        if len(cardVals) == 2:
            return value
        else:
            return cardVals[0]
    else:
        return -1

# Return the value of the quad if it exists, -1 if there is no quad
def isQuad(cardVals):
    if len(cardVals) != 4 and len(cardVals) != 5:
        return -1

    cardVals.sort()
    if cardVals[0] == cardVals[1] == cardVals[2] == cardVals[3] or (len(cardVals) == 5 and cardVals[1] == cardVals[2] == cardVals[3] == cardVals[4]):
        return cardVals[1]
    else:
        return -1

# Return the value of the highest card in the straight if it exists, -1 if it does not
def isStraight(cardVals):
    if len(cardVals) != 5:
        return -1

    cardVals.sort()
    if cardVals[0] == cardVals[1] - 1 == cardVals[2] - 2 == cardVals[3] - 3 == cardVals[4] - 4:
        return cardVals[4]
    else:
        return -1

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

        cardVals = convertToNumerical(cardsToPlay)
        toBeatVals = convertToNumerical(GAME.cardsToBeat)

        if len(toBeatVals) != 0 and len(cardVals) != len(toBeatVals):
            embed.description = "Invalid card selection."
            await ctx.send(embed=embed)
            return

        from main import showHand
        if len(cardsToPlay) == 1:
            if len(toBeatVals) == 0 or cardVals[0] > toBeatVals[0]:
                file = showHand(ctx.author, cardsToPlay)
                embed.set_image(url="attachment://hand.png")
                embed.description = "Card played."
                await ctx.send(file=file, embed=embed)
            elif cardVals[0] <= toBeatVals[0]:
                embed.description = "That card isn't high enough."
                await ctx.send(embed=embed)
                return
        elif len(cardsToPlay) == 2:
            pairVal = isPair(cardVals)
            if pairVal == -1:
                embed.description = "That's not a valid pair of cards to play!"
                await ctx.send(embed=embed)
                return

            if len(toBeatVals) == 0 or cardVals[0] > toBeatVals[0]:
                file = showHand(ctx.author, cardsToPlay)
                embed.set_image(url="attachment://hand.png")
                embed.description = "Cards played."
                await ctx.send(file=file, embed=embed)
            elif cardVals[0] <= toBeatVals[0]:
                embed.description = "That pair isn't high enough."
                await ctx.send(embed=embed)
                return
        elif len(cardsToPlay) == 3:
            tripleVal = isTriple(cardVals)
            if tripleVal == -1:
                embed.description = "That's not a valid triple to play!"
                await ctx.send(embed=embed)
                return

            if len(toBeatVals) == 0 or cardVals[0] > toBeatVals[0]:
                file = showHand(ctx.author, cardsToPlay)
                embed.set_image(url="attachment://hand.png")
                embed.description = "Cards played."
                await ctx.send(file=file, embed=embed)
            elif cardVals[0] <= toBeatVals[0]:
                embed.description = "That triple isn't high enough."
                await ctx.send(embed=embed)
                return
        elif len(cardsToPlay) == 4:
            quadVal = isQuad(cardVals)
            if quadVal == -1:
                embed.description = "That's not a valid quad to play!"
                await ctx.send(embed=embed)
                return

            if len(toBeatVals) == 0 or cardVals[0] > toBeatVals[0]:
                file = showHand(ctx.author, cardsToPlay)
                embed.set_image(url="attachment://hand.png")
                embed.description = "Cards played."
                await ctx.send(file=file, embed=embed)
            elif cardVals[0] <= toBeatVals[0]:
                embed.description = "That quad isn't high enough."
                await ctx.send(embed=embed)
                return
        elif len(cardsToPlay) == 5:
            fullHouseVal = isFullHouse(cardVals)
            straightVal = isStraight(cardVals)

            if fullHouseVal != -1:
                toBeatFHVal = isFullHouse(toBeatVals)
                if len(toBeatVals) == 0:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")
                    embed.description = "Cards played."
                    await ctx.send(file=file, embed=embed)
                elif toBeatFHVal == -1:
                    embed.description = "You can't play a full house on that!"
                    await ctx.send(embed=embed)
                    return
                elif fullHouseVal > toBeatFHVal:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")
                    embed.description = "Cards played."
                    await ctx.send(file=file, embed=embed)
                else:
                    embed.description = "That full house is not high enough."
                    await ctx.send(embed=embed)
                    return
            elif straightVal != -1:
                toBeatSVal = isStraight(toBeatVals)
                if len(toBeatVals) == 0:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")
                    embed.description = "Cards played."
                    await ctx.send(file=file, embed=embed)
                elif toBeatSVal == -1:
                    embed.description = "You cannot play a straight on that!"
                    await ctx.send(embed=embed)
                    return
                elif straightVal > toBeatSVal:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")
                    embed.description = "Cards played."
                    await ctx.send(file=file, embed=embed)
                else:
                    embed.description = "That straight is not high enough."
                    await ctx.send(embed=embed)
                    return
            else:
                quadVal = isQuad(cardVals)
                if quadVal == -1:
                    embed.description = "That's not a valid combo to play!"
                    await ctx.send(embed=embed)
                    return

                if len(toBeatVals) == 0 or cardVals[0] > toBeatVals[0]:
                    file = showHand(ctx.author, cardsToPlay)
                    embed.set_image(url="attachment://hand.png")
                    embed.description = "Cards played."
                    await ctx.send(file=file, embed=embed)
                elif quadVal <= isQuad(toBeatVals):
                    embed.description = "That quad isn't high enough."
                    await ctx.send(embed=embed)
                    return

        GAME.cardsToBeat = cardsToPlay
        GAME.turnIndex += 1
        GAME.numPasses = 0

        for card in cardsToPlay:
            GAME.playerHands[str(ctx.author.id)].remove(card)

        if len(GAME.playerHands[str(ctx.author.id)]) == 0:
            embed.description = "You finished!"
            GAME.finished.append(str(ctx.author.id))
            GAME.activePlayers.remove(str(ctx.author.id))
            await ctx.send(embed=embed)

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
