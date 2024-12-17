# 🌍 Voyager: AI-Powered Travel Companion

Voyager is an innovative travel planning application that leverages artificial intelligence to transform your travel experience. From personalized itineraries to intelligent chatbot assistance, Voyager makes travel planning intuitive, informative, and exciting.

## 🚀 Features

### Travel Planning
- **Real-time Weather Forecasts**: Get up-to-the-minute meteorological insights for your destination
- **Destination Attractions**: Discover top attractions tailored to your interests
- **Personalized Budget Estimation**: Generate comprehensive budget breakdowns with interactive charts
- **Travel Plan Generation**: Create and download detailed travel plans as PDF documents

### AI Travel Chatbot
- **Natural Language Interaction**: Engage with an intelligent travel assistant
- **Advanced NLP Capabilities**:
  - Sentiment analysis
  - Intent detection
  - Entity extraction
- **Contextual Conversation**: Maintain conversation memory for personalized interactions

## 🛠️ Tech Stack

### Programming & Framework
- **Python**: Primary programming language
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis

### Natural Language Processing
- **SentenceTransformers**: Advanced semantic understanding
- **TextBlob**: Sentiment analysis and linguistic processing

### Database & Storage
- **ChromaDB**: Vector database for efficient information retrieval

### Additional Technologies
- **ReportLab**: PDF document generation
- **OpenWeatherMap API**: Real-time weather data

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/voyager-travel-planner.git
cd voyager-travel-planner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
Open `api_service.py` and replace the placeholder with your OpenWeatherMap API key:
```python
WEATHER_API_KEY = "your_openweathermap_api_key"
```

### 4. Launch the Application
```bash
streamlit run app.py
```

### 5. Access the Application
Open `http://localhost:8501` in your web browser


## 🎮 How to Use

### Travel Planner
1. Navigate to the Travel Planner section
2. Input your destination, budget, and interests in the sidebar
3. Explore:
   - Detailed weather forecasts
   - Recommended attractions
   - Personalized budget charts
4. Generate and download a comprehensive travel plan

### AI Travel Chatbot
1. Switch to the Chatbot page
2. Ask travel-related questions
3. Receive intelligent, context-aware responses with sentiment analysis

## 🧰 Dependencies
Install all required dependencies with:
```bash
pip install -r requirements.txt
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License
MIT License

**Author**: Your Name  
**GitHub**: YourGitHubProfile

---

**Happy Traveling with Voyager! 🌎✈️**