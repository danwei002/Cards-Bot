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

from io import BytesIO
from discord.ext.commands import Bot, has_permissions, CheckFailure
from discord.ext.tasks import loop
from PIL import Image, ImageDraw, ImageColor, ImageFont
from discord.ext import tasks
from random import randrange
from discord.ext import commands

import main
from main import client, dumpData, loadData, gameDraw, showHand


def inGameCheck(ID):
    if not main.gameUnderway or not main.gameStarted:
        return False
    if ID not in main.players:
        return False
    return True


class Betting(commands.Cog):
    @commands.command(description="Raise your bet.",
                      brief="Raise your bet",
                      name='raise',
                      pass_context=True)
    async def __raise(self, ctx, raiseBy: float):
        loadData()
        ID = str(ctx.author.id)
        if not inGameCheck(ID):
            await ctx.send("Can't use this command now.")
            return
        if main.money[ID] < raiseBy:
            await ctx.send("Insufficient funds for such a bet.")
            return

        if raiseBy + main.bets[ID] <= main.maxBet:
            await ctx.send("Does not beat the current highest bet.")
            return
        main.bets[ID] += raiseBy
        main.money[ID] -= raiseBy
        main.maxBet = main.bets[ID]
        main.pot += raiseBy
        await ctx.send(ctx.author.mention + " you raised your bet to $" + str(main.bets[ID]))

        dumpData()

    @commands.command(description="Call to the most recent raise.",
                      brief="Call to the most recent raise",
                      name='call',
                      pass_context=True)
    async def __call(self, ctx):
        loadData()
        ID = str(ctx.author.id)
        if not inGameCheck(ID):
            await ctx.send("Can't use this command now.")
            return
        if main.money[ID] < main.maxBet:
            await ctx.send("Insufficient funds to match.")
            return
        if ID in main.bets:
            difference = main.maxBet - main.bets[ID]
            main.pot += difference
            main.bets[ID] = main.maxBet
            main.money[ID] -= difference
        else:
            main.pot += main.maxBet
            main.bets[ID] = main.maxBet
            main.money[ID] -= main.maxBet
        await ctx.send(ctx.author.mention + " you matched a bet of $" + str(main.maxBet))
        dumpData()

    @commands.command(description="Forfeit your bet and lay down your hand.",
                      brief="Forfeit your bet",
                      name='fold',
                      pass_context=True)
    async def __fold(self, ctx):
        loadData()
        ID = str(ctx.author.id)
        if not inGameCheck(ID):
            await ctx.send("Can't use this command now.")
            return

        main.players.remove(ID)
        del main.bets[ID]

        await ctx.send(ctx.author.mention + " you have folded.")

    @commands.command(description="View the money in the pot.",
                      brief="View the money in the pot",
                      name='pot',
                      pass_context=True)
    async def __pot(self, ctx):
        ID = str(ctx.author.id)
        if not inGameCheck(ID):
            await ctx.send("Can't use this command now.")
            return
        await ctx.send("The pot contains $" + str(main.pot))


def setup(bot):
    bot.add_cog(Betting(bot))
