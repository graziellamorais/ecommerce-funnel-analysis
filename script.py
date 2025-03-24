import pandas as pd

# Load data
visits = pd.read_csv('visits.csv', parse_dates=[1])
cart = pd.read_csv('cart.csv', parse_dates=[1])
checkout = pd.read_csv('checkout.csv', parse_dates=[1])
purchase = pd.read_csv('purchase.csv', parse_dates=[1])

# Clean data: Remove duplicates and standardize user_id format
cart['user_id'] = cart['user_id'].astype(str).str.strip()
checkout['user_id'] = checkout['user_id'].astype(str).str.strip()
purchase['user_id'] = purchase['user_id'].astype(str).str.strip()

cart = cart.drop_duplicates(subset='user_id')
checkout = checkout.drop_duplicates(subset='user_id')
purchase = purchase.drop_duplicates(subset='user_id')

# Merge data
visits_cart_merge = pd.merge(visits, cart, how='left', on='user_id')
total_visits = len(visits_cart_merge)

# Percentage of users who visited but didn't add to cart
no_cart = len(visits_cart_merge[visits_cart_merge.cart_time.isnull()])
percent_no_cart = float(no_cart) / total_visits * 100
print(f"Percent of users who didn't add to cart: {percent_no_cart:.2f}%")

cart_checkout_merge = pd.merge(cart, checkout, how='left', on='user_id')
total_cart = len(cart_checkout_merge)

# Percentage of users who added to cart but didn't proceed to checkout
no_checkout = len(cart_checkout_merge[cart_checkout_merge.checkout_time.isnull()])
percent_no_checkout = float(no_checkout) / total_cart * 100
print(f"Percent of users who added to cart but didn't checkout: {percent_no_checkout:.2f}%")

# Fully merged data
all_data = visits.merge(cart, how='left', on='user_id') \
                 .merge(checkout, how='left', on='user_id') \
                 .merge(purchase, how='left', on='user_id')

print(all_data.head())

# Percentage of users who proceeded to checkout but didn't purchase
total_checkout = len(all_data[all_data.checkout_time.notnull()])
no_purchase = len(all_data[(all_data.checkout_time.notnull()) & (all_data.purchase_time.isnull())])
percent_no_purchase = float(no_purchase) / total_checkout * 100
print(f"Percent of users who checked out but didn't purchase: {percent_no_purchase:.2f}%")

# Clean drop-off rates by converting to float and handling NaN values
drop_off_rates: dict[str, float] = {
    'Visit → Cart': float(round(percent_no_cart, 2)) if not pd.isna(percent_no_cart) else 0.0,
    'Cart → Checkout': float(round(percent_no_checkout, 2)) if not pd.isna(percent_no_checkout) else 0.0,
    'Checkout → Purchase': float(round(percent_no_purchase, 2)) if not pd.isna(percent_no_purchase) else 0.0
}

# Find the weakest step without Pylance type issues
weakest_step = max(drop_off_rates, key=drop_off_rates.get)  # type: ignore
print(f"Weakest step: {weakest_step} ({drop_off_rates[weakest_step]:.2f}%)")

# Ensure the 'visit_time' and 'purchase_time' columns are datetime objects
all_data['visit_time'] = pd.to_datetime(all_data['visit_time'])
all_data['purchase_time'] = pd.to_datetime(all_data['purchase_time'])

# Create a new column 'time_to_purchase' that is the difference between 'purchase_time' and 'visit_time'
all_data['time_to_purchase'] = (all_data['purchase_time'] - all_data['visit_time'])

# Examine the result by printing the new column
print(all_data[['user_id', 'time_to_purchase']].head())  # Print the first few rows

# Calculate the average time to purchase
average_time_to_purchase = all_data['time_to_purchase'].mean()

# Print the average time to purchase
print(f"The average time from visit to purchase is: {average_time_to_purchase}")
