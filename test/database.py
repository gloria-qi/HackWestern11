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
            self.conn = None
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                item TEXT,
                quantity REAL,
                unit TEXT,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        ''')

        # Purchase tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_tracking (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                buyer TEXT,
                total_price REAL,
                is_purchased BOOLEAN DEFAULT 0,
                user1 TEXT,
                user2 TEXT,
                user1_share REAL,
                user2_share REAL,
                FOREIGN KEY(user1) REFERENCES users(username),
                FOREIGN KEY(user2) REFERENCES users(username)
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
        """Remove a friend connection between two users."""
        cursor = self.conn.cursor()
        query = "DELETE FROM friends WHERE user1 = ? AND user2 = ?"
        cursor.execute(query, (username, friend_username))
        self.conn.commit()
        return True

    def get_grocery_items(self, username):
        """Retrieve grocery list for a user."""
        query = "SELECT item, quantity, unit FROM grocery_lists WHERE username = ?"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    def remove_grocery_item(self, username, item):
        """Remove an item from the user's grocery list."""
        query = "DELETE FROM grocery_lists WHERE username = ? AND item = ?"
        self.cursor.execute(query, (username, item))
        self.conn.commit()

    def track_matched_item_purchase(self, item, user1, user2, buyer=None):
        """Track a matched item for potential purchase."""
        cursor = self.conn.cursor()
        
        # First, check if this match already exists
        cursor.execute('''
            SELECT match_id FROM purchase_tracking 
            WHERE item = ? AND 
            ((user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?))
        ''', (item, user1, user2, user2, user1))
        
        existing_match = cursor.fetchone()
        if existing_match:
            # Update existing match
            match_id = existing_match[0]
            cursor.execute('''
                UPDATE purchase_tracking 
                SET buyer = ?, is_purchased = 0, total_price = NULL 
                WHERE match_id = ?
            ''', (buyer, match_id))
        else:
            # Create new match tracking
            cursor.execute('''
                INSERT INTO purchase_tracking 
                (item, user1, user2, buyer, is_purchased) 
                VALUES (?, ?, ?, ?, 0)
            ''', (item, user1, user2, buyer))
            match_id = cursor.lastrowid
        
        self.conn.commit()
        return match_id

    def complete_item_purchase(self, match_id, total_price):
        """Complete the purchase and record the total price."""
        cursor = self.conn.cursor()
        
        # Retrieve match details
        cursor.execute('''
            SELECT item, user1, user2, buyer 
            FROM purchase_tracking 
            WHERE match_id = ?
        ''', (match_id,))
        
        match_details = cursor.fetchone()
        if not match_details:
            raise ValueError("Invalid match ID")
        
        item, user1, user2, buyer = match_details
        
        # Determine users involved in the purchase
        if buyer == user1:
            other_user = user2
        else:
            other_user = user1
        
        # Basic split: equal halves
        user1_share = total_price / 2
        user2_share = total_price / 2
        
        # Update the purchase tracking
        cursor.execute('''
            UPDATE purchase_tracking
            SET is_purchased = 1, 
                total_price = ?, 
                user1_share = ?, 
                user2_share = ?
            WHERE match_id = ?
        ''', (total_price, user1_share, user2_share, match_id))
        
        self.conn.commit()
        
        return {
            'item': item,
            'buyer': buyer,
            'total_price': total_price,
            'user1': user1,
            'user2': user2,
            'user1_share': user1_share,
            'user2_share': user2_share
        }

    def get_purchase_history(self, username):
        """Retrieve purchase history for a user."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT item, buyer, total_price, user1_share, user2_share
            FROM purchase_tracking
            WHERE (user1 = ? OR user2 = ?) AND is_purchased = 1
        ''', (username, username))
        
        return cursor.fetchall()

    def get_ongoing_purchases(self, username):
        """
        Retrieve ongoing purchases involving the user where a friend is buying.
        
        Returns a list of tuples: [(buyer, item), ...]
        """
        cursor = self.conn.cursor()
        
        # Find purchases where the user is involved and a buyer is selected
        cursor.execute('''
            SELECT buyer, item
            FROM purchase_tracking
            WHERE (user1 = ? OR user2 = ?) AND 
                buyer IS NOT NULL AND 
                buyer != ? AND 
                is_purchased = 0
        ''', (username, username, username))
        
        return cursor.fetchall()
    def get_tracked_purchase_items(self, username):
        """
        Retrieve items that are currently being tracked for purchase by the user.
        
        Args:
            username (str): Username to check for tracked purchases
        
        Returns:
            List[str]: List of items being purchased
        """
        cursor = self.conn.cursor()
        
        # Find items where the user is the buyer and purchase is not completed
        cursor.execute('''
            SELECT DISTINCT item
            FROM purchase_tracking
            WHERE buyer = ? AND is_purchased = 0
        ''', (username,))
        
        return [item[0] for item in cursor.fetchall()]