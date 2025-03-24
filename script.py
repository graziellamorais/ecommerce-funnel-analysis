import pandas as pd

# Function to load data
def load_data():
    visits = pd.read_csv('visits.csv', parse_dates=[1])
    cart = pd.read_csv('cart.csv', parse_dates=[1])
    checkout = pd.read_csv('checkout.csv', parse_dates=[1])
    purchase = pd.read_csv('purchase.csv', parse_dates=[1])
    return visits, cart, checkout, purchase

# Function to clean data by removing duplicates and standardizing user_id format
def clean_data(cart, checkout, purchase):
    cart['user_id'] = cart['user_id'].astype(str).str.strip()
    checkout['user_id'] = checkout['user_id'].astype(str).str.strip()
    purchase['user_id'] = purchase['user_id'].astype(str).str.strip()

    cart = cart.drop_duplicates(subset='user_id')
    checkout = checkout.drop_duplicates(subset='user_id')
    purchase = purchase.drop_duplicates(subset='user_id')

    return cart, checkout, purchase

# Function to calculate drop-off percentages
def calculate_drop_off_percentages(visits, cart, checkout, purchase):
    # Merge visits with cart data
    visits_cart_merge = pd.merge(visits, cart, how='left', on='user_id')
    total_visits = len(visits_cart_merge)
    no_cart = len(visits_cart_merge[visits_cart_merge.cart_time.isnull()])
    percent_no_cart = float(no_cart) / total_visits * 100

    # Merge cart with checkout data
    cart_checkout_merge = pd.merge(cart, checkout, how='left', on='user_id')
    total_cart = len(cart_checkout_merge)
    no_checkout = len(cart_checkout_merge[cart_checkout_merge.checkout_time.isnull()])
    percent_no_checkout = float(no_checkout) / total_cart * 100

    # Fully merge visits, cart, checkout, and purchase data
    all_data = visits.merge(cart, how='left', on='user_id') \
                     .merge(checkout, how='left', on='user_id') \
                     .merge(purchase, how='left', on='user_id')

    total_checkout = len(all_data[all_data.checkout_time.notnull()])
    no_purchase = len(all_data[(all_data.checkout_time.notnull()) & (all_data.purchase_time.isnull())])
    percent_no_purchase = float(no_purchase) / total_checkout * 100

    return percent_no_cart, percent_no_checkout, percent_no_purchase, all_data

# Function to print drop-off percentages
def print_drop_off_percentages(percent_no_cart, percent_no_checkout, percent_no_purchase):
    print(f"Percent of users who didn't add to cart: {percent_no_cart:.2f}%")
    print(f"Percent of users who added to cart but didn't checkout: {percent_no_checkout:.2f}%")
    print(f"Percent of users who checked out but didn't purchase: {percent_no_purchase:.2f}%")

# Function to calculate and print the weakest step
def calculate_weakest_step(percent_no_cart, percent_no_checkout, percent_no_purchase):
    drop_off_rates = {
        'Visit → Cart': float(round(percent_no_cart, 2)) if not pd.isna(percent_no_cart) else 0.0,
        'Cart → Checkout': float(round(percent_no_checkout, 2)) if not pd.isna(percent_no_checkout) else 0.0,
        'Checkout → Purchase': float(round(percent_no_purchase, 2)) if not pd.isna(percent_no_purchase) else 0.0
    }
    weakest_step = max(drop_off_rates, key=drop_off_rates.get)
    print(f"Weakest step: {weakest_step} ({drop_off_rates[weakest_step]:.2f}%)")

# Function to calculate time to purchase and print the result
def calculate_time_to_purchase(all_data):
    all_data['visit_time'] = pd.to_datetime(all_data['visit_time'])
    all_data['purchase_time'] = pd.to_datetime(all_data['purchase_time'])
    all_data['time_to_purchase'] = (all_data['purchase_time'] - all_data['visit_time'])
    
    # Print the average time to purchase
    average_time_to_purchase = all_data['time_to_purchase'].mean()
    print(f"The average time from visit to purchase is: {average_time_to_purchase}")

# Main function to execute the full process
def main():
    # Load data
    visits, cart, checkout, purchase = load_data()

    # Clean data
    cart, checkout, purchase = clean_data(cart, checkout, purchase)

    # Calculate drop-off percentages
    percent_no_cart, percent_no_checkout, percent_no_purchase, all_data = calculate_drop_off_percentages(visits, cart, checkout, purchase)

    # Print drop-off percentages
    print_drop_off_percentages(percent_no_cart, percent_no_checkout, percent_no_purchase)

    # Calculate and print the weakest step
    calculate_weakest_step(percent_no_cart, percent_no_checkout, percent_no_purchase)

    # Calculate and print time to purchase
    calculate_time_to_purchase(all_data)

if __name__ == "__main__":
    main()
