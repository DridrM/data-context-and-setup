from math import radians, sin, cos, asin, sqrt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Compute distance between two pairs of coordinates (lon1, lat1, lon2, lat2)
    See - (https://en.wikipedia.org/wiki/Haversine_formula)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def return_significative_coef(model):
    """
    Returns p_value, lower and upper bound coefficients
    from a statsmodels object.
    """
    # Extract p_values
    p_values = model.pvalues.reset_index()
    p_values.columns = ['variable', 'p_value']

    # Extract coef_int
    coef = model.params.reset_index()
    coef.columns = ['variable', 'coef']
    return p_values.merge(coef,
                          on='variable')\
                   .query("p_value<0.05").sort_values(by='coef',
                                                      ascending=False)


def plot_kde_plot(df, variable, dimension):
    """
    Plot a side by side kdeplot for `variable`, split
    by `dimension`.
    """
    g = sns.FacetGrid(df,
                      hue=dimension,
                      col=dimension)
    g.map(sns.kdeplot, variable)


def it_costs(n_sellers: float, n_products: float, alpha = 3157.27, beta = 978.23) -> float:
    """Compute the it costs of Olist"""
    return round(alpha * np.sqrt(n_sellers) + beta * np.sqrt(n_products))


def optimal_nb_sellers(seller_df: pd.DataFrame, 
                     criterias: list,
                     total_seller_remove: int, 
                     yield_ = False) -> dict:
    """Compute the margin or the yield vs the number of sellers removed classified by a list of criterias"""
    
    # Sort the sellers by the criterias
    df = seller_df.sort_values(by = criterias, ascending = True).reset_index().copy()
    # Set the output dict
    margin_dict = {}
    # Ceil the maximum number of sellers to remove as the maximum number of sellers
    max_remove = min(total_seller_remove, df.shape[0])
    
    # Iterate over the number of sellers to remove
    for n in range(max_remove):
        
        # If yield argument is choosen, compute the yield
        if yield_:
            margin_dict[n] =  1 - it_costs(df.shape[0], df.quantity.sum()) / df.profits.sum()
        
        # Else compute the margin
        else:
            margin_dict[n] =  df.profits.sum() - it_costs(df.shape[0], df.quantity.sum())
        
        # Drop the worst seller of the iteration given the criterias
        df = df.drop(labels = n, axis = 0)
    
    return margin_dict