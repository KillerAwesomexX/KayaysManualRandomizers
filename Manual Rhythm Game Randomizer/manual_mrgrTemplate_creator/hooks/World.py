# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import item_table, category_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging
from math import floor
########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    logging.info('Running MRGR version 2.2.2')

    from random import shuffle, randint

    #Universal Tracker bypass
    if hasattr(multiworld, "generation_is_fake"):
        return item_pool
    
    catRemove = []
    for key in category_table.keys():
        print(key)
        if (key == '(Goal Information Item)'):
            continue
        else:
            if (not is_option_enabled(multiworld, player, category_table[key]['yaml_option'][0])):
                catRemove.append(key)

    #init most variables
    itemNamesToRemove = []
    locationNamesToRemove = []
    startingSongs = []
    addChance = get_option_value(multiworld, player, "extra_locations")
    song_rolled = get_option_value(multiworld, player, "song_total")
    startAmt = get_option_value(multiworld, player, "start_total")

    #setup song list, trap list, and sheetname
    songList = []
    traps = []
    
    #init all the items for future use.
    for item in item_table:
        i = item.get("category", "nuh-uh") #the generic filler has no category.
        if i[0] == "(Songs)":
            if (len(i) > 1):
                if i[1] not in catRemove:
                    songList.append(item["name"])
            else:
                songList.append(item["name"])
        elif i[0] == "(Traps)":
            traps.append(item["name"])
            itemNamesToRemove.append(item["name"]) #Remove the trap from the pool since we'll be generating them with add_filler_items
        elif i[0] != "(Goal Information Item)":
            if item.get("progression_skip_balancing"): #the goal mode item
                sheetName = item["name"]
                sheetTotal = item["count"]

    #remove any songs before we do anything
    removeList = [] + get_option_value(multiworld, player, "remove_song")
    if (removeList):
        for song in removeList:
            songList.remove(song)
            itemNamesToRemove.append(song)
            locationNamesToRemove.append(song + " - 0")
            locationNamesToRemove.append(song + " - 1")

    #Error checking for song amount
    if (song_rolled > len(songList)):
        print ("Amount of songs is more than the world can handle! Setting it to the amount of songs total.")
        song_rolled = len(songList) - startAmt
    
    #get the total amount of sheets needed for the goal. shouldn't need the for item in item_table, but it should guarantee finding it.
    sheetAmt = (floor((get_option_value(multiworld, player, "music_sheets")/100)*(sheetTotal)))
    
    #Error checking in case we have too many music sheets.
    maxLoc = floor((song_rolled)*(1+(addChance/100)))
    maxItem = (song_rolled+sheetTotal+2)
    if (maxItem > maxLoc):
        print ("Reducing music sheets since too many were in the pool.")
        if maxLoc <= floor((song_rolled+2)*1.2): newSheetTotal = floor(maxLoc-(song_rolled+2))
        else: newSheetTotal = floor(maxLoc-(song_rolled+2))
        # 30 songs rolled + 5 starting songs is 70 locations MAX, multiplied by the addchance percent, then
        # subtracted by 30 potential song items plus the goal information items and if we can, a little bit of overhead.
        for x in range(newSheetTotal, sheetAmt+1):
            itemNamesToRemove.append(sheetName)
        sheetAmt = (floor((get_option_value(multiworld, player, "music_sheets")/100)*(newSheetTotal)))
    
    if (sheetAmt == 0):
        #if somehow we have no sheets, make sure there's at least one.
        itemNamesToRemove.pop(0)
        sheetAmt = 1
    
    #final prep before removing anything
    songAmt = len(songList)
    shuffle(songList)
    
    #place any song near the front of the list, to make sure it does not end up being removed
    forceList = [] + get_option_value(multiworld, player, "force_song")
    if (forceList):
        for song in forceList:
            songList.remove(song)
            songList.insert((1+startAmt),song)
    
    #remove any generic Location information
    for i in range(1,sheetTotal+1):
        if (i != sheetAmt):
            locationNamesToRemove.append(sheetName + "s Needed - " + str(i))
            

    #since we shuffled the list, we can take the first result from the song list for it to be random.
    #the first location will help with telling the player what song is their goal.
    #NOTE: this only works if a starting hint is applied (which it should be in the YAML)

    if (get_option_value(multiworld,player,"force_goal")):
        goalList = [] + get_option_value(multiworld,player,"force_goal")
        shuffle(goalList)
        goalSong = goalList[0]
        songList.remove(goalList[0])
    else:
        goalSong = songList[0]
        songList.pop(0)
    itemNamesToRemove.append(goalSong)
    locationNamesToRemove.append(goalSong + " - 1")

    #Place the goal song at the SheetAmt location
    for l in multiworld.get_unfilled_locations(player=player):
        if (l.name == (sheetName + "s Needed - " + str(sheetAmt))):
                location = l
                break
    for i in item_pool:
            if (i.name == goalSong):
                item_to_place = i
                break
    location.place_locked_item(item_to_place)
    item_pool.remove(item_to_place)

    #Set the goal song's location to have a generic item. 
    for l in multiworld.get_unfilled_locations(player=player):
            if (l.name == (goalSong + " - 0")):
                location = l
                break
    for i in item_pool:
            if (i.name == "Goal Song"):
                item_to_place = i
                break
    location.place_locked_item(item_to_place)
    item_pool.remove(item_to_place)

    #Make sure the victory location is set up.
    #victory_location = multiworld.get_location("__Manual Game Complete__", player) - Manual Update made it so you can rename the Goal, this (as of now) is obsolete and will error out.
    #victory_location = multiworld.get_location("Finished Goal Song", player)
    #victory_location.access_rule = lambda state: state.has(sheetName, player, sheetAmt)

    #Set up all starting songs.
    for i in range(1,startAmt+1):
        startingSongs.append(songList[0])
        songList.pop(0)

    #Remove any unnecessary locations
    #if (startAmt != 10):
    #    for i in range(startAmt+1,11):
    #        locationNamesToRemove.append("Starting Song " + str(i))
    
    #Only remove the extra location if the amount rolled is higher.
    #80 > 75 would get it removed.
    for song in songList:
        if (randint(0,100) > addChance):
            locationNamesToRemove.append(song + " - 1")

    #place all of the starting songs
    #for x in range(1, startAmt+1):
    #    for l in multiworld.get_unfilled_locations(player=player):
    #        if (l.name == ("Starting Song " + str(x))):
    #            location = l
    #            break
    #    for i in item_pool:
    #        if (i.name == (startingSongs[x-1])):
    #            item_to_place = i
    #            break
    #    location.place_locked_item(item_to_place)
    #    item_pool.remove(item_to_place)


    #code below SHOULD do the same thing as the code above
    for x in range(1,startAmt+1):
        for i in item_pool:
            if i.name == startingSongs[x-1]:
                start_item = i
                break
        multiworld.push_precollected(start_item)
        item_pool.remove(start_item)

    #remove any song that was not rolled.
    if (songAmt != song_rolled):
        removeSong = []
        for i in range(song_rolled,songAmt-startAmt-1):
            itemNamesToRemove.append(songList[i-1])
            locationNamesToRemove.append(songList[i-1]+ " - 0")
            locationNamesToRemove.append(songList[i-1]+ " - 1")
            removeSong.append(songList[i-1])
        for songName in removeSong:
            songList.remove(songName)


    # Use this hook to remove items from the world
    for itemName in itemNamesToRemove:
        for i in item_pool:
            if (i.name == itemName):
                item_pool.remove(i)
                break

    # Use this hook to remove locations from the world
    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

    #adds additional songs at the end
    valueThing = len(multiworld.get_unfilled_locations(player=player))-(sheetTotal+song_rolled)
    if (5 < valueThing):
        for x in range (1,(floor(valueThing*(get_option_value(multiworld, player, "duplicate_songs")/100)))+1):
            new_item = world.create_item(songList[x-1])
            item_pool.append(new_item)

    item_pool = world.add_filler_items(item_pool, traps)

    #used to help debug this kinda.
    #debugMW(item_pool)
    return item_pool
    
    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    
    ### Example way to use this hook: 
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string
    
    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
