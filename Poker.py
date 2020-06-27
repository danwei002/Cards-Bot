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
from main import client, dumpData, loadData, gameDraw, showHand

def betCheck():
    needToMatch = []
    for ID, bet in main.bets.items():
        if bet < main.maxBet:
            needToMatch.append(ID)
    return needToMatch


class Poker(commands.Cog):
    @commands.command(description="Deal next card in Poker",
                      brief="Deal next card in Poker",
                      pass_context=True)
    async def next(self, ctx):
        if not main.gameStarted:
            await ctx.send("No game is active.")
            return

        if not main.gameUnderway:
            await ctx.send("The game is not yet underway.")
            return

        if main.players.count(str(ctx.author.id)) <= 0:
            await ctx.send("You are not in this game.")
            return

        if main.currentGame != "POKER":
            await ctx.send("This command is only for POKER games.")
            return

        needToMatch = betCheck()
        if len(needToMatch):
            await ctx.send("All players must either match the highest bet or fold.\nPlayers who still must take action:")
            for ID in needToMatch:
                await ctx.send(client.get_user(int(ID)).mention)
            return

        me = client.get_user(716357127739801711)
        gameDraw(me, 1)
        dumpData()
        await ctx.send("**CARD DEALT: " + str(len(main.hands[str(me.id)])) + "/5**", file=showHand(me))

    @commands.command(description="Show the community cards.",
                      brief="Show the community cards",
                      pass_context=True)
    async def cards(self, ctx):
        if not main.gameStarted:
            await ctx.send("No game is active.")
            return

        if not main.gameUnderway:
            await ctx.send("The game is not yet underway.")
            return

        if main.players.count(str(ctx.author.id)) <= 0:
            await ctx.send("You are not in this game.")
            return

        if main.currentGame != "POKER":
            await ctx.send("This command is only for POKER games.")
            return

        me = client.get_user(716357127739801711)
        await ctx.send(file=showHand(me))

def setup(bot):
    bot.add_cog(Poker(bot))
