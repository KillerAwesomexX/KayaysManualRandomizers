# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table, category_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

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

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    pass

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    logging.info('Running MRGR version pre 2.3')

    #Universal Tracker bypass
    if hasattr(multiworld, "generation_is_fake") and hasattr(multiworld, "re_gen_passthrough"):
        if world.game in multiworld.re_gen_passthrough:
            slot_data = multiworld.re_gen_passthrough[world.game]
            world.mrgrGoalSong = slot_data["Goal Song"]
            world.mrgrSheetName = slot_data["Sheet Name"]
            world.mrgrSheetAmt = slot_data["Sheets Needed"]
        return item_pool

    from random import shuffle, randint
    from math import floor
    
    catRemove = []
    for key in category_table.keys():
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

    # SAVE FOR LATER
    world.mrgrSheetName = sheetName

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
        logging.info("Amount of songs is more than the world can handle! Setting it to the amount of songs total.")
        song_rolled = len(songList) - startAmt

    #final prep before removing anything
    songAmt = len(songList)
    shuffle(songList)
    
    #place any song near the front of the list, to make sure it does not end up being removed
    forceList = [] + get_option_value(multiworld, player, "force_song")
    if (forceList):
        for song in forceList:
            songList.remove(song)
            songList.insert((1+startAmt),song)

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
    world.mrgrGoalSong = goalSong
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

    #add sheets to pool
    valueThing = floor((len(multiworld.get_unfilled_locations(player=player))-song_rolled)*(get_option_value(multiworld, player, "sheet_percent")/100))
    for x in range(1,valueThing):
        new_item = world.create_item(sheetName)
        item_pool.append(new_item)
    sheetAmt = floor(valueThing*(get_option_value(multiworld, player, "music_sheets")/100))
    
    # SAVE FOR LATER
    world.mrgrSheetAmt = sheetAmt

    #adds additional songs at the end
    valueThing = len(multiworld.get_unfilled_locations(player=player))-(sheetAmt+song_rolled)
    if (5 < valueThing):
        for x in range (1,(floor(valueThing*(get_option_value(multiworld, player, "duplicate_songs")/100)))+1):
            new_item = world.create_item(songList[x-1])
            item_pool.append(new_item)

    item_pool = world.adjust_filler_items(item_pool, traps)

    #used to help debug this kinda.
    #debugMW(item_pool)
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        remove_specific_item(item_pool, item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    # return values from prev step
    goalSong = world.mrgrGoalSong
    sheetName = world.mrgrSheetName
    sheetAmt = world.mrgrSheetAmt

    # Adjust Goal Song requirements.
    if hasattr(multiworld, "generation_is_fake"):
        # Note, we switch to unfilled locations here since we skip placing the Goal Item earlier
        for l in multiworld.get_unfilled_locations(player=player):
            if (l.name == (goalSong + " - 0")):
                location = l
                break
    else:
        for l in multiworld.get_filled_locations(player=player):
            if (l.name == (goalSong + " - 0")):
                location = l
                break
    location.access_rule = lambda goalState: goalState.has("Goal Amount Reached", player)
    
    # Adjust Goal Amount requirements
    for l in multiworld.get_filled_locations(player=player):
            if (l.name == ("0_GOAL_AMOUNT_REACHED")):
                location = l
                break
    location.access_rule = lambda goalState: goalState.has(sheetName, player, int(sheetAmt))
    return
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
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    # return values from prev step
    goalSong = world.mrgrGoalSong
    sheetName = world.mrgrSheetName
    sheetAmt = world.mrgrSheetAmt

    slot_data["visible_events"]['Goal Amount Reached'] = [("(!" + str(sheetAmt) + " " + str(sheetName)+"s to Unlock Goal!)")]
    slot_data["Goal Song"] = str(goalSong)
    slot_data["Sheets Needed"] = str(sheetAmt)
    slot_data["Sheet Name"] = str(sheetName)
    logging.info(str(slot_data))
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

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data
