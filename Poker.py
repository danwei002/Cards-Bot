# Work with Python 3.6
# USED IMPORTS
import random
from random import randrange
import asyncio
import discord
from discord.ext import commands
import discord.ext.commands
from discord.ext.commands import Bot, has_permissions, CheckFailure
from discord.ext import tasks
import json
import sys
import io
from timeit import default_timer as timer
from PIL import Image, ImageDraw, ImageColor
import main
from main import *

def betCheck(GAME):
    needToMatch = []
    for player, status in GAME.playerStatus.items():
        if status == "Active":
            needToMatch.append(player)
    return needToMatch


class Poker(commands.Cog):
    @commands.command(description="Deal next card in Poker",
                      brief="Deal next card in Poker",
                      pass_context=True)
    async def next(self, ctx):
        if not checkInGame(ctx.author):
            await ctx.send("Cannot use this command now.")
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            await ctx.send("You are not in the specified game's channel. Please go there.")
            return

        if not GAME.gameUnderway:
            await ctx.send("This game is not yet underway.")
            return

        if not isinstance(GAME, TexasHoldEm):
            await ctx.send("This command is only for Texas Hold 'Em")
            return

        if GAME.playerStatus[str(ctx.author.id)] == "Fold":
            await ctx.send(ctx.author.mention + " you are not participating in this hand, please wait for the next hand to start.")
            return

        needToMatch = betCheck(GAME)
        if len(needToMatch):
            await ctx.send("All players must either match the highest bet or fold.\nPlayers who still must take action:")
            for ID in needToMatch:
                await ctx.send(client.get_user(int(ID)).mention)
            return

        me = client.get_user(716357127739801711)
        GAME.deal(me, 1)
        dumpData()
        await ctx.send("**CARD DEALT**", file=showHand(me, GAME.communityCards))

    @commands.command(description="Show the community cards.",
                      brief="Show the community cards",
                      pass_context=True)
    async def cards(self, ctx):
        if not checkInGame(ctx.author):
            await ctx.send("Cannot use this command now.")
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            await ctx.send("You are not in the specified game's channel. Please go there.")
            return

        if not GAME.gameUnderway:
            await ctx.send("This game is not yet underway.")
            return

        if not isinstance(GAME, TexasHoldEm):
            await ctx.send("This command is only for Texas Hold 'Em")
            return

        me = client.get_user(716357127739801711)
        await ctx.send(file=showHand(me, GAME.communityCards))

def setup(bot):
    bot.add_cog(Poker(bot))
