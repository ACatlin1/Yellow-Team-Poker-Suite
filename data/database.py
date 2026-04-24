"""
**************************************************************************

database.py is for:

SQLite3 transmission of data to the database.

**************************************************************************
"""
import sqlite3
from datetime import datetime

DB_NAME = "poker_game.db"


def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            chips INTEGER DEFAULT 1000,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS save_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            slot_number INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            saved_at TEXT NOT NULL,
            FOREIGN KEY (player_name) REFERENCES players(name),
            UNIQUE(player_name, slot_number)
        )
        """)
        conn.commit()


def create_player(name, chips=1000):
    try:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO players (name, chips, wins, losses, draws, games_played, created_at)
            VALUES (?, ?, 0, 0, 0, 0, ?)
            """, (name, chips, datetime.now().isoformat()))
            conn.commit()
            print(f"Player '{name}' created.")
    except sqlite3.IntegrityError:
        print(f"Player '{name}' already exists.")


def get_player(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, name, chips, wins, losses, draws, games_played, created_at
        FROM players
        WHERE name = ?
        """, (name,))
        return cursor.fetchone()


def update_player_chips(name, chips):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE players
        SET chips = ?
        WHERE name = ?
        """, (chips, name))
        conn.commit()


def record_win(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE players
        SET wins = wins + 1,
            games_played = games_played + 1
        WHERE name = ?
        """, (name,))
        conn.commit()


def record_loss(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE players
        SET losses = losses + 1,
            games_played = games_played + 1
        WHERE name = ?
        """, (name,))
        conn.commit()


def record_draw(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE players
        SET draws = draws + 1,
            games_played = games_played + 1
        WHERE name = ?
        """, (name,))
        conn.commit()


def save_slot_record(player_name, slot_number, file_path):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO save_slots (player_name, slot_number, file_path, saved_at)
        VALUES (?, ?, ?, ?)
        """, (player_name, slot_number, file_path, datetime.now().isoformat()))
        conn.commit()


def get_save_slots(player_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT slot_number, file_path, saved_at
        FROM save_slots
        WHERE player_name = ?
        ORDER BY saved_at DESC
        """, (player_name,))
        return cursor.fetchall()


def delete_save_slot_record(player_name, slot_number):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM save_slots
        WHERE player_name = ? AND slot_number = ?
        """, (player_name, slot_number))
        conn.commit()


def show_all_players():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT name, chips, wins, losses, draws, games_played
        FROM players
        """)
        return cursor.fetchall()
