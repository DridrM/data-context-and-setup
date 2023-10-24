import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist


class Order:
    '''
    DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''
    def __init__(self):
        # Assign an attribute ".data" to all new instances of Order
        self.data = Olist().get_data()

    def get_wait_time(self, is_delivered = True) -> pd.DataFrame:
        """
        Returns a DataFrame with:
        [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        and filters out non-delivered orders unless specified
        """
        # Hint: Within this instance method, you have access to the instance of the class Order in the variable self, as well as all its attributes
        orders = self.data['orders'].copy()
        
        if is_delivered:
            # If true replace the order df by a filtered version of the df by order status = delivered
            orders = orders.loc[orders.loc[:, 'order_status'] == 'delivered', :]
        
        else:
            # Else don't modify the df
            pass
        
        # Date time columns names
        columns = orders.columns[3:]

        # Transform to datetime time columns
        for col in columns:
            orders.loc[:, col] = pd.to_datetime(orders[col]).copy()
        
        # Create the orders_wait_time df
        orders_wait_time = pd.DataFrame(columns = ["order_id", "wait_time", "expected_wait_time", "delay_vs_expected", "order_status"])
        
        # Create the columns wait times
        orders_wait_time.loc[:, 'wait_time'] = orders.loc[:, 'order_delivered_customer_date'] - orders.loc[:, 'order_purchase_timestamp']
        orders_wait_time.loc[:, 'expected_wait_time'] = orders.loc[:, 'order_estimated_delivery_date'] - orders.loc[:, 'order_purchase_timestamp']

        # Fill the column delay vs expected
        delay_vs_expected = orders_wait_time.loc[:, 'expected_wait_time'].dt.days - orders_wait_time.loc[:, 'wait_time'].dt.days
        orders_wait_time.loc[:, "delay_vs_expected"] = delay_vs_expected.apply(lambda x: x if x >= 0 else 0)

        # Fill the column order status
        orders_wait_time.loc[:, "order_status"] = orders.loc[:, "order_status"]
        
        # Fill the column order id
        orders_wait_time.loc[:, "order_id"] = orders.loc[:, "order_id"]
        
        return orders_wait_time

    def get_review_score(self):
        """
        Returns a DataFrame with:
        order_id, dim_is_five_star, dim_is_one_star, review_score
        """
        reviews = self.data['order_reviews'].copy()
        
        # Create the new empty df
        review_score = pd.DataFrame(columns = ["order_id", "dim_is_five_star", "dim_is_one_star", "review_score"])

        # Create the column dim is five star
        review_score.loc[:, "dim_is_five_star"] = reviews.loc[:, "review_score"].apply(lambda x: 1 if x == 5 else 0)

        # Create the column dim is one star
        review_score.loc[:, "dim_is_one_star"] = reviews.loc[:, "review_score"].apply(lambda x: 1 if x == 1 else 0)

        # Fill the column review score
        review_score.loc[:, "review_score"] = reviews.loc[:, "review_score"]

        # Fill the column order id
        review_score.loc[:, "order_id"] = reviews.loc[:, "order_id"]
        
        return review_score

    def get_number_products(self):
        """
        Returns a DataFrame with:
        order_id, number_of_products
        """
        items = self.data['order_items'].copy()
        
        # Create the new df
        number_products = items.loc[:, ["order_id", "order_item_id"]].groupby(by = "order_id").count().reset_index()       
        
        return number_products

    def get_number_sellers(self):
        """
        Returns a DataFrame with:
        order_id, number_of_sellers
        """
        items = self.data['order_items'].copy()
        
        # Create the new df
        number_sellers = items.loc[:, ["order_id", "seller_id"]].groupby(by = "order_id").count().reset_index()
        
        return number_sellers

    def get_price_and_freight(self):
        """
        Returns a DataFrame with:
        order_id, price, freight_value
        """
        items = self.data['order_items'].copy()
        
        # Creat new df
        price_fret = items.loc[:, ["order_id", "price", "freight_value"]].groupby(by = "order_id").agg('sum').reset_index()
        
        return price_fret

    # Optional
    def get_distance_seller_customer(self):
        """
        Returns a DataFrame with:
        order_id, distance_seller_customer
        """
        pass  # YOUR CODE HERE

    def get_training_data(self,
                          is_delivered=True,
                          with_distance_seller_customer=False):
        """
        Returns a clean DataFrame (without NaN), with the all following columns:
        ['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected',
        'order_status', 'dim_is_five_star', 'dim_is_one_star', 'review_score',
        'number_of_products', 'number_of_sellers', 'price', 'freight_value',
        'distance_seller_customer']
        """
        # Hint: make sure to re-use your instance methods defined above
        pass  # YOUR CODE HERE
