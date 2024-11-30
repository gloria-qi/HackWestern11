import streamlit as st
from models import User
from database import DatabaseManager

class GroceryShareApp:
    def __init__(self):
        """Initialize the application with database manager"""
        self.db = DatabaseManager()

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
                hashed_password = User.hash_password(password)
                if self.db.login_user(username, hashed_password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = 'dashboard'
                    st.success(f'Welcome, {username}!')
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
                else:
                    hashed_password = User.hash_password(new_password)
                    if self.db.register_user(new_username, hashed_password, email):
                        st.success('Registration successful! Please login.')
                        st.session_state.page = 'login'
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
            st.experimental_rerun()

    def render_grocery_list_page(self):
        st.header('Add Grocery Items')
        item = st.text_input('Item Name')
        quantity = st.number_input('Quantity', min_value=0.0, step=0.1)
        unit = st.selectbox('Unit',
                            ['kg', 'lbs', 'pieces', 'pack', 'box', 'bottle'])

        if st.button('Add Item'):
            self.db.add_grocery_item(st.session_state.username, item, quantity, unit)
            st.success(f'Added {quantity} {unit} of {item} to your list')

    def render_friends_page(self):
        st.header('Add Friends')
        friend_username = st.text_input('Enter Friend\'s Username')

        if st.button('Add Friend'):
            if self.db.add_friend(st.session_state.username, friend_username):
                st.success(f'{friend_username} added to your friends')
            else:
                st.error('Could not add friend')

        st.subheader('Your Friends')
        friends = self.db.get_friends(st.session_state.username)
        for friend in friends:
            st.write(friend)

    def render_matches_page(self):
        st.header('Grocery Matches')
        matches = self.db.find_matching_groceries(st.session_state.username)

        if matches:
            for friend, items in matches.items():
                st.subheader(f'Matches with {friend}')
                for item in items:
                    st.write(f"**{item['item']}**: "
                             f"You want {item['user_quantity']} {item['unit']}, "
                             f"{friend} wants {item['friend_quantity']} {item['unit']}")
        else:
            st.info('No matching grocery items found among your friends')
