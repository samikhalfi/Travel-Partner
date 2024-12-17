import spacy
from textblob import TextBlob
from collections import Counter
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class NLPService:
    def __init__(self):
        # Load spaCy model for advanced NLP tasks
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model... Please wait.")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def analyze_sentiment(self, text, thresholds=None):
        """
        Analyze sentiment of the text using TextBlob and provide detailed insights.
        
        Args:
            text (str): Input text to analyze.
            thresholds (dict): Custom thresholds for sentiment categories.
        
        Returns:
            dict: Contains polarity, subjectivity, and sentiment category.
        """
        if not text.strip():
            return {"error": "Input text is empty or invalid."}

        # Set default thresholds
        if thresholds is None:
            thresholds = {
                "very_positive": 0.5,
                "positive": 0,
                "negative": -0.5,
            }

        blob = TextBlob(text)
        
        # Sentiment polarity and subjectivity
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Categorize sentiment
        if polarity > thresholds["very_positive"]:
            sentiment_category = "Very Positive"
        elif polarity > thresholds["positive"]:
            sentiment_category = "Positive"
        elif polarity == 0:
            sentiment_category = "Neutral"
        elif polarity > thresholds["negative"]:
            sentiment_category = "Negative"
        else:
            sentiment_category = "Very Negative"
        
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment_category": sentiment_category
        }

    def extract_key_entities(self, text):
        """
        Extract key named entities and their frequency from the text.
        
        Args:
            text (str): Input text to analyze.

        Returns:
            dict: Named entities grouped by type with frequencies.
        """
        if not text.strip():
            return {"error": "Input text is empty or invalid."}

        doc = self.nlp(text)
        entities = Counter()

        for ent in doc.ents:
            entities[(ent.label_, ent.text)] += 1
        
        # Organize entities by type
        entity_summary = {}
        for (label, text), count in entities.items():
            if label not in entity_summary:
                entity_summary[label] = []
            entity_summary[label].append({"entity": text, "count": count})
        
        return entity_summary

    def analyze_conversation_intent(self, text, use_keywords=True):
        """
        Analyze the intent of the conversation using keyword matching.
        
        Args:
            text (str): Input text to analyze.
            use_keywords (bool): If True, use keyword-based intent detection.

        Returns:
            dict: Detected intents and sentiment analysis.
        """
        if not text.strip():
            return {"error": "Input text is empty or invalid."}

        intent_keywords = {
            "travel_planning": ["trip", "vacation", "travel", "destination", "plan"],
            "budget_inquiry": ["cost", "price", "budget", "expense", "money"],
            "recommendation": ["suggest", "recommend", "advice", "help"],
            "complaint": ["problem", "issue", "bad", "terrible", "wrong"],
            "praise": ["great", "awesome", "amazing", "wonderful", "excellent"]
        }

        detected_intents = []

        # Keyword-based intent detection
        if use_keywords:
            text_lower = text.lower()
            for intent, keywords in intent_keywords.items():
                matched_keywords = [kw for kw in keywords if kw in text_lower]
                if matched_keywords:
                    detected_intents.append({"intent": intent, "keywords_matched": matched_keywords})

        # Sentiment analysis
        sentiment = self.analyze_sentiment(text)

        return {
            "detected_intents": detected_intents,
            "sentiment": sentiment
        }

    def detect_language(self, text):
        """
        Detect the language of the input text.

        Args:
            text (str): Input text to analyze.

        Returns:
            str: Detected language code (e.g., 'en' for English).
        """
        if not text.strip():
            return {"error": "Input text is empty or invalid."}
        
        blob = TextBlob(text)
        return blob.detect_language()


class ConversationMemory:
    def __init__(self, max_history=50, embedding_model='all-MiniLM-L6-v2'):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="conversation_memory")
        self.embedder = SentenceTransformer(embedding_model)
        self.max_history = max_history
        self.history: List[Dict] = []

    def add_conversation(self, user_message: str, ai_response: str):
        conv_id = str(uuid.uuid4())
        full_text = f"User: {user_message}\nAI: {ai_response}"
        embedding = self.embedder.encode(full_text).tolist()

        # Add to vector database
        self.collection.add(
            ids=[conv_id],
            embeddings=[embedding],
            documents=[full_text]
        )

        # Store in memory
        conversation_entry = {
            "id": conv_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": uuid.uuid1().time
        }

        self.history.append(conversation_entry)

        if len(self.history) > self.max_history:
            old_entry = self.history.pop(0)
            self.collection.delete(ids=[old_entry["id"]])

    def retrieve_relevant_context(self, query: str, top_k: int = 3):
        query_embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results.get('documents', [])

    def get_recent_history(self, num_messages: int = 5):
        return self.history[-num_messages:]