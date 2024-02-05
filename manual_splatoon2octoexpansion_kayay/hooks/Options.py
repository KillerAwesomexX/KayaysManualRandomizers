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
class MemCakeGoal(Toggle):
    """Turns on Mem Cake Hunt. This option is best suited for a sync game, or for those who like good ol' McGuffin hunts."""
    display_name = "mem_cake_hunt"
    default = True

class MemCakeRequired(Range):
    """If you play with Mem Cake Hunt on, you will need this many Mem Cakes to beat your goal."""
    display_name = "mem_cake_amount"
    range_start = 10
    range_end = 40
    default = 20

class FinalBossGoal(Toggle):
    """Makes the final boss of the game and their requirements as a part of your victory condition.
    Keep in mind this section of the game can easily last 30+ minutes just to get to the boss.
    If include_escape is turned on, this will automatically be applied."""
    display_name = "final_boss_as_goal"
    default = False

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    options["memHunt"] = MemCakeGoal
    options["memAmt"] = MemCakeRequired
    options["final_boss_as_goal"] = FinalBossGoal
    return options