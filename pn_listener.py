#!/usr/bin/env python3

import asyncio
import socketio
import json
import argparse

#sio = socketio.Client(engineio_logger=True, logger=True)
sio = socketio.Client()
#sio = socketio.AsyncClient(engineio_logger=True, logger=True)
#sio = socketio.AsyncClient()

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

#SocketIO Code
@sio.event
def connect():
    print('connection established')


@sio.on('gC')
#async def my_event(data):
def my__gc_event(data):
    parseGCEvent(data)
    #if not sio.connected:
    #    sio.emit("action", data={"type":"RUP"},callback=2)
    #sio.emit("action", data={"type":"RUP"},callback=2)

@sio.on('rup')
#async def my_event(data):
def my_rup_event(data):
    myrup = rup(json.dumps(data, default=lambda o: o.__dict__, indent=4))
    parseRUPEvent(myrup)
    return 2

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
    #print(json.dumps(evtData, default=lambda o: o.__dict__, indent=4))
    if( "pC" in evtData.keys()):
        for player in evtData['pC'].keys():
            if( "cards" in evtData['pC'][player]):
                print("Player Cards:" + str(evtData['pC'][player]['cards']))
    if( "oTC" in evtData.keys()):
        print("Community Cards: " + str(evtData['oTC']))
    #if("players" in evtData.keys()):
    #    if not (evtData['players'] is None):
    #        print("Players: " + str(evtData['players']))
    if("gameResult" in evtData.keys()):
        print("gameResult" + str(json.dumps(evtData['gameResult'], default=lambda o: o.__dict__, indent=4)))
    #if("pGS" in evtData.keys()):
    #    print("Player Status" + str(evtData['pGS']))

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