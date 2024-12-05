import json
import pandas as pd
from datetime import datetime

def parse_transactions(json_data):
    """
    Parse transaction data from JSON and convert to a pandas DataFrame.
    
    Args:
        json_data (str or dict): JSON data either as a string or dictionary
    
    Returns:
        pandas.DataFrame: Formatted transaction data
    """
    # Load JSON if it's a string
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Convert to DataFrame
    df = pd.DataFrame(data['transactions'])
    
    # Convert date strings to datetime objects
    df['date'] = pd.to_datetime(df['date'])
    
    # Format amount as currency
    df['amount'] = df['amount'].apply(lambda x: f"${abs(x):.2f}")
    
    # Reorder columns for better readability
    columns_order = ['date', 'amount', 'merchant', 'category', 'termText']
    df = df[columns_order]
    
    # Sort by date
    df = df.sort_values('date')
    
    return df

def display_summary(df):
    """
    Print summary statistics about the transactions.
    
    Args:
        df (pandas.DataFrame): Transaction data
    """
    # Convert amount strings back to float for calculations
    amounts = df['amount'].apply(lambda x: float(x.replace('$', '')))
    
    print("\nTransaction Summary:")
    print(f"Total Transactions: {len(df)}")
    print(f"Date Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"Total Spent: ${abs(amounts.sum()):.2f}")
    print("\nTransactions by Category:")
    print(df['category'].value_counts())
