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

from CardEval import evaluateHand, handType
from io import BytesIO
from discord.ext.commands import Bot, has_permissions, CheckFailure
from discord.ext.tasks import loop
from PIL import Image, ImageDraw, ImageColor, ImageFont
from discord.ext import tasks
from random import randrange
from discord.ext import commands


BOT_PREFIX = "%"
TOKEN = ""

client = Bot(command_prefix=BOT_PREFIX)

# Card constants
offset = 10
cardWidth = 138
cardHeight = 210

# Data storage
hands = {}
userSortType = {}
handColors = {}
players = []


gameType = {"5card": 0}

# Game variables
currentGame = ""
gameStarted = False
gameUnderway = False
gameChannelID = None
currGame = "cards"

# Betting
money = {}
bets = {}
pot = 0


@client.event
async def on_ready():
    loadData()
    hands.clear()
    players.clear()
    gameLoop.start()
    print("Now online.")


# Load user hands
def loadData():
    global hands, userSortType, players, handColors, money
    with open('hands.json') as hFile:
        hands = json.load(hFile)
    with open('sortType.json') as sTFile:
        userSortType = json.load(sTFile)
    with open('players.json') as pFile:
        players = json.load(pFile)
    with open('handColors.json') as hCFile:
        handColors = json.load(hCFile)
    with open('econ.json') as eFile:
        money = json.load(eFile)


# Dump user hands
def dumpData():
    global hands, userSortType, players, handColors, money
    with open('hands.json', 'w') as hFile:
        json.dump(hands, hFile)
    with open('sortType.json', 'w') as sTFile:
        json.dump(userSortType, sTFile)
    with open('players.json', 'w') as pFile:
        json.dump(players, pFile)
    with open('handColors.json', 'w') as hCFile:
        json.dump(handColors, hCFile)
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
    global gameUnderway, gameStarted, players, hands
    gameStarted = False
    gameUnderway = False
    hands.clear()
    players.clear()


# Card generator
cardChoices = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

order = {"deck/AD.png": 0, "deck/AC.png": 1, "deck/AH.png": 2, "deck/AS.png": 3, "deck/2D.png": 4, "deck/2C.png": 5,
         "deck/2H.png": 6, "deck/2S.png": 7, "deck/3D.png": 8, "deck/3C.png": 9, "deck/3H.png": 10, "deck/3S.png": 11,
         "deck/4D.png": 12, "deck/4C.png": 13, "deck/4H.png": 14, "deck/4S.png": 15, "deck/5D.png": 16,
         "deck/5C.png": 17, "deck/5H.png": 18, "deck/5S.png": 19, "deck/6D.png": 20, "deck/6C.png": 21,
         "deck/6H.png": 22, "deck/6S.png": 23,
         "deck/7D.png": 24, "deck/7C.png": 25, "deck/7H.png": 26, "deck/7S.png": 27, "deck/8D.png": 28,
         "deck/8C.png": 29, "deck/8H.png": 30, "deck/8S.png": 31, "deck/9D.png": 32, "deck/9C.png": 33,
         "deck/9H.png": 34, "deck/9S.png": 35,
         "deck/10D.png": 36, "deck/10C.png": 37, "deck/10H.png": 38, "deck/10S.png": 39, "deck/JD.png": 40,
         "deck/JC.png": 41, "deck/JH.png": 42, "deck/JS.png": 43, "deck/QD.png": 44, "deck/QC.png": 45,
         "deck/QH.png": 46, "deck/QS.png": 47,
         "deck/KD.png": 48, "deck/KC.png": 49, "deck/KH.png": 50, "deck/KS.png": 51}

