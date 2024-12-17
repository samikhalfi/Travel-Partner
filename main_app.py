import streamlit as st
import os
from services.api_services import get_destination_recommendations, get_weather_info, get_attractions
from utils.budget_utils import estimate_trip_budget, generate_budget_visualization
from utils.pdf_generator import generate_pdf
from utils.ui_utils import apply_apple_style_ui
from litellm import completion
from services.nlp_services import ConversationMemory, NLPService
from pages.chatbot_page import chatbot_page
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
def display_recommendations(recommendations):
    if recommendations:
        for rec in recommendations:
            title = rec.get('title', 'No title')
            url = rec.get('url', '#')
            snippet = rec.get('snippet', 'No description available')
            st.markdown(f"- **[{title}]({url})**: {snippet}")
    else:
        st.write("No specific travel recommendations found.")

def travel_planner_page():

    # Apply Apple-style UI
    apply_apple_style_ui()

    st.sidebar.title("🌍 Travel Planner Input")
    
    # Sidebar Inputs
    destination = st.sidebar.text_input("Enter your destination (e.g., Paris, Tokyo)")
    budget = st.sidebar.number_input("Enter your budget (in USD)", min_value=100)
    interests = st.sidebar.multiselect("Select your interests", 
        ["Culture", "Food", "Adventure", "Nature", "History", "Nightlife", "Shopping", "Wellness"]
    )

    # Initialize conversation memory
    conversation_memory = ConversationMemory()

    # Display Last Conversations
    st.sidebar.write("### Last Conversations: ")
    recent_conversations = conversation_memory.get_recent_history(5)
    for i, conv in enumerate(recent_conversations, 1):
        st.sidebar.write(f"{i}. User: {conv['user_message'][:30]}...")

    if destination and budget > 0 and interests:
        st.title("🌍 Voyager: Your Intelligent Travel Companion")
        st.markdown("*Plan your perfect journey with AI-powered insights*")
        
        col1, col2, col3 = st.columns(3)
        
        # Fetch weather, attractions, and recommendations
        weather_data = get_weather_info(destination)
        attractions = get_attractions(destination)
        recommendations = get_destination_recommendations(destination)

        with col1:
            st.subheader("🌤️ Weather Forecast")
            if weather_data:
                weather_description = weather_data['weather'][0]['description']
                temperature = weather_data['main']['temp']
                st.markdown(f"**{weather_description}** - {temperature}°C")
            else:
                st.write("Weather data not available.")

        with col2:
            st.subheader("🏆 Top Attractions")
            if attractions:
                for attraction in attractions:
                    st.markdown(f"- {attraction.get('name', 'Unnamed Attraction')}")
            else:
                st.write("No attractions data available.")

        with col3:
            st.subheader("🌍 Travel Blogs")
            if recommendations:
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
                # Generate travel plan using Groq API
                travel_plan = generate_travel_plan(destination, budget, interests, weather_data, attractions)
                st.subheader("🗺️ Personalized Travel Plan")
                st.write(travel_plan)

                # Generate PDF for Download
                pdf_file_path = generate_pdf(travel_plan, destination)
                st.download_button("Download Travel Plan as PDF", 
                                   data=open(pdf_file_path, "rb"), 
                                   file_name=pdf_file_path)

                # Save the conversation in memory
                conversation_memory.add_conversation(
                    f"Travel Plan for {destination}", 
                    travel_plan
                )
        else:
            st.error("Could not fetch weather or attractions. Please try again.")
    else:
        st.warning("Please fill in all fields.")
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

def main():
    """
    Multi-page Streamlit application
    """
    st.set_page_config(
        page_title="AI Travel Planner",
        page_icon="🌍",
        layout="wide"
    )

    # Sidebar for page navigation
    page = st.sidebar.radio("Navigate", ["Travel Planner", "AI Assistant Chatbot"])

    if page == "Travel Planner":
        travel_planner_page()
    else:
        chatbot_page()

if __name__ == "__main__":
    main()

