import streamlit as st
import requests
import pandas as pd
import datetime

# OpenWeatherMap API key
API_KEY = "c07e1beaff20b31ea93ead728d56170c"

# Function to fetch weather data
def get_weather(city):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Title and sidebar
st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("Interactive Weather Dashboard")
st.sidebar.header("User Input")

# Initialize weather history
if "weather_history" not in st.session_state:
    st.session_state.weather_history = pd.DataFrame(columns=["City", "Country", "Temp (°C)", "Humidity (%)", "Wind (m/s)", "Condition"])

# Sidebar input widgets
city = st.sidebar.text_input("Enter a city", value="Miami")

selected_date = st.sidebar.date_input("Select date", datetime.date.today())
selected_time = st.sidebar.time_input("Select time", datetime.datetime.now().time())

if st.sidebar.button("Get Weather"):
    data = get_weather(city)

    if data.get("cod") != 200:
        st.error(f"City not found: {city}")
    else:
        st.success(f"Weather for: {data['name']}, {data['sys']['country']}")

        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        condition = data['weather'][0]['description'].capitalize()

        # Add to session state
        new_row = {
            "City": data['name'],
            "Country": data['sys']['country'],
            "Temp (°C)": temp,
            "Humidity (%)": humidity,
            "Wind (m/s)": wind,
            "Condition": condition
        }
        st.session_state.weather_history = pd.concat(
            [st.session_state.weather_history, pd.DataFrame([new_row])],
            ignore_index=True
        )

        # Current weather output
        st.subheader("Current Weather Details")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature (°C)", temp)
            st.metric("Humidity (%)", humidity)
        with col2:
            st.metric("Wind Speed (m/s)", wind)
            st.write(f"**Condition**: {condition}")
            icon_url = f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
            st.image(icon_url)

        # Map display
        st.subheader("Location on Map")
        coords = pd.DataFrame([[data['coord']['lat'], data['coord']['lon']]], columns=['lat', 'lon'])
        st.map(coords)

        # Bar chart
        st.subheader("Weather Metrics Comparison")
        chart_df = pd.DataFrame({
            'Metric': ['Temperature (°C)', 'Humidity (%)', 'Wind Speed (m/s)'],
            'Value': [temp, humidity, wind]
        })
        chart_df.set_index("Metric", inplace=True)
        st.bar_chart(chart_df)

        # Info
        st.info("Data from OpenWeatherMap.org")

# Checkbox to display weather history
if st.checkbox("Show Weather Search History"):
    if not st.session_state.weather_history.empty:
        st.subheader("Weather Search History")
        st.dataframe(st.session_state.weather_history, use_container_width=True)
    else:
        st.warning("No search history yet.")

# Footer
st.caption(f"Selected date: {selected_date}, Time: {selected_time}")
