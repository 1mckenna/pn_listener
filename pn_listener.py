#!/usr/bin/env python3

import socketio
import json
import argparse
import sys
import os
from queue import *
from deuces import *
from pn_player import Player
from signal import signal, SIGINT

evaluator = Evaluator()
communityCards = []
playerList = []
debugLogging = False
gameLogFile = ""
firstGC = True
firstRUP = True
lastGC=""
lastRUP=""

#sio = socketio.Client(engineio_logger=True, logger=True)
sio = socketio.Client()
sio.eio.logger.setLevel("CRITICAL")
sio.eio.ping_interval = 30
sio.eio.ping_timeout = 30

def handler(signal_received, frame):
    print("\nI'm Dying How Are You?\n")
    if( sio.connected ):
        sio.disconnect()
    exit(0)

def parseArgs():
    global debugLogging
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--game', dest="game", help='pokernow.club game id', nargs=1, required=True)
    parser.add_argument('-n', '--npt', dest="npt", default='', help='pokernow.club npt cookie value (copy from browser)', nargs=1)
    parser.add_argument('-a', '--apt', dest="apt", default='', help='pokernow.club apt cookie value (copy from browser)', nargs=1)
    parser.add_argument('-l', '--log', dest="log", default='', help='Enable Game Logging', nargs=1)
    parser.add_argument('-d', '--debug', dest="debug", default=False, action='store_true', help='Enable Debug Logging (saves to ./debug.log)')
    args = parser.parse_args()
    if not args.game and (not args.npt or not args.apt):
        print("You must a gameid and a npt/apt cookie value")
        raise SystemExit(-1)
    if(args.debug):
        #Enable Debug Logging
        debugLogging = True
    return args

