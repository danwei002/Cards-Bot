# CARDS BOT
from discord.ext import commands

import main
from main import loadData, dumpData, checkInGame, getGame, channelCheck

class Betting(commands.Cog):
    @commands.command(description="Raise your bet.",
                      brief="Raise your bet",
                      name='raise',
                      pass_context=True)
    async def __raise(self, ctx, raiseBy: float):
        loadData()
        ID = str(ctx.author.id)
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

        if main.money[ID] < raiseBy:
            await ctx.send("Insufficient funds for such a bet.")
            return

        if raiseBy + GAME.bets[ID] <= GAME.maxBet:
            await ctx.send("Does not beat the current highest bet.")
            return

        GAME.bets[ID] += raiseBy
        main.money[ID] -= raiseBy
        GAME.maxBet = GAME.bets[ID]
        GAME.pot += raiseBy
        await ctx.send(ctx.author.mention + " you raised your bet to $" + str(GAME.bets[ID]))

        dumpData()

    @__raise.error
    async def raise_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid arguments detected for command 'raise'. Try %raise <raiseBy>.")

    @commands.command(description="Call to the highest bet.",
                      brief="Call to the highest bet",
                      name='call',
                      pass_context=True)
    async def __call(self, ctx):
        loadData()
        ID = str(ctx.author.id)
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

        if str(ID) in GAME.bets:
            if GAME.bets[ID] == GAME.maxBet:
                await ctx.send("You are already matching the highest bet.")
                return

        if main.money[ID] < GAME.maxBet:
            await ctx.send("Insufficient funds to match.")
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
        await ctx.send(ctx.author.mention + " you matched a bet of $" + str(GAME.maxBet))
        dumpData()

    @commands.command(description="Forfeit your bet and lay down your hand.",
                      brief="Forfeit your bet",
                      name='fold',
                      pass_context=True)
    async def __fold(self, ctx):
        loadData()
        ID = str(ctx.author.id)
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

        GAME.players.remove(ID)
        del GAME.bets[ID]

        await ctx.send(ctx.author.mention + " you have folded.")

    @commands.command(description="View the money in the pot.",
                      brief="View the money in the pot",
                      name='pot',
                      pass_context=True)
    async def __pot(self, ctx):
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
        await ctx.send(ctx.author.mention + " the pot contains $" + str(GAME.pot))

    @commands.command(description="Check the current highest bet.",
                      brief="Check the current highest bet",
                      name='highest',
                      pass_context=True)
    async def __highest(self, ctx):
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
        await ctx.send(ctx.author.mention + " the current highest bet is $" + str(GAME.maxBet))

def setup(bot):
    bot.add_cog(Betting(bot))
