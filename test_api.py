import requests

API_KEY = "GET YOUR OWN KEY!"
lat = 27.7172   # Example: Kathmandu
lon = 85.3240
radius = 500
category_value = 0  # All satellites

url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/25544/41.702/-76.014/0/2/300/&apiKey={API_KEY}"

r = requests.get(url)
print("Status code:", r.status_code)
print("Response text:", r.text)