class rup(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

class gameComm(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)   

def getPrintPrettyStr(card_ints):
    output = " "
    for i in range(len(card_ints)):
        c = card_ints[i]
        if i != len(card_ints) - 1:
            output += Card.int_to_pretty_str(c) + ","
        else:
            output += Card.int_to_pretty_str(c) + " "
    return output


def isKnownPlayer(strPlayerID):
    global playerList
    for p in playerList:
        if( p.playerID == strPlayerID):
            return True
    return False

def returnPlayerIndex(strPlayerID):
    global playerList
    count = 0
    for p in playerList:
        if( p.playerID == strPlayerID):
            return count
        count = count + 1
    return -1

def muckCards():
    global playerList
    for p in playerList:
        p.clearHoleCards()

def printPlayerList():
    global playerList
    for player in playerList:
        print(str(player.get_name()) + " ["+player.playerID+"]\t<" + player.get_playerstatus() +">\t "+str(player.get_stacksize())+" c")

def writeGameLog(inputStr):
    global gameLogFile
    with open(gameLogFile[0], 'a') as logFile:
        logFile.write(inputStr + '\n')    

def writeDebugLog(inputStr):
    with open("debug.log", 'a') as logFile:
        logFile.write(inputStr + '\n')

#SocketIO Code
@sio.event
def connect():
    try:
        pass
    except Exception as e:
        print("connect: ")
        print(e)

@sio.on('gC')
def my_gc_event(data):
    global firstGC
    global lastGC
    try:
        if(firstGC):
            firstGC=False
            lastGC = data
            parseGCEvent(data)
        else:
            if(lastGC == data):
                #This is a duplice message we do nothing
                pass
            else:
                lastGC = data
                parseGCEvent(data)
        if(len(playerList) == 0):
            sio.emit("action", data={"type":"RUP"},callback=2)
        # if not sio.connected:
        #     sio.emit("action", data={"type":"RUP"},callback=2)
        #sio.emit("action", data={"type":"RUP"},callback=2)
        sio.sleep(1)
    except Exception as e:
        print("gc: ")
        print(e)

def updatePlayerList():
    #emit event to update player list
    print("Requesting Player Update")
    try:
        sio.emit("action", data={"type":"RUP"},callback=2)
    except Exception as e:
        print("updateplayer: ")
        print(e)

@sio.on('rup')
def my_rup_event(data):
    global firstRUP
    global lastRUP
    try:
        if(firstRUP):
            firstRUP = False
            lastRUP = data
            myrup = rup(json.dumps(data, default=lambda o: o.__dict__, indent=4))
            parseRUPEvent(myrup)
            return 2
        else:
            if(lastRUP == data):
                #This is a duplice message we do nothing
                pass
            else:
                lastRUP = data
                myrup = rup(json.dumps(data, default=lambda o: o.__dict__, indent=4))
                parseRUPEvent(myrup)
        sio.sleep(1)
    except Exception as e:
        print("rup: ")
        print(e)

@sio.event
def disconnect():
    try:
        pass
    except Exception as e:
        print("disconnect: ")
        print(e)

def start_server(gameID, cookieVal):
    try:
        sio.connect('https://www.pokernow.club/socket.io/?gameID='+gameID, wait=True, wait_timeout=60, transports="websocket", headers={
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'Upgrade',
        'Host': 'www.pokernow.club',
        'Origin': 'https://www.pokernow.club',
        'Pragma': 'no-cache',
        'Sec-WebSocket-Extensions':'client_max_window_bits',
        'Sec-WebSocket-Version': '13',
        'Upgrade': 'websocket',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'Cookie': cookieVal
        })
    except Exception as e:
        print("start-server exception")
        print(e)
        # pass
#END SocketIO Code

def parseRUPEvent(evtData):
    global playerList
    global debugLogging
    if(debugLogging):
        writeDebugLog(str(json.dumps(evtData, default=lambda o: o.__dict__, indent=4)))
    for player in evtData.players.keys():
        if(len(playerList) > 0):
            #Check if Player ID Exists
            if( isKnownPlayer(str(evtData.players[player]['id']))):
                #Get Player Item # so we can update them
                itemNum = returnPlayerIndex(str(evtData.players[player]['id']))
                #Update Player
                playerList[itemNum].set_name(str(evtData.players[player]['name']))
                playerList[itemNum].set_stacksize(evtData.players[player]['stack'])
                playerList[itemNum].set_playerstatus(evtData.players[player]['status'])
            else:
                #Add Player
                p = Player(str(evtData.players[player]['id']))
                p.set_name(str(evtData.players[player]['name']))
                playerList.append(p)
        else:
            #Add Player
            p = Player(str(evtData.players[player]['id']))
            p.set_name(str(evtData.players[player]['name']))
            playerList.append(p)
    
def parseGCEvent(evtData):
    global evaluator
    global communityCards
    global playerList
    global debugLogging
    global gameLogFile
    if(debugLogging):
        writeDebugLog(json.dumps(evtData, default=lambda o: o.__dict__, indent=4))
    if( "pC" in evtData.keys()):
        for player in evtData['pC'].keys():
            if( "cards" in evtData['pC'][player]):
                c1 = Card.new(evtData['pC'][player]['cards'][0])
                c2 = Card.new(evtData['pC'][player]['cards'][1])
                itemNum = returnPlayerIndex(str(player))
                try:
                    playerList[itemNum].set_holecards( [ c1, c2 ] )
                    if( len(communityCards) > 2 ):
                        print("Community Cards ("+str(len(communityCards))+"): " + getPrintPrettyStr(communityCards))
                        print(str(playerList[itemNum].get_name()) + " Cards: " + getPrintPrettyStr(playerList[itemNum].get_holecards()) + "("+ evaluator.class_to_string( evaluator.get_rank_class( evaluator.evaluate(communityCards, playerList[itemNum].get_holecards() ) ) ) +")")
                        if not (gameLogFile == ''):
                            writeGameLog("Community Cards ("+str(len(communityCards))+"): " + getPrintPrettyStr(communityCards))
                            writeGameLog(str(playerList[itemNum].get_name()) + " Cards: " + getPrintPrettyStr(playerList[itemNum].get_holecards()) + "("+ evaluator.class_to_string( evaluator.get_rank_class( evaluator.evaluate(communityCards, playerList[itemNum].get_holecards() ) ) ) +")")

                    else:
                        print(str(playerList[itemNum].get_name()) + " Cards: " + getPrintPrettyStr(playerList[returnPlayerIndex(str(player))].get_holecards()))
                        if not (gameLogFile == ''):
                            writeGameLog(str(playerList[itemNum].get_name()) + " Cards: " + getPrintPrettyStr(playerList[returnPlayerIndex(str(player))].get_holecards()))
                except:
                    pass
    if( "oTC" in evtData.keys()):
        #Clear Board Cards So we can just add them all
        communityCards.clear()
        for cCard in evtData['oTC']['1']:
            communityCards.append(Card.new(cCard))
        if( len(communityCards) > 2):
            print("Community Cards: "+ getPrintPrettyStr(communityCards))
            if not (gameLogFile == ''):
                writeGameLog("Community Cards: "+ getPrintPrettyStr(communityCards))
    if("gameResult" in evtData.keys()):
        if(type(evtData['gameResult']) == dict):
            #When we see gameResult the hand is ended
            print("Hand Complete")
            if not (gameLogFile == ''):
                writeGameLog("Hand Complete")
            #Clear Board Cards
            communityCards.clear()
            #Clear Player Cards
            muckCards()
            #Request for an update to the players list
            updatePlayerList()
            #Print PlayerList
            printPlayerList()
    #if("cHB" in evtData.keys()):
    #    print("cHB: " + str(json.dumps(evtData['cHB'], default=lambda o: o.__dict__, indent=4)))
    #if("tB" in evtData.keys()):
    #    for player in evtData['tB'].keys():
    #        print(player + " tB: " + str(json.dumps(evtData['tB'][player], default=lambda o: o.__dict__, indent=4)))
            #print(str(player) + " Action: " + str(evtData['tB'][player]))#<D> seems to be N/A, check ==check # is amount bet
    #if("gT" in evtData.keys()):
    #    print("gT" + str(json.dumps(evtData['gT'], default=lambda o: o.__dict__, indent=4)))

#Create our Cookie String with APT/NPT values
def getCookieVal(aptVal, nptVal):
    cookieStr=""
    if(aptVal != ''):
        cookieStr +='apt='+aptVal[0]+';'
    if(nptVal != ''):
        cookieStr +='npt='+nptVal[0]+';'
    return cookieStr

def main():
    pass

if __name__ == '__main__':
    args = parseArgs()
    if not (args.log == ''):
        gameLogFile = args.log
    signal(SIGINT, handler)
    try:
        sio.start_background_task(start_server(args.game[0], getCookieVal(args.apt, args.npt)))
        sio.wait()
    except Exception as e:
        print(e)
    while True:
        pass