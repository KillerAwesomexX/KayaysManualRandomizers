Hello and welcome to this program I made cause I wanted a custom song list for Beat Saber lol.
This is Version 2.2.1.b PR

# CHANGELOG #
Version 2.2.1.b PR
- Fixed ASCII related checks
- Added a key when sorting to ensure capital letters and lowercase letters get treated the same way
- Fix various problems with the Configuration example

Version 2.2.1.a PR
- Removed leftover filler fix due to the new update
- World now runs at before_create_items_filler, due to the Manual update changing which hooks run where
- Updated to 7/9/24 version of Manual
- Changed meta.json to include a generic apworld decription, a small comment for what version MRGR is, and two option presets
- Goal now uses a static Victory name, since looking for the Manual Game Completion location results in an error
- Added an error check in case the song file would error out
- Added an ASCII check to ensure that Archipelago can handle text provided by the user
- Added a new setting, asciiTest
- Added an ASCII passthrough as well as an ASCII replacement just in case
- World.py looks for the static Victoy name rather than Manual Game Completion
- Included a brief example and explanation of all the configurations you can add to your song file

Version 2.2.0
- Added a temporary fix for leftover Filler items flooding the Multiworld output
- Changed how Goal Song information is generated, removing any need for the Goal Amount item
- Added categories.json, only used to hide the Goal Information Item category from the client
- Removed MRGRStartHints, now that the Goal Song information is trimmed down.
- Changed how Goal McGuffin items are categorized, it should put them near the top rather than somewhere in the middle.
- Changed a variable in the JSONGenerator so its a little easier to understand what it does
- Added a new script JSONtoSongFile for those who want to rebuild previous MRGR JSON files back into song lists.
- Reworded some descriptions for options related to forcing songs
- Added a passthrough for Universal Tracker, which should fix locations not being in logic despite having the items for them while using UT

Version 2.1.0
- Rewrote Sheet Removal Code, the old one was garbage
- Reverted goal locking item culling code
- Added Force Goal as an option
- Added MRGRStartHints to Hooks/Options.py, you should be able to generate a YAML via the Template Generator now

Version 2.0.0
- Converted the original Randomizer into the JSONGenerator
- Removes a lot of the options, as they have been moved to YAML options.
- Locations and Songs generate the maximum amount every time.
- New generic locations have been added for use with hooks/Options.py and hooks/World.py
- New song.txt options, including debug (now that APWorldGoal.txt has been removed), sortDisable, and sheetAmount
- If song.txt is missing, it will now ask for a file - Originally done by superriderth for the previous version of this, I figured I'd add that same functionality for this version
- song.txt now allows Trap definition! Go crazy if you want.
- Song Items will now add the category associated with it.
- Songs are now sorted by default

- Replaced options from the original Randomizer into YAML options.
- - These are: Extra Location Percent, Sheet Amount Percent, Song Amount, and Starting Songs
- - New options have been added: Force Song/Remove Song, Filler/Trap percent (added by Manual by default), and Duplicate Song percent

- Added some error checking just in case for both song amount and sheet amount
- Sheets and Goal song are now set and told to the player through the multiworld. While this needs two items, they're set as filler so it shouldn't mess around with generation too much.
- Redid the item removal hook since the next() method had me running into errors left and right.
- Ability to force a song into the pool as well as remove one.

Version 1.1.0 - made by silasary
- Added support for configuration options within song.txt
- Added support for categories with | after the song name
- Added support for category headers with ## before the category name
- Added support for blank lines in song.txt

Version 1.0.2
- Updated to the newest Manual APWorld 12-3-2023.
- Added a sample APWorld of Rhythm Heaven Fever in the Example Files.
- Finally added a changelog.

Version 1.0.1
- Changed one line of code that made the game name the player name.

# INSTRUCTIONS #

1. Create a list of songs or use a predefined list

Simply open up a text file, and start placing your songs within! All songs must be on a new line.
You can also check out the Example Files for help with additional things, such as configuration options
for running the python script and setting up categories.

If you do not have a song list or you want a pre-generated list, there are a few made in the Example Files folder
If you choose to use a file from the Example Files folder, copy and paste its contents to song.txt


2. Copy the template folder

For safety, its beneficial to create a copy of the template apworld folder (named manual_mrgrTemplate_creator)


3. Run the Python script in the copied template folder

Run the JSON Generator in the data folder.

If there is no file named song.txt, you will be asked by the script to provide a text file.

This script will ask you a few questions to generate the game.json, unless its provided within the song.txt config values.
Afterwards it will generate all of the items and locations
NOTE: The program will automatically remove spaces from the Game name and the player name


4. (OPTIONAL) Change the options in Options.py

If you want to, you can change the maximum amount of songs in Options.py
By default, the option is set to 400 maximum songs.


4. Rename the folder to manual_(gamename)_(playername) 

Your game name and player name from step 2 will be used in this step. The gamename and playername must be lowercase.


5. Zip up the renamed folder and rename the .zip file to manual_(gamename)_(playername).apworld

If you cannot rename the extension, you may have to check your windows settings.


6. Place the apworld file in your Archipelago installation

Place your apworld within C:\ProgramData\Archipelago\custom_worlds, or install it via the Install APWorld option in the Archipelago launcher.


7. Generate template settings via the AP Launcher

Run the ArchipelagoLauncher within the Archipelago folder. Then, select Generate Template Settings. If you've
done everything correctly, you should have a YAML file named Manual_(gamename)_(playername). From there, edit
the YAML file and you're good to go!

All that's left is to generate your game! Have fun!
