#!/usr/bin/env python3

import asyncio
import socketio
import json
import argparse
from deuces import *

evaluator = Evaluator()
communityCards = []
#sio = socketio.Client(engineio_logger=True, logger=True)
sio = socketio.Client()


firstGC = True
firstRUP = True
lastGC=""
lastRUP=""

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--game', dest="game", help='pokernow.club game id', nargs=1, required=True)
    parser.add_argument('-n', '--npt', dest="npt", default='', help='pokernow.club npt cookie value (copy from browser)', nargs=1)
    parser.add_argument('-a', '--apt', dest="apt", default='', help='pokernow.club apt cookie value (copy from browser)', nargs=1)
    args = parser.parse_args()
    if not args.game and (not args.npt or not args.apt):
        print("You must a gameid and a npt/apt cookie value")
        raise SystemExit(-1)
    return args

class rup(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

class player(object):
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



#SocketIO Code
@sio.event
def connect():
    print('connection established')


@sio.on('gC')
#async def my_event(data):
def my_gc_event(data):
    global firstGC
    global lastGC
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
    #if not sio.connected:
    #    sio.emit("action", data={"type":"RUP"},callback=2)
    #sio.emit("action", data={"type":"RUP"},callback=2)

@sio.on('rup')
#async def my_event(data):
def my_rup_event(data):
    global firstRUP
    global lastRUP
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

@sio.event
def disconnect():
    print('disconnected from server')

#async def start_server(gameID, cookieVal):
def start_server(gameID, cookieVal):
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
    sio.wait()
#END SocketIO Code

#async def parseRUPEvent(evtData):
def parseRUPEvent(evtData):
    for player in evtData.players.keys():
        print("Name: "+str(evtData.players[player]['name'])+"\tID:"+evtData.players[player]['id']+"\t("+str(evtData.players.values())+")")
    
#async def parseGCEvent(evtData):
def parseGCEvent(evtData):
    global evaluator
    global communityCards
    #print(json.dumps(evtData, default=lambda o: o.__dict__, indent=4))
    if( "pC" in evtData.keys()):
        for player in evtData['pC'].keys():
            if( "cards" in evtData['pC'][player]):
                c1 = Card.new(evtData['pC'][player]['cards'][0])
                c2 = Card.new(evtData['pC'][player]['cards'][1])
                hand = [c1, c2] 
                if( len(communityCards) > 2 ):
                    print("Community Cards ("+str(len(communityCards))+"): " + getPrintPrettyStr(communityCards))
                    print(str(player)+" Cards: " + getPrintPrettyStr(hand) + "("+ evaluator.class_to_string(evaluator.get_rank_class(evaluator.evaluate(communityCards,hand))) +")")
                else:
                    print(str(player)+" Cards: " + getPrintPrettyStr(hand))

    if( "oTC" in evtData.keys()):
        #print("Community Cards: " + str(evtData['oTC']))
        #Clear Board Cards So we can just add them all
        communityCards.clear()
        for cCard in evtData['oTC']['1']:
            communityCards.append(Card.new(cCard))
        if( len(communityCards) > 2):
            print("Community Cards: "+ getPrintPrettyStr(communityCards))
    if("gameResult" in evtData.keys()):
        if(type(evtData['gameResult']) == dict):
            #When we see gameResult the hand is ended
            print("Hand Complete")
            #Clear Board Cards
            communityCards.clear()

            #print("gameResult: " + str(json.dumps(evtData['gameResult'], default=lambda o: o.__dict__, indent=4)))
    #if("pGS" in evtData.keys()):
    #    print("Player Status" + str(evtData['pGS']))
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

#async def main():
def main():
    args = parseArgs()
    start_server(args.game[0], getCookieVal(args.apt, args.npt))

if __name__ == '__main__':
    main()