pokerOrder = {"deck/2D.png": 4, "deck/2C.png": 5,
              "deck/2H.png": 6, "deck/2S.png": 7, "deck/3D.png": 8, "deck/3C.png": 9, "deck/3H.png": 10, "deck/3S.png": 11,
              "deck/4D.png": 12, "deck/4C.png": 13, "deck/4H.png": 14, "deck/4S.png": 15, "deck/5D.png": 16,
              "deck/5C.png": 17, "deck/5H.png": 18, "deck/5S.png": 19, "deck/6D.png": 20, "deck/6C.png": 21,
              "deck/6H.png": 22, "deck/6S.png": 23,
              "deck/7D.png": 24, "deck/7C.png": 25, "deck/7H.png": 26, "deck/7S.png": 27, "deck/8D.png": 28,
              "deck/8C.png": 29, "deck/8H.png": 30, "deck/8S.png": 31, "deck/9D.png": 32, "deck/9C.png": 33,
              "deck/9H.png": 34, "deck/9S.png": 35,
              "deck/10D.png": 36, "deck/10C.png": 37, "deck/10H.png": 38, "deck/10S.png": 39, "deck/JD.png": 40,
              "deck/JC.png": 41, "deck/JH.png": 42, "deck/JS.png": 43, "deck/QD.png": 44, "deck/QC.png": 45,
              "deck/QH.png": 46, "deck/QS.png": 47,
              "deck/KD.png": 48, "deck/KC.png": 49, "deck/KH.png": 50, "deck/KS.png": 51, "deck/AD.png": 52, "deck/AC.png": 53, "deck/AH.png": 54, "deck/AS.png": 55}

presOrder = {"deck/3D.png": 8, "deck/3C.png": 9, "deck/3H.png": 10,
             "deck/3S.png": 11,
             "deck/4D.png": 12, "deck/4C.png": 13, "deck/4H.png": 14, "deck/4S.png": 15, "deck/5D.png": 16,
             "deck/5C.png": 17, "deck/5H.png": 18, "deck/5S.png": 19, "deck/6D.png": 20, "deck/6C.png": 21,
             "deck/6H.png": 22, "deck/6S.png": 23,
             "deck/7D.png": 24, "deck/7C.png": 25, "deck/7H.png": 26, "deck/7S.png": 27, "deck/8D.png": 28,
             "deck/8C.png": 29, "deck/8H.png": 30, "deck/8S.png": 31, "deck/9D.png": 32, "deck/9C.png": 33,
             "deck/9H.png": 34, "deck/9S.png": 35,
             "deck/10D.png": 36, "deck/10C.png": 37, "deck/10H.png": 38, "deck/10S.png": 39, "deck/JD.png": 40,
             "deck/JC.png": 41, "deck/JH.png": 42, "deck/JS.png": 43, "deck/QD.png": 44, "deck/QC.png": 45,
             "deck/QH.png": 46, "deck/QS.png": 47,
             "deck/KD.png": 48, "deck/KC.png": 49, "deck/KH.png": 50, "deck/KS.png": 51, "deck/AD.png": 52,
             "deck/AC.png": 53, "deck/AH.png": 54, "deck/AS.png": 55, "deck/2D.png": 56, "deck/2C.png": 57,
             "deck/2H.png": 58, "deck/2S.png": 59}

suitOrder = {"deck/AD.png": 0, "deck/2D.png": 1, "deck/3D.png": 2, "deck/4D.png": 3, "deck/5D.png": 4,
             "deck/6D.png": 5, "deck/7D.png": 6, "deck/8D.png": 7, "deck/9D.png": 8, "deck/10D.png": 9,
             "deck/JD.png": 10, "deck/QD.png": 11, "deck/KD.png": 12,
             "deck/AC.png": 13, "deck/2C.png": 14, "deck/3C.png": 15, "deck/4C.png": 16, "deck/5C.png": 17,
             "deck/6C.png": 18, "deck/7C.png": 19, "deck/8C.png": 20, "deck/9C.png": 21, "deck/10C.png": 22,
             "deck/JC.png": 23, "deck/QC.png": 24, "deck/KC.png": 25,
             "deck/AH.png": 26, "deck/2H.png": 27, "deck/3H.png": 28, "deck/4H.png": 29, "deck/5H.png": 30,
             "deck/6H.png": 31, "deck/7H.png": 32, "deck/8H.png": 33, "deck/9H.png": 34, "deck/10H.png": 35,
             "deck/JH.png": 36, "deck/QH.png": 37, "deck/KH.png": 38,
             "deck/AS.png": 39, "deck/2S.png": 40, "deck/3S.png": 41, "deck/4S.png": 42, "deck/5S.png": 43,
             "deck/6S.png": 44, "deck/7S.png": 45, "deck/8S.png": 46,
             "deck/9S.png": 47, "deck/10S.png": 48, "deck/JS.png": 49, "deck/QS.png": 50, "deck/KS.png": 51}

ORDER = order

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

tempDeck = deck
drawDeck = deck

suits = ['C', 'D', 'H', 'S']


