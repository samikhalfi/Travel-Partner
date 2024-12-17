import streamlit as st
import requests
import os
from geopy.geocoders import Nominatim
from fpdf import FPDF
from litellm import completion
import plotly.express as px
import pandas as pd

SERPER_API_KEY = "3fd431e800f4ff4f3e7f4452961880958170ad18"
FOURSQUARE_API_KEY = 'fsq3SR3dOaH7SaGGtfjOy4ufUpxvWEXFTKTlMbMH9oRSnfk='
OPENWEATHER_API_KEY = '4f810fbc16783e4a18cfe46cdf064876'
GROQ_API_KEY = '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'

os.environ['GROQ_API_KEY'] = GROQ_API_KEY

# Fetch Destination Recommendations from Serper API
def get_destination_recommendations(destination):
    try:
        url = f'https://google.serper.dev/search?q={destination} travel guide&num=10'
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            recommendations = []
            for item in data.get('organic', []):
                if 'travel' in item.get('title', '').lower() or 'guide' in item.get('title', '').lower():
                    recommendations.append(item)
            return recommendations
        else:
            st.error(f"Error fetching recommendations: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error in destination recommendations: {str(e)}")
        return []

# Fetch Weather Information from OpenWeather API
def get_weather_info(destination):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={OPENWEATHER_API_KEY}&units=metric'
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching weather: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error in weather fetch: {str(e)}")
        return None

# Fetch Attractions from Foursquare API
def get_attractions(destination):
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            "Accept": "application/json",
            "Authorization": FOURSQUARE_API_KEY
        }
        params = {"query": "tourist attractions", "near": destination, "limit": 10}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            st.error(f"Error fetching attractions: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Attractions fetch error: {e}")
        return []

