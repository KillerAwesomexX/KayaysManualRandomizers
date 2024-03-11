#Version 1.0.1
#Changelog

#I missed one line of code and it made the player's name the same as the game's name. Whoops!

#Version 1.1.0
#This version was done by silasary. Big thanks to her!
#Changelog

#Added support for configuration options within song.txt
#Added support for categories with | after the song name
#Added support for category headers with ## before the category name
#Added support for blank lines in song.txt

#Version 2.0.0
#Changelog

#Converted the original Randomizer into the JSONGenerator
#Removes a lot of the options, as they have been moved to YAML options.
#Locations and Songs generate the maximum amount every time.
#New generic locations have been added for use with hooks/Options.py and hooks/World.py
#New song.txt options, including debug (now that APWorldGoal.txt has been removed), sortDisable, and sheetAmount
#If song.txt is missing, it will now ask for a file - Originally done by superriderth for the
#   previous version of this, I figured I'd add that same functionality for this version
#song.txt now allows Trap definition! Go crazy if you want.
#Song Items will now add the category associated with it.
#Songs are now sorted by default

#Replaced options from the original Randomizer into YAML options.
#These are: Extra Location Percent, Sheet Amount Percent, Song Amount, and Starting Songs
#New options have been added: Force Song/Remove Song, Filler/Trap percent (added by Manual by default), and Duplicate Song percent

#Added some error checking just in case for both song amount and sheet amount
#Sheets and Goal song are now set and told to the player through the multiworld
#   While this needs two items, they're set as filler so it shouldn't mess around with it too much
#Redid the item removal hook since the next() method had me running into errors left and right.
#Ability to force a song into the pool as well as remove one.

#Version 2.1.0 Generator
#Changelog

#Reverted Goal Locking Item culling

#Version 2.2.0 Generator
#Changelog

#Music Sheets are now categorized near the top.


from json import dumps
from math import floor

from tkinter import Tk
from tkinter.filedialog import askopenfilename
#uses for each import
#json uses dumps for encoding dictionary/arrays to the output
#floor is needed cause im dumb and i hate floats (sorry anyone named float this comment wasn't for you)
#tkinter for a song.txt dialog box in case one was not found.

#Adds Locations

def addLocations(songList: list[str], musicSheet, config: dict[str,str]):
    #Generates a list of locations.
    x=0
    addLocate = []
    
    #Generates generic starting song locations for later use
    #for i in range(1,11):
    #    dictJSON = {
    #        "name": "Starting Song " + str(i),
    #        "category": ["(!Start!)"],
    #    }
    #    addLocate.append(dictJSON)

    #Generate Victory location
    dictJSON = {
            "name": "Finished " + config.get("game"),
            "category": [],
            "requires": "|" + musicSheet +":1|",
            "victory": True
        }
    addLocate.append(dictJSON)

    #Generate locations with two checks.
    while (x != len(songList)):
        if "|" in songList[x]:
            name, categories = songList[x].split("|", 1)
        else:
            name, categories = songList[x], ""
        dictJSON = {
            "name": name + " - 0",
            "category": ["(Song List)"] + (categories.split("|") if categories else []),
            "requires": "|" + name +"|"
        }
        addLocate.append(dictJSON)
        dictJSON = {
            "name": name + " - 1",
            "category": ["(Song List)"] + (categories.split("|") if categories else []),
            "requires": "|" + name +"|"
        }
        addLocate.append(dictJSON)
        x = x+1
    
    #Generate generic total sheet locations.
    if (config.get("sheetAmount")):
        sheetsMax = int(config.get("sheetAmount"))
    else:
        sheetsMax = (floor(len(songList)/3))
        if (sheetsMax > 50):
            sheetsMax = 50
    for i in range(1,sheetsMax+1):
        dictJSON = {
            "name": musicSheet + "s Needed - " + str(i),
            "category": ["(!Goal Amount!)"],
            "requires": "|" + musicSheet + ":" + str(i) + "|"
        }
        addLocate.append(dictJSON)
    
    itemFile = open("locations.json", "w")
    jsonOutput=dumps(addLocate, indent=4)
    itemFile.write(jsonOutput)
    itemFile.close()

#Adds Items

def addItems(songList,musicSheet,config):
    #generate flow needed
    if (config.get("sheetAmount")):
        sheets = int(config.get("sheetAmount"))
    else:
        sheets = (floor(len(songList)/3))
        if (sheets > 50):
            print ("Total sheet amount exceeded 50!")
            print ("If you want to change this value, please specify it in the config values")
            sheets = 50
    addItem = []
    dictJSON = {
        "count": sheets,
        "name": musicSheet,
        "category": ["("+musicSheet+")"],
        "progression_skip_balancing": True
    }
    addItem.append(dictJSON)

    #add traps next
    traps = []
    if config.get("traps"):
        traps = (config.get("traps").split(", "))
    if (traps):
        for t in traps:
            dictJSON = {
                "count": 1,
                "name": t,
                "category": ["(Traps)"],
                "trap": True
            }
            addItem.append(dictJSON)

    #generate songs
    y = 0
    itemFile = open("items.json", "w")

    while (y != len(songList)):
        if "|" in songList[y]:
            name, categories = songList[y].split("|", 1)
        else:
            name, categories = songList[y], ""
        dictJSON = {
            "name": name,
            "count": 1,
            "category": ["(Songs)"] + (categories.split("|") if categories else []),
            "progression": True
            }
        addItem.append(dictJSON)
        y = y+1
    #Generate generic Goal items to help the player find information about their world
    dictJSON = {
        "count": 1,
        "name": "Goal Song",
        "category": ["(Goal Information Item)"],
        "filler": True
    }
    addItem.append(dictJSON)
    #Removed since the item associated with it is now unused
    #dictJSON = {
    #    "count": 1,
    #    "name": "Goal Amount",
    #    "category": ["(Goal Information Item)"],
    #    "filler": True
    #}
    #addItem.append(dictJSON)
    #dump to JSON
    jsonOutput=dumps(addItem, indent=4)
    itemFile.write(jsonOutput)
    itemFile.close()

