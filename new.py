import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =====================================
# CONFIG
# =====================================

API_KEY = "cb4d5d3818a1078b46cd3bfad2296cab"

st.set_page_config(
    page_title="Smart Weather Forecast System",
    page_icon="🌦️",
    layout="wide"
)

# =====================================
# STYLING
# =====================================

st.markdown("""
<style>
.weather-card{
    background:#1e293b;
    padding:20px;
    border-radius:15px;
    color:white;
}
.big-temp{
    font-size:52px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# API FUNCTIONS
# =====================================

def get_weather(city):
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        response = requests.get(url, timeout=15)

        if response.status_code == 401:
            st.error("Invalid API Key")
            return None

        if response.status_code == 404:
            st.error("City not found")
            return None

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(
            "Network blocked. If you are using an online Pyodide "
            "environment, OpenWeather requests may not be allowed."
        )
        return None

    except requests.exceptions.Timeout:
        st.error("Request timed out.")
        return None

    except Exception as e:
        st.error(str(e))
        return None


def get_forecast(city):
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/forecast"
            f"?q={city}&appid={API_KEY}&units=metric"
        )

        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


def get_aqi(lat, lon):
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/air_pollution"
            f"?lat={lat}&lon={lon}&appid={API_KEY}"
        )

        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


# =====================================
# APP UI
# =====================================

st.title("🌦 Smart Weather Forecast System")
st.write("Current Weather • AQI • 5-Day Forecast")

if "history" not in st.session_state:
    st.session_state.history = []

city = st.text_input("Enter City Name", "Rewa")

if st.button("Search Weather"):

    weather = get_weather(city)

    if weather is None:
        st.stop()

    st.session_state.history.append(city)

    temp = weather["main"]["temp"]
    feels_like = weather["main"]["feels_like"]
    humidity = weather["main"]["humidity"]
    pressure = weather["main"]["pressure"]

    wind_speed = weather["wind"]["speed"]

    description = weather["weather"][0]["description"]
    icon = weather["weather"][0]["icon"]

    country = weather["sys"]["country"]

    lat = weather["coord"]["lat"]
    lon = weather["coord"]["lon"]

    sunrise = datetime.fromtimestamp(
        weather["sys"]["sunrise"]
    ).strftime("%H:%M:%S")

    sunset = datetime.fromtimestamp(
        weather["sys"]["sunset"]
    ).strftime("%H:%M:%S")

    icon_url = (
        f"https://openweathermap.org/img/wn/{icon}@4x.png"
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(icon_url, width=140)

    with col2:
        st.markdown(
            f"""
            <div class='weather-card'>
                <div class='big-temp'>{temp} °C</div>
                <h2>{city.title()}, {country}</h2>
                <h4>{description.title()}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Temperature", f"{temp} °C")
    c2.metric("Feels Like", f"{feels_like} °C")
    c3.metric("Humidity", f"{humidity}%")
    c4.metric("Wind Speed", f"{wind_speed} m/s")
    c5.metric("Pressure", f"{pressure} hPa")

    st.divider()

    s1, s2 = st.columns(2)

    s1.success(f"🌅 Sunrise : {sunrise}")
    s2.error(f"🌇 Sunset : {sunset}")

    st.divider()

    st.subheader("🌍 Air Quality Index")

    aqi_data = get_aqi(lat, lon)

    if aqi_data:
        aqi = aqi_data["list"][0]["main"]["aqi"]

        aqi_map = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }

        st.metric(
            "AQI",
            f"{aqi} - {aqi_map.get(aqi, 'Unknown')}"
        )

    st.divider()

    st.subheader("📅 5-Day Forecast")

    forecast = get_forecast(city)

    if forecast:

        rows = []

        for item in forecast["list"]:
            rows.append({
                "Date & Time": item["dt_txt"],
                "Temperature": item["main"]["temp"],
                "Humidity": item["main"]["humidity"],
                "Weather": item["weather"][0]["main"]
            })

        df = pd.DataFrame(rows)

        st.dataframe(df, use_container_width=True)

        st.line_chart(
            df.set_index("Date & Time")["Temperature"]
        )

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("Search History")

for item in reversed(st.session_state.history):
    st.sidebar.write("•", item)