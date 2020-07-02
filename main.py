# CARDS BOT
import random
import requests
import json
import asyncio
import discord.ext.commands
import discord
import re
import Game

from Game import Game, TexasHoldEm
from sortingOrders import order, presOrder, pokerOrder, suitOrder
from io import BytesIO
from discord.ext.commands import Bot, has_permissions
from discord.ext.tasks import loop
from PIL import Image, ImageDraw, ImageColor, ImageFont
from random import randrange


BOT_PREFIX = "%"
TOKEN = ""

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

# Card constants
offset = 10
cardWidth = 138
cardHeight = 210

# Data storage
hands = {}
userSortType = {}
money = {}
handColors = {}

gameList = []

uncategorized = ['rc', 'hand', 'draw', 'setColor', 'setSort', 'game', 'join', 'start']

def hasCommandByName(name: str):
    for command in client.commands:
        if command.name == name:
            return command
    return None

@client.command(description="Custom help command.",
                name="help",
                pass_context=True)
async def __help(ctx, param: str = None):
    if param is None:
        embed = discord.Embed(title="Cards Bot Commands",
                              description="To view a help page, just add the page number after the %help command. For example: %help 3",
                              color=0x00ff00)
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
        embed.add_field(name="Page 1: Betting",
                        value="Commands associated with betting in games such as Texas Hold 'Em.", inline=False)
        embed.add_field(name="Page 2: Economy", value="Commands associated with the economy system of the bot.",
                        inline=False)
        embed.add_field(name="Page 3: Games", value="Commands for the different card games.", inline=False)
        embed.add_field(name="Page 4: No Category", value="Commands without a specific category.", inline=False)
        await ctx.send(embed=embed)

    if param.isdecimal():
        if int(param) == 1:
            commands = client.get_cog('Betting').get_commands()
            embed = discord.Embed(title="Betting Commands", description="To view a specific command, enter the command's name after the %help command. For example: %help rc.", color=0x00ff00)
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            for command in commands:
                embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)
            await ctx.send(embed=embed)
        elif int(param) == 2:
            commands = client.get_cog('Economy').get_commands()
            embed = discord.Embed(title="Economy Commands", description="To view a specific command, enter the command's name after the %help command. For example: %help rc.", color=0x00ff00)
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            for command in commands:
                embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)
            await ctx.send(embed=embed)
        elif int(param) == 3:
            embed = discord.Embed(title="Game Commands", description="To view a help page, just add the page number after the %help command. For example: %help 3.", color=0x00ff00)
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            embed.add_field(name="Page 5: Texas Hold 'Em", value="Commands for Texas Hold 'Em.", inline=False)
            await ctx.send(embed=embed)
        elif int(param) == 4:
            embed = discord.Embed(title="Uncategorized Commands", description="To view a specific command, enter the command's name after the %help command. For example: %help rc.", color=0x00ff00)
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            for name in uncategorized:
                command = hasCommandByName(name)
                embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)
            await ctx.send(embed=embed)
        elif int(param) == 5:
            embed = discord.Embed(title="Texas Hold 'Em Commands", description="To view a specific command, enter the command's name after the %help command. For example: %help rc.", color = 0x00ff00)
            embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
            commands = client.get_cog('Poker').get_commands()
            for command in commands:
                embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)
            await ctx.send(embed=embed)
    else:
        command = hasCommandByName(param)
        if command is None:
            return

        embed = discord.Embed(title=BOT_PREFIX + command.name, description=command.help, color=0x00ff00)
        embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
        await ctx.send(embed=embed)


@client.event
async def on_ready():
    loadData()
    hands.clear()
    gameLoop.start()
    print("Now online.")

# Check if a user in participating in a game
def checkInGame(user: discord.Member):
    for GAME in gameList:
        if GAME.hasPlayer(user):
            return True
    return False

# Get a Game object by its 6-digit ID
def getGameByID(ID):
    for GAME in gameList:
        if GAME.ID == ID:
            return GAME

# Check if a Game object exists given a 6-digit ID
def hasGame(ID):
    for GAME in gameList:
        if GAME.ID == ID:
            return True
    return False

