# Work with Python 3.6
# USED IMPORTS
from discord.ext import commands
import discord.ext.commands
from discord.ext.commands import Bot, has_permissions, CheckFailure
import main
from main import client, dumpData, loadData, showHand

imgUrl = "https://i.imgur.com/ydS4u8P.png"

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

        embed = discord.Embed(title="User Balance", color=0x00ff00)
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        embed.set_thumbnail(url=imgUrl)
        embed.description = "$" + str(main.money[str(user.id)])
        await ctx.send(embed=embed)

    @bal.error
    async def bal_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=imgUrl)
            embed.description = "Invalid user provided."
            embed.set_footer(text="Mention a user to check their balance.")
            await ctx.send(embed=embed)

    @commands.command(description="Set money for user. Requires administrator permissions.",
                      brief="Set money for user",
                      help="Set the balance of a user to a specified value. Requires administrator permissions for use. Mention a user to"
                           " set their balance. Format is %setbal <mention user> <balance amount>.",
                      pass_context=True)
    @has_permissions(administrator=True)
    async def setbal(self, ctx, user: discord.Member = None, amount: float = None):
        embed = discord.Embed(title="Set User Balance", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=imgUrl)

        loadData()

        if amount is None or user is None:
            embed.description = "Invalid format for command. Try %setbal <mention user> <amount>."
            await ctx.send(embed=embed)
            return

        if str(user.id) not in main.money:
            main.money.update({str(user.id): amount})
        else:
            main.money[str(user.id)] = amount

        embed.description = "Balance for " + user.display_name + " set to $" + str(amount) + "."
        await ctx.send(embed=embed)
        dumpData()

    @setbal.error
    async def setbal_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error",
                                  description="Invalid arguments detected for command 'setbal'. Try %setbal <mention user> <amount> or check %help setbal for more details.",
                                  color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=imgUrl)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="Permissions Error",
                                  description="You do not have permission to use this command.",
                                  color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=imgUrl)
            await ctx.send(embed=embed)

    @commands.command(description="Pay a user.",
                      brief="Pay a user",
                      help="Pay a user from your own balance. You must have sufficient funds to pay the value you specified. Mention"
                           " the user who you'd like to pay. Format is %pay <mention user> <payment amount>.",
                      pass_context=True)
    async def pay(self, ctx, user: discord.Member = None, amount: float = None):
        embed = discord.Embed(title="Payment", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=imgUrl)
        if user is None:
            embed.description = "No recipient provided."
            await ctx.send(embed=embed)
            return

        if amount is None:
            embed.description = "No amount provided."
            await ctx.send(embed=embed)
            return

        if amount <= 0:
            embed.description = "Payments must be greater than $0."
            await ctx.send(embed=embed)
            return

        if str(user.id) not in main.money:
            main.money.update({str(user.id): 10000})

        if str(ctx.author.id) not in main.money:
            main.money.update({str(ctx.author.id): 10000})

        if amount > main.money[str(ctx.author.id)]:
            embed.description = "Insufficient funds for payment."
            embed.add_field(name="Your Balance", value=str(main.money[str(ctx.author.id)]))
            return

        main.money[str(ctx.author.id)] -= amount
        main.money[str(user.id)] += amount

        embed.description = "Payment of $" + str(amount) + " sent to " + user.display_name + "."
        embed.add_field(name="Your New Balance", value=str(main.money[str(ctx.author.id)]))
        embed.add_field(name=user.display_name + "'s New Balance", value=str(main.money[str(user.id)]), inline=False)
        await ctx.send(embed=embed)
        dumpData()

    @pay.error
    async def pay_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=imgUrl)
            embed.description = "Invalid arguments detected for command 'pay'. Try %pay <mention user> <amount>."
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