# Generate Travel Plan using Groq API via Litellm
def generate_travel_plan(destination, budget, interests, weather_data, attractions):
    user_query = f"""
    You are a friendly and knowledgeable travel guide. Based on the following:
    Destination: {destination}
    Budget: {budget}
    Interests: {interests}
    Weather: {weather_data['weather'][0]['description']} with a temperature of {weather_data['main']['temp']}°C
    Attractions: {', '.join([attraction['name'] for attraction in attractions])}

    Please create a personalized, friendly, and engaging 5 day travel plan. Make sure to:
    1. Provide a day-by-day itinerary with fun activities, places to visit, and food recommendations.
    2. Suggest budget-friendly options while considering the user's interests and preferences.
    3. Include helpful travel tips, such as what to pack or how to get around.
    4. Keep the tone conversational and warm, like a local guide sharing their favorite spots.
    """

    try:
        response = completion(
            model="groq/llama3-8b-8192",  # The model you wish to use
            messages=[{"role": "user", "content": user_query}],
            temperature=0.9,  # Adjust creativity level (0.0 - 1.0)
            max_tokens=3500,  # Control the length of the response
            top_p=0.7,  # Nucleus sampling (0.0 - 1.0)
            frequency_penalty=0.5,  # Avoid repetition of words
            presence_penalty=0.3  # Reduce repetition of topics
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating travel plan: {e}")
        return "Sorry, there was an error generating your travel plan."

# Function to generate a PDF
def generate_pdf(travel_plan, destination):
    pdf = FPDF()
    pdf.add_page()
    
    # Add a font that supports Unicode (DejaVuSans or other)
    pdf.add_font("DejaVuSans", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVuSans", size=12)
    
    pdf.cell(200, 10, txt=f"Travel Plan for {destination}", ln=True, align="C")
    pdf.ln(10)
    
    # Use multi_cell to handle long text and preserve line breaks
    pdf.multi_cell(0, 10, travel_plan)
    
    # Create PDF file path
    pdf_file_path = f"{destination}_travel_plan.pdf"
    
    # Output PDF to file
    pdf.output(pdf_file_path)
    
    return pdf_file_path

# Display the recommendations from the API
def display_recommendations(recommendations):
    if recommendations:
        for rec in recommendations:
            title = rec.get('title', 'No title')
            url = rec.get('url', '#')
            snippet = rec.get('snippet', 'No description available')
            st.markdown(f"- **[{title}]({url})**: {snippet}")
    else:
        st.write("No specific travel recommendations found.")

def estimate_trip_budget(destination, duration=7):
    """Provide budget estimation and breakdown"""
    try:
        # Simulated budget estimation (would use more sophisticated API in production)
        base_costs = {
            'accommodation': 100 * duration,
            'food': 50 * duration,
            'local_transport': 20 * duration,
            'attractions': 30 * duration,
            'miscellaneous': 50
        }
        total_estimated_budget = sum(base_costs.values())
        
        return {
            'total_estimated_budget': total_estimated_budget,
            'cost_breakdown': base_costs
        }
    except Exception as e:
        st.error(f"Budget estimation error: {e}")
        return None

def generate_budget_visualization(budget_info):
    """Create a budget breakdown visualization"""
    if not budget_info:
        return None
    
    df = pd.DataFrame.from_dict(budget_info['cost_breakdown'], orient='index', columns=['Cost'])
    df.index.name = 'Category'
    df = df.reset_index()
    
    fig = px.pie(df, values='Cost', names='Category', 
                 title='Travel Budget Breakdown',
                 color_discrete_sequence=px.colors.sequential.Plasma_r)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def apple_style_ui():
    st.markdown("""
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;

    }
    .stApp {
        max-width: 99%;
        margin: 0 auto;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);

    }
    .stButton > button {
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit Interface
def run():
    apple_style_ui()
    st.sidebar.title("🌍 Travel Planner Input")
    
    # Sidebar Inputs
    destination = st.sidebar.text_input("Enter your destination (e.g., Paris, Tokyo)")
    budget = st.sidebar.number_input("Enter your budget (in USD)", min_value=100)
    interests = st.sidebar.multiselect("Select your interests", ["Culture", "Food", "Adventure", "Nature", "History", "Nightlife", "Shopping", "Wellness"])

    # Display Last Conversations
    if 'conversations' not in st.session_state:
        st.session_state['conversations'] = []

    st.sidebar.write("### Last Conversations: ")
    for i, conversation in enumerate(st.session_state['conversations'][-5:], 1):
        st.sidebar.write(f"{i}. {conversation[:30]}...")

    if destination and budget > 0 and interests:
        st.title("🌍 Voyager: Your Intelligent Travel Companion")
        st.markdown("*Plan your perfect journey with AI-powered insights*")
        
        col1, col2, col3 = st.columns(3)
        
        # Fetch weather, attractions, and recommendations only once
        weather_data = get_weather_info(destination)
        attractions = get_attractions(destination)
        recommendations = get_destination_recommendations(destination)

        with col1:
            st.subheader("🌤️ Weather Forecast")
            if weather_data:  # Check if weather data exists
                weather_description = weather_data['weather'][0]['description']
                temperature = weather_data['main']['temp']
                st.markdown(f"**{weather_description}** - {temperature}°C")
            else:
                st.write("Weather data not available.")

        with col2:
            st.subheader("🏆 Top Attractions")
            if attractions:  # Check if attractions data exists
                for attraction in attractions:
                    st.markdown(f"- {attraction.get('name', 'Unnamed Attraction')}")
            else:
                st.write("No attractions data available.")

        with col3:
            st.subheader("🌍 Travel Blogs")
            if recommendations:  # Check if recommendations data exists
                display_recommendations(recommendations[:3])
            else:
                st.write("No travel recommendations found.")
        
        st.subheader("💰 Budget Breakdown")
        budget_info = estimate_trip_budget(destination)
        if budget_info:
            budget_fig = generate_budget_visualization(budget_info)
            st.plotly_chart(budget_fig)
        else:
            st.write("Could not estimate the budget. Please try again.")

        if weather_data and len(attractions) > 0:
            if st.button("✨ Craft My Journey", use_container_width=True):
                travel_plan = generate_travel_plan(destination, budget, interests, weather_data, attractions)
                st.subheader("🗺️ Personalized Travel Plan")
                st.write(travel_plan)

                # Generate PDF for Download
                pdf_file_path = generate_pdf(travel_plan, destination)
                st.download_button("Download Travel Plan as PDF", data=open(pdf_file_path, "rb"), file_name=pdf_file_path)

                # Save the conversation for chat history
                st.session_state['conversations'].append(f"Travel Plan for {destination}: {travel_plan}")
            
            user_message = st.text_area("Chat with your travel assistant", "")
            if user_message:
                conversation_history = [{"role": "user", "content": user_message}]
                travel_assistant_response = completion(
                    model="groq/llama3-8b-8192",
                    messages=conversation_history
                )
                chat_response = travel_assistant_response['choices'][0]['message']['content']
                st.write(chat_response)

                # Save chat in the session memory
                st.session_state['conversations'].append(f"User: {user_message}")
                st.session_state['conversations'].append(f"Bot: {chat_response}")
        else:
            st.error("Could not fetch weather or attractions. Please try again.")
    else:
        st.warning("Please fill in all fields.")

if __name__ == "__main__":
    run()