# Get a Game object that the user is participating in
def getGame(user: discord.Member):
    for GAME in gameList:
        if GAME.hasPlayer(user):
            return GAME

# Check if message and game channel match
def channelCheck(GAME, CHANNEL):
    return GAME.channel == CHANNEL

# Load all data
def loadData():
    global hands, userSortType, players, handColors, money
    with open('hands.json') as hFile:
        hands = json.load(hFile)
    with open('sortType.json') as sTFile:
        userSortType = json.load(sTFile)
    with open('handColors.json') as hCFile:
        handColors = json.load(hCFile)
    with open('econ.json') as eFile:
        money = json.load(eFile)

def loadHands():
    global hands
    with open('hands.json') as hFile:
        hands = json.load(hFile)

def loadPreferences():
    global userSortType, handColors
    with open('sortType.json') as sTFile:
        userSortType = json.load(sTFile)
    with open('handColors.json') as hCFile:
        handColors = json.load(hCFile)

def loadEconomy():
    global money
    with open('econ.json') as eFile:
        money = json.load(eFile)


# Dump all data
def dumpData():
    global hands, userSortType, players, handColors, money
    with open('hands.json', 'w') as hFile:
        json.dump(hands, hFile)
    with open('sortType.json', 'w') as sTFile:
        json.dump(userSortType, sTFile)
    with open('handColors.json', 'w') as hCFile:
        json.dump(handColors, hCFile)
    with open('econ.json', 'w') as eFile:
        json.dump(money, eFile)

def dumpHands():
    global hands
    with open('hands.json', 'w') as hFile:
        json.dump(hands, hFile)

def dumpPreferences():
    global userSortType, handColors
    with open('sortType.json', 'w') as sTFile:
        json.dump(userSortType, sTFile)
    with open('handColors.json', 'w') as hCFile:
        json.dump(handColors, hCFile)

def dumpEconomy():
    global money
    with open('econ.json', 'w') as eFile:
        json.dump(money, eFile)


# Add card to user's hand
def addCard(user: discord.Member, card: str):
    global hands
    if str(user.id) in hands:
        hands[str(user.id)].append(card)
    else:
        hands.update({str(user.id): [card]})


# Reset all game data and variables
def resetData():
    global hands
    hands.clear()


# Card generator
cardChoices = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = ['C', 'D', 'H', 'S']

# Card ordering dictionary
ORDER = order

# Deck constant
deck = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
        "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
        "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
        "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
        "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
        "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
        "deck/10D.png", "deck/10C.png", "deck/10H.png",
        "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png", "deck/QC.png",
        "deck/QH.png", "deck/QS.png",
        "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]

# Return a discord File object representing the user's hand
def showHand(user, userHand):
    userHand = sortHand(user, userHand)

    # Find dimensions
    numCards = len(userHand)
    maxWidth = (int(cardWidth / 3) * (numCards - 1)) + cardWidth + 20

    COLOR = ""
    if not str(user.id) in handColors:
        COLOR = "#078528"
    else:
        COLOR = handColors[str(user.id)]

    # Create base hand image
    HAND = Image.new("RGB", (maxWidth, cardHeight + 20), ImageColor.getrgb(COLOR))
    DRAW = ImageDraw.Draw(HAND)

    font = ImageFont.truetype('calibri.ttf', size=14)
    for i in range(0, numCards):
        card = Image.open(userHand[i])
        card = card.resize((cardWidth, cardHeight))
        HAND.paste(card, (10 + int(cardWidth / 3) * i, 10))
        DRAW.text((30 + int(cardWidth / 3) * i, 15), str(i), fill=ImageColor.getrgb("#ffffff"), font=font)

    with BytesIO() as img:
        HAND.save(img, 'PNG')
        img.seek(0)
        file = discord.File(fp=img, filename='hand.png')
        return file

