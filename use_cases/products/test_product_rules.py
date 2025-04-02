import datetime
import json  # For pretty printing results if needed

from email.mime.text import MIMEText
from business_rules.variables import BaseVariables, numeric_rule_variable, string_rule_variable, select_rule_variable
from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC, FIELD_SELECT
from business_rules import run_all

# --- Configuration (Move these to a config file in a real application) ---
# These are placeholder values. Replace them with your actual credentials.
EMAIL_SENDER = "your_email@example.com"  # Replace with your email
EMAIL_RECIPIENT = "recipient@example.com"  # Replace with recipient email
SMS_NUMBER = "+1234567890"  # Replace with a phone number
RULES_FILE = "rules-simple.json"  # Name of the JSON file containing the rules
# --- End Configuration ---

# Dummy classes for demonstration purposes


class Product:
    """
    Represents a product in the system.
    """

    def __init__(self, id, current_inventory, price, orders, related_products=None, stock_state=None):
        """
        Initializes a Product object.

        Args:
            id (int): The product ID.
            current_inventory (int): The current inventory level.
            price (float): The product price.
            orders (list): A list of Order objects related to this product.
            related_products (list, optional): A list of related product IDs. Defaults to None.
            stock_state (str, optional): The current stock state (e.g., 'available', 'last_items'). Defaults to None.
        """
        self.id = id
        self.current_inventory = current_inventory
        self.price = price
        self.orders = orders
        self.related_products = related_products or []
        self.stock_state = stock_state

    def save(self):
        """
        Simulates saving the product to a database.
        """
        print(
            f"Saving product {self.id} with price {self.price} and stock state {self.stock_state}")


class ProductOrder:
    """
    Represents an order for a product.
    """
    objects = []  # Class-level list to store all created orders

    def __init__(self, product_id, quantity):
        """
        Initializes a ProductOrder object.

        Args:
            product_id (int): The ID of the product being ordered.
            quantity (int): The quantity of the product being ordered.
        """
        self.product_id = product_id
        self.quantity = quantity

    @staticmethod
    def create(product_id, quantity):
        """
        Creates a new ProductOrder and adds it to the objects list.

        Args:
            product_id (int): The ID of the product being ordered.
            quantity (int): The quantity of the product being ordered.
        """
        order = ProductOrder(product_id, quantity)
        ProductOrder.objects.append(order)
        print(f"Created order: {order.__dict__}")


class Order:
    """
    Represents a generic order with an expiration date.
    """

    def __init__(self, expiration_date):
        """
        Initializes an Order object.

        Args:
            expiration_date (datetime.date): The expiration date of the order.
        """
        self.expiration_date = expiration_date


class Products:
    """
    A utility class to manage product data.
    """
    all_products = []  # Class-level list to store all products

    @staticmethod
    def top_holiday_items():
        """
        Returns a list of top holiday items.

        Returns:
            list: A list of dictionaries, each representing a holiday item.
        """
        return [
            {'label': 'Christmas Tree', 'name': 'christmas_tree'},
            {'label': 'Gift Wrap', 'name': 'gift_wrap'},
            {'label': 'Ornaments', 'name': 'ornaments'},
        ]

    @staticmethod
    def add_product(product):
        """
        Adds a product to the all_products list.

        Args:
            product (Product): The Product object to add.
        """
        Products.all_products.append(product)

    @staticmethod
    def get_all_products():
        """
        Returns all products in the all_products list.

        Returns:
            list: A list of Product objects.
        """
        return Products.all_products


class ProductVariables(BaseVariables):
    """
    Defines the variables that can be used in the business rules, based on a Product.
    """

    def __init__(self, product):
        """
        Initializes a ProductVariables object.

        Args:
            product (Product): The Product object to extract variables from.
        """
        self.product = product

    @numeric_rule_variable
    def current_inventory(self):
        """
        Returns the current inventory level of the product.
        """
        return self.product.current_inventory

    @numeric_rule_variable(label='Days until expiration')
    def expiration_days(self):
        """
        Returns the number of days until the last order expires.
        Returns 999 if there are no orders.
        """
        if not self.product.orders:
            return 999  # Handle case where there are no orders
        last_order = self.product.orders[-1]
        return (last_order.expiration_date - datetime.date.today()).days

    @string_rule_variable()
    def current_month(self):
        """
        Returns the current month as a string (e.g., "December").
        """
        return datetime.datetime.now().strftime("%B")

    @select_rule_variable(options=Products.top_holiday_items())
    def goes_well_with(self):
        """
        Returns the list of related products.
        """
        return self.product.related_products


