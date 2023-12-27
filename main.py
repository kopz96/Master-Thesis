import streamlit as st
import pandas as pd
import tempfile
import Predict as p
import re
import time
import random

# Create a Streamlit app
st.set_page_config(layout="wide")  # Set the page layout to wide
st.title("Scan and Pay")

# Load the user data from the CSV file
users_df = pd.read_csv('users.csv', dtype=str)

# Check if the user is logged in
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

# Initialize an empty basket DataFrame
if 'basket_df' not in st.session_state:
    st.session_state.basket_df = pd.DataFrame(columns=['Product', 'Quantity'])

# Login Page
def login_page():
    st.subheader("Login")
    login_email = st.text_input("Email", key="log_email")
    login_password = st.text_input("Password", type="password", key="log_password")
    if st.button("Login"):
        user = users_df[(users_df['email'] == login_email) & (users_df['password'] == login_password)]
        if not user.empty:
            st.session_state.is_logged_in = True
            st.session_state.user_email = login_email
        else:
            st.error("Login failed. Invalid email or password.")

# Home Page
def scanpay():
    #st.title('Upload Images')
    st.title('Identify Product from Images')
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Create a temporary file, save the uploaded file into it
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        prediction = p.predict(tfile.name)

        # Extract bounding box information
        predictions_info = prediction["predictions"]

        for info in predictions_info:
            product_name = info["mapped_product_name"]
            quantity = info["quantity"] if "quantity" in info else 1

            # Check if the product is already in the basket
            if product_name in st.session_state.basket_df['Product'].values:
                # Update the quantity if the product is already in the basket
                st.session_state.basket_df.loc[st.session_state.basket_df['Product'] == product_name, 'Quantity'] += quantity
            else:
                # Add a new row if the product is not in the basket
                st.session_state.basket_df = st.session_state.basket_df.append({'Product': product_name, 'Quantity': quantity}, ignore_index=True)

        return prediction

# Basket Page
def basket():
    st.subheader("Basket")
    #st.write("This is the Basket page.")

    # Check if the basket is not empty
    if not st.session_state.basket_df.empty:
        st.write("Products in the basket:")

        # Display the products in the basket with quantity and buttons
        for index, row in st.session_state.basket_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Use beta_columns for better layout control

            # Column 1: Product name
            col1.write(f"Product: {row['Product']}")

            # Column 2: Quantity
            col2.write(f"Quantity: {row['Quantity']}")

            # Column 3: Price per piece
            price_per_piece = 2
            col3.write(f"Price per piece: €{price_per_piece:.2f}")

            # Column 4 and 5: Buttons for decreasing and increasing quantity
            decrease_button = col5.button(f"Decrease", key=f"decrease_button_{index}")
            increase_button = col4.button(f"Increase", key=f"increase_button_{index}")

            # Decrease the quantity by 1 when the decrease button is clicked
            if decrease_button:
                st.session_state.basket_df.at[index, 'Quantity'] -= 1

            # Increase the quantity by 1 when the increase button is clicked
            if increase_button:
                st.session_state.basket_df.at[index, 'Quantity'] += 1

    else:
        st.write("The basket is empty.")

# Summary Page
def summary():
    st.subheader("Summary")


    # Check if the basket is not empty
    if not st.session_state.basket_df.empty:
        st.write("Products in the basket:")

        total_price = 0  # Initialize total price

        # Display the products in the basket with quantity, price per piece, and total price
        for index, row in st.session_state.basket_df.iterrows():
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Use beta_columns for better layout control

            # Column 1: Product name
            col1.write(f"Product: {row['Product']}")

            # Column 2: Quantity
            col2.write(f"Quantity: {row['Quantity']}")

            # Column 3: Price per piece
            price_per_piece = 2
            col3.write(f"Price per piece: €{price_per_piece:.2f}")

            # Column 4: Total price for the product
            product_total_price = row['Quantity'] * price_per_piece
            col4.write(f"Total Price: €{product_total_price:.2f}")

            # Update the total price
            total_price += product_total_price
            st.session_state.total_amount = total_price
        # Display the total price at the end
        st.write(f"Total Price for all products: €{total_price:.2f}")

    else:
        st.write("The basket is empty.")


# Payment Page
def payment():
    st.subheader("Payment Information")
    st.write("Enter your payment details for the payment process.")

    # Input fields for payment information
    name = st.text_input("Name (Alphabets only):", key="payment_name")
    iban = st.text_input("IBAN (16-digit number only):", key="payment_iban")
    card_expiry = st.text_input("Card Expiry (MM/YYYY):", key="payment_expiry")

    # Access the total amount variable from the session state
    total_amount_from_basket = st.session_state.total_amount
    st.write(f"Total Amount from the Basket: €{total_amount_from_basket:.2f}")

    # Button to initiate the payment process
    if st.button("Make Payment"):
        # Validate the input values
        if not name.isalpha():
            st.error("Name should contain only alphabets.")
        elif not re.match(r'^\d{16}$', iban):
            st.error("IBAN should be a 16-digit number.")
        elif not re.match(r'^(0[1-9]|1[0-2])/(20\d{2})$', card_expiry):
            st.error("Card Expiry should be in MM/YYYY format.")
        else:
            # Display success message if the input is valid
            st.success("Payment process successful!")

# Sidebar navigation
st.sidebar.subheader("Navigation")
pages = ["ScanPay", "Basket", "Summary", "Payment"]

# If the user is logged in, allow navigation to other pages
if st.session_state.is_logged_in:
    selected_page = st.sidebar.selectbox("Select Page", pages)
    if selected_page == "ScanPay":
        prediction = scanpay()
    elif selected_page == "Basket":
        basket()
    elif selected_page == "Summary":
        summary()
    elif selected_page == "Payment":
        payment()
else:
    # If not logged in, show the login page
    login_page()