# Sort user's hand based on their preferred sorting style
def sortHand(user: discord.Member, HAND):
    global ORDER, presOrder, suitOrder, order
    h = []
    loadPreferences()
    loadHands()
    if str(user.id) not in userSortType:
        userSortType.update({str(user.id): 'd'})

    dumpPreferences()
    dumpHands()

    if userSortType[str(user.id)] == 'p':
        ORDER = presOrder
    elif userSortType[str(user.id)] == 's':
        ORDER = suitOrder
    else:
        ORDER = order

    for card in HAND:
        val = ORDER[card]
        index = 0
        while index < len(h) and val > ORDER[h[index]]:
            index += 1

        if index >= len(h):
            h.append(card)
        else:
            h.insert(index, card)

    return h


"""
Commands Start Here
"""

@client.command(description="Generate a random card. Duplicates can appear.",
                brief="Generate a random card",
                help="This command generates a random card from the 52-card deck. Format is %rc. No parameters are required.",
                pass_context=True)
async def rc(ctx):
    embed = discord.Embed(title="Random Card", description="", color=0x00ff00)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    selectCard = random.choice(cardChoices)
    selectSuit = random.choice(suits)

    if selectCard == 'A':
        embed.description += "Ace of "
    elif selectCard == 'J':
        embed.description += "Jack of "
    elif selectCard == 'Q':
        embed.description += "Queen of "
    elif selectCard == 'K':
        embed.description += "King of "
    else:
        embed.description += selectCard + " of "

    if selectSuit == 'D':
        embed.description += "Diamonds"
    elif selectSuit == 'C':
        embed.description += "Clubs"
    elif selectSuit == 'H':
        embed.description += "Hearts"
    elif selectSuit == 'S':
        embed.description += "Spades"

    imgName = "deck/" + selectCard + selectSuit + ".png"
    file = discord.File(imgName, filename='card.png')
    embed.set_thumbnail(url="attachment://card.png")
    await ctx.send(file=file, embed=embed)


@client.command(description="Pull a number of random cards from the deck.",
                brief="Draw a number of cards from the deck",
                help="Pull a number of specified random cards from the deck and add them to your hand. This command is not available while in a game. "
                     "Format for this command is %draw <number of cards>. Number of cards should be between 1-52 inclusive.",
                pass_context=True)
async def draw(ctx, cards: int = 1):
    loadHands()
    embed = discord.Embed(title="Draw Card", description=None, color=0x00ff00)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
    if cards > 52 or cards <= 0:
        embed.description = "You cannot draw this number of cards. Provide a number between 1 and 52 inclusive."
        await ctx.send(embed=embed)
        return

    if str(ctx.author.id) in hands and len(hands[str(ctx.author.id)]) + cards > 52:
        embed.description = "You cannot hold more than 52 cards."
        await ctx.send(embed=embed)
        return

    if checkInGame(ctx.author):
        embed.description = "Cannot use this command while in a game."
        await ctx.send(embed=embed)
        return

    drawDeck = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
                "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
                "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
                "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
                "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
                "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
                "deck/10D.png", "deck/10C.png", "deck/10H.png",
                "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png", "deck/QC.png",
                "deck/QH.png", "deck/QS.png",
                "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]

    for i in range(0, cards):
        cardName = random.choice(drawDeck)
        drawDeck.remove(cardName)
        addCard(ctx.author, cardName)

    embed.description = str(cards) + " card(s) dealt."
    embed.set_footer(text="Check your hand using '%hand'")
    await ctx.send(embed=embed)
    dumpHands()


@client.command(description="View your hand.",
                brief="View your hand",
                help="View the cards you have in your hand. The bot will PM you an image containing your hand. Format is %hand without any parameters.",
                pass_context=True)