class ProductActions(BaseActions):
    """
    Defines the actions that can be performed by the business rules on a Product.
    """

    def __init__(self, product):
        """
        Initializes a ProductActions object.

        Args:
            product (Product): The Product object to perform actions on.
        """
        self.product = product

    @rule_action(params={"sale_percentage": FIELD_NUMERIC})
    def put_on_sale(self, sale_percentage):
        """
        Puts the product on sale by reducing its price.

        Args:
            sale_percentage (float): The percentage to reduce the price by (e.g., 0.25 for 25%).
        """
        self.product.price = (1.0 - sale_percentage) * self.product.price
        self.product.save()

    @rule_action(params={"number_to_order": FIELD_NUMERIC})
    def order_more(self, number_to_order):
        """
        Creates a new order for more of the product.

        Args:
            number_to_order (int): The quantity to order.
        """
        ProductOrder.create(product_id=self.product.id,
                            quantity=number_to_order)

    @rule_action(params=[{'fieldType': FIELD_SELECT,
                          'name': 'stock_state',
                          'label': 'Stock state',
                          'options': [
                              {'label': 'Available', 'name': 'available'},
                              {'label': 'Last items', 'name': 'last_items'},
                              {'label': 'Out of stock', 'name': 'out_of_stock'}
                          ]}])
    def change_stock_state(self, stock_state):
        """
        Changes the stock state of the product.

        Args:
            stock_state (str): The new stock state (e.g., 'available', 'last_items').
        """
        self.product.stock_state = stock_state
        self.product.save()

    @rule_action()
    def send_low_stock_email(self):
        """
        Sends an email alert for low stock.
        """
        subject = f"Low Stock Alert: Product {self.product.id}"
        body = f"Product {self.product.id} is running low on stock. Current inventory: {self.product.current_inventory}"
        self._send_email(subject, body)

    @rule_action()
    def send_low_stock_sms(self):
        """
        Sends an SMS alert for low stock.
        """
        message = f"Low Stock Alert: Product {self.product.id} - Inventory: {self.product.current_inventory}"
        self._send_sms(message)

    def _send_email(self, subject, body):
        """
        Simulates sending an email.

        Args:
            subject (str): The email subject.
            body (str): The email body.
        """
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECIPIENT

            print(
                f"Simulating sending Email from {EMAIL_SENDER} to {EMAIL_RECIPIENT}: Subject: {subject}")
        except Exception as e:
            print(f"Error sending email: {e}")

    def _send_sms(self, message):
        """
        Simulates sending an SMS.

        Args:
            message (str): The SMS message.
        """
        # In a real application, you would use an SMS gateway API here
        print(f"Simulating sending SMS to {SMS_NUMBER}: {message}")
        # Example using Twilio (you'd need to install the twilio library)
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     to=SMS_NUMBER,
        #     from_="+YOUR_TWILIO_NUMBER",
        #     body=message
        # )
        # print(f"SMS sent with SID: {message.sid}")


def load_rules_from_json(filepath):
    """
    Loads the business rules from a JSON file.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        list: A list of rules loaded from the JSON file.
    """
    try:
        with open(filepath, 'r') as f:
            rules = json.load(f)
        return rules
    except FileNotFoundError:
        print(f"Error: Rules file not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return []


# Load rules from JSON file
rules = load_rules_from_json(RULES_FILE)

# Example usage
# Create some dummy data
today = datetime.date.today()
product1 = Product(1, 30, 100, [Order(today + datetime.timedelta(days=3))])
product2 = Product(2, 3, 50, [Order(today + datetime.timedelta(days=30))])
product3 = Product(3, 15, 75, [Order(today + datetime.timedelta(days=10))])
product4 = Product(4, 8, 20, [])

# Add products to Products class
Products.add_product(product1)
Products.add_product(product2)
Products.add_product(product3)
Products.add_product(product4)

# Run the rules for each product
for product in [product1, product2, product3, product4]:
    print(f"\n--- Processing product {product.id} ---")
    run_all(rule_list=rules,
            defined_variables=ProductVariables(product),
            defined_actions=ProductActions(product))

print("\n--- Final Product Orders ---")
for order in ProductOrder.objects:
    print(order.__dict__)

print("\n--- Processing products with stop_on_first_trigger=True ---")
for product in Products.get_all_products():
    print(f"\n--- Processing product {product.id} ---")
    run_all(rule_list=rules,
            defined_variables=ProductVariables(product),
            defined_actions=ProductActions(product),
            stop_on_first_trigger=True
            )
