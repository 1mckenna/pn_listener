
class Player:
    "Player Class for pn_listener"
    playerID = ""
    playerStatus = "unknown"
    playerName = ""
    playerHand = []
    playerStackSize = 0

    def __init__(self, playerID):
        self.playerID = playerID
    
    def set_name(self, pName):
        self.playerName = pName
    
    def get_name(self):
        return self.playerName
    
    def set_stacksize(self, stack):
        self.playerStackSize = stack

    def get_stacksize(self):
        return self.playerStackSize

    def clearHoleCards(self):
        self.playerHand.clear()

    def set_holecards(self, holeCardList):
        self.playerHand = holeCardList

    def get_holecards(self):
        return self.playerHand

    def get_playerstatus(self):
        return self.playerStatus

    def set_playerstatus(self, pStatus):
        self.playerStatus = pStatus
