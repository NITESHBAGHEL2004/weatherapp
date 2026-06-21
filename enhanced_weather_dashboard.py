import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import json

# Page Configuration
st.set_page_config(
    page_title="Premium Weather Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ENHANCED CUSTOM CSS ====================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .main {
        padding: 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 10px;
    }
    
    .hero-subtitle {
        font-size: 16px;
        color: rgba(255,255,255,0.9);
        font-weight: 300;
    }
    
    /* Current Weather Display */
    .current-weather-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .weather-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
    }
    
    .location-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 35px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .temp-display {
        font-size: 84px;
        font-weight: 800;
        line-height: 1;
        margin: 20px 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-label {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #333;
        margin: 10px 0;
    }
    
    .metric-unit {
        font-size: 14px;
        color: #667eea;
        font-weight: 600;
    }
    
    /* AQI Card */
    .aqi-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin: 20px 0;
    }
    
    .aqi-indicator {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        font-weight: 800;
        color: white;
        margin: 0 auto;
    }
    
    .aqi-good {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .aqi-fair {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    }
    
    .aqi-poor {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .aqi-veryPoor {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    }
    
    .aqi-hazardous {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    
    /* Humidity Indicator */
    .humidity-bar {
        width: 100%;
        height: 30px;
        background: #e0e0e0;
        border-radius: 15px;
        overflow: hidden;
        margin: 15px 0;
    }
    
    .humidity-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 12px;
    }
    
    /* Forecast Cards */
    .forecast-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-top: 3px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .forecast-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transform: translateY(-8px);
    }
    
    .forecast-day {
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }
    
    .forecast-emoji {
        font-size: 32px;
        margin: 10px 0;
    }
    
    .forecast-temp {
        font-size: 18px;
        font-weight: 700;
        color: #667eea;
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .info-title {
        font-weight: 700;
        color: #333;
        margin-bottom: 10px;
        font-size: 14px;
    }
    
    .info-content {
        color: #666;
        font-size: 13px;
        line-height: 1.6;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 15px 25px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Divider */
    hr {
        background: linear-gradient(90deg, transparent, #ddd, transparent);
        border: none;
        height: 1px;
        margin: 30px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #999;
        font-size: 12px;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #eee;
    }
    
    /* Section Title */
    .section-title {
        font-size: 24px;
        font-weight: 800;
        color: #333;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
        display: inline-block;
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
    """Fetch comprehensive weather data from Open-Meteo API"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,is_day,uv_index,visibility",
            "hourly": "temperature_2m,relative_humidity_2m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,uv_index_max",
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


@st.cache_data(ttl=600)
def fetch_air_quality_data(latitude, longitude):
    """Fetch air quality data from Open-Meteo Air Quality API"""
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "pm2_5,pm10,no2,o3,so2,uv_index,us_aqi",
            "forecast_days": 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        st.warning(f"Air quality data temporarily unavailable")
        return None


@st.cache_data
def get_weather_emoji(code):
    """Get weather emoji based on WMO weather code"""
    weather_codes = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️",
        51: "🌧️", 53: "🌧️", 55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "⛈️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️", 80: "🌧️", 81: "🌧️",
        82: "⛈️", 85: "❄️", 86: "❄️", 95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return weather_codes.get(code, "🌤️")


@st.cache_data
def get_weather_description(code):
    """Get weather description based on WMO weather code"""
    descriptions = {
        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
        45: "Foggy", 48: "Foggy", 51: "Light Drizzle", 53: "Moderate Drizzle",
        55: "Dense Drizzle", 61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
        71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow", 77: "Snow Grains",
        80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
        85: "Slight Snow Showers", 86: "Heavy Snow Showers", 95: "Thunderstorm",
        96: "Thunderstorm with Hail", 99: "Thunderstorm with Hail"
    }
    return descriptions.get(code, "Unknown")


def get_aqi_category(aqi):
    """Get AQI category and color"""
    if aqi <= 50:
        return "Good", "#11998e", "#38ef7d"
    elif aqi <= 100:
        return "Fair", "#f6d365", "#fda085"
    elif aqi <= 150:
        return "Poor", "#fa709a", "#fee140"
    elif aqi <= 200:
        return "Very Poor", "#a8edea", "#fed6e3"
    else:
        return "Hazardous", "#eb3349", "#f45c43"


def get_aqi_emoji(aqi):
    """Get AQI emoji based on value"""
    if aqi <= 50:
        return "😊"
    elif aqi <= 100:
        return "😐"
    elif aqi <= 150:
        return "😷"
    elif aqi <= 200:
        return "😢"
    else:
        return "😵"


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
        "weather_emoji": get_weather_emoji(current["weather_code"]),
        "uv_index": round(current.get("uv_index", 0), 1),
        "visibility": round(current.get("visibility", 0) / 1000, 1)
    }


def process_air_quality(aq_data):
    """Process air quality data"""
    if not aq_data or "current" not in aq_data:
        return None
    
    current = aq_data["current"]
    return {
        "pm2_5": round(current.get("pm2_5", 0), 1),
        "pm10": round(current.get("pm10", 0), 1),
        "no2": round(current.get("no2", 0), 1),
        "o3": round(current.get("o3", 0), 1),
        "so2": round(current.get("so2", 0), 1),
        "us_aqi": round(current.get("us_aqi", 0))
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
            "wind_speed": round(daily["windspeed_10m_max"][i], 1),
            "uv_index": round(daily["uv_index_max"][i], 1)
        })
    
    return pd.DataFrame(forecast_list)


def get_day_name(date_str):
    """Convert date string to day name"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%A")


# ==================== DISPLAY FUNCTIONS ====================

def display_hero_header():
    """Display premium hero header"""
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🌦️ Premium Weather Dashboard</div>
        <div class="hero-subtitle">Real-time Forecasts • Air Quality • Advanced Metrics</div>
    </div>
    """, unsafe_allow_html=True)


def display_current_weather_section(current_weather):
    """Display current weather with premium design"""
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="location-card">
            <h2 style="margin: 0; font-size: 28px; margin-bottom: 5px;">{current_weather['city']}</h2>
            <p style="margin: 0; opacity: 0.9; font-size: 14px;">{current_weather['country']} • {datetime.now().strftime("%A, %B %d, %Y")}</p>
            <div class="temp-display">{current_weather['temperature']}°</div>
            <p style="margin: 0; font-size: 18px; opacity: 0.95;">{current_weather['weather_emoji']} {current_weather['weather_description']}</p>
            <p style="margin-top: 8px; font-size: 14px; opacity: 0.85;">Feels like {current_weather['feels_like']}°C</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="weather-card">
            <div class="metric-label">🌡️ Temperature</div>
            <div class="metric-value">{current_weather['temperature']}°C</div>
            <div class="metric-unit">Actual Temperature</div>
            
            <hr style="margin: 15px 0; border: none; height: 1px; background: #eee;">
            
            <div class="metric-label">🤔 Feels Like</div>
            <div class="metric-value">{current_weather['feels_like']}°C</div>
            <div class="metric-unit">Apparent Temperature</div>
        </div>
        """, unsafe_allow_html=True)


def display_humidity_card(humidity):
    """Display humidity with visual indicator"""
    st.markdown(f"""
    <div class="weather-card">
        <div class="metric-label">💧 Humidity</div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div class="metric-value">{humidity}%</div>
        </div>
        <div class="humidity-bar">
            <div class="humidity-fill" style="width: {humidity}%;">
                {humidity}%
            </div>
        </div>
        <div style="font-size: 12px; color: #999; margin-top: 10px; text-align: center;">
            Relative Humidity
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_wind_card(wind_speed, wind_direction):
    """Display wind information"""
    wind_descriptions = {
        range(0, 2): "Calm",
        range(2, 6): "Light",
        range(6, 12): "Light Breeze",
        range(12, 20): "Moderate Breeze",
        range(20, 29): "Fresh Breeze",
        range(29, 39): "Strong Wind",
        range(39, 50): "Gale",
        range(50, 1000): "Strong Gale"
    }
    
    description = "Calm"
    for wind_range, desc in wind_descriptions.items():
        if wind_speed in wind_range:
            description = desc
            break
    
    st.markdown(f"""
    <div class="weather-card">
        <div class="metric-label">💨 Wind</div>
        <div class="metric-value">{wind_speed}</div>
        <div class="metric-unit">km/h • {description}</div>
        <div style="margin-top: 15px; padding: 12px; background: #f5f5f5; border-radius: 8px;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">Direction</div>
            <div style="font-size: 18px; font-weight: 700; color: #333;">{wind_direction}°</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_uv_index_card(uv_index):
    """Display UV Index"""
    if uv_index <= 2:
        uv_color = "#11998e"
        uv_text = "Low"
    elif uv_index <= 5:
        uv_color = "#f6d365"
        uv_text = "Moderate"
    elif uv_index <= 7:
        uv_color = "#fa709a"
        uv_text = "High"
    elif uv_index <= 10:
        uv_color = "#ff6b6b"
        uv_text = "Very High"
    else:
        uv_color = "#eb3349"
        uv_text = "Extreme"
    
    st.markdown(f"""
    <div class="weather-card">
        <div class="metric-label">☀️ UV Index</div>
        <div class="metric-value" style="color: {uv_color};">{uv_index}</div>
        <div class="metric-unit">{uv_text} Exposure</div>
        <div style="margin-top: 15px; padding: 12px; background: {uv_color}20; border-radius: 8px;">
            <div style="font-size: 11px; color: #999;">
                {'No protection required' if uv_index <= 2 else 'Wear sunscreen' if uv_index <= 5 else 'Extra protection needed'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_visibility_card(visibility):
    """Display visibility"""
    if visibility >= 10:
        vis_text = "Excellent"
        vis_color = "#11998e"
    elif visibility >= 5:
        vis_text = "Good"
        vis_color = "#38ef7d"
    elif visibility >= 1:
        vis_text = "Moderate"
        vis_color = "#f6d365"
    else:
        vis_text = "Poor"
        vis_color = "#fa709a"
    
    st.markdown(f"""
    <div class="weather-card">
        <div class="metric-label">👁️ Visibility</div>
        <div class="metric-value" style="color: {vis_color};">{visibility}</div>
        <div class="metric-unit">km • {vis_text}</div>
    </div>
    """, unsafe_allow_html=True)


def display_aqi_section(air_quality):
    """Display Air Quality Index"""
    st.markdown('<div class="section-title">🌍 Air Quality</div>', unsafe_allow_html=True)
    
    if air_quality:
        aqi = air_quality["us_aqi"]
        category, color1, color2 = get_aqi_category(aqi)
        emoji = get_aqi_emoji(aqi)
        
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        
        with col1:
            aqi_class = f"aqi-{category.lower().replace(' ', '')}"
            st.markdown(f"""
            <div class="aqi-card">
                <div style="text-align: center;">
                    <h3 style="color: #333; margin-bottom: 15px;">Air Quality Index</h3>
                    <div class="aqi-indicator aqi-{category.lower().replace(' ', '')}">
                        {aqi}
                    </div>
                    <div style="margin-top: 20px;">
                        <div style="font-size: 28px; margin-bottom: 10px;">{emoji}</div>
                        <div style="font-size: 20px; font-weight: 700; color: #333;">{category}</div>
                        <div style="font-size: 12px; color: #999; margin-top: 5px;">Air Quality Level</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="aqi-card">
                <div style="margin-bottom: 15px;">
                    <div class="metric-label">PM2.5</div>
                    <div class="metric-value" style="color: #667eea;">{air_quality['pm2_5']}</div>
                    <div class="metric-unit">μg/m³</div>
                </div>
                <hr style="border: none; height: 1px; background: #eee; margin: 15px 0;">
                <div>
                    <div class="metric-label">PM10</div>
                    <div class="metric-value" style="color: #667eea;">{air_quality['pm10']}</div>
                    <div class="metric-unit">μg/m³</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="aqi-card">
                <div style="margin-bottom: 15px;">
                    <div class="metric-label">NO₂</div>
                    <div class="metric-value" style="color: #667eea;">{air_quality['no2']}</div>
                    <div class="metric-unit">ppb</div>
                </div>
                <hr style="border: none; height: 1px; background: #eee; margin: 15px 0;">
                <div>
                    <div class="metric-label">O₃</div>
                    <div class="metric-value" style="color: #667eea;">{air_quality['o3']}</div>
                    <div class="metric-unit">ppb</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔄 Air quality data will load shortly...")


def display_metrics_grid(current_weather):
    """Display comprehensive metrics grid"""
    st.markdown('<div class="section-title">📊 Current Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_humidity_card(current_weather['humidity'])
    
    with col2:
        display_wind_card(current_weather['wind_speed'], current_weather['wind_direction'])
    
    with col3:
        display_uv_index_card(current_weather['uv_index'])
    
    with col4:
        display_visibility_card(current_weather['visibility'])


def display_forecast_cards(forecast_df):
    """Display forecast as professional cards"""
    st.markdown('<div class="section-title">📅 7-Day Forecast</div>', unsafe_allow_html=True)
    
    cols = st.columns(7)
    
    for idx, (i, row) in enumerate(forecast_df.head(7).iterrows()):
        with cols[idx]:
            day_name = get_day_name(row['date'])
            date_obj = datetime.strptime(row['date'], "%Y-%m-%d")
            
            st.markdown(f"""
            <div class="forecast-card">
                <div class="forecast-day">{day_name[:3]}</div>
                <div style="font-size: 11px; color: #999; margin-bottom: 10px;">{date_obj.strftime('%m/%d')}</div>
                <div class="forecast-emoji">{row['weather_emoji']}</div>
                <div class="forecast-temp">{row['max_temp']}°</div>
                <div style="font-size: 12px; color: #999; margin: 5px 0;">{row['min_temp']}°</div>
                <div style="font-size: 10px; color: #666; margin-top: 8px;">{row['weather_description']}</div>
            </div>
            """, unsafe_allow_html=True)


def display_detailed_forecast_table(forecast_df):
    """Display detailed forecast table"""
    st.markdown('<div class="section-title">📋 Detailed 14-Day Forecast</div>', unsafe_allow_html=True)
    
    display_df = forecast_df.copy()
    display_df['Day'] = display_df['date'].apply(get_day_name)
    display_df['Date'] = pd.to_datetime(display_df['date']).dt.strftime('%m/%d')
    display_df['Weather'] = display_df['weather_emoji'] + ' ' + display_df['weather_description']
    display_df['Max Temp'] = display_df['max_temp'].astype(str) + '°C'
    display_df['Min Temp'] = display_df['min_temp'].astype(str) + '°C'
    display_df['Precipitation'] = display_df['precipitation'].astype(str) + ' mm'
    display_df['Wind'] = display_df['wind_speed'].astype(str) + ' km/h'
    display_df['UV Index'] = display_df['uv_index'].astype(str)
    
    display_table = display_df[['Day', 'Date', 'Weather', 'Max Temp', 'Min Temp', 'Precipitation', 'Wind', 'UV Index']]
    st.dataframe(display_table, use_container_width=True, hide_index=True, height=400)


def plot_temperature_chart(forecast_df):
    """Create professional temperature trend chart"""
    st.markdown('<div class="section-title">🌡️ Temperature Trend</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['max_temp'],
        mode='lines+markers',
        name='High Temp',
        line=dict(color='#FF6B6B', width=4),
        marker=dict(size=10, symbol='circle')
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['min_temp'],
        mode='lines+markers',
        name='Low Temp',
        line=dict(color='#4ECDC4', width=4),
        marker=dict(size=10, symbol='circle')
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['max_temp'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['min_temp'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='Temperature Range',
        fillcolor='rgba(102,126,234,0.15)'
    ))
    
    fig.update_layout(
        title='Temperature Forecast (°C)',
        xaxis_title='Date',
        yaxis_title='Temperature',
        hovermode='x unified',
        height=450,
        template='plotly_white',
        font=dict(size=12),
        plot_bgcolor='rgba(240,242,246,0.5)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_precipitation_chart(forecast_df):
    """Create professional precipitation chart"""
    st.markdown('<div class="section-title">💧 Precipitation Forecast</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    colors = ['#667eea' if x > 0 else '#e0e0e0' for x in forecast_df['precipitation']]
    
    fig.add_trace(go.Bar(
        x=forecast_df['date_formatted'],
        y=forecast_df['precipitation'],
        marker=dict(color=colors),
        name='Precipitation',
        hovertemplate='<b>%{x}</b><br>Precipitation: %{y} mm<extra></extra>'
    ))
    
    fig.update_layout(
        title='Precipitation Forecast (mm)',
        xaxis_title='Date',
        yaxis_title='Precipitation',
        hovermode='x',
        height=450,
        template='plotly_white',
        font=dict(size=12),
        plot_bgcolor='rgba(240,242,246,0.5)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_wind_chart(forecast_df):
    """Create professional wind speed chart"""
    st.markdown('<div class="section-title">💨 Wind Speed Forecast</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    fig.add_trace(go.Scatter(
        x=forecast_df['date_formatted'],
        y=forecast_df['wind_speed'],
        mode='lines+markers',
        fill='tozeroy',
        name='Wind Speed',
        line=dict(color='#FF9F43', width=4),
        marker=dict(size=10),
        fillcolor='rgba(255,159,67,0.15)'
    ))
    
    fig.update_layout(
        title='Wind Speed Forecast (km/h)',
        xaxis_title='Date',
        yaxis_title='Wind Speed',
        hovermode='x',
        height=450,
        template='plotly_white',
        font=dict(size=12),
        plot_bgcolor='rgba(240,242,246,0.5)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_uv_index_chart(forecast_df):
    """Create UV Index chart"""
    st.markdown('<div class="section-title">☀️ UV Index Forecast</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    forecast_df['date_formatted'] = pd.to_datetime(forecast_df['date']).dt.strftime('%m/%d')
    
    fig.add_trace(go.Bar(
        x=forecast_df['date_formatted'],
        y=forecast_df['uv_index'],
        marker=dict(
            color=forecast_df['uv_index'],
            colorscale='YlOrRd',
            colorbar=dict(title="UV Index")
        ),
        name='UV Index',
        hovertemplate='<b>%{x}</b><br>UV Index: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='UV Index Forecast',
        xaxis_title='Date',
        yaxis_title='UV Index',
        hovermode='x',
        height=450,
        template='plotly_white',
        font=dict(size=12),
        plot_bgcolor='rgba(240,242,246,0.5)',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ==================== MAIN APPLICATION ====================

def main():
    """Main application function"""
    
    display_hero_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔍 Search Location")
        
        search_query = st.text_input(
            "City Search",
            placeholder="Enter city name...",
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
                    "Found Cities",
                    range(len(city_options)),
                    format_func=lambda x: city_options[x],
                    key="city_selector"
                )
                selected_city = cities[selected_index]
            else:
                st.warning("No cities found")
        
        st.divider()
        
        st.markdown("## ⭐ Quick Access Cities")
        favorite_cities = {
            "Delhi": (28.7041, 77.1025),
            "Mumbai": (19.0760, 72.8777),
            "London": (51.5074, -0.1278),
            "New York": (40.7128, -74.0060),
            "Tokyo": (35.6762, 139.6503),
            "Dubai": (25.2048, 55.2708),
            "Sydney": (-33.8688, 151.2093),
            "Paris": (48.8566, 2.3522),
            "Toronto": (43.6629, -79.3957),
            "Singapore": (1.3521, 103.8198)
        }
        
        for city_name, (lat, lon) in favorite_cities.items():
            if st.button(f"📍 {city_name}", use_container_width=True, key=f"fav_{city_name}"):
                selected_city = {
                    "name": city_name,
                    "latitude": lat,
                    "longitude": lon,
                    "country": "India" if city_name in ["Delhi", "Mumbai"] else "Other"
                }
    
    # Default to Delhi
    if selected_city is None:
        selected_city = {
            "name": "Delhi",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "country": "India"
        }
    
    # Fetch data
    weather_data = fetch_weather_data(selected_city["latitude"], selected_city["longitude"])
    air_quality_data = fetch_air_quality_data(selected_city["latitude"], selected_city["longitude"])
    
    if weather_data:
        # Process data
        current_weather = process_current_weather(weather_data, selected_city["name"], selected_city["country"])
        forecast_df = process_forecast_data(weather_data)
        air_quality = process_air_quality(air_quality_data)
        
        # Current Weather Section
        display_current_weather_section(current_weather)
        
        st.divider()
        
        # Metrics Grid
        display_metrics_grid(current_weather)
        
        st.divider()
        
        # Air Quality
        display_aqi_section(air_quality)
        
        st.divider()
        
        # 7-Day Forecast
        display_forecast_cards(forecast_df)
        
        st.divider()
        
        # Tabs for detailed views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📊 Detailed Forecast", "🌡️ Temperature", "💧 Precipitation", "💨 Wind", "☀️ UV Index"]
        )
        
        with tab1:
            display_detailed_forecast_table(forecast_df)
        
        with tab2:
            plot_temperature_chart(forecast_df)
        
        with tab3:
            plot_precipitation_chart(forecast_df)
        
        with tab4:
            plot_wind_chart(forecast_df)
        
        with tab5:
            plot_uv_index_chart(forecast_df)
        
        # Footer
        st.markdown("""
        <div class="footer">
            <p>📡 Data from Open-Meteo API | ⏰ Updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>🎨 Premium Weather Dashboard | Made with ❤️ using Streamlit</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.error("❌ Unable to fetch weather data. Please try again later.")


if __name__ == "__main__":
    main()
