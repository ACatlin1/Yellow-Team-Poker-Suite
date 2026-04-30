"""
**************************************************************************

database.py is for:

SQLite3 transmission of data to the database.

**************************************************************************
"""

import sqlite3
import hashlib
import os
import pickle


class DatabaseManager:

    def __init__(self, db_name="poker_data.db"):
        # Ensure the connection
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.init_db()


    def _hash_password(self, password):
        """Creates a secure hash of the password."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()


    def init_db(self):
        """Creates the players table if it doesn't already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Player stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    chips INTEGER DEFAULT 1000,
                    games_played INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0
                )
            ''')
            # Saved games table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_games (
                username TEXT PRIMARY KEY,
                game_state BLOB NOT NULL
            )
        ''')
            conn.commit()


    def register_player(self, username, password):
        """Attempts to register a new player. Returns True if successful, False if username exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO players (username, password_hash) VALUES (?, ?)",
                    (username, self._hash_password(password))
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False


    def verify_login(self, username, password):
        """Checks if the username and password match a record in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM players WHERE username = ? AND password_hash = ?",
                (username, self._hash_password(password))
            )
            result = cursor.fetchone()
            return result is not None


    def get_player_stats(self, username):
        """Retrieves a player's chip count and win records."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT chips, games_played, games_won FROM players WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    "chips": result[0],
                    "games_played": result[1],
                    "games_won": result[2]
                }
            return None


    def update_post_game_stats(self, username, chip_delta, is_winner=False):
        """Updates the database after a hand concludes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Increment games played, and optionally games won
            win_increment = 1 if is_winner else 0
            
            cursor.execute('''
                UPDATE players 
                SET chips = chips + ?, 
                    games_played = games_played + 1,
                    games_won = games_won + ?
                WHERE username = ?
            ''', (chip_delta, win_increment, username))
            conn.commit()


    def has_saved_game(self, username):
        """Checks if a saved game exists for the given user."""
        query = "SELECT 1 FROM saved_games WHERE username = ? LIMIT 1"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"[DB Error] Could not check for saved game: {e}")
            return False
    

    def save_game_state(self, username, game_state):
        """Saves or Updates a game state"""
        try:
            serialized = pickle.dumps(game_state)

            query = """
                INSERT INTO saved_games (username, game_state)
                VALUES (?, ?)
                ON CONFLICT(username) DO UPDATE SET game_state = excluded.game_state
            """

            cursor = self.conn.cursor()
            cursor.execute(query, (username, serialized))
            self.conn.commit()

            print(f"[DB] Saved game for {username}")
            return True

        except Exception as e:
            print(f"[DB Error] Could not save game: {e}")
            return False
    

    def get_saved_game(self, username):
        """Retrieve the saved game"""
        try:
            query = "SELECT game_state FROM saved_games WHERE username = ? LIMIT 1"
            cursor = self.conn.cursor()
            cursor.execute(query, (username,))
            row = cursor.fetchone()

            if not row:
                print(f"[DB] No saved game found for {username}")
                return None

            serialized = row[0]
            game_state = pickle.loads(serialized)

            print(f"[DB] Loaded saved game for {username}")
            return game_state

        except Exception as e:
            print(f"[DB Error] Could not load saved game: {e}")
            return None
    