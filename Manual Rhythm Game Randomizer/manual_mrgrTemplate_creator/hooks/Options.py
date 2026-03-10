# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions, OptionList
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class ExtraLocations(Range):
    """The percent chance for an additional location to be added when you complete a song."""
    display_name = "Additional Location Percentage"
    range_start = 40
    range_end = 100
    default = 80

class MusicSheetAmt(Range):
    """The percentage of goal locking items needed in order to win your game."""
    display_name = "Goal Percentage"
    range_start = 30
    range_end = 100
    default = 80

class SongAmount(Range):
    """The amount of songs in your world. Does not include Starting Songs and the Goal Song."""
    display_name = "Total Songs"
    range_start = 10
    range_end = 400
    #Range_End has been set to an arbitrary value. If you have more than this value, feel free to change it.
    default = 40

class SheetPool(Range):
    """The percentage of your item pool that is made up of goal locking items."""
    display_name = "SheetPercentage"
    range_start = 40
    range_end = 80
    default = 50

class DuplicateSong(Range):
    """The percent of your item pool that replaces filler/trap items with additional songs."""
    display_name = "Duplicate Song Percentage"
    range_start = 0
    range_end = 60
    default = 10

class StartingSongs(Range):
    """The amount of songs you start with."""
    display_name = "Start Amount"
    range_start = 1
    range_end = 10
    default = 5

class ForceSong(OptionList):
    """Guarantees the song(s) specifed will be generated in the multiworld. Song name must be identical to the one in the list of songs."""
    display_name = "Force Songs"
    verify_item_name = True

class RemoveSong(OptionList):
    """Removes the song(s) specifed will NOT be generated in the multiworld. Song name must be identical to the one in the list of songs."""
    display_name = "Remove Songs"
    verify_item_name = True

class GoalSong(OptionList):
    """Guarantees one of the songs specified will be your goal song. Song name must be identical to the one in the list of songs."""
    display_name = "Force Goal"
    verify_item_name = True

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["song_total"] = SongAmount
    options["extra_locations"] = ExtraLocations
    options["duplicate_songs"] = DuplicateSong
    options["sheet_percent"] = SheetPool
    options["music_sheets"] = MusicSheetAmt
    options["start_total"] = StartingSongs
    options["force_song"] = ForceSong
    options["remove_song"] = RemoveSong
    options["force_goal"] = GoalSong
    return options


# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    options.type_hints["start_hints"].default = ["Goal Song"]
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