def drawCard(user: discord.Member):
    selectCard = random.choice(cardChoices)
    selectSuit = random.choice(suits)
    imgName = "deck/" + selectCard + selectSuit + ".png"
    addCard(user, imgName)
    card = Image.open(str(imgName))
    card = card.resize((69, 105))
    return card


def gameDraw(user: discord.Member, numDraws: int):
    global tempDeck, deck
    for i in range(0, numDraws):
        if len(tempDeck) < numDraws:
            tempDeck = deck

        selectCard = random.choice(tempDeck)
        addCard(user, selectCard)
        tempDeck.remove(selectCard)


def endGame():
    loadData()
    global gameStarted, gameUnderway, players, hands, currGame
    gameStarted = False
    gameUnderway = False
    for player in players:
        hands[player].clear()

    players.clear()
    currGame = "cards"
    if "716357127739801711" in hands:
        del hands["716357127739801711"]


def showHand(user: discord.Member):
    loadData()

    sortHand(user)
    # Get user PFP
    pfpUrl = user.avatar_url
    headers = {'User-Agent': 'CardsBot'}
    r = requests.get(str(pfpUrl), stream=True, headers=headers)
    pfp = Image.open(BytesIO(r.content))
    pfp = pfp.resize((32, 32))

    # Find dimensions
    sortHand(user)
    userHand = hands[str(user.id)]
    numCards = len(userHand)
    maxWidth = (int(cardWidth / 3) * (numCards - 1)) + cardWidth + 20

    # Test font size
    font = ImageFont.truetype('calibri.ttf', size=20)
    textWidth = font.getsize(str(user.name))[0]
    bottomTextWidth = font.getsize("Number of Cards: " + str(numCards))[0]

    # Check size and width
    if textWidth > maxWidth:
        maxWidth = textWidth + 69

    if bottomTextWidth > maxWidth:
        maxWidth = bottomTextWidth + 69

    COLOR = ""
    if not str(user.id) in handColors:
        COLOR = "#078528"
    else:
        COLOR = handColors[str(user.id)]

    # Create base hand image
    HAND = Image.new("RGB", (maxWidth, cardHeight + 130), ImageColor.getrgb(COLOR))
    DRAW = ImageDraw.Draw(HAND)

    # Fill top grey bar
    DRAW.rectangle([0, 0, HAND.width, 50], outline=ImageColor.getrgb("#000000"), fill=ImageColor.getrgb("#3e434a"),
                   width=2)

    # Fill bottom grey bar
    DRAW.rectangle([0, cardHeight + 80, HAND.width, HAND.height], outline=ImageColor.getrgb("#000000"),
                   fill=ImageColor.getrgb("#3e434a"), width=2)

    # Draw text and superimpose PFP
    DRAW.text((55, 17), str(user.name), fill=ImageColor.getrgb("#ffffff"), font=font)
    HAND.paste(pfp, (9, 9))

    # Add statistics to bottom bar
    DRAW.text((9, cardHeight + 97), "Number of Cards: " + str(numCards), fill=ImageColor.getrgb("#ffffff"), font=font)

    font = ImageFont.truetype('calibri.ttf', size=14)
    for i in range(0, numCards):
        card = Image.open(userHand[i])
        card = card.resize((cardWidth, cardHeight))
        HAND.paste(card, (10 + int(cardWidth / 3) * i, 60))
        DRAW.text((30 + int(cardWidth / 3) * i, 275), str(i), fill=ImageColor.getrgb("#ffffff"), font=font)

    HAND.save('hand.png', format='PNG')
    file = discord.File(open('hand.png', 'rb'))
    dumpData()
    return file


def sortHand(user: discord.Member):
    global hands
    global ORDER, presOrder, suitOrder, order
    h = []
    loadData()
    if str(user.id) not in userSortType:
        userSortType.update({str(user.id): 'd'})

    dumpData()

    if userSortType[str(user.id)] == 'p':
        ORDER = presOrder
    elif userSortType[str(user.id)] == 's':
        ORDER = suitOrder
    else:
        ORDER = order

    for card in hands[str(user.id)]:
        val = ORDER[card]
        index = 0
        while index < len(h) and val > ORDER[h[index]]:
            index += 1

        if index >= len(h):
            h.append(card)
        else:
            h.insert(index, card)

    hands[str(user.id)] = h


@client.command(description="Generate a random card. Duplicates can appear.",
                brief="Generate a random card",
                pass_context=True)
