# Work with Python 3.6
# USED IMPORTS
from discord.ext import commands
import discord.ext.commands
from discord.ext.commands import Bot, has_permissions, CheckFailure
import main
from main import client, dumpData, loadData, showHand

class Economy(commands.Cog):
    @commands.command(description="Check user balance.",
                      brief="Check user balance",
                      help="Check a user's balance. Mention a user to check their balance, or none to check your own. Format is %bal <mention user/none>.",
                      pass_context=True)
    async def bal(self, ctx, user: discord.Member = None):
        loadData()
        if user is None:
            user = ctx.author

        if str(user.id) not in main.money:
            main.money.update({str(user.id): 10000})
            dumpData()
        await ctx.send(user.name + " has $" + str(main.money[str(user.id)]))

    @bal.error
    async def bal_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user provided.")

    @commands.command(description="Set money for user. Requires administrator permissions.",
                      brief="Set money for user",
                      help="Set the balance of a user to a specified value. Requires administrator permissions for use. Mention a user to"
                           " set their balance. Format is %setbal <mention user> <balance amount>.",
                      pass_context=True)
    @has_permissions(administrator=True)
    async def setbal(self, ctx, user: discord.Member = None, amount: float = None):
        loadData()
        if user is None:
            user = ctx.author

        if amount is None:
            await ctx.send("No amount detected.")
            return

        if str(user.id) not in main.money:
            main.money.update({str(user.id): amount})
        else:
            main.money[str(user.id)] = amount

        await ctx.send("Money set.")
        dumpData()

    @setbal.error
    async def setbal_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid arguments detected.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")

    @commands.command(description="Pay a user.",
                      brief="Pay a user",
                      help="Pay a user from your own balance. You must have sufficient funds to pay the value you specified. Mention"
                           " the user who you'd like to pay. Format is %pay <mention user> <payment amount>.",
                      pass_context=True)
    async def pay(self, ctx, user: discord.Member = None, amount: float = None):
        loadData()
        if user is None:
            await ctx.send("No recipient provided.")
            return

        if amount is None:
            await ctx.send("No amount detected.")
            return

        if amount <= 0:
            await ctx.send("That is not a valid amount to pay.")
            return

        if str(user.id) not in main.money:
            main.money.update({str(user.id): 10000})

        if str(ctx.author.id) not in main.money:
            main.money.update({str(ctx.author.id): 10000})

        if amount > main.money[str(ctx.author.id)]:
            await ctx.send("You do not have sufficient funds to make this payment.")
            return

        main.money[str(ctx.author.id)] -= amount
        main.money[str(user.id)] += amount

        await ctx.send(ctx.author.mention + " you paid $" + str(amount) + " to " + user.name + ".")
        dumpData()

    @pay.error
    async def pay_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid format for command. Try %pay <mention user> <amount>.")


def setup(bot):
    bot.add_cog(Economy(bot))
