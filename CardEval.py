import itertools


def hasFlush(__suits):
    for suit in __suits:
        if suit != __suits[0]:
            return False
    return True


def hasStraight(__cards):
    __cards.sort()
    for card in __cards:
        print(card)
    return __cards[0] == __cards[1] - 1 == __cards[2] - 2 == __cards[3] - 3 == __cards[4] - 4


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


def num_pairs(__cards):
    res = 0
    for i in range(0, len(__cards)):
        for j in range(i + 1, len(__cards)):
            if __cards[i] == __cards[j]:
                res += 1
    return res
