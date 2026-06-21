import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from streamlit_lottie import stream_lottie
import json

# Page Configuration
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .weather-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .city-name {
        font-size: 36px;
        font-weight: bold;
    }
    .temp-display {
        font-size: 72px;
        font-weight: bold;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== API FUNCTIONS ====================

@st.cache_data(ttl=3600)
def search_cities(query):
    """Search for cities using Open-Meteo Geocoding API"""
    try:
        if len(query) < 2:
            return []
        
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": query,
            "count": 10,
            "language": "en",
            "format": "json"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            return data["results"]
        return []
    except Exception as e:
        st.error(f"Error searching cities: {e}")
        return []


@st.cache_data(ttl=600)
def fetch_weather_data(latitude, longitude):
    """Fetch weather data from Open-Meteo API"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "timezone": "auto",
            "forecast_days": 14
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None


@st.cache_data
def get_weather_emoji(code):
    """Get weather emoji based on WMO weather code"""
    weather_codes = {
        0: "☀️",      # Clear sky
        1: "🌤️",      # Mainly clear
        2: "⛅",      # Partly cloudy
        3: "☁️",      # Overcast
        45: "🌫️",     # Foggy
        48: "🌫️",     # Foggy (depositing)
        51: "🌧️",     # Light drizzle
        53: "🌧️",     # Moderate drizzle
        55: "🌧️",     # Dense drizzle
        61: "🌧️",     # Slight rain
        63: "🌧️",     # Moderate rain
        65: "⛈️",     # Heavy rain
        71: "❄️",     # Slight snow
        73: "❄️",     # Moderate snow
        75: "❄️",     # Heavy snow
        77: "❄️",     # Snow grains
        80: "🌧️",     # Slight rain showers
        81: "🌧️",     # Moderate rain showers
        82: "⛈️",     # Violent rain showers
        85: "❄️",     # Slight snow showers
        86: "❄️",     # Heavy snow showers
        95: "⛈️",     # Thunderstorm
        96: "⛈️",     # Thunderstorm with hail
        99: "⛈️"      # Thunderstorm with hail
    }
    return weather_codes.get(code, "🌤️")


@st.cache_data
def get_weather_description(code):
    """Get weather description based on WMO weather code"""
    descriptions = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy (Depositing)",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Slight Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Slight Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Slight Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Thunderstorm with Hail"
    }
    return descriptions.get(code, "Unknown")


# ==================== DATA PROCESSING FUNCTIONS ====================

def process_current_weather(weather_data, city_name, country):
    """Process current weather data"""
    current = weather_data["current"]
    return {
        "city": city_name,
        "country": country,
        "temperature": round(current["temperature_2m"]),
        "feels_like": round(current["apparent_temperature"]),
        "humidity": current["relative_humidity_2m"],
        "wind_speed": round(current["wind_speed_10m"], 1),
        "wind_direction": current["wind_direction_10m"],
        "weather_code": current["weather_code"],
        "weather_description": get_weather_description(current["weather_code"]),
        "weather_emoji": get_weather_emoji(current["weather_code"])
    }


def process_forecast_data(weather_data):
    """Process daily forecast data"""
    daily = weather_data["daily"]
    forecast_list = []
    
    for i in range(len(daily["time"])):
        forecast_list.append({
            "date": daily["time"][i],
            "max_temp": round(daily["temperature_2m_max"][i]),
            "min_temp": round(daily["temperature_2m_min"][i]),
            "weather_code": daily["weather_code"][i],
            "weather_description": get_weather_description(daily["weather_code"][i]),
            "weather_emoji": get_weather_emoji(daily["weather_code"][i]),
            "precipitation": round(daily["precipitation_sum"][i], 1),
            "wind_speed": round(daily["windspeed_10m_max"][i], 1)
        })
    
    return pd.DataFrame(forecast_list)


def get_day_name(date_str):
    """Convert date string to day name"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%A")


def get_weather_color(code):
    """Get gradient color based on weather condition"""
    if code in [0, 1]:  # Clear/Mainly clear
        return "linear-gradient(135deg, #FFD89B 0%, #19547B 100%)"
    elif code in [2, 3]:  # Cloudy
        return "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
    elif code in [45, 48]:  # Fog
        return "linear-gradient(135deg, #9099a2 0%, #7b8794 100%)"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:  # Rain
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    elif code in [71, 73, 75, 77, 85, 86]:  # Snow
        return "linear-gradient(135deg, #a8dadc 0%, #457b9d 100%)"
    elif code in [95, 96, 99]:  # Thunderstorm
        return "linear-gradient(135deg, #434343 0%, #000000 100%)"
    else:
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"


