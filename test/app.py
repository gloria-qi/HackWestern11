import streamlit as st
from models import User
from database import DatabaseManager
from streamlit_lottie import st_lottie
import requests

class GroceryShareApp:
    def __init__(self):
        """Initialize the application with database manager"""
        self.db = DatabaseManager()
        
    def apply_custom_styling(self):
        st.markdown("""
        <style>
        /* Global App Styling */
        .stApp {
            background: linear-gradient(to bottom, #1c1c1c, #333333);
            font-family: 'Poppins', sans-serif;
            color: white;
        }
        
        /* Sidebar Styling */
        .stSidebar {
            background-color: #262626;
            border-right: 2px solid #F39C12;
        }
        
        /* Header Styling */
        h1, h2, h3 {
            color: #F39C12;
            text-align: center;
            font-weight: 600;
        }
        
        /* Input and Button Styling */
        .stTextInput > div > div > input {
            background-color: #3a3a3a;
            color: white;
            border: 1px solid #F39C12;
        }
        
        .stButton > button {
            background-color: #F39C12;
            color: black;
            font-weight: bold;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #ff9d2f;
            transform: scale(1.05);
        }
        </style>
        """, unsafe_allow_html=True)


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
        self.apply_custom_styling()
        st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(to bottom, #1c1c1c, #333333);
            color: white;
        }
        .stSidebar {
            background-color: #262626;
        }
        h1, h2, h3 {
            color: #F39C12;
        }
        img {
            border-radius: 15px;
            box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
        st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
    .stApp {
        background: linear-gradient(to bottom, #1c1c1c, #333333);
        font-family: 'Poppins', sans-serif;
        color: white;
    }
    h1, h2, h3 {
        color: #F39C12;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

        st.markdown("<h1 style='text-align: center; color: white;'>Welcome to GroceryShare 🛒</h1>", unsafe_allow_html=True)
    
        auth_mode = st.radio('Choose Action', ['Login', 'Register'])
        col1, col2 = st.columns([1, 2])


        if auth_mode == 'Login':
            st.subheader("🔑 Login")
            username = st.text_input('👤 Username', placeholder="Enter your username")
            password = st.text_input('🔒 Password', placeholder="Enter your password", type='password')

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
            st.subheader("📝 Register")
            new_username = st.text_input('👤 Username', placeholder="Enter your username")
            email = st.text_input('Email Address')
            new_password = st.text_input('🔒 Password', placeholder="Enter your password", type='password')
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
                        
    def render_grocery_list_page(self):
        st.markdown("""
        <div style='background-color: #262626; 
                    padding: 20px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h3 style='color: #F39C12; text-align: center;'>
                🛒 Manage Your Grocery List
            </h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            item = st.text_input('Item Name', placeholder="Enter item name")
        
        with col2:
            quantity = st.number_input('Quantity', 
                                    min_value=0.0, 
                                    step=0.1, 
                                    format="%.2f")
        
        with col3:
            unit = st.selectbox('Unit', 
                                ['kg', 'lbs', 'pieces', 'pack', 'box', 'bottle'],
                                index=0)

        # Enhanced Add Item Button with columns for better alignment
        col_space1, col_button, col_space2 = st.columns([1,2,1])
        
        with col_button:
            if st.button('Add Item', use_container_width=True):
                if item and quantity > 0:
                    self.db.add_grocery_item(st.session_state.username, item, quantity, unit)
                    st.success(f'Added {quantity} {unit} of {item} to your list')
                else:
                    st.warning('Please enter a valid item and quantity')
                    
    def render_dashboard(self):
        # Custom styling for dashboard
        st.markdown("""
        <style>
        .dashboard-sidebar {
            background-color: #262626;
            border-right: 2px solid #F39C12;
            padding: 20px;
            border-radius: 10px;
        }
        .dashboard-nav-button {
            width: 100%;
            text-align: left;
            background-color: transparent;
            color: white !important;
            border: 1px solid #3a3a3a;
            margin-bottom: 10px;
        }
        .dashboard-nav-button:hover {
            background-color: #F39C12 !important;
            color: black !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Custom sidebar layout
        st.sidebar.markdown(f"""
        <div class="dashboard-sidebar">
            <h2 style="color: #F39C12; text-align: center;">
                👤 {st.session_state.username}
            </h2>
            <hr style="border-color: #F39C12;">
        </div>
        """, unsafe_allow_html=True)

        # Navigation with icons and better styling
        nav_options = [
            '🛒 Grocery List', 
            '👥 Friends', 
            '🔗 Matches'
        ]
        
        # Create custom radio button with better styling
        nav_style = """
        <style>
        div[role="radiogroup"] > label {
            background-color: #3a3a3a !important;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            width: 100%;
            display: block;
            text-align: left;
        }
        div[role="radiogroup"] > label:hover {
            background-color: #F39C12 !important;
            color: black !important;
        }
        </style>
        """
        st.sidebar.markdown(nav_style, unsafe_allow_html=True)
        
        # Navigation radio with custom layout
        tab = st.sidebar.radio('Dashboard Navigation', 
                                nav_options, 
                                label_visibility='collapsed')

        # Logout button with styling
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        if st.sidebar.button('🚪 Logout', 
                            use_container_width=True, 
                            help='Exit your GroceryShare session'):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = 'login'
            st.experimental_rerun()

        # Render appropriate page based on navigation
        if '🛒 Grocery List' in tab:
            self.render_grocery_list_page()
        elif '👥 Friends' in tab:
            self.render_friends_page()
        elif '🔗 Matches' in tab:
            self.render_matches_page()

        # Optional: Add a welcome message or dashboard summary
        st.markdown(f"""
        <div style='background-color: #262626; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin-top: 20px;
                    text-align: center;'>
            <h3 style='color: #F39C12;'>Welcome to Your GroceryShare Dashboard</h3>
            <p>Hello, {st.session_state.username}! 
            Manage your groceries, connect with friends, and find matching items.</p>
        </div>
        """, unsafe_allow_html=True)

    def render_friends_page(self):
        st.header('🤝 Friends Management')
        
        # Styled friend addition section
        st.markdown("""
        <div style='background-color: #262626; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin-bottom: 20px;'>
            <h4 style='color: #F39C12; text-align: center;'>
                Add New Friends
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        friend_username = st.text_input('Enter Friend\'s Username', 
                                        placeholder="Username to add")
        
        col_space, col_button, col_space2 = st.columns([1,2,1])
        
        with col_button:
            if st.button('Add Friend', use_container_width=True):
                if not friend_username:
                    st.warning('Please enter a username')
                elif friend_username == st.session_state.username:
                    st.error('You cannot add yourself as a friend')
                else:
                    if self.db.add_friend(st.session_state.username, friend_username):
                        st.success(f'{friend_username} added to your friends')
                    else:
                        st.error('Could not add friend. Check the username exists.')

        # Friends List with Card-like Display
        st.subheader('Your Friends')
        friends = self.db.get_friends(st.session_state.username)
        
        if friends:
            for friend in friends:
                st.markdown(f"""
                <div style='background-color: #3a3a3a; 
                            padding: 10px; 
                            border-radius: 8px; 
                            margin-bottom: 10px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;'>
                    <span>{friend}</span>
                    <button style='background-color: #F39C12; 
                                color: black; 
                                border: none; 
                                padding: 5px 10px; 
                                border-radius: 5px;'>
                        View Profile
                    </button>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info('No friends added yet. Start connecting!')

    def render_matches_page(self):
        st.header('🤝 Grocery Matches')
        
        matches = self.db.find_matching_groceries(st.session_state.username)

        if matches:
            for friend, items in matches.items():
                st.markdown(f"""
                <div style='background-color: #262626; 
                            padding: 15px; 
                            border-radius: 10px; 
                            margin-bottom: 15px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    <h4 style='color: #F39C12; margin-bottom: 10px;'>
                        Matches with {friend}
                    </h4>
                    {''.join([f"""
                    <div style='background-color: #3a3a3a; 
                                padding: 10px; 
                                border-radius: 8px; 
                                margin-bottom: 5px;'>
                        <strong>{item['item']}</strong>: 
                        You want {item['user_quantity']} {item['unit']}, 
                        {friend} wants {item['friend_quantity']} {item['unit']}
                    </div>
                    """ for item in items])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info('No matching grocery items found among your friends')
