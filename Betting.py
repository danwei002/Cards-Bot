# CARDS BOT
from discord.ext import commands

import discord
import main
from main import loadEconomy, dumpEconomy, checkInGame, getGame, channelCheck

class Betting(commands.Cog):
    @commands.command(description="Raise your bet.",
                      brief="Raise your bet",
                      name='raise',
                      help="Raise your bet by a specified amount. Format for this command is %raise <amount>. Requires sufficient balance to use.",
                      pass_context=True)
    async def __raise(self, ctx, raiseBy: float = None):
        loadEconomy()
        ID = str(ctx.author.id)
        embed = discord.Embed(title="Bet Raise", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import client
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in a game."
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Game ID", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        embed.set_footer(text="Format is %raise <amount to raise by>.")
        embed.add_field(name="Your Balance", value="$" + str(main.money[ID]), inline=False)

        if GAME.playerStatus[ID] == "Fold":
            embed.description = "You are not participating in the current hand. Wait for the next one to start."
            await ctx.send(embed=embed)
            return

        if main.money[ID] < raiseBy:
            embed.description = "You do not have the funds to raise by $" + str(raiseBy) + "."
            await ctx.send(embed=embed)
            return

        if raiseBy + GAME.bets[ID] <= GAME.maxBet:
            embed.add_field(name="Current Highest Bet", value="$" + str(GAME.maxBet), inline=False)
            embed.description = "Does not beat the current highest bet."
            await ctx.send(embed=embed)
            return

        GAME.bets[ID] += raiseBy
        main.money[ID] -= raiseBy
        GAME.maxBet = GAME.bets[ID]
        GAME.pot += raiseBy
        dumpEconomy()

        embed.remove_field(1)
        embed.add_field(name="Your New Balance", value="$" + str(main.money[ID]), inline=False)
        embed.add_field(name="Current Highest Bet", value="$" + str(GAME.maxBet), inline=False)
        embed.add_field(name="Pot", value="$" + str(GAME.pot))
        embed.description = "You raised your bet to $" + str(GAME.bets[ID])

        await ctx.send(embed=embed)

    @__raise.error
    async def raise_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error", description="Invalid arguments detected for command 'raise'. Try %raise <raiseBy> or check %help raise for more details.", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            from main import client
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            await ctx.send(embed=embed)

    @commands.command(description="Call to the highest bet.",
                      brief="Call to the highest bet",
                      name='call',
                      help="Match the current highest bet. Format is %call. No parameters are needed. Requires sufficient balance to use.",
                      pass_context=True)
    async def __call(self, ctx):
        loadEconomy()
        ID = str(ctx.author.id)
        embed = discord.Embed(title="Bet Call", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import client
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in a game."
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Game ID", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        embed.set_footer(text="Format is %raise <amount to raise by>.")
        embed.add_field(name="Your Balance", value="$" + str(main.money[ID]), inline=False)

        if GAME.playerStatus[ID] == "Fold":
            embed.description = "You are not participating in the current hand. Wait for the next one to start."
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Current Highest Bet", value="$" + str(GAME.maxBet), inline=False)
        if str(ID) in GAME.bets:
            if GAME.bets[ID] == GAME.maxBet:
                embed.description = "Your bet already matches the highest bet."
                await ctx.send(embed=embed)
                return

        if main.money[ID] < GAME.maxBet:
            embed.description = "You do not have the funds to match the highest bet."
            await ctx.send(embed=embed)
            return

        if ID in GAME.bets:
            difference = GAME.maxBet - GAME.bets[ID]
            GAME.pot += difference
            GAME.bets[ID] = GAME.maxBet
            main.money[ID] -= difference
        else:
            GAME.pot += GAME.maxBet
            GAME.bets[ID] = GAME.maxBet
            main.money[ID] -= GAME.maxBet

        dumpEconomy()

        embed.set_field_at(1, name="Your New Balance", value = str(main.money[ID]), inline=False)
        embed.add_field(name="Pot", value="$" + str(GAME.pot))
        embed.description = "You matched the highest bet of $" + str(GAME.maxBet) + "."
        await ctx.send(embed=embed)

    @commands.command(description="Forfeit your bet and lay down your hand.",
                      brief="Forfeit your bet",
                      name='fold',
                      help="Fold and forfeit, taking no further part in the hand. You will lose any amount you already bet. Format is %fold. No parameters are needed.",
                      pass_context=True)
    async def __fold(self, ctx):
        loadEconomy()
        ID = str(ctx.author.id)
        embed = discord.Embed(title="Fold", color=0x00ff00)
        from main import client
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in a game."
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Game ID", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        GAME.playerStatus[ID] = "Fold"
        embed.description = "You have folded."
        await ctx.send(embed=embed)

    @commands.command(description="View the money in the pot.",
                      brief="View the money in the pot",
                      name='pot',
                      help="See how much money is currently available to be won in the pot. Format is %pot. No parameters are needed.",
                      pass_context=True)
    async def __pot(self, ctx):
        embed = discord.Embed(title="Pot", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import client
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in a game."
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Game ID", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        embed.description = "The pot currently contains $" + str(GAME.pot) + "."
        await ctx.send(embed=embed)

    @commands.command(description="Check the current highest bet.",
                      brief="Check the current highest bet",
                      name='highest',
                      help="Check what the current highest bet is. Format is %highest. No parameters are needed.",
                      pass_context=True)
    async def __highest(self, ctx):
        embed = discord.Embed(title="Highest Bet", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import client
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "You are not in a game."
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "You are not in the specified game's channel. Please go there."
            await ctx.send(embed=embed)
            return

        embed.add_field(name="Game ID", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "This game has not started."
            embed.set_footer(text="Use %start to start this game.")
            await ctx.send(embed=embed)
            return

        embed.description = "The current highest bet is $" + str(GAME.maxBet) + "."
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Betting(bot))
