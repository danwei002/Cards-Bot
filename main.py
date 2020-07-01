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

# Card constants
offset = 10
cardWidth = 138
cardHeight = 210

# Data storage
hands = {}
userSortType = {}
money = {}
handColors = {}
players = []

gameList = []

@client.event
async def on_ready():
    loadData()
    hands.clear()
    players.clear()
    gameLoop.start()
    print("Now online.")


def checkInGame(user: discord.Member):
    for GAME in gameList:
        if GAME.hasPlayer(user):
            return True
    return False

def getGameByID(ID):
    for GAME in gameList:
        if GAME.ID == ID:
            return GAME

def hasGame(ID):
    for GAME in gameList:
        if GAME.ID == ID:
            return True
    return False

def getGame(user: discord.Member):
    for GAME in gameList:
        if GAME.hasPlayer(user):
            return GAME

def channelCheck(GAME, CHANNEL):
    return GAME.channel == CHANNEL

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
suits = ['C', 'D', 'H', 'S']

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

drawDeck = deck

def drawCard(user: discord.Member):
    selectCard = random.choice(cardChoices)
    selectSuit = random.choice(suits)
    imgName = "deck/" + selectCard + selectSuit + ".png"
    addCard(user, imgName)
    card = Image.open(str(imgName))
    card = card.resize((69, 105))
    return card


def showHand(user, userHand):
    loadData()

    userHand = sortHand(user, userHand)
    # Get user PFP
    pfpUrl = user.avatar_url
    headers = {'User-Agent': 'CardsBot'}
    r = requests.get(str(pfpUrl), stream=True, headers=headers)
    pfp = Image.open(BytesIO(r.content))
    pfp = pfp.resize((32, 32))

    # Find dimensions
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

    with BytesIO() as img:
        HAND.save(img, 'PNG')
        img.seek(0)
        file = discord.File(fp=img, filename='hnd.png')
        dumpData()
        return file

def sortHand(user: discord.Member, HAND):
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


@client.command(description="Generate a random card. Duplicates can appear.",
                brief="Generate a random card",
                pass_context=True)
async def rc(ctx):
    loadData()
    if checkInGame(ctx.author):
        await ctx.send("Cannot use this command while in a game.")
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

    if checkInGame(ctx.author):
        await ctx.send("Cannot use this command while in a game.")
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


@client.command(description="Refill the deck",
                brief="Refill the deck",
                pass_context=True)
async def refill(ctx):
    if checkInGame(ctx.author):
        await ctx.send("Cannot use this command while in a game.")
        return
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

    await ctx.author.send(file=showHand(ctx.author, hands[str(ctx.author.id)]))


@client.command(description="Set sorting type. Use 'p' for president-style sorting (3 low, 2 high), 'd' for default sorting (A low, K high), 's' for suit sorting (diamonds - spades).",
                brief="Set sorting type",
                aliases=['ss'],
                pass_context=True)
async def setSort(ctx, sortType: str = None):
    loadData()
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
    global gameList, gameIndex
    if checkInGame(ctx.author):
        await ctx.send("You are already in a game.")
        return

    emoji1 = '1️⃣'
    msg = await ctx.send("**           CHOOSE GAME**\n**-------------------------------**\n**REACT WITH:\n" + emoji1 + " - Texas Hold 'Em**\n**-------------------------------**\n")

    await msg.add_reaction(emoji1)

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
            ID = randrange(100000, 1000000)
            while hasGame(ID):
                ID = randrange(100000, 1000000)
            GAME = TexasHoldEm(ctx.channel, ID)
            gameList.append(GAME)
            await ctx.send("A Texas Hold 'Em game has been created with ID " + str(ID) + ". Use %join " + str(ID) + " to join this game.")


@client.command(description="Join a game that is not yet underway.",
                brief="Join a game that is not yet underway",
                pass_context=True)
async def join(ctx, ID: int):
    loadData()
    if str(ctx.author.id) not in money:
        money.update({str(ctx.author.id): 10000})

    if not hasGame(ID):
        await ctx.send("Invalid game ID.")
        return

    if checkInGame(ctx.author):
        await ctx.send("You have already joined a game.")
        return

    if not channelCheck(getGameByID(ID), ctx.channel):
        await ctx.send("You are not in the specified game's channel. Please go there.")
        return

    GAME = getGameByID(ID)
    if GAME.gameUnderway:
        await ctx.send("This game is already underway. You will be joined in for the next hand.")
        GAME.players.append(str(ctx.author.id))
        GAME.playerStatus.update({str(ctx.author.id): "Fold"})
        return

    GAME.players.append(str(ctx.author.id))
    if str(ctx.author.id) in hands:
        del hands[str(ctx.author.id)]

    await ctx.send(ctx.author.mention + " you joined game " + str(ID))
    dumpData()


@client.command(description="Leave a game you joined (forfeits any bets made if the game was already underway).",
                brief="Leave a game you joined and forfeit any bets made if the game was already underway",
                pass_context=True)
async def leave(ctx):
    if not checkInGame(ctx.author):
        await ctx.send("You did not join any games.")
        return

    GAME = getGame(ctx.author)
    if not channelCheck(GAME, ctx.channel):
        await ctx.send("You are not in the specified game's channel. Please go there.")
        return

    GAME.players.remove(str(ctx.author.id))
    loadData()
    if str(ctx.author.id) in hands:
        del hands[str(ctx.author.id)]
    dumpData()
    await ctx.send(ctx.author.mention + " you left game " + str(GAME.ID))


@client.command(description="Start the game.",
                brief="Start the game",
                pass_context=True)
async def start(ctx):
    if not checkInGame(ctx.author):
        await ctx.send("You are not apart of any active games.")
        return

    GAME = getGame(ctx.author)

    if not channelCheck(GAME, ctx.channel):
        await ctx.send("You are not in the specified game's channel. Please go there.")
        return

    if GAME.gameUnderway:
        await ctx.send("Your game has already begun.")
        return

    await GAME.startGame()


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
@has_permissions(administrator=True)
async def reset(ctx):
    loadData()
    hands.clear()
    dumpData()
    await ctx.send("All user hands have been reset.")


@reset.error
async def reset_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send("You are not authorized to use this command.")
    elif isinstance(error, discord.ext.commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")


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

    dumpData()


client.load_extension('Poker')
client.load_extension('Economy')
client.load_extension('Betting')
client.run(TOKEN)
