# FOR COMBO RECOGNITION AND EVALUATION

# Check for a flush
def hasFlush(__suits):
    for suit in __suits:
        if suit != __suits[0]:
            return False
    return True


# Find a straight in a set of 5 cards
def hasStraight(__cards):
    __cards.sort()
    return __cards[0] == __cards[1] - 1 == __cards[2] - 2 == __cards[3] - 3 == __cards[4] - 4


# Find a quadruple in a set of 5 cards
def hasQuad(__cards):
    __cards.sort()
    cardSet = set(__cards)
    if len(cardSet) > 2:
        return False

    for x in cardSet:
        matches = 0
        for y in __cards:
            if x == y:
                matches += 1
        if matches == 4:
            return True
    return False


# Find a triple in a set of 5 cards
def hasTriple(__cards):
    __cards.sort()
    cardSet = set(__cards)
    if len(cardSet) > 3:
        return False

    for x in cardSet:
        matches = 0
        for y in __cards:
            if x == y:
                matches += 1
        if matches == 3:
            return True

    return False


# Find the number of pairs in a set of 5 cards
def num_pairs(__cards):
    res = 0
    for i in range(0, len(__cards)):
        for j in range(i + 1, len(__cards)):
            if __cards[i] == __cards[j]:
                res += 1
    return res


# Find a pair of values in a set of 5 cards
def get_pair(__cards):
    for i in range(0, len(__cards)):
        for j in range(i + 1, len(__cards)):
            if __cards[i] == __cards[j]:
                return __cards[i]


# Get the sum of values of a hand
def get_sum(__cards):
    res = 0
    for i in range(0, len(__cards)):
        res += __cards[i]
    return res


# Score a 5 card hand with a numerical value
def evaluateHand(cards):
    cardVals = []
    cardSuits = []
    conversion = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    for card in cards:
        if len(card) == 11:
            if card[5] == 'J' or card[5] == 'Q' or card[5] == 'K' or card[5] == 'A':
                cardVals.append(conversion[card[5]])
            else:
                cardVals.append(int(card[5]))
            cardSuits.append(card[6])
        else:
            cardVals.append(10)
            cardSuits.append(card[7])

    cardVals.sort()

    royalFlush = hasFlush(cardSuits) and cardVals[0] == 10
    flush = hasFlush(cardSuits)
    straight = hasStraight(cardVals)
    fourKind = hasQuad(cardVals)
    fullHouse = hasTriple(cardVals) and num_pairs(cardVals) == 4
    triple = hasTriple(cardVals) and num_pairs(cardVals) == 3
    twoPair = num_pairs(cardVals) == 2
    onePair = num_pairs(cardVals) == 1 and not hasTriple(cardVals)

    if royalFlush:
        return 30000
    elif flush and straight:
        return 15000 + cardVals[len(cardVals) - 1]
    elif fourKind:
        value = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value]
        return 12000 + value * 30 + cardVals[0]
    elif fullHouse:
        value = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value]
        if len(cardVals) == 2:
            value *= 30
            value += cardVals[0] * 4
        else:
            value *= 4
            value += cardVals[0] * 30
        return 8000 + value
    elif flush:
        return 7000 + cardVals[len(cardVals) - 1]
    elif straight:
        return 6000 + cardVals[len(cardVals) - 1]
    elif triple:
        value = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value]
        return 4000 + value * 30 + cardVals[0] + cardVals[1]
    elif twoPair:
        value1 = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value1]
        value2 = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value2]
        return 3000 + value1 * 30 + value2 * 30 + cardVals[0]
    elif onePair:
        value = get_pair(cardVals)
        cardVals = [v for v in cardVals if v != value]
        return 2000 + value * 20 + get_sum(cardVals)
    else:
        return 1000 + cardVals[4] * 5 + cardVals[3] * 4 + cardVals[2] * 3 + cardVals[1] * 2 + cardVals[0]


# Return a string corresponding to combo type
def handType(handValue):
    if 1000 <= handValue < 2000:
        return "High Card"
    elif 2000 <= handValue < 3000:
        return "One Pair"
    elif 3000 <= handValue < 4000:
        return "Two Pairs"
    elif 4000 <= handValue < 6000:
        return "Three of a Kind"
    elif 6000 <= handValue < 7000:
        return "Straight"
    elif 7000 <= handValue < 8000:
        return "Flush"
    elif 8000 <= handValue < 12000:
        return "Full House"
    elif 12000 <= handValue < 15000:
        return "Four of a Kind"
    elif 15000 <= handValue < 30000:
        return "Straight Flush"
    elif handValue >= 30000:
        return "Royal Flush"
