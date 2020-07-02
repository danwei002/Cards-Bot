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
    @commands.command(description="Deal next card in Texas Hold 'Em.",
                      brief="Deal next card in Texas Hold 'Em",
                      help="Deal the next community card in a game of Texas Hold 'Em. You must be participating in a hand of Texas Hold 'Em to use this command.",
                      pass_context=True)
    async def next(self, ctx):
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

        if not isinstance(GAME, TexasHoldEm):
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "You are not in a Texas Hold 'Em game."
            await ctx.send(embed=embed)
            return

        embed.set_thumbnail(url=TexasHoldEm.imageUrl)
        embed.title = "Texas Hold 'Em"
        if not GAME.gameUnderway:
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        if GAME.playerStatus[str(ctx.author.id)] == "Fold":
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "You are not participating in this hand. Wait for the next hand to start."
            await ctx.send(embed=embed)
            return

        embed.set_author(name="", icon_url="")
        embed.set_footer(text="Use %leave to leave this game.")
        needToMatch = betCheck(GAME)
        me = client.get_user(716357127739801711)
        file = showHand(ctx.author, GAME.communityCards)
        embed.set_image(url="attachment://hand.png")
        if len(needToMatch):
            embed.description = "Not all players have matched the highest bet or folded."
            playersToMatch = ""
            for ID in needToMatch:
                user = client.get_user(int(ID))
                playersToMatch += user.name + "\n"

            embed.add_field(name="Need to Call/Fold", value=playersToMatch)
            embed.add_field(name="Pot", value="$" + str(GAME.pot))
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.add_field(name="Community Cards", value="Cards Dealt: " + str(len(GAME.communityCards)), inline=False)
            await ctx.send(file=file, embed=embed)
            return

        GAME.deal(me, 1)
        file = showHand(ctx.author, GAME.communityCards)
        embed.set_image(url="attachment://hand.png")
        playerList = ""
        for playerID in GAME.players:
            user = client.get_user(int(playerID))
            playerList += user.name + "\n"

        embed.description = "Next card dealt."
        embed.add_field(name="Players", value=playerList)
        embed.add_field(name="Pot", value="$" + str(GAME.pot))
        embed.add_field(name="Game ID", value=str(GAME.ID))
        embed.add_field(name="Community Cards", value="Cards Dealt: " + str(len(GAME.communityCards)), inline=False)
        await ctx.send(file=file, embed=embed)

    @commands.command(description="Show the community cards.",
                      brief="Show the community cards",
                      help="Show the current dealt community cards for a game of Texas Hold 'Em. You must be in a game of Texas Hold 'Em to use this command.",
                      pass_context=True)
    async def cards(self, ctx):
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

        if not isinstance(GAME, TexasHoldEm):
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "You are not in a Texas Hold 'Em game."
            await ctx.send(embed=embed)
            return

        embed.set_thumbnail(url=TexasHoldEm.imageUrl)
        embed.title = "Texas Hold 'Em"
        if not GAME.gameUnderway:
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        embed.set_author(name="", icon_url="")
        file = showHand(ctx.author, GAME.communityCards)
        embed.set_image(url="attachment://hand.png")
        playerList = ""
        for playerID in GAME.players:
            user = client.get_user(int(playerID))
            playerList += user.name + "\n"
        embed.add_field(name="Players", value=playerList)
        embed.add_field(name="Pot", value="$" + str(GAME.pot))
        embed.add_field(name="Game ID", value=str(GAME.ID))
        embed.add_field(name="Community Cards", value="Cards Dealt: " + str(len(GAME.communityCards)), inline=False)
        await ctx.send(file=file, embed=embed)

def setup(bot):
    bot.add_cog(Poker(bot))
