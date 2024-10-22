from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import os
from time import sleep

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
        data = json.loads(response.text)

        # Normalize the data and add a timestamp
        df2 = pd.json_normalize(data['data'])
        df2['Timestamp'] = pd.to_datetime('now')  # Ensure correct column name with uppercase 'T'

        # Concatenate the new data with the existing DataFrame
        df = pd.concat([df, df2], ignore_index=True)

        # Write DataFrame to CSV
        file_path = r'/Users/marlonthompson/Desktop/Crypto/Crypto.csv'
        if not os.path.isfile(file_path):
            df.to_csv(file_path, index=False, header=True)
        else:
            df.to_csv(file_path, mode='a', index=False, header=False)

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
# Optionally print the final DataFrame

