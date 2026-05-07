Poker Suite

This software intends to offer the user the ability to play poker. It 
contains three variants of Texas Hold 'Em, 5-Card Draw, and 7-Card Stud.



Set Up

Download this software from https://github.com/ACatlin1/Yellow-Team-Poker-Suite .
This is initially intended to run on the server PlayIt.gg. However, if you wish to
set up your own server, open UI / manager.py then change the server info on 
lines 150 and 151 to your preference.



Start Up

Upon initially loading the game you will encounter a login screen. Select a
username and set a password. This will be the basis of your profile. Usernames 
must be unique. After you register you must log in. At the moment, there is no
password reset or recovery.



Lobby Screen

Once logged in, there will be options available. The initial tab is a toggle menu
that allows you to choose your game variant. Beneath that is a tab to choose how many
computer run opponents you wish to play. This only applies to single play, offline
games.

On the right lower side, there are 4 buttons. Single Player will launch an offline
single player game with the rules you have selected above. Multiplayer will open a
connection to the server and wait for an opponent. If an opponent joins, then a game 
can commence. If there is no opponent, then the exit button will take you back to the 
lobby. View Stats will show you your game stats. Exit will close the screen.



Game Play

Each game variant still runs off the standard poker actions of check (or call), 
raise (or bet), and fold. The unique actions of each variant play out just like they 
would on the table. Hold 'Em runs through the flop, turn, and river with betting between
each phase. Draw allows the user to pick up to 3 cards to discard and replace. Stud hands 
out all 7 cards with betting options after each. At any point you can pause the game. If
the user saves and exits, the game may be resumed at a later time.



Features

    *User registration/login
    *Play a poker game with user choice of rules
        *Hold 'Em
        *Draw
        *Stud
    *Handle betting
    *Handle game rounds
    *Handle game phases
    *Handle round winner and assign the pot
    *Handle new hands
    *Track user stats



Project Structure

|_core
    |_cards.py
    |_logic.py
    |_npc.py
    |_players.py
    |_scoring.py

|_data
    |_database.py
    |_storage.py
    |_poker_data.db
    |_user_profiles.db

|_netowrk
    |_client.py
    |_server.py

|_ui
    |_auth.py
    |_lobby.py
    |_manager.py
    |_sprites.py
    |_stats.py
    |_table.py
    |_widgets.py
    |_assets
        |_PNG
            |_card sprites

|_variants
    |_draw.py
    |_holdem.py
    |_stud.py

main.py
.gitignore
README.md



Security

Passowrds are hashed and saved in the user_profiles database. If real money were introduced
then additional security will be needed.


Authors

Yellow Team
    Andrew Catlin
    Domminque Smiley
    Noor Ramadan



Roadmap

To advance this game several feature upgrades are planned.
    Improvements to bot AI to be more dynamic.
    Improvements to visual layout:
        Card layout and positioning
        Chip display
        Personal purse display
        More interesting winner screens
    More game types can be added.
    More user stats can be tracked.
    Real money could be implemented.