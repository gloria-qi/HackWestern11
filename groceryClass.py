import streamlit as st
import sqlite3
import hashlib
from typing import List, Dict

class GroceryShareApp:
    def __init__(self):
        # Initialize database connection
        self.conn = sqlite3.connect('grocery_share.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user1 TEXT,
                user2 TEXT,
                FOREIGN KEY(user1) REFERENCES users(username),
                FOREIGN KEY(user2) REFERENCES users(username),
                PRIMARY KEY(user1, user2)
            )
        ''')
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

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register a new user."""
        cursor = self.conn.cursor()
        hashed_password = self.hash_password(password)
        try:
            cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                           (username, hashed_password, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username: str, password: str) -> bool:
        """Authenticate user login."""
        cursor = self.conn.cursor()
        hashed_password = self.hash_password(password)
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

    def run(self):
        st.set_page_config(page_title="GroceryShare", page_icon="🛒")

        # Initialize session state variables
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = None

        # Page routing logic
        if st.session_state.page == 'login':
            self.render_login_page()
        elif st.session_state.logged_in:
            self.render_dashboard()
        else:
            st.stop()

    def render_login_page(self):
        st.title('GroceryShare: Login or Register')
        auth_mode = st.radio('Choose Action', ['Login', 'Register'])

        if auth_mode == 'Login':
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')

            if st.button('Login'):
                if self.login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = 'dashboard'
                    st.success(f'Welcome, {username}!')
                    # No need to rerun, just update session state to trigger re-render
                else:
                    st.error('Invalid credentials')

        else:
            new_username = st.text_input('Choose Username')
            email = st.text_input('Email Address')
            new_password = st.text_input('Create Password', type='password')
            confirm_password = st.text_input('Confirm Password', type='password')

            if st.button('Register'):
                if new_password != confirm_password:
                    st.error('Passwords do not match')
                elif self.register_user(new_username, new_password, email):
                    st.success('Registration successful! Please login.')
                    st.session_state.page = 'login'
                    # No need to rerun, just update session state to trigger re-render
                else:
                    st.error('Username or email already exists')

    def render_dashboard(self):
        st.sidebar.title(f'Welcome, {st.session_state.username}')

        # Navigation tabs
        tab = st.sidebar.radio('Navigation',
                               ['Grocery List', 'Friends', 'Matches'])

        if tab == 'Grocery List':
            self.render_grocery_list_page()
        elif tab == 'Friends':
            self.render_friends_page()
        elif tab == 'Matches':
            self.render_matches_page()

        # Logout functionality
        if st.sidebar.button('Logout'):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = 'login'
            # No need to rerun, just update session state to trigger re-render
            st.experimental_rerun()

    def render_grocery_list_page(self):
        st.header('Add Grocery Items')
        item = st.text_input('Item Name')
        quantity = st.number_input('Quantity', min_value=0.0, step=0.1)
        unit = st.selectbox('Unit',
                            ['kg', 'lbs', 'pieces', 'pack', 'box', 'bottle'])

        if st.button('Add Item'):
            self.add_grocery_item(st.session_state.username, item, quantity, unit)
            st.success(f'Added {quantity} {unit} of {item} to your list')

    def render_friends_page(self):
        st.header('Add Friends')
        friend_username = st.text_input('Enter Friend\'s Username')

        if st.button('Add Friend'):
            if self.add_friend(st.session_state.username, friend_username):
                st.success(f'{friend_username} added to your friends')
            else:
                st.error('Could not add friend')

        st.subheader('Your Friends')
        friends = self.get_friends(st.session_state.username)
        for friend in friends:
            st.write(friend)

    def render_matches_page(self):
        st.header('Grocery Matches')
        matches = self.find_matching_groceries(st.session_state.username)

        if matches:
            for friend, items in matches.items():
                st.subheader(f'Matches with {friend}')
                for item in items:
                    st.write(f"**{item['item']}**: "
                             f"You want {item['user_quantity']} {item['unit']}, "
                             f"{friend} wants {item['friend_quantity']} {item['unit']}")
        else:
            st.info('No matching grocery items found among your friends')


def main():
    app = GroceryShareApp()
    app.run()


if __name__ == '__main__':
    main()