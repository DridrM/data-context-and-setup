import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist


class Order:
    '''
    DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''
    def __init__(self) -> None:
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
        
        # Date time columns names
        columns = orders.columns[3:]

        # Transform to datetime time columns
        for col in columns:
            orders.loc[:, col] = pd.to_datetime(orders[col]).copy()
        
        # Create the orders_wait_time df
        orders_wait_time = pd.DataFrame(columns = ["order_id", "wait_time", "expected_wait_time", "delay_vs_expected", "order_status"])
        
        # Create the columns wait times
        orders_wait_time.loc[:, 'wait_time'] = (orders.loc[:, 'order_purchase_timestamp'] - orders.loc[:, 'order_delivered_customer_date']) / np.timedelta64(24, 'h')
        orders_wait_time.loc[:, 'expected_wait_time'] = (orders.loc[:, 'order_purchase_timestamp'] - orders.loc[:, 'order_estimated_delivery_date']) / np.timedelta64(24, 'h')

        # Fill the column delay vs expected
        delay_vs_expected = (orders.loc[:, 'order_delivered_customer_date'] - orders.loc[:, 'order_estimated_delivery_date']) / np.timedelta64(24, 'h')
        orders_wait_time.loc[:, "delay_vs_expected"] = delay_vs_expected.apply(lambda x: x if x >= 0 else 0)

        # Fill the column order status
        orders_wait_time.loc[:, "order_status"] = orders.loc[:, "order_status"]
        
        # Fill the column order id
        orders_wait_time.loc[:, "order_id"] = orders.loc[:, "order_id"]
        
        return orders_wait_time

    def get_review_score(self) -> pd.DataFrame:
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

    def get_number_products(self) -> pd.DataFrame:
        """
        Returns a DataFrame with:
        order_id, number_of_products
        """
        items = self.data['order_items'].copy()
        
        # Create the new df
        number_products = items.loc[:, ["order_id", "order_item_id"]].groupby(by = "order_id").count().reset_index()
        # Rename the counting column
        number_products.rename(columns = {"order_item_id": "number_of_products"}, inplace = True)
        
        return number_products

    def get_number_sellers(self):
        """
        Returns a DataFrame with:
        order_id, number_of_sellers
        """
        items = self.data['order_items'].copy()
        
        # Create the new df
        number_sellers = items.loc[:, ["order_id", "seller_id"]].groupby(by = "order_id").count().reset_index()
        # Rename the counting column
        number_sellers.rename(columns = {"seller_id": "number_of_sellers"}, inplace = True)
        
        return number_sellers

    def get_price_and_freight(self) -> pd.DataFrame:
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
        # import data
        data = self.data
        orders = data['orders']
        order_items = data['order_items']
        sellers = data['sellers']
        customers = data['customers']

        # Since one zip code can map to multiple (lat, lng), take the first one
        geo = data['geolocation']
        geo = geo.groupby('geolocation_zip_code_prefix',
                          as_index=False).first()

        # Merge geo_location for sellers
        sellers_mask_columns = [
            'seller_id', 'seller_zip_code_prefix', 'geolocation_lat', 'geolocation_lng'
        ]

        sellers_geo = sellers.merge(
            geo,
            how='left',
            left_on='seller_zip_code_prefix',
            right_on='geolocation_zip_code_prefix')[sellers_mask_columns]

        # Merge geo_location for customers
        customers_mask_columns = ['customer_id', 'customer_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']

        customers_geo = customers.merge(
            geo,
            how='left',
            left_on='customer_zip_code_prefix',
            right_on='geolocation_zip_code_prefix')[customers_mask_columns]

        # Match customers with sellers in one table
        customers_sellers = customers.merge(orders, on='customer_id')\
            .merge(order_items, on='order_id')\
            .merge(sellers, on='seller_id')\
            [['order_id', 'customer_id','customer_zip_code_prefix', 'seller_id', 'seller_zip_code_prefix']]
        
        # Add the geoloc
        matching_geo = customers_sellers.merge(sellers_geo,
                                            on='seller_id')\
            .merge(customers_geo,
                   on='customer_id',
                   suffixes=('_seller',
                             '_customer'))
        # Remove na()
        matching_geo = matching_geo.dropna()

        matching_geo.loc[:, 'distance_seller_customer'] =\
            matching_geo.apply(lambda row:
                               haversine_distance(row['geolocation_lng_seller'],
                                                  row['geolocation_lat_seller'],
                                                  row['geolocation_lng_customer'],
                                                  row['geolocation_lat_customer']),
                               axis=1)
        # Since an order can have multiple sellers,
        # return the average of the distance per order
        order_distance =\
            matching_geo.groupby('order_id',
                                 as_index=False).agg({'distance_seller_customer':
                                                      'mean'})

        return order_distance

    def get_training_data(self,
                          is_delivered = True,
                          with_distance_seller_customer = False) -> pd.DataFrame:
        """
        Returns a clean DataFrame (without NaN), with the all following columns:
        ['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected',
        'order_status', 'dim_is_five_star', 'dim_is_one_star', 'review_score',
        'number_of_products', 'number_of_sellers', 'price', 'freight_value',
        'distance_seller_customer']
        """
        # Hint: make sure to re-use your instance methods defined above
        
        return self.get_wait_time(is_delivered)\
            .merge(self.get_review_score(), on = 'order_id')\
                .merge(self.get_number_products(), on = 'order_id')\
                    .merge(self.get_number_sellers(), on = 'order_id')\
                        .merge(self.get_price_and_freight(), on = 'order_id')\
                            .merge(self.get_distance_seller_customer(), on = 'order_id').dropna(axis = 0)
