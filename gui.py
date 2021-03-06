import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import random
import cards
import Assets
import threading
import time
import socket


# Window setup
window = tk.Tk()
window.title("PCSS Project - Lukas Kristensen")
window.geometry("1200x700")
window.resizable(False, False)

cardObjects, playerCards, shopCards, boardArray, shopArray = [], [], [], ["", "", "", "", "", "", "", "", "", ""], ["", "", "", "", ""]

# Loads the assets into the program with the ImageTkinter image format
for x in range(len(Assets.cardImg)):
    Assets.cardImg[x] = ImageTk.PhotoImage(Assets.cardImg[x])

for x in range(len(Assets.shopImg)):
    Assets.shopImg[x] = ImageTk.PhotoImage(Assets.shopImg[x])

cardImgLen = len(Assets.cardImg)-1

# Loading non categorised assets into the program
bgPT = ImageTk.PhotoImage(Assets.bg1)
backgroundL = Label(image=bgPT)

textBut = Image.open("Assets/testButtonTexture.jpg")
textButPT = ImageTk.PhotoImage(textBut)

CDunknown = Image.open("Assets/unknown1low.jpg")
CDunknownPT = ImageTk.PhotoImage(CDunknown)

runCheck = False
# Array of events from the combat, which is being animated for the user in the moveCard() function
queueEvents = []

def clientServerReceive():
    # Next 7 lines made with help from the lecture 7 powerpoint: "Lecture 7: Network Programming", by Jesper Rindom Jensen
    s = socket.socket()
    port = 20000
    s.connect(('127.0.0.1', port))
    messageRecv = s.recv(1024)
    messageRecv = messageRecv.decode()
    splitMsg = messageRecv.split(' ')
    time.sleep(0.0001)
    print("[SERVER]:",messageRecv)

    if splitMsg[0] == "combat":
        queueEvents.append(splitMsg)
        moveCard()

    if splitMsg[0] == "EnemyBoard":
        print("[SYSTEM]: Received enemy board from server")
        for c in range(5,10):
            if (boardArray[c] == ""):
                cardPlaceStrHold = cards.Cards()
                cardPlaceStrHold.searchData(str(splitMsg[c-4]))
                playerCards[c].configure(image=Assets.cardImg[int(splitMsg[c-4])])
                playerCards[c].configure(text="\n\n\n\n\n\n\n\n\n\n\n" + str(cardPlaceStrHold.get_damage()) + "                " + str(cardPlaceStrHold.get_health()))
                boardArray[c] = splitMsg[c-4]
                if len(cardObjects) > c:
                    cardObjects[c] = cardPlaceStrHold
                cardObjects.append(cardPlaceStrHold)

    if messageRecv == "Close":
        print("System message: Closing serverReceive()...")
        s.close()

    if messageRecv != "Close":
        clientServerReceiveStart()

def clientServerReceiveStart():
    # Function for threading the clientServerReceive function
    threadSend = threading.Thread(target=clientServerReceive)
    threadSend.start()
    if len(queueEvents)>0:
        print("Server:", queueEvents[len(queueEvents)-1])

def serverSend(boardArray):
    # Next 15 lines made with help from the lecture 7 powerpoint: "Lecture 7: Network Programming", by Jesper Rindom Jensen
    s = socket.socket()
    port = 20001
    print("PORT CREATED SERVER_SENDING")
    s.bind(('', port))
    print("Socket binded to %s" % (port))
    s.listen(5)
    print("SOCKET LISTENING")

    while True:
        c, addr = s.accept()
        print("Got information from", addr)
        output = (str(boardArray[4])+" "+str(boardArray[3])+" "+str(boardArray[2])+" "+str(boardArray[1])+" "+str(boardArray[0]))
        c.sendall(output.encode("utf-8"))
        return True

def moveCard():
    # Simulates the game in the GUI, by animating the game events received from the server
    animationSpeed = 0.04
    framesPerAnimation = 11
    while len(queueEvents) > 0:
        if queueEvents[0][1]=="Player1":
            for i in range (framesPerAnimation):
                lengthAD = int(queueEvents[0][3])-int(queueEvents[0][5])
                perMove = (lengthAD*120)/framesPerAnimation
                defaultCardX = -720-((int(queueEvents[0][3]) - 5) * 120)
                playerCards[int(queueEvents[0][3])].place(y = 350-(i*8), x=defaultCardX+(i*perMove))
                time.sleep(animationSpeed)
                if i == 10:
                    cardObjects[int(queueEvents[0][3])].losehp(cardObjects[int(queueEvents[0][5])+5].get_damage())
                    cardObjects[int(queueEvents[0][5])+5].losehp(cardObjects[int(queueEvents[0][3])].get_damage())
                    displayGUI.updateCards(self="")

            for i in range (framesPerAnimation):
                playerCards[int(queueEvents[0][3])].place(y = 270+(i*8), x=defaultCardX+(framesPerAnimation*perMove)-(i*perMove))
                if i == 10:
                    playerCards[int(queueEvents[0][3])].place(y=350, x=defaultCardX)
                time.sleep(animationSpeed)
            queueEvents.pop(0)
            return

        if queueEvents[0][1]=="Player0":
            for i in range (framesPerAnimation):
                lengthAD = int(queueEvents[0][3]) - int(queueEvents[0][5])
                perMove = (lengthAD * 120) / framesPerAnimation
                defaultCardX = 480 - ((int(queueEvents[0][3])+5) * 120)
                playerCards[int(queueEvents[0][3])+5].place(y = 100+(i*8), x=defaultCardX+(i*perMove))
                time.sleep(animationSpeed)
                if i == 10:
                    cardObjects[int(queueEvents[0][3])+5].losehp(cardObjects[int(queueEvents[0][5])].get_damage())
                    cardObjects[int(queueEvents[0][5])].losehp(cardObjects[int(queueEvents[0][3])+5].get_damage())
                    displayGUI.updateCards(self="")
            for i in range (framesPerAnimation):
                playerCards[int(queueEvents[0][3])+5].place(y = 188-(i*8), x=defaultCardX+(framesPerAnimation*perMove)-(i*perMove))
                time.sleep(animationSpeed)
                if i == 10:
                    playerCards[int(queueEvents[0][3])+5].place(y=100, x=defaultCardX)
            queueEvents.pop(0)


