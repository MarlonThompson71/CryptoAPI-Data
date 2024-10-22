from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import os
from time import sleep
import seaborn as sns
import matplotlib.pyplot as plt

# Set up API details
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start': '1',
    'limit': '15',
    'convert': 'USD'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '3ad520a3-8613-49b5-8eb0-284596de9723',
}

session = Session()
session.headers.update(headers)

# Initialize an empty DataFrame
df = pd.DataFrame()

def api_runner():
    global df  # Use the global DataFrame

    try:
        response = session.get(url, params=parameters)
        
        # Check if the response status code is OK (200)
        if response.status_code == 200:
            data = json.loads(response.text)

            if 'data' in data:
                df2 = pd.json_normalize(data['data'])
                df2['Timestamp'] = pd.to_datetime('now')

                # Concatenate the new data with the existing DataFrame
                df = pd.concat([df, df2], ignore_index=True)

                # Write DataFrame to CSV
                file_path = r'/Users/marlonthompson/Desktop/Crypto/Crypto1.csv'
                if not os.path.isfile(file_path):
                    df.to_csv(file_path, index=False, header=True)
                else:
                    df.to_csv(file_path, mode='a', index=False, header=False)

                # Group by 'name' and calculate mean of percent changes
                percent_change_cols = [
                    'quote.USD.percent_change_1h', 'quote.USD.percent_change_24h', 
                    'quote.USD.percent_change_7d', 'quote.USD.percent_change_30d', 
                    'quote.USD.percent_change_60d', 'quote.USD.percent_change_90d'
                ]

                # Check for missing columns
                missing_cols = [col for col in percent_change_cols if col not in df.columns]
                if missing_cols:
                    print(f"Missing columns: {missing_cols}")
                    return

                df3 = df.groupby('name', sort=False)[percent_change_cols].mean()

                if not df3.empty:
                    df4 = df3.stack().reset_index()
                    df4.columns = ['name', 'percent_change', 'values']

                    # Replace percent change column names
                    df4['percent_change'] = df4['percent_change'].replace({
                        'quote.USD.percent_change_1h': '1hr',
                        'quote.USD.percent_change_24h': '24hr',
                        'quote.USD.percent_change_7d': '7d',
                        'quote.USD.percent_change_30d': '30d',
                        'quote.USD.percent_change_60d': '60d',
                        'quote.USD.percent_change_90d': '90d'
                    })

                    # Save df4 to CSV
                    df4_file_path = r'/Users/marlonthompson/Desktop/Crypto/df7.csv'
                    df4.to_csv(df4_file_path, index=False)
                    print(f"df7 saved to {df4_file_path}")

                    # Create a point plot
                    sns.catplot(x='percent_change', y='values', hue='name', data=df4, kind='point')
                    plt.show()

                else:
                    print("No data to plot.")
            else:
                print("Key 'data' not found in the response.")
                print("Full response:", data)  # Print the entire response for debugging
        else:
            print(f"Error: {response.status_code} - {response.reason}")

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

# Main loop to call the API multiple times
max_iterations = 333  # Define the maximum number of iterations
for i in range(max_iterations):
    api_runner()  # Call the API runner
    print(f'API Runner completed. Iteration: {i + 1}')
    print(f'DataFrame size: {df.shape[0]}')  # Print size of the DataFrame
    sleep(60)  # Wait for 60 seconds before the next request

# Print the final DataFrame
print("Final DataFrame:")
print(df)
