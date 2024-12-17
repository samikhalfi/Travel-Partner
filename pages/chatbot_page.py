import streamlit as st
from litellm import completion
from services.nlp_services import NLPService, ConversationMemory
import streamlit.components.v1 as components

def render_sentiment_metric_card(sentiment):

    st.markdown("""
    <style>
    .sentiment-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;    
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sentiment-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .sentiment-value {
        font-size: 18px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sentiment color mapping
    color_map = {
        "Very Positive": "#2ecc71",
        "Positive": "#27ae60",
        "Neutral": "#f39c12",
        "Negative": "#e74c3c",
        "Very Negative": "#c0392b"
    }
    
    # Create sentiment card
    sentiment_category = sentiment.get('sentiment_category', 'Unknown')
    st.markdown(f"""
    <div class="sentiment-card">
        <div class="sentiment-title">Sentiment Analysis</div>
        <div class="sentiment-value" style="color: {color_map.get(sentiment_category, '#333')};">
            📊 {sentiment_category}
        </div>
        <div class="sentiment-value">
            Polarity: {sentiment.get('polarity', 0):.2f}
        </div>
        <div class="sentiment-value">
            Subjectivity: {sentiment.get('subjectivity', 0):.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

def chatbot_page():
    """
    Dedicated chatbot page with advanced NLP features
    """
    st.title("🤖 Travel Assistant Chatbot")
    
    # Initialize NLP services
    nlp_service = NLPService()
    conversation_memory = ConversationMemory()
    
    # Chat input
    user_message = st.chat_input("Ask me anything about your travel plans!")
    
    if user_message:
        # Retrieve relevant context from memory
        relevant_context = conversation_memory.retrieve_relevant_context(user_message)
        context = "\n".join([str(item) for item in relevant_context]) if relevant_context else ""

        full_message = f"{context}\nUser: {user_message}"

        # Sentiment Analysis
        sentiment = nlp_service.analyze_sentiment(user_message)
        
        # Render sentiment metric card
        render_sentiment_metric_card(sentiment)

        # Intent Analysis
        intent_analysis = nlp_service.analyze_conversation_intent(user_message)
        
        # Display Detected Intents
        if intent_analysis['detected_intents']:
            st.subheader("🎯 Detected Intents")
            for intent in intent_analysis['detected_intents']:
                st.write(f"**Intent**: {intent['intent']}")
                st.write(f"**Keywords Matched**: {', '.join(intent['keywords_matched'])}")
        else:
            st.write("No specific intent detected.")

        # Entity Extraction
        entities = nlp_service.extract_key_entities(user_message)
        
        # Display entities
        if entities:
            st.subheader("🏷️ Extracted Entities")
            for entity_type, entity_list in entities.items():
                st.write(f"**{entity_type}:**")
                for entity in entity_list:
                    st.write(f"- {entity['entity']} (count: {entity['count']})")
        
        # Generate response using Groq API
        conversation_history = [{"role": "user", "content": full_message}]
        travel_assistant_response = completion(
            model="groq/llama3-8b-8192",
            messages=conversation_history
        )
        chat_response = travel_assistant_response['choices'][0]['message']['content']
        
        # Display chat response
        st.write(chat_response)

        # Save chat in the conversation memory
        conversation_memory.add_conversation(user_message, chat_response)

def main():
    """
    Main function to run the chatbot page
    """
    chatbot_page()

if __name__ == "__main__":
    main()