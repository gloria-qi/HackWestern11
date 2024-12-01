import streamlit as st
from models import User
from database import DatabaseManager
import cv2


class GroceryShareApp:
    def __init__(self):
        """Initialize the application with database manager"""
        self.db = DatabaseManager("friends.db")
        
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
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = None
        if st.session_state.page == 'login':
            self.render_login_page()
        elif st.session_state.logged_in:
            self.render_dashboard()
        else:
            st.stop()

    def render_login_page(self):
        self.apply_custom_styling()
        st.markdown("<h1 style='text-align: center;'>Welcome to GroceryShare 🛒</h1>", unsafe_allow_html=True)
    
        auth_mode = st.radio('Choose Action', ['Login', 'Register'])
        
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

    def render_dashboard(self):
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

        st.sidebar.markdown(f"""
        <div class="dashboard-sidebar">
            <h2 style="color: #F39C12; text-align: center;">
                👤 {st.session_state.username}
            </h2>
            <hr style="border-color: #F39C12;">
        </div>
        """, unsafe_allow_html=True)

        nav_options = [
            '🛒 Grocery List', 
            '👥 Friends', 
            '🔗 Matches'
        ]
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
        tab = st.sidebar.radio('Dashboard Navigation', 
                                nav_options, 
                                label_visibility='collapsed')

        if st.sidebar.button('🚪 Logout', 
                            use_container_width=True, 
                            help='Exit your GroceryShare session'):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = 'login'
            st.experimental_rerun()

        # Render appropriate page based on navigation
        if tab == '🛒 Grocery List':
            self.render_grocery_list_page()
        elif tab == '👥 Friends':
            self.render_friends_page()
        elif tab == '🔗 Matches':
            self.render_matches_page()

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

        item = st.text_input('Item Name', placeholder="Enter item name")
        quantity = st.number_input('Quantity', min_value=0.0, step=0.1, format="%.2f")
        unit = st.selectbox('Unit', ['kg', 'lbs', 'pieces', 'pack', 'box', 'bottle'])

        if st.button('Add Item'):
            if item and quantity > 0:
                self.db.add_grocery_item(st.session_state.username, item, quantity, unit)
                st.success(f'Added {round(quantity, 1)} {unit} of {item} to your list')
            else:
                st.warning('Please enter a valid item and quantity')

        st.header('Your Grocery List')
        grocery_items = self.db.get_grocery_items(st.session_state.username) 
        if grocery_items:
            st.write("Here are the items you’ve added:")
            for index, (item, quantity, unit) in enumerate(grocery_items):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.write(f"**{item}**")
                with col2:
                    st.write(f"{round(quantity, 1)} {unit}")
                with col3:
                    if st.button(f"📝 Edit", key=f"edit_{index}"):
                        st.warning("Edit functionality not implemented yet!")  
                with col4:
                    if st.button(f"❌ Remove", key=f"remove_{index}"):
                        self.db.remove_grocery_item(st.session_state.username, item)
                        st.success(f"Removed {item} from your grocery list.")
                        st.session_state.page = st.session_state.page
                        st.experimental_rerun()
        else:
            st.info("No items in your grocery list. Start adding some!")


    def render_matches_page(self):
        st.header("🔗 Grocery Matches, Cost Splitting, and Purchases")

        # Fetch the user's grocery items
        user_grocery_items = self.db.get_grocery_items(st.session_state.username)

        if not user_grocery_items:
            st.info("You have no items in your grocery list to match with friends.")
            return

        # Check if there are any ongoing purchases involving the user
        ongoing_purchases = self.db.get_ongoing_purchases(st.session_state.username)
        if ongoing_purchases:
            st.warning("⚠️ Purchase Updates:")
            for purchase in ongoing_purchases:
                st.write(f"🛒 {purchase[0]} is purchasing {purchase[1]} for the group!")

        # Show the user's grocery items
        st.subheader('Your Grocery Items')
        for item, quantity, unit in user_grocery_items:
            st.write(f"{item} - {round(quantity, 1)} {unit}")

        # Fetch friends and compare grocery lists
        matches_found = False
        friends = self.db.get_friends(st.session_state.username)

        if not friends:
            st.info("You have no friends to compare with.")
            return

        # Get already tracked purchase items
        tracked_purchase_items = self.db.get_tracked_purchase_items(st.session_state.username)

        # Loop over each friend
        for friend in friends:
            # Find matches for the current friend
            matches = self.db.find_matching_items(st.session_state.username, friend)

            if not matches:
                st.info(f"No matches found with {friend}.")
                continue

            st.subheader(f"Matches with {friend}")

            total_user_cost = 0.0  # Total cost for the user
            total_friend_cost = 0.0  # Total cost for the friend

            # Loop through each matching item
            for match in matches:
                item = match['item']
                user_quantity = match['user1_quantity']
                friend_quantity = match['user2_quantity']
                unit = match['unit']

                matches_found = True

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"🟢 Match with {friend}: {item} - You need {round(user_quantity, 1)} {unit}, {friend} needs {round(friend_quantity, 1)} {unit}")
                with col2:
                    # Disable button if item is already being tracked for purchase
                    if item in tracked_purchase_items:
                        st.markdown(f"**You're buying {item}**")
                    else:
                        if st.button(f"I'll Buy - {item}", key=f"purchase_{item}_{friend}"):
                            self.db.track_matched_item_purchase(item, st.session_state.username, friend, st.session_state.username)
                            st.success(f"You're buying {item} for the group!")
                            st.experimental_rerun()

                # Input the cost per unit for the item
                cost_per_unit = st.number_input(
                    f"Enter cost per {unit} for {item}",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    key=f"cost_{item}_{friend}"
                )

                if cost_per_unit > 0:
                    # Calculate total and split costs
                    total_quantity = user_quantity + friend_quantity
                    total_cost = total_quantity * cost_per_unit
                    user_cost = (user_quantity / total_quantity) * total_cost
                    friend_cost = (friend_quantity / total_quantity) * total_cost

                    # Add to the total costs
                    total_user_cost += user_cost
                    total_friend_cost += friend_cost

                    # Display cost breakdown
                    st.markdown(f"""
                    <div style='background-color: #f5f5f5; 
                                padding: 10px; 
                                border-radius: 8px; 
                                margin-bottom: 10px; color: black;'>
                        <b>Item:</b> {item} <br>
                        <b>Your Quantity:</b> {round(user_quantity, 1)} {unit} <br>
                        <b>{friend}'s Quantity:</b> {round(friend_quantity, 1)} {unit} <br>
                        <b>Total Cost:</b> ${total_cost:.2f} <br>
                        <b>Your Share:</b> ${user_cost:.2f} <br>
                        <b>{friend}'s Share:</b> ${friend_cost:.2f}
                    </div>
                    """, unsafe_allow_html=True)

            # Display the total cost for this friend
            st.markdown(f"""
            <div style='background-color: #262626; 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin-top: 20px; 
                        color: white;'>
                <b>Total Cost with {friend}:</b> <br>
                <b>Your Total Share:</b> ${total_user_cost:.2f} <br>
                <b>{friend}'s Total Share:</b> ${total_friend_cost:.2f}
            </div>
            """, unsafe_allow_html=True)

        if not matches_found:
            st.info("No matches found with your friends' grocery lists.")
        else:
            st.write("These are the matches based on your grocery lists. You can now coordinate purchases with your friends.")
            # Add "Scan Receipt" button
            if st.button("Scan Receipt"):
                self.scan_receipt()


    def render_friends_page(self):
            st.markdown("""
                <style>
                input, button {
                    border: 2px solid #F39C12 !important;
                    outline: none !important;
                    background-color: #262626; 
                    color: white; 
                    border-radius: 5px; 
                }
                input:focus {
                    border: 2px solid #F39C12 !important; 
                }
                input.valid {
                    border: 2px solid green !important;
                }
                input.invalid {
                    border: 2px solid red !important; 
                }
                button:hover {
                    background-color: #F39C12; 
                    color: black; 
                }
                </style>
            """, unsafe_allow_html=True)
            
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
            
            friend_username = st.text_input('Enter Friend\'s Username', placeholder="Username to add")
            
            col_space, col_button, col_space2 = st.columns([1, 2, 1])
            
            with col_button:
                if st.button('Add Friend', use_container_width=True):
                    if not friend_username:
                        st.warning('Please enter a username')
                    elif friend_username == st.session_state.username:
                        st.error('You cannot add yourself as a friend')
                    else:
                        result = self.db.add_friend(st.session_state.username, friend_username)
                        if result:
                            st.success(f'{friend_username} added to your friends')
                            st.session_state.page = 'friends'
                            st.rerun()
                        else:
                            # Provide more specific error messages
                            st.error(f'Unable to add {friend_username}. Check if the username exists or is already your friend.')


            # Friends List with Card-like Display
            st.subheader('Your Friends')
            friends = self.db.get_friends(st.session_state.username)

            if friends:
                for friend in friends:
                    # Create card-like display for each friend
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
                
                for index, friend in enumerate(friends):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"👤 {friend}") 
                    with col2:
                        if st.button(f"❌ Remove {friend}", key=f"remove_{index}_{friend}"):
                            self.db.remove_friend(st.session_state.username, friend)
                            st.success(f"{friend} has been removed.")
                            # Refresh page and show updated list
                            st.session_state.page = 'friends'
                            st.experimental_rerun()
            else:
                st.info("You have no friends added yet. Start connecting!")

    def scan_receipt(self):
        """Launch the camera for scanning a receipt and display it in Streamlit."""
        # Initialize the camera
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            st.error("Error: Could not access the camera.")
            return

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Create a placeholder for the camera feed
        frame_placeholder = st.empty()

        while True:
            success, frame = cam.read()
            if not success:
                st.warning("Warning: Failed to capture frame. Retrying...")
                continue

            # Convert the frame to RGB (Streamlit expects RGB images)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the frame in Streamlit
            frame_placeholder.image(frame_rgb, caption="Scan Receipt", use_container_width=True)

            # Check for 'q' key press to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        cam.release()
        cv2.destroyAllWindows()
        frame_placeholder.empty()  # Clear the placeholder when done