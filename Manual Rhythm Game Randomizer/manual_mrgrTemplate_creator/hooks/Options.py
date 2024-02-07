# Object classes from AP that represent different types of options that you can create
from Options import FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, SpecialRange

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



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
    range_start = 10
    range_end = 100
    default = 80

class SongAmount(Range):
    """The amount of songs in your world. Does not include Starting Songs and the Goal Song."""
    display_name = "Total Songs"
    range_start = 10
    range_end = 150
    default = 40

class StartingSongs(Range):
    """The amount of songs you start with."""
    display_name = "Start Amount"
    range_start = 1
    range_end = 10
    default = 5


# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    options["extra_locations"] = ExtraLocations
    options["music_sheets"] = MusicSheetAmt
    options["song_total"] = SongAmount
    options["start_total"] = StartingSongs
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    return options