def exitProg():
    print ("Exiting...")
    y="wuh oh"
    while (y == "wuh oh"):
        y = input("Press enter to leave the program: ")
        quit()

from json import load

#All of the values
songs = []
categories = []
traps = []
musicSheet = ""
gameName = ""
playerName = ""
fillerName = ""

#Set up item json
try:
    itemFile = open("items.json", "r")
except:
    print("items.json File Not Found!")
    exitProg()

jsonInput = load(itemFile)
itemFile.close()

#setup game json
try:
    gameFile = open("game.json", "r")
except:
    print("game.json File Not Found!")
    exitProg()

jsonGameInput = load(gameFile)
gameFile.close()

for i in jsonInput:
    catList = i["category"]
    if catList[0] == "(Traps)":
        traps.append(i["name"])
    elif catList[0] != "(Goal Information Item)" and catList[0] != "(Songs)":
        musicSheet = (i["name"])
    elif catList [0] == "(Goal Information Item)":
        pass
    else:
        songs.append(i["name"])
        try:
            if catList[1] in categories:
                pass
            else:
                categories.append(catList[1])              
        except:
            pass

gameName = jsonGameInput["game"]
playerName = jsonGameInput["player"]
fillerName = jsonGameInput["filler_item_name"]


songRemake = open("song.txt", "w")
songRemake.write("#Any \"comment\" in these files start with #.")
songRemake.write("\n#Items here must be on a new line.\n")
songRemake.write("#List: " + gameName + " - Created By: " + playerName + "\n\n")

songRemake.write("#$game=" + gameName + "\n")
songRemake.write("#$creator=" + playerName + "\n")
songRemake.write("#$filler_item_name=" + fillerName + "\n")
songRemake.write("#$musicSheet=" + musicSheet + "\n")
if traps:
    songRemake.write("#$traps=")
    y = 0
    for t in traps:
        songRemake.write(t)
        if y+1 != len(traps):
            songRemake.write(", ")
        y = y+1
songRemake.write("\n")

if(categories):
    categories.sort()
    for cat in categories:
        songRemake.write("\n##" + cat+"\n\n")
        for song in songs:
            for i in jsonInput:
                catList = i["category"]
                if i["name"] == song:
                    if catList[1] == cat:
                        songRemake.write(song +"\n")

else:
    for song in songs:
        songRemake.write(song + "\n")

songRemake.close()

