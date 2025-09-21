import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim

API_KEY = "GET YOUR OWN KEY!"  

st.set_page_config(page_title="Satellite + ISS Tracker", layout="wide")
st.title("🛰️ Satellite + ISS Tracker")

city_name = st.text_input("Enter your city name:", "Kathmandu")

category = st.selectbox(
    "Select Satellite Category:",
    ["All", "Weather", "Communication", "Amateur"]
)
category_dict = {"All": 0, "Weather": 1, "Communication": 2, "Amateur": 3}
category_value = category_dict[category]

radius = st.slider("Search Radius (in km):", 100, 1000, 500)

if st.button("Track Satellites"):
    try:
        geolocator = Nominatim(user_agent="satellite_tracker")
        location = geolocator.geocode(city_name)

        if location is None:
            st.error("City not found.")
        else:
            lat, lon = location.latitude, location.longitude
            st.success(f'Coordinates: {lat:.4f}, {lon:.4f}')

           
            url = f"https://api.n2yo.com/rest/v1/satellite/above/{lat}/{lon}/0/{radius}/{category_value}/&apiKey={API_KEY}"
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                response = r.json()
            except Exception as e:
                st.error(f"N2YO API request failed: {e}")
                response = {}

            satellites_df = pd.DataFrame()
            if "above" in response and len(response["above"]) > 0:
                satellites_df = pd.DataFrame(response['above'])
                satellites_df['Type'] = 'Other Satellites'
                # Replace negative or missing altitudes
                satellites_df['satalt'] = satellites_df['satalt'].apply(lambda x: x if x > 0 else 10)
                st.subheader(f"Satellites above {city_name}")
                st.dataframe(satellites_df[['satname','satid','intDesignator','launchDate','satlat','satlng','satalt']])
            else:
                st.warning("No satellites found in this area.")

            #ISS DATA!
            iss_url = f"https://api.n2yo.com/rest/v1/satellite/positions/25544/{lat}/{lon}/0/1/&apiKey={API_KEY}"
            try:
                r2 = requests.get(iss_url, timeout=10)
                r2.raise_for_status()
                iss_data = r2.json()
                iss_lat = iss_data['positions'][0]['satlatitude']
                iss_lon = iss_data['positions'][0]['satlongitude']
                # Ensure positive altitude for plotting
                iss_alt = max(iss_data['positions'][0].get('satalt', 0), 10)
            except Exception as e:
                st.warning(f"ISS API failed: {e}")
                iss_lat, iss_lon, iss_alt = 0, 0, 10

            
            if not satellites_df.empty:
                iss_df = pd.DataFrame([{
                    'satname':'International Space Station',
                    'satlat': iss_lat,
                    'satlng': iss_lon,
                    'satalt': iss_alt,
                    'Type':'ISS'
                }])
                plot_df = pd.concat([satellites_df[['satname','satlat','satlng','satalt','Type']], iss_df], ignore_index=True)
            else:
                plot_df = pd.DataFrame([{
                    'satname':'International Space Station',
                    'satlat': iss_lat,
                    'satlng': iss_lon,
                    'satalt': iss_alt,
                    'Type':'ISS'
                }])

           
            fig = px.scatter_geo(
                plot_df,
                lat='satlat',
                lon='satlng',
                color='Type',
                hover_name='satname',
                size='satalt',  # all values guaranteed >= 10
                projection='natural earth',
                title=f'Satellites above {city_name} + ISS Position'
            )
            fig.update_geos(showland=True, landcolor="LightGreen")
            fig.update_layout(height=600, margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
