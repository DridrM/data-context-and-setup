import os
import re
import pandas as pd

# Setting the relative path
RELATIVE_CSV_PATH = "../data/csv"

class Olist:
    
    def __init__(self, relative_csv_path = RELATIVE_CSV_PATH) -> None:
        """
        Arguments :
        - relative_csv_path : relative path to the csv to load
        - csv path : absolute path recontructed from the relative csv path and the path to the cwd
        """
        self.relative_csv_path = relative_csv_path
        self.csv_path = os.path.join(os.path.dirname(__file__), relative_csv_path)
    
    def get_data(self) -> dict:
        """
        This function returns a Python dict.
        Its keys should be 'sellers', 'orders', 'order_items' etc...
        Its values should be pandas.DataFrames loaded from csv files
        """
        # Hints 1: Build csv_path as "absolute path" in order to call this method from anywhere.
            # Do not hardcode your path as it only works on your machine ('Users/username/code...')
            # Use __file__ instead as an absolute path anchor independant of your usename
            # Make extensive use of `breakpoint()` to investigate what `__file__` variable is really
        # Hint 2: Use os.path library to construct path independent of Mac vs. Unix vs. Windows specificities
        
        # Listing csv files with os.listdir and remove non csv file names from the list
        pattern = r"\.csv"
        file_names = [path for path in os.listdir(self.csv_path) if re.search(pattern, path)]
        
        # List containing df names
        key_names = [name.replace('.csv', '').replace('_dataset', '').replace('olist_', '') for name in file_names]
        
        # Dict containing each df from csv and their names as dict keys
        data = {name: pd.read_csv(os.path.join(self.csv_path, file_name)) for name, file_name in zip(key_names, file_names)}
        
        return data
    
    def ping(self) -> None:
        """
        You call ping I print pong.
        """
        print("pong")

# Tests with name == main
if __name__ == "__main__":
    olist_test = Olist()
    data_test = olist_test.get_data()
    print(len(data_test))