async def rc(ctx):
    loadData()
    if gameStarted and str(ctx.author.id) in players:
        await ctx.send("This command is not available while you are in a game.")
        return

    card = drawCard(ctx.author)
    card.save('drawn.png', format='PNG')
    file = discord.File(open('drawn.png', 'rb'))
    dumpData()
    await ctx.send(ctx.author.mention, file=file)


@client.command(description="Pull a number of random cards from the deck. Pulled cards cannot be pulled a second time unless the deck is reset.",
                brief="Draw a number of cards from the deck",
                pass_context=True)
async def draw(ctx, cards: int = 1):
    loadData()

    if gameStarted and str(ctx.author.id) in players:
        await ctx.send("This command is not available while you are in a game.")
        return

    global drawDeck
    if cards > len(drawDeck):
        await ctx.send("Not enough cards left in the deck.")
        return
    for i in range(0, cards):
        cardName = random.choice(drawDeck)
        drawDeck.remove(cardName)
        addCard(ctx.author, cardName)
    await ctx.send("You have received your cards " + ctx.author.mention)
    dumpData()


@client.command(description="View how many cards are left in the deck.",
                brief="View how many cards are left in the deck",
                pass_context=True)
async def deck(ctx):
    global drawDeck
    if len(drawDeck) == 1:
        await ctx.send("There is " + str(len(drawDeck)) + " card left in the deck.")
    else:
        await ctx.send("There are " + str(len(drawDeck)) + " cards left in the deck.")


@client.command(description="Refill the deck",
                brief="Refill the deck",
                pass_context=True)
async def refill(ctx):
    global drawDeck
    drawDeck = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
                "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
                "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
                "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
                "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
                "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
                "deck/10D.png", "deck/10C.png", "deck/10H.png",
                "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png",
                "deck/QC.png",
                "deck/QH.png", "deck/QS.png",
                "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]
    await ctx.send("Deck refilled!")


@client.command(description="View your hand.",
                brief="View your hand",
                pass_context=True)
async def hand(ctx):
    loadData()
    if str(ctx.author.id) not in hands:
        await ctx.send("You have no cards in your hand " + ctx.author.mention)
        return

    await ctx.author.send(file=showHand(ctx.author))


@client.command(description="Set sorting type. Use 'p' for president-style sorting (3 low, 2 high), 'd' for default sorting (A low, K high), 's' for suit sorting (diamonds - spades).",
                brief="Set sorting type",
                aliases=['ss'],
                pass_context=True)
async def setSort(ctx, sortType: str = None):
    global order, presOrder, ORDER
    if sortType is None:
        await ctx.send("Invalid sorting type detected. Try 'p', 's', or 'd'.")
        return

    if sortType == 'd':
        await ctx.send("Sorting type set to default. Ace is low, king is high.")
        ORDER = order
    elif sortType == 'p':
        await ctx.send("Sorting type set to president-style. 3-K, A, 2.")
        ORDER = presOrder
    elif sortType == 's':
        await ctx.send("Sorting type set to by suit. Diamonds - Spades")
        ORDER = suitOrder

    if str(ctx.author.id) in hands:
        userSortType[str(ctx.author.id)] = sortType
    else:
        userSortType.update({str(ctx.author.id): sortType})
    dumpData()


@client.command(description="Start a game.",
                brief="Start a game",
                aliases=['5card'],
                pass_context=True)
