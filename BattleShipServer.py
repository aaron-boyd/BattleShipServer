import random
import socket


class Player:
    name = ''
    hostname = ''
    messages = []
    opponentIP = ''
    ready = False

    def __init__(self, h):
        self.hostname = h
        self.messages = []
        self.opponentIP = ''

    def sendMessages(self, client):
        message = ''
        print('Player messages: ', self.messages)
        for m in self.messages:
            message += m + '-'
        client.send(message.encode())
        self.messages = []

    def addMessage(self, msg):
        self.messages.append(msg)


class Server():
    playerList = [Player('') for count in range(0)]
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = ''
    port = 0
    running = False

    def __init__(self):

        self.hostname = '10.24.131.127'
        self.getPort(self.serverSock)
        self.serverSock.listen(32)
        self.serverSock.setblocking(False)
        self.start()


    def run(self):
        self.connect()

    def start(self):
        self.run()

    def connect(self):
        print("Listening on", self.hostname, ":", self.port, "\n-------------------------------------------")
        while True:
            try:
                client, address = self.serverSock.accept()
                player = self.isInList(address[0])
                print('Connected to', address[0], ":", address[1])
                if player is not None:
                    print("Player is in the list")
                    if self.hasEnemy(player.hostname):  # Player has enemy
                        self.handlePlayerWithOpponent(player, client)
                    else:  # Player has no enemy
                        self.handlePlayerWithoutOpponent(player, client)
                else:  # New Player
                    self.handleNewPlayer(client, address)
                client.close()
                print("Client lost\n--------------------------------------------------------------")

            except:
                pass

    def getPort(self, socket):
        passed = False
        while not passed:
            try:
                port = random.randint(0, 1500) + 5000
                self.serverSock.bind((self.hostname, port))
                self.port = port
                passed = True
            except:
                pass

    def handlePlayerWithOpponent(self, player, client):
        print("Player has enemy")
        enemy = self.getEnemy(player.hostname)
        print('Enemy IP:', enemy.hostname)
        self.handleMessage(player, enemy, client)

    def handlePlayerWithoutOpponent(self, player, client):
        print("Player does not have enemy")
        for other in self.playerList:  # Search for opponent
            if self.connectPlayers(player, other) == True:  # Opponent found
                break
        self.handleNullMessage(player, client)

    def handleNewPlayer(self, client, address):
        print('New Player')
        player = Player(address[0])
        self.playerList.append(player)
        player.name = client.recv(1024).decode()[5:-1]
        player.addMessage('NULL')
        player.sendMessages(client)

    def handleMessage(self, player, enemy, client):
        message = client.recv(1024).decode()[:-2]
        print("Message from player: ", message)

        if 'LEAVE' in message:
            enemy.addMessage('LEAVE')
            player.addMessage('NULL')
        elif 'CLOSE' in message:
            enemy.addMessage('CLOSE')
            player.addMessage('CLOSE')
        elif 'FINISHED_PLACING_SHIPS' in message:
            player.ready = True
            if player.ready and enemy.ready:
                player.addMessage('SET_TURN-FALSE')
                enemy.addMessage('SET_TURN-TRUE')
            else:
                player.addMessage('NULL')
        elif 'SET_TURN' in message:
            turn = message[9:-1]
            enemy.addMessage('SET_TURN')
            enemy.addMessage(turn)
            player.addMessage('NULL')
        elif 'RESULT' in message:
            if 'HIT' in message:
                enemy.addMessage('RESULT-HIT')
                enemy.addMessage('SET_TURN-TRUE')
                player.addMessage('SET_TURN-FALSE')
            elif 'MISS' in message:
                enemy.addMessage('RESULT-MISS')
                enemy.addMessage('SET_TURN-FALSE')
                player.addMessage('SET_TURN-TRUE')
            elif 'SINK' in message:
                enemy.addMessage(message)
                enemy.addMessage('SET_TURN-TRUE')
                player.addMessage('SET_TURN-FALSE')
        elif 'MOVE' in message:
            print('Move: ', message)
            enemy.addMessage(message)
            player.addMessage('NULL')
        elif 'END_GAME' in message:
            enemy.addMessage('END_GAME')
            player.addMessage('END_GAME')
        else:
            enemy.addMessage('NULL')
            player.addMessage('NULL')

        player.sendMessages(client)

    def handleNullMessage(self, player, client):
        message = client.recv(1024).decode()[:-2]
        print(message)
        player.addMessage('NULL')
        player.sendMessages(client)

    def isInList(self, hostname) -> Player:
        for p in self.playerList:
            if p.hostname == hostname:
                return p
        return None

    def hasEnemy(self, hostname) -> bool:
        for p in self.playerList:
            if p.opponentIP == hostname:
                return True
        return False

    def getEnemy(self, hostname) -> Player:
        for p in self.playerList:
            if p.opponentIP == hostname:
                return p
        return None

    def getPlayer(self, hostname) -> Player:
        for p in self.playerList:
            if p.hostname == hostname:
                return p
        return None

    def findEnemy(self, hostname) -> Player:
        for p in self.playerList:
            if p.opponentIP == '' and p.hostname != hostname:
                return p
        return None

    def connectPlayers(self, player1, player2) -> bool:
        print("Attempting to connect players")
        if player1.opponentIP == '' and player2.opponentIP == '':
            if player1.hostname != player2.hostname:
                player1.opponentIP = player2.hostname
                player2.opponentIP = player1.hostname
                player1.addMessage('SET_OPPONENT_NAME')
                player1.addMessage(player2.name)
                player2.addMessage('SET_OPPONENT_NAME')
                player2.addMessage(player1.name)
                print('Connected players!')
                return True
        print("Failed to connect players")
        return False


s= Server()