async def hand(ctx):
    loadHands()
    embed = discord.Embed(title=ctx.author.name + "'s Hand", description=None, color=0x00ff00)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)

    if checkInGame(ctx.author):
        GAME = getGame(ctx.author)
        if GAME.gameUnderway:
            file = showHand(ctx.author, GAME.playerHands[str(ctx.author.id)])
            embed.set_image(url="attachment://hand.png")
            embed.add_field(name="Number of Cards", value=str(len(GAME.playerHands[str(ctx.author.id)])))
            await ctx.author.send(file=file, embed=embed)
        else:
            embed.description = "Your game has not started yet."
            await ctx.send(embed=embed)
    else:
        if str(ctx.author.id) not in hands or len(hands[str(ctx.author.id)]) == 0:
            embed.description = "You have no cards in your hand."
            await ctx.author.send(embed=embed)
            return

        file = showHand(ctx.author, hands[str(ctx.author.id)])
        embed.set_image(url="attachment://hand.png")
        embed.add_field(name="Number of Cards", value=str(len(hands[str(ctx.author.id)])))
        await ctx.author.send(file=file, embed=embed)


@client.command(description="Set sorting type. Use 'p' for president-style sorting (3 low, 2 high), 'd' for default sorting (A low, K high), 's' for suit sorting (diamonds - spades).",
                brief="Set sorting type",
                aliases=['ss'],
                help="Set your preferred hand sorting style. Format for this command is %setSort <sortType>.\nUse 'p' for president-style 3 lowest, 2 highest sorting.\n "
                     "Use 'd' for default ace low, king high sorting.\n Use 's' for sorting by suit.\n",
                pass_context=True)