def shopBuy(shopNumber):
    # Updates the server board depending on the shop number the player bought
    if len(cardObjects) < 5:
        for i in range(cardImgLen+1):
            # Checks if the shopNumber is equal to a number from the data base to identify the shop number
            if shopArray[shopNumber] == i:
                for c in range(5):
                    # Checks if the space is empty
                    if (boardArray[c] == ""):
                        # Loads data into the game board
                        cardPlaceStrHold = cards.Cards()
                        cardPlaceStrHold.searchData(str(i))
                        playerCards[c].configure(image=Assets.cardImg[i])
                        playerCards[c].configure(text="\n\n\n\n\n\n\n\n\n\n\n" + str(cardPlaceStrHold.get_damage()) + "                " + str(cardPlaceStrHold.get_health()))
                        boardArray[c] = i
                        if len(cardObjects) > c:
                            cardObjects[c] = cardPlaceStrHold
                        cardObjects.append(cardPlaceStrHold)
                        return


def shopRandom():
    # Randomizes shop cards
    for i in range(5):
        rand = random.randint(0, cardImgLen)
        shopCards[i].configure(image=Assets.shopImg[rand])
        shopArray[i] = rand
    if len(cardObjects) > 0:
        displayGUI.updateCards(self="")
        displayGUI(True)

def endRound():
    # When the player presses the "end round" button the game begins
    if len(cardObjects)<5:
        print("System message: Select 5 cards to begin the game...")
    # Starts a new thread to animating the game
    if len(cardObjects)==5:
        threadSend = threading.Thread(target=moveCard)
        threadSend.start()

        displayGUI.updateCards("")
        clientServerReceiveStart()
        serverSend(boardArray)
    elif len(cardObjects)>8:
        print("System message: Game ended")

def cardSelect(cardNumber):
    # If the player presses on a card it is removed from the game
    if len(cardObjects) < 6:
        boardArray[cardNumber] = ""
        playerCards[cardNumber].configure(image=CDunknownPT, text="")
        displayGUI.updateCards(self="")
        try: cardObjects.pop(cardNumber-1)
        except IndexError: print("System message: No active cards to delete")

    if len(cardObjects) > 5:
        print("System message: Can't make any board changes while the game is running")



class displayGUI():
    # GUI Set-up made with help from: https://www.geeksforgeeks.org/python-gui-tkinter/
    def __init__(self, runcheck: bool):
        # Places the player cards
        for i in range(10):
            if i < 5:
                playerCards[i].place(relx=1, x=-720 - ((i - 5) * 120), y=350, anchor=NE)
            if i >= 5:
                playerCards[i].place(relx=1, x=480 - (i * 120), y=100, anchor=NE)

        # Places the shop cards
        for i in range(5):
            shopCards[i].place(relx=1, x=-1150, y=110 + (i * 95), anchor=NW)

        # Places the "end round" button
        sceneUpdateButton = tk.Button(window, width=250, height=50, image=textButPT, compound=LEFT, command=endRound)
        sceneUpdateButton.place(relx=1, x=-500, y=620, anchor=NE)

        # Places the background
        backgroundL.grid(row=0, column=0)
        window.mainloop()

    def updateCards(self):
        # Updates card information for each GUI card element
        for i in range(len(cardObjects)):
            if int(cardObjects[i].get_health())<1:
                boardArray[i]=""
            if boardArray[i] != "":
                playerCards[i].configure(text="\n\n\n\n\n\n\n\n\n\n\n" + str(cardObjects[i].get_damage()) + "                " + str(cardObjects[i].get_health()))
            if boardArray[i] == "":
                playerCards[i].configure(text="", image=CDunknownPT)

    def setup(self):
        # Creates 10 GUI elements when the program starts for the player cards
        for i in range(10):
            if i < 5:
                stringHolder = tk.Button(window, width=105, height=185, image=CDunknownPT, fg="white", compound=tk.CENTER, command=lambda holder=i: cardSelect(holder))
                playerCards.append(stringHolder)
            else:
                stringHolder = tk.Button(window, width=105, height=185, image=CDunknownPT, fg="white", compound=tk.CENTER, command=lambda holder=i: cardSelect(holder))
                playerCards.append(stringHolder)

        # Creates 5 GUI elements when the program starts for the shop elements
        for i in range(5):
            stringHolder = tk.Button(window, width=290, height=95, command=lambda holder=i: shopBuy(holder))
            shopCards.append(stringHolder)
        shopRandom()
