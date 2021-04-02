#!/usr/bin/env python3

import asyncio
import socketio
import json
import argparse

#sio = socketio.Client(engineio_logger=True, logger=True)
sio = socketio.Client()

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

#SocketIO Code
@sio.event
def connect():
    print('connection established')

@sio.on('gC')
def my_event(data):
    print(json.dumps(data, indent=4))

@sio.event
def disconnect():
    print('disconnected from server')

def start_server(gameID, cookieVal):
    print('Game: '+gameID + '\tCookie Value: '+cookieVal)
    sio.connect('https://www.pokernow.club/socket.io/?gameID='+gameID+'&EIO=3', wait=True, wait_timeout=60, transports="websocket", headers={
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'Upgrade',
    'Host': 'www.pokernow.club',
    'Origin': 'https://www.pokernow.club',
    'Pragma': 'no-cache',
    'Sec-WebSocket-Extensions':'permessage-deflate; client_max_window_bits',
    'Sec-WebSocket-Version': '13',
    'Upgrade': 'websocket',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'Cookie': cookieVal
    })
    sio.wait()
#'Sec-WebSocket-Key': '',
#END SocketIO Code

#Create our Cookie String with APT/NPT values
def getCookieVal(aptVal, nptVal):
    cookieStr=""
    if(aptVal != ''):
        cookieStr +='apt='+aptVal[0]+';'
    if(nptVal != ''):
        cookieStr +='npt='+nptVal[0]+';'
    print(cookieStr)
    return cookieStr

def main():
    args = parseArgs()
    start_server(args.game[0], getCookieVal(args.apt, args.npt))

    
if __name__ == '__main__':
    main()