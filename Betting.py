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

class Betting(commands.Cog):
    @commands.command(description="Raise your bet.",
                      brief="Raise your bet",
                      name='raise',
                      pass_context=True)
    async def __raise(self, ctx):
        a = 1

    @commands.command(description="Call to the most recent raise.",
                      brief="Call to the most recent raise",
                      name='call',
                      pass_context=True)
    async def __call(self, ctx):
        a = 1

    @commands.command(description="Forfeit your bet and lay down your hand.",
                      brief="Forfeit your bet",
                      name='fold',
                      pass_context=True)
    async def __fold(self, ctx):
        a = 1


def setup(bot):
    bot.add_cog(Betting(bot))