async def game(ctx):
    global currentGame, gameStarted, tempDeck, deck, gameChannelID, currGame
    if gameStarted:
        await ctx.send("There is another game underway.")
        return

    emoji1 = '1️⃣'
    emoji2 = '2️⃣'
    msg = await ctx.send("**           CHOOSE GAME**\n**-------------------------------**\n**REACT WITH:\n" + emoji1 + " - Texas Hold 'Em**\n" + emoji2 + "** - Five-Card Draw**\n**-------------------------------**\n")

    await msg.add_reaction(emoji1)
    await msg.add_reaction(emoji2)

    rxn = None

    def check(reaction, user):
        global rxn
        rxn = reaction
        return not user.bot

    try:
        rxn = await client.wait_for('reaction_add', timeout=50.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Nobody chose in time.")
        return
    else:
        if str(rxn[0].emoji) == emoji1:
            currentGame = "POKER"
            currGame = "Texas Hold 'Em"
            await ctx.send("Texas Hold 'Em selected.")
        elif str(rxn[0].emoji) == emoji2:
            currentGame = "5CARD"
            await ctx.send("Five-Card Draw selected.")

        gameStarted = True
        gameChannelID = ctx.channel.id
        tempDeck = deck


@client.command(description="Join a game that is not yet underway.",
                brief="Join a game that is not yet underway",
                pass_context=True)
async def join(ctx):
    loadData()
    if not gameStarted:
        await ctx.send("There is no active game to join.")
    elif not gameUnderway and gameStarted:
        if players.count(str(ctx.author.id)) > 0:
            await ctx.send("You are already in this game.")
        else:
            await ctx.send(ctx.author.mention + " you joined the game.")
            players.append(str(ctx.author.id))
            if str(ctx.author.id) in hands:
                del hands[str(ctx.author.id)]
    else:
        await ctx.send("A game is already underway.")
    dumpData()


@client.command(description="Start the game.",
                brief="Start the game",
                pass_context=True)
async def start(ctx):
    loadData()
    global players, gameStarted, gameUnderway, currentGame
    if not gameStarted:
        await ctx.send("There is no game to start.")
        return

    if gameUnderway:
        await ctx.send("The game is already underway.")
        return

    if players.count(str(ctx.author.id)) <= 0:
        await ctx.send("You are not in this game.")
        return

    output = "Game started.\nIn this game:\n"
    for ID in players:
        user = client.get_user(int(ID))
        output += user.mention + "\n"

    await ctx.send(output)
    global tempDeck
    tempDeck = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
                "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
                "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
                "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
                "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
                "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
                "deck/10D.png", "deck/10C.png", "deck/10H.png",
                "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png",
                "deck/QC.png",
                "deck/QH.png", "deck/QS.png",
                "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]
    gameUnderway = True

    if currentGame == "POKER":
        hands.update({"716357127739801711": []})
        for ID in players:
            user = client.get_user(int(ID))
            gameDraw(user, 2)

        gameDraw(client.get_user(716357127739801711), 3)


@client.command(description="Set a custom color using a hex code for your hand.",
                brief="Set a custom color for your hand",
                aliases=['sc', 'setColour'],
                pass_context=True)
async def setColor(ctx, colour: str):
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', colour)
    if not match:
        await ctx.send("That is not a valid hex color code.")
        return

    loadData()
    if not str(ctx.author.id) in handColors:
        handColors.update({str(ctx.author.id): colour})
    else:
        handColors[str(ctx.author.id)] = colour

    await ctx.send("New custom colour set.")
    dumpData()


@client.command(description="Reset hands.",
                brief="Reset hands",
                pass_context=True)
async def reset(ctx):
    loadData()
    hands.clear()
    dumpData()
    await ctx.send("All user hands have been reset.")


@reset.error
async def reset_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send("You are not authorized to use this command.")


@loop(seconds=1)
async def gameLoop():
    await client.change_presence(activity=discord.Game(name=currGame))
    global gameChannelID
    dumpData()
    if not gameStarted:
        return

    if gameUnderway:
        if currentGame == "POKER":
            loadData()
            if len(hands["716357127739801711"]) == 5:
                channel = client.get_channel(gameChannelID)
                await channel.send("All cards dealt, revealing all players' hands...")

                score = {}
                overallMax = 0
                for ID in players:
                    user = client.get_user(int(ID))
                    community = hands["716357127739801711"]
                    maxScore = 0

                    for i in range(0, 5):
                        for j in range(i + 1, 5):
                            for k in range(j + 1, 5):
                                cardVals = [hands[str(user.id)][0], hands[str(user.id)][1], community[i], community[j], community[k]]
                                maxScore = max(maxScore, evaluateHand(cardVals))

                    score.update({maxScore: ID})
                    overallMax = max(maxScore, overallMax)

                    await channel.send("**" + user.name + " has a " + handType(maxScore) + ". Score of " + str(maxScore) + "**", file=showHand(user))

                await channel.send("The winner is " + client.get_user(int(score[overallMax])).mention)
                endGame()


@client.event
async def on_message(msg):
    global money
    await client.process_commands(msg)

    if str(msg.author.id) not in money:
        money.update({str(msg.author.id): 10000})

    dumpData()


client.load_extension('Poker')
client.load_extension('Economy')
client.load_extension('Betting')
client.run(TOKEN)
