import sqlite3
from typing import List, Dict

class DatabaseManager:
    def __init__(self, db_path: str = 'grocery_share.db'):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.create_tables()
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)
            self.connection = None
            self.cursor = None


    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')
        
        # Friends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user1 TEXT,
                user2 TEXT,
                FOREIGN KEY(user1) REFERENCES users(username),
                FOREIGN KEY(user2) REFERENCES users(username),
                PRIMARY KEY(user1, user2)
            )
        ''')
        
        # Grocery lists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grocery_lists (
                username TEXT,
                item TEXT,
                quantity REAL,
                unit TEXT,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')
        
        self.conn.commit()

    def register_user(self, username: str, hashed_password: str, email: str) -> bool:
        """Register a new user."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                           (username, hashed_password, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username: str, hashed_password: str) -> bool:
        """Authenticate user login."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                       (username, hashed_password))
        return cursor.fetchone() is not None

    def add_friend(self, current_user: str, friend_username: str) -> bool:
        """Add a friend connection between two users."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO friends (user1, user2) VALUES (?, ?)',
                           (current_user, friend_username))
            cursor.execute('INSERT INTO friends (user1, user2) VALUES (?, ?)',
                           (friend_username, current_user))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_friends(self, username: str) -> List[str]:
        """Retrieve list of friends for a user."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT user2 FROM friends WHERE user1 = ?', (username,))
        return [friend[0] for friend in cursor.fetchall()]

    def add_grocery_item(self, username: str, item: str, quantity: float, unit: str):
        """Add an item to user's grocery list."""
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO grocery_lists (username, item, quantity, unit) VALUES (?, ?, ?, ?)',
                       (username, item, quantity, unit))
        self.conn.commit()

    def find_matching_groceries(self, username: str) -> Dict[str, List[Dict]]:
        """Find matching grocery items among friends."""
        friends = self.get_friends(username)
        cursor = self.conn.cursor()

        # Get current user's grocery items
        cursor.execute('SELECT item, quantity, unit FROM grocery_lists WHERE username = ?', (username,))
        user_items = cursor.fetchall()

        matching_items = {}
        for friend in friends:
            friend_matches = []
            for item, quantity, unit in user_items:
                # Check if friend has same item
                cursor.execute('''
                    SELECT username, quantity, unit 
                    FROM grocery_lists 
                    WHERE username = ? AND item = ?
                ''', (friend, item))
                friend_item = cursor.fetchone()

                if friend_item:
                    friend_matches.append({
                        'item': item,
                        'user_quantity': quantity,
                        'friend_quantity': friend_item[1],
                        'unit': unit
                    })

            if friend_matches:
                matching_items[friend] = friend_matches

        return matching_items

    def close_connection(self):
        """Close database connection."""
        self.conn.close()
        
    def remove_friend(self, username, friend_username):
        cursor = self.conn.cursor()
        query = "DELETE FROM friends WHERE user1 = ? AND user2 = ?"
        cursor.execute(query, (username, friend_username))
        self.conn.commit()
        return True
    def get_grocery_items(self, username):
        query = "SELECT item, quantity, unit FROM grocery_lists WHERE username = ?"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()
    def remove_grocery_item(self, username, item):
        query = "DELETE FROM grocery_lists WHERE username = ? AND item = ?"
        self.cursor.execute(query, (username, item))
        self.conn.commit()
