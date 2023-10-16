import requests

# Send a POST request to the /user/1 - 500 endpoint.
for i in range(1, 500):
    response = requests.post(f'http://127.0.0.1:8000/user/{i}')

    # Print the response.
    print(response.json())
# Compare this snippet from serverPROJECT/asyncio.py:
