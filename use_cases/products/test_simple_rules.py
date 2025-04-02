import json
from business_rules.engine import run_all
from business_rules.variables import BaseVariables, numeric_rule_variable
from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC
import datetime


class DummyProduct:
    """
    A dummy product class for testing purposes.
    """

    def __init__(self, current_inventory, expiration_days):
        self.current_inventory = current_inventory
        self.expiration_days = expiration_days
        self.price = 100  # Default price for testing

    def save(self):
        """
        Simulates saving the product.
        """
        print(f"Saving product with price: {self.price}")


class ProductVariables(BaseVariables):
    """
    Variables for the dummy product.
    """

    def __init__(self, product):
        self.product = product

    @numeric_rule_variable
    def current_inventory(self):
        return self.product.current_inventory

    @numeric_rule_variable
    def expiration_days(self):
        return self.product.expiration_days


class ProductActions(BaseActions):
    """
    Actions for the dummy product.
    """

    def __init__(self, product):
        self.product = product

    @rule_action(params={"sale_percentage": FIELD_NUMERIC})
    def put_on_sale(self, sale_percentage):
        self.product.price = (1.0 - sale_percentage) * self.product.price
        self.product.save()


def load_rules_from_json(filepath):
    """
    Loads rules from a JSON file.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        list: A list of rules.
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


def test_rules_with_product(product, rules_filepath):
    """
    Tests the given product against the rules loaded from the JSON file.

    Args:
        product (DummyProduct): The product to test.
        rules_filepath (str): The path to the rules JSON file.

    Returns:
        bool: True if any rule was triggered, False otherwise.
    """
    rules = load_rules_from_json(rules_filepath)
    if not rules:
        return False

    triggered = False
    for rule in rules:
        result = run_all(
            rule_list=[rule],
            defined_variables=ProductVariables(product),
            defined_actions=ProductActions(product),
        )
        if result:
            triggered = True
    return triggered


def main():
    """
    Main function to demonstrate the testing.
    """
    rules_filepath = "./use_cases/products/rules-simple.json"

    # Test case 1: Should trigger the rule (expiration_days < 5 and current_inventory > 20)
    product1 = DummyProduct(current_inventory=30, expiration_days=3)
    print(f"\nTesting product 1 (inventory: {product1.current_inventory}, expiration: {product1.expiration_days})")
    test_rules_with_product(product1, rules_filepath)
    print(f"Product 1 final price: {product1.price}")

    # Test case 2: Should NOT trigger the rule (expiration_days > 5)
    product2 = DummyProduct(current_inventory=30, expiration_days=10)
    print(f"\nTesting product 2 (inventory: {product2.current_inventory}, expiration: {product2.expiration_days})")
    test_rules_with_product(product2, rules_filepath)
    print(f"Product 2 final price: {product2.price}")

    # Test case 3: Should NOT trigger the rule (current_inventory < 20)
    product3 = DummyProduct(current_inventory=10, expiration_days=3)
    print(f"\nTesting product 3 (inventory: {product3.current_inventory}, expiration: {product3.expiration_days})")
    test_rules_with_product(product3, rules_filepath)
    print(f"Product 3 final price: {product3.price}")

    # Test case 4: Should NOT trigger the rule (current_inventory < 20 and expiration_days > 5)
    product4 = DummyProduct(current_inventory=10, expiration_days=10)
    print(f"\nTesting product 4 (inventory: {product4.current_inventory}, expiration: {product4.expiration_days})")
    test_rules_with_product(product4, rules_filepath)
    print(f"Product 4 final price: {product4.price}")

if __name__ == "__main__":
    main()