# Game.json generation

def genGame(config: dict[str,str]) -> str:
    itemFile = open("game.json", "w")
    gName = config.get("game") or str(input("Enter the game's name: "))
    gName = gName.replace(" ","") #formatting for manual
    pName = config.get("creator") or str(input("Enter the player's name: "))
    pName = pName.replace(" ","")
    dictJSON ={
        "game": gName,
        "player": pName,
        "filler_item_name": config.get("filler_item_name") or input("Enter the filler item's name: ")
    }
    jsonOutput=dumps(dictJSON, indent = 4)
    itemFile.write(jsonOutput)
    itemFile.close()
    return gName

# I made this after .isnumeric failed. I'm crying too don't worry

def convertIntTest(inp,fail):
    try:
        inp = int(inp)
    except:
        print("Value is not an integer. This will be set to " + str(fail))
        return fail
    return inp

# Exits the program, had this a lot of times once I added a couple of error prompts.

def exitProg():
    print ("Exiting...")
    y="play vivid stasis if you've read this"
    while (y == "play vivid stasis if you've read this"):
        y = input("Press enter to leave the program: ")
        quit()

config = {
    "game": "",
    "creator": "",
    "musicSheet": "",
    "filler_item_name": "",
    "traps":[],
    "sort_disable": "",
    "sheetAmount": "",
    "debug": ""
}

#Setup list of songs
category_header = ""

#if we have a song.txt included, open that.
#if not, ask for one.
try: 
    with open("song.txt", "r") as f:
        songFile = f.readlines()
    print ("Using song.txt")
except:
    Tk().withdraw()
    with open(askopenfilename(title="Select a song file", filetypes=(("Text Files", "*.txt"),("All Files", "*.*"))), "r") as f:
        songFile = f.readlines()
    print ("Using provided file")

songListFile = []

for songName in songFile:
    songName = songName.strip()
    if not songName:
            continue
    else:
        if songName[0] == "#":
            if songName[1] == "$":
                k,v = songName[2:].strip().split("=", 1)
                config[k] = v
            elif songName[1] == "#":
                category_header = songName[2:].strip()
            continue
        elif ":" in songName:
            print("Song names cannot contain ':' characters\n" + songName + " contains a ':' character")
            exitProg()
        else:
            songName = songName.strip()
            if category_header:
                songName = songName + "|" + category_header
            songListFile.append(songName)

if not songListFile:
    print ("song.txt has no songs!")
    exitProg()

# Sort list for ease of finding songs in the client
sortOff = config.get("sort_disable")
if (not sortOff):
    songListFile.sort()

#Check if there's at least 10 songs within the list
if (len(songListFile) < 10):
    print ("song.txt has less than 10 songs! Please make sure there is more than 10 songs within the multiworld.")
    exitProg()

#Check if there's a dupicate song or a null string within the list
names = [n.split('|')[0] for n in songListFile]
if len(names) != len(set(names)):
    print ("song.txt contains a duplicate song.\nDuplicate songs name: " + repr([n for n in names if names.count(n) > 1]))
    exitProg()

musicSheet = config.get('musicSheet') or str(input("Enter the name of the item that will unlock your goal song: "))
if (musicSheet.replace(" ", "") == ""):
    print("Value has no data. The name of the item will be set to Progressive Flow")
    musicSheet = "Progressive Flow"

print ("Generating game.json information: ")
genGame(config)

print ("Adding items...")
addItems(songListFile, musicSheet, config)

print ("Adding locations...")
addLocations(songListFile, musicSheet, config)

if (config.get("debug")):
    print ("Outputing debug.txt")
    newFile = open("debug.txt","w")
    newFile.write ("Total locations: " + str(len(songListFile)*2))
    newFile.write ("\nTotal songs: " + str((len(songListFile))))
    if (config.get("sheetAmount")):
        newFile.write ("\nAmount of " + musicSheet + ": " + str(config.get("sheetAmount")))
    else:
        newFile.write ("\nAmount of " + musicSheet + ": " + str(len(songListFile)))
    newFile.write ("\n\nSong List: \n")
    for song in songListFile:    
        newFile.write((str(song.split("|")[0])) + " - " + (str(song.split("|")[1])) + "\n")
    newFile.write("\n\n")
    newFile.write(str(songListFile))
    newFile.close()
    print (str(songListFile))

print ("\nAll finished!")
exitProg()