# ==================== UI COMPONENT FUNCTIONS ====================

def display_current_weather(current_weather):
    """Display current weather information"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; color: white;">
            <h2 style="margin: 0; font-size: 24px;">{current_weather['city']}, {current_weather['country']}</h2>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.8); font-size: 14px;">
                {datetime.now().strftime("%A, %B %d, %Y")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; color: white; text-align: right;">
            <h1 style="margin: 0; font-size: 56px;">{current_weather['temperature']}°</h1>
            <p style="margin: 5px 0; font-size: 20px;">{current_weather['weather_emoji']} {current_weather['weather_description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Weather metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Feels Like", f"{current_weather['feels_like']}°C", 
                 delta=f"{current_weather['feels_like'] - current_weather['temperature']}°")
    
    with metric_col2:
        st.metric("Humidity", f"{current_weather['humidity']}%")
    
    with metric_col3:
        st.metric("Wind Speed", f"{current_weather['wind_speed']} km/h")
    
    with metric_col4:
        st.metric("Wind Direction", f"{current_weather['wind_direction']}°")


def display_forecast_cards(forecast_df):
    """Display forecast as interactive cards"""
    st.subheader("🗓️ Extended Forecast (14 Days)")
    
    # Create columns for forecast cards
    cols = st.columns(7)
    
    for idx, (i, row) in enumerate(forecast_df.head(7).iterrows()):
        with cols[idx]:
            day_name = get_day_name(row['date'])
            date_obj = datetime.strptime(row['date'], "%Y-%m-%d")
            
            st.markdown(f"""
            <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-weight: bold; color: #333;">{day_name[:3]}</p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">{date_obj.strftime('%m/%d')}</p>
                <p style="margin: 10px 0; font-size: 24px;">{row['weather_emoji']}</p>
                <p style="margin: 5px 0; font-weight: bold; color: #667eea;">{row['max_temp']}°</p>
                <p style="margin: 5px 0; color: #999;">{row['min_temp']}°</p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">{row['weather_description']}</p>
            </div>
            """, unsafe_allow_html=True)


def display_detailed_forecast(forecast_df):
    """Display detailed forecast table"""
    st.subheader("📊 Detailed Forecast Table")
    
    display_df = forecast_df.copy()
    display_df['Day'] = display_df['date'].apply(get_day_name)
    display_df['Date'] = pd.to_datetime(display_df['date']).dt.strftime('%m/%d')
    display_df['Weather'] = display_df['weather_emoji'] + ' ' + display_df['weather_description']
    display_df['Temp Range'] = display_df['max_temp'].astype(str) + '° / ' + display_df['min_temp'].astype(str) + '°'
    display_df['Precipitation'] = display_df['precipitation'].astype(str) + ' mm'
    display_df['Wind'] = display_df['wind_speed'].astype(str) + ' km/h'
    
    display_table = display_df[['Day', 'Date', 'Weather', 'Temp Range', 'Precipitation', 'Wind']]
    st.dataframe(display_table, use_container_width=True, hide_index=True)


def plot_temperature_chart(forecast_df):
    """Create temperature trend chart"""
    st.subheader("📈 Temperature Trend")
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['max_temp'],
        mode='lines+markers',
        name='High',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['min_temp'],
        mode='lines+markers',
        name='Low',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Temperature Forecast',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_precipitation_chart(forecast_df):
    """Create precipitation chart"""
    st.subheader("💧 Precipitation Forecast")
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    fig.add_trace(go.Bar(
        x=forecast_df['date_formatted'],
        y=forecast_df['precipitation'],
        marker=dict(color='#667eea'),
        name='Precipitation'
    ))
    
    fig.update_layout(
        title='Precipitation Forecast',
        xaxis_title='Date',
        yaxis_title='Precipitation (mm)',
        hovermode='x',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_wind_chart(forecast_df):
    """Create wind speed chart"""
    st.subheader("💨 Wind Speed Forecast")
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['wind_speed'],
        mode='lines+markers',
        fill='tozeroy',
        name='Wind Speed',
        line=dict(color='#FF9F43', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Wind Speed Forecast',
        xaxis_title='Date',
        yaxis_title='Wind Speed (km/h)',
        hovermode='x',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ==================== MAIN APP ====================

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 48px; margin: 0;">🌤️ Weather Dashboard</h1>
        <p style="color: #666; font-size: 16px; margin: 10px 0;">Real-time Weather Forecast & Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for search
    with st.sidebar:
        st.title("🔍 Search Weather")
        
        search_query = st.text_input(
            "Enter city name:",
            placeholder="e.g., Delhi, London, New York...",
            key="search_query"
        )
        
        cities = []
        selected_city = None
        
        if search_query:
            cities = search_cities(search_query)
            
            if cities:
                city_options = [f"{city['name']}, {city.get('admin1', '')}, {city['country']}" 
                               for city in cities]
                selected_index = st.selectbox(
                    "Select a city:",
                    range(len(city_options)),
                    format_func=lambda x: city_options[x],
                    key="city_selector"
                )
                selected_city = cities[selected_index]
            else:
                st.warning("No cities found. Try a different search.")
        
        st.divider()
        
        # Favorite cities
        st.subheader("⭐ Quick Access")
        favorite_cities = {
            "Delhi": (28.7041, 77.1025),
            "Mumbai": (19.0760, 72.8777),
            "London": (51.5074, -0.1278),
            "New York": (40.7128, -74.0060),
            "Tokyo": (35.6762, 139.6503),
            "Dubai": (25.2048, 55.2708),
            "Sydney": (-33.8688, 151.2093),
            "Paris": (48.8566, 2.3522)
        }
        
        for city_name, (lat, lon) in favorite_cities.items():
            if st.button(f"📍 {city_name}", use_container_width=True, key=f"fav_{city_name}"):
                selected_city = {
                    "name": city_name,
                    "latitude": lat,
                    "longitude": lon,
                    "country": "India" if city_name in ["Delhi", "Mumbai"] else "Other"
                }
    
    # Default to Delhi if no city is selected
    if selected_city is None:
        selected_city = {
            "name": "Delhi",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "country": "India"
        }
    
    # Fetch and display weather data
    weather_data = fetch_weather_data(selected_city["latitude"], selected_city["longitude"])
    
    if weather_data:
        # Process current weather
        current_weather = process_current_weather(
            weather_data,
            selected_city["name"],
            selected_city["country"]
        )
        
        # Process forecast
        forecast_df = process_forecast_data(weather_data)
        
        # Display current weather
        display_current_weather(current_weather)
        
        st.divider()
        
        # Display forecast cards
        display_forecast_cards(forecast_df)
        
        st.divider()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Detailed Forecast", "🌡️ Temperature", "💧 Precipitation", "💨 Wind"])
        
        with tab1:
            display_detailed_forecast(forecast_df)
        
        with tab2:
            plot_temperature_chart(forecast_df)
        
        with tab3:
            plot_precipitation_chart(forecast_df)
        
        with tab4:
            plot_wind_chart(forecast_df)
        
        # Additional information
        st.divider()
        st.subheader("ℹ️ Additional Information")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.info(f"""
            **Current Conditions**
            - Temperature: {current_weather['temperature']}°C
            - Feels Like: {current_weather['feels_like']}°C
            - Humidity: {current_weather['humidity']}%
            """)
        
        with info_col2:
            st.info(f"""
            **Wind Information**
            - Speed: {current_weather['wind_speed']} km/h
            - Direction: {current_weather['wind_direction']}°
            - Max Wind (Today): {forecast_df.iloc[0]['wind_speed']} km/h
            """)
        
        with info_col3:
            st.info(f"""
            **Today's Forecast**
            - High: {forecast_df.iloc[0]['max_temp']}°C
            - Low: {forecast_df.iloc[0]['min_temp']}°C
            - Precipitation: {forecast_df.iloc[0]['precipitation']} mm
            """)
        
        # Footer
        st.markdown("""
        ---
        <div style="text-align: center; color: #999; font-size: 12px; margin-top: 30px;">
            <p>Data provided by Open-Meteo API | Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>Made with ❤️ using Streamlit</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("Unable to fetch weather data. Please try again later.")


if __name__ == "__main__":
    main()