async def setSort(ctx, sortType: str = None):
    loadPreferences()
    embed = discord.Embed(title="Sorting Style", description=None, color=0x00ff00)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
    global order, presOrder, ORDER
    if sortType is None:
        embed.description = "No sorting type provided."
        embed.add_field(name="President-Style (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="Default (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)
        await ctx.send(embed=embed)
        return

    if sortType == 'd':
        embed.description = "Sorting type set to Default."
        embed.add_field(name="President-Style (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="Default (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)
        ORDER = order
    elif sortType == 'p':
        embed.description = "Sorting type set to President-Style."
        embed.add_field(name="President-Style (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="Default (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)
        ORDER = presOrder
    elif sortType == 's':
        embed.description = "Sorting type set to Suits-Style."
        embed.add_field(name="President-Style (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="Default (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)
        ORDER = suitOrder
    else:
        embed.description = "Try 'p', 'd', or 's'."
        embed.add_field(name="President-Style (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="Default (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)

    if str(ctx.author.id) in hands:
        userSortType[str(ctx.author.id)] = sortType
    else:
        userSortType.update({str(ctx.author.id): sortType})
    await ctx.send(embed=embed)
    dumpPreferences()


@client.command(description="Start a game.",
                brief="Start a game",
                aliases=['5card'],
                help="Use this command to start a new game. You can only use this command outside of a game. Format is %game without parameters.",
                pass_context=True)
async def game(ctx):
    global gameList
    if checkInGame(ctx.author):
        embed = discord.Embed(title=None, description="You are already in a game.", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        return

    emoji1 = '1️⃣'
    embed = discord.Embed(title="Game Selection", description="Select a game type by reacting to this message with the given emoji.", color=0x00ff00)
    embed.set_thumbnail(url=client.get_user(716357127739801711).avatar_url)
    embed.add_field(name="Texas Hold 'Em", value=emoji1)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji1)
    rxn = None

    def check(reaction, user):
        global rxn
        rxn = reaction
        return not user.bot

    try:
        rxn = await client.wait_for('reaction_add', timeout=50.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(embed=discord.Embed(title="Game Selection", description="Nobody chose in time...", color=0x00ff00))
        return
    else:
        if str(rxn[0].emoji) == emoji1:
            ID = randrange(100000, 1000000)
            while hasGame(ID):
                ID = randrange(100000, 1000000)
            GAME = TexasHoldEm(ctx.channel, ID)
            gameList.append(GAME)
            embed = discord.Embed(title="Game Creation", description="Texas Hold 'Em game created.", color=0x00ff00)
            embed.add_field(name="Game ID", value=str(ID))
            embed.add_field(name="Joining", value="%join " + str(ID))
            embed.set_thumbnail(url=GAME.imageUrl)
            await ctx.send(embed=embed)


@client.command(description="Join a game using its 6-digit ID.",
                brief="Join a game.",
                help="Join an existing game using its 6-digit ID. Format for this command is %join <6-digit ID>.",
                pass_context=True)
async def join(ctx, ID: int):
    loadData()
    embed = discord.Embed(title=None, description=None, color=0x00ff00)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if str(ctx.author.id) not in money:
        money.update({str(ctx.author.id): 10000})

    if checkInGame(ctx.author):
        embed.description = "You are already in a game."
        await ctx.send(embed=embed)
        return

    if not hasGame(ID):
        embed.description = "Invalid game ID."
        await ctx.send(embed=embed)
        return

    if not channelCheck(getGameByID(ID), ctx.channel):
        embed.description = "You are not in the specified game's channel. Please go there."
        await ctx.send(embed=embed)
        return

    GAME = getGameByID(ID)
    if str(ctx.author.id) in hands:
        del hands[str(ctx.author.id)]

    if GAME.gameUnderway:
        embed.description = "You join a game that was already underway. You will be joined in for the next hand."
        embed.add_field(name="Game ID", value=GAME.ID)
        GAME.players.append(str(ctx.author.id))
        GAME.playerStatus.update({str(ctx.author.id): "Fold"})
        await ctx.send(embed=embed)
        return

    GAME.players.append(str(ctx.author.id))
    embed.description = "You joined a game."
    embed.add_field(name="Game ID", value=GAME.ID)
    embed.set_thumbnail(url=GAME.imageUrl)
    await ctx.send(embed=embed)
    dumpData()


@client.command(description="Leave a game you are apart of and forfeits any bets made if the game was already underway.",
                brief="Leave a game you joined and forfeit any bets made if the game was already underway",
                help="Leave a game you are apart of, thus forfeiting any bets you made already. Format is %leave without any parameters.",
                pass_context=True)
async def leave(ctx):
    embed = discord.Embed(title=None, description=None, color=0x00ff00)
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

    GAME.players.remove(str(ctx.author.id))
    loadHands()
    if str(ctx.author.id) in hands:
        del hands[str(ctx.author.id)]
    dumpHands()
    embed.description = "You left your game."
    embed.add_field(name="Game ID", value=str(GAME.ID))
    embed.set_thumbnail(url=GAME.imageUrl)
    await ctx.send(embed=embed)


@client.command(description="Start the game.",
                brief="Start the game",
                help="Start the game you are apart of if it was not already underway. Format is %start without any parameters.",
                pass_context=True)
async def start(ctx):
    embed = discord.Embed(title=None, description=None, color=0x00ff00)
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

    if GAME.gameUnderway:
        embed.description = "Your game has already started."
        embed.add_field(name="Game ID", value=str(GAME.ID))
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.send(embed=embed)
        return

    await GAME.startGame()


@client.command(description="Set a custom color using a hex code for your hand.",
                brief="Set a custom color for your hand",
                aliases=['sc', 'setColour'],
                help="Set a custom color for the image that displays your hand. A valid color hex code in the format #123ABC is required. Format is %setColor <hex code>.",
                pass_context=True)
async def setColor(ctx, colour: str):
    embed = discord.Embed(title="Custom Colour", description=None, color=0x00ff00)
    embed.set_thumbnail(url="https://i.imgur.com/FCCMHHi.png")
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', colour)
    if not match:
        embed.description="Invalid colour hex code."
        await ctx.send(embed=embed)
        return

    loadData()
    if not str(ctx.author.id) in handColors:
        handColors.update({str(ctx.author.id): colour})
    else:
        handColors[str(ctx.author.id)] = colour

    embed.colour = int(colour[1:], 16)
    embed.description = "Custom colour set."
    embed.add_field(name="Colour", value="<-----")

    await ctx.send(embed=embed)
    dumpData()


@loop(seconds=1)
async def gameLoop():
    for GAME in gameList:
        await GAME.gameLoop()


@client.event
async def on_message(msg):
    global money
    await client.process_commands(msg)

    if str(msg.author.id) not in money:
        money.update({str(msg.author.id): 10000})
        dumpEconomy()


client.load_extension('Poker')
client.load_extension('Economy')
client.load_extension('Betting')
client.run(TOKEN)
