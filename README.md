# PantryPal 🛒

## Overview

**PantryPal** is a collaborative grocery list management application that allows users to connect with friends, share grocery lists, and find matching items across their networks. Built with **Streamlit** and **SQLite**, this app makes grocery planning cheaper and reduces student food waste. 🤝🍏

## Why We Made It 🎓💸

As university students, we understand the struggle of cooking for one person. 🍽️ Shopping for groceries often means buying items in large quantities or bulk, which can be both wasteful and expensive. 🛒💰 Many items are packaged for families or larger households, leaving us with leftovers that go bad and money wasted. 

**PantryPal** was created to solve this problem. By connecting students with friends and sharing grocery lists, we can avoid buying excess food. Instead, users can purchase what they need, share items with others, and reduce both food waste and financial waste. 🌱💵 This app helps students save money and eat more efficiently while reducing their environmental impact. 🌍✨

## Features 🌟

- **User Authentication 🔐**:
  - Secure user registration and login
  - Password hashing for enhanced security

- **Friend Management 👥**:
  - Add and connect with friends within the app
  - View your current friend list

- **Grocery List Tracking 📝**:
  - Add grocery items with quantity and unit
  - Track personal grocery needs

- **Matching Groceries 🔄**:
  - Automatically find matching grocery items among friends
  - Easily identify shared shopping needs

## Prerequisites 🖥️

- Python 3.8+
- pip (Python package manager)

## Installation 🚀

1. Clone the repository

2. Create a virtual environment (optional but recommended)

3. Install required dependencies

## Dependencies 📦

- **Streamlit**: For building the app's interactive web interface.
- **SQLite3**: For managing the database.
- **hashlib**: For securely hashing passwords.

## How to Run 🏃‍♀️

To run the application, execute the following command in your terminal:

```bash
streamlit run main.py
```

This will launch the app in your default web browser.

## Project Structure 📁

- `main.py`: Primary application entry point (runs the Streamlit app)
- `models.py`: Defines the database models and migrations
- `app.py`: Core application logic (handles user interactions and functionality)
- `grocery_share.db`: SQLite database file (automatically created)

## Usage 🛒

1. **Registration**: Create a new account or log in.
2. **Add Friends**: Navigate to the "Friends" tab to add friends by their username.
3. **Create Grocery List**: Add items to your grocery list, specifying quantities and units.
4. **Find Matches**: Check the "Matches" tab to see grocery items that are shared with your friends.

## Security Notes 🔒

- Passwords are securely hashed using SHA-256.
- Unique constraints prevent the creation of duplicate usernames and emails.
- Friend connections are secure and bidirectional (both users must approve the connection).

## Potential Improvements 🔧

- Implement email verification for account security.
- Add password reset functionality for user convenience.
- Allow shared or collaborative editing of grocery lists.
- Create more sophisticated matching algorithms to improve item suggestions.
- Implement data export/import (e.g., CSV or JSON).

