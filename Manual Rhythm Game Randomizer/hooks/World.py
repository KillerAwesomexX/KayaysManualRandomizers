# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from .BaseClasses import MultiWorld, CollectionState, ItemClassification

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value

from math import floor
########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. set_rules - Creates rules for accessing regions and locations
##    3. generate_basic - Creates the item pool and runs any place_item options
##    4. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################


# Called before regions and locations are created. Not clear why you'd want this, but it's here.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information.
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

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def before_generate_basic(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    from random import shuffle, randint
    
    # Use this hook to remove items from the item pool
    #init most variables
    itemNamesToRemove = [] # List of item names
    locationNamesToRemove = []
    startingSongs = []

    #setup song list and sheetname
    songList = []
    for item in item_table:
        songList.append(item["name"])
    
    #the old code DID NOT remove goal song and goal amount. so go go gadget repeating code it is.
    songList.pop(-1) #removes the manual defined filler item.
    songList.pop(-1) #removes Goal Amount from the song list.
    songList.pop(-1) #removes Goal Song from the song list.
    
    print (str(songList))
    #this should find the goal lock item as long as its the first in the json. only way this should not be the case
    #is if the JSON Generator has been tampered with.
    sheetName = songList[0]
    songList.pop(0)
    
    #get the total amount of sheets needed for the goal. shouldn't need the for item in item_table, but it should guarantee finding it.
    sheetAmt = get_option_value(multiworld, player, "music_sheets")
    for item in item_table:
        if item["name"] == sheetName:
            sheetTotal = item["count"]
    sheetAmt = (floor((sheetAmt/100)*(sheetTotal)))
    if (sheetAmt == 0):
        sheetAmt = 1
    
    #final prep before removing anything
    songAmt = len(songList)
    shuffle(songList)
    
    #remove any generic Location information
    for i in range(1,sheetTotal+1):
        if (i != sheetAmt):
            locationNamesToRemove.append(sheetName + "s Needed - " + str(i))
            
    #Set the generic Location with a custom item to not mess with the multiworld as much
    for l in multiworld.get_unfilled_locations(player=player):
        if (l.name == (sheetName + "s Needed - " + str(sheetAmt))):
                location = l
                break
    for i in item_pool:
            if (i.name == "Goal Amount"):
                item_to_place = i
                break
    location.place_locked_item(item_to_place)
    item_pool.remove(item_to_place)

    #since we shuffled the list, we can take the first result from the song list for it to be random.
    #the first location will help with telling the player what song is their goal.
    #NOTE: this only works if a starting hint is applied (which it should be in the YAML)
    goalSong = songList[0]
    songList.pop(0)
    itemNamesToRemove.append(goalSong)
    locationNamesToRemove.append(goalSong + " - 1")

    #Set the goal song's location to have a generic item for tracking it, as well as changing the requirements since we removed the item. 
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
    location.access_rule = lambda state: state.has(sheetName, player, sheetAmt)

    #Make sure the victory location is set up.
    victory_location = multiworld.get_location("__Manual Game Complete__", player)
    victory_location.access_rule = lambda state: state.has(sheetName, player, sheetAmt)

    #apply the (X) amount of starting songs to the list.
    startAmt = get_option_value(multiworld, player, "start_total")
    for i in range(1,startAmt+1):
        startingSongs.append(songList[0])
        songList.pop(0)
    if (startAmt != 10):
        for i in range(startAmt+1,11):
            locationNamesToRemove.append("Starting Song " + str(i))
    
    #Only remove the extra location if the amount rolled is higher.
    #80 > 75 would get it removed.
    addChance = get_option_value(multiworld, player, "extra_locations")
    for song in songList:
        if (randint(0,100) > addChance):
            locationNamesToRemove.append(song + " - 1")

    #place all of the starting songs
    for x in range(1, startAmt+1):
        for l in multiworld.get_unfilled_locations(player=player):
            if (l.name == ("Starting Song " + str(x))):
                location = l
                break
        for i in item_pool:
            if (i.name == (startingSongs[x-1])):
                item_to_place = i
                break
        location.place_locked_item(item_to_place)
        item_pool.remove(item_to_place)

    #remove any song that was not rolled.
    if (songAmt != get_option_value(multiworld, player, "song_total")):
        for i in range(get_option_value(multiworld, player, "song_total"),songAmt-startAmt-1):
            itemNamesToRemove.append(songList[i-1])
            locationNamesToRemove.append(songList[i-1]+ " - 0")
            locationNamesToRemove.append(songList[i-1]+ " - 1")
    
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

    return item_pool
    
    # Some other useful hook options:
    
    ## Place an item at a specific location
    #previously used these but they break generation too often for me. could be my small brain but i've had this error way too many times for me to use it.
    #location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    #item_to_place = next(i for i in item_pool if i.name == "Item Name")
    #location.place_locked_item(item_to_place)
    #item_pool.remove(item_to_place)

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is called before the victory location has the victory event placed and locked
def before_pre_fill(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is called after the victory location has the victory event placed and locked
def after_pre_fill(world: World, multiworld: MultiWorld, player: int):
    pass

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data
