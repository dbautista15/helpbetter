"""
ML Analyzer for Introspect - Pattern Recognition in Journal Entries
"""

import sys
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from datetime import datetime


class Analyzer:
    """ML-powered journal entry analyzer."""

    def __init__(self):
        """Initialize the analyzer with ML model."""
        sys.stderr.write("📦 Loading ML model...\n")
        sys.stderr.flush()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        sys.stderr.write("✅ ML model loaded successfully\n")
        sys.stderr.flush()

    def analyze_entry(
        self, new_entry_text: str, past_entries: List[Dict], mood_rating: int = 3
    ) -> Dict:
        """Analyze a new journal entry by comparing to past entries."""
        sys.stderr.write(f"🧠 Analyzing entry: '{new_entry_text[:50]}...'\n")
        sys.stderr.flush()

        # Generate embedding
        new_embedding = self.model.encode(new_entry_text)
        sys.stderr.write(f"✅ Generated embedding (shape: {new_embedding.shape})\n")
        sys.stderr.flush()

        # Find similar entries
        similar_entries = []
        if len(past_entries) > 0:
            similar_entries = self._find_similar_entries(
                new_embedding, past_entries, top_k=3
            )
            sys.stderr.write(f"📊 Found {len(similar_entries)} similar entries\n")
            sys.stderr.flush()
        else:
            sys.stderr.write("🔭 No past entries to compare (first entry!)\n")
            sys.stderr.flush()

        # Detect sentiment
        mood = self._detect_sentiment(new_entry_text)
        sys.stderr.write(
            f"😊 Detected mood: {mood['detected']} (confidence: {mood['confidence']:.2f})\n"
        )
        sys.stderr.flush()

        # Generate summary label
        summary = self._generate_summary_label(new_entry_text, mood_rating, mood)
        sys.stderr.write(f"📋 Generated summary: {summary['title']}\n")
        sys.stderr.flush()

        # Generate insight
        insight = self._generate_insight(
            new_entry_text, similar_entries, mood, past_entries
        )
        sys.stderr.write(f"💡 Generated insight\n")
        sys.stderr.flush()

        return {
            "embedding": new_embedding,
            "insight": insight,
            "similar_entries": similar_entries,
            "mood": mood,
            "summary": summary,
        }

    def _find_similar_entries(
        self, new_embedding: np.ndarray, past_entries: List[Dict], top_k: int = 3
    ) -> List[Dict]:
        """Find the most similar past entries using cosine similarity."""
        if len(past_entries) == 0:
            return []

        past_embeddings = np.array([entry["embedding"] for entry in past_entries])
        similarities = cosine_similarity(new_embedding.reshape(1, -1), past_embeddings)[
            0
        ]
        top_indices = np.argsort(similarities)[::-1][:top_k]

        similar = []
        for idx in top_indices:
            similarity_score = float(similarities[idx])
            if similarity_score > 0.3:
                similar.append(
                    {
                        "text": past_entries[idx]["text"],
                        "similarity": similarity_score,
                        "timestamp": past_entries[idx]["timestamp"],
                        "mood": past_entries[idx].get("mood", 3),
                    }
                )
        return similar

    def _detect_sentiment(self, text: str) -> Dict:
        """Detect sentiment/mood of the entry."""
        positive_refs = [
            "I feel great and happy today",
            "Everything is wonderful",
            "I'm excited and optimistic",
        ]
        negative_refs = [
            "I feel sad and worried",
            "Everything is difficult",
            "I'm anxious and stressed",
        ]

        text_embedding = self.model.encode(text).reshape(1, -1)
        positive_embeddings = self.model.encode(positive_refs)
        negative_embeddings = self.model.encode(negative_refs)

        positive_sim = cosine_similarity(text_embedding, positive_embeddings).mean()
        negative_sim = cosine_similarity(text_embedding, negative_embeddings).mean()

        if positive_sim > negative_sim:
            detected = "positive"
            confidence = float((positive_sim - negative_sim + 1) / 2)
        else:
            detected = "negative"
            confidence = float((negative_sim - positive_sim + 1) / 2)

        confidence = max(0.0, min(1.0, confidence))
        return {"detected": detected, "confidence": confidence}

    def _generate_summary_label(
        self, text: str, mood_rating: int, mood_analysis: Dict
    ) -> Dict:
        """
        Generate a summary label for timeline display.

        Returns:
            {
                'title': str,        # "Work - Performance Review"
                'themes': List[str], # ["work", "mental_health"]
                'emotion': str       # "struggling but persisting"
            }
        """

        # Theme categories - semantic clusters of related concepts
        theme_categories = {
            "work": [
                "work",
                "job",
                "career",
                "presentation",
                "meeting",
                "boss",
                "manager",
                "colleague",
                "deadline",
                "project",
                "interview",
                "promotion",
                "performance",
                "client",
                "review",
            ],
            "relationships": [
                "relationship",
                "partner",
                "friend",
                "family",
                "conflict",
                "communication",
                "connection",
                "love",
                "breakup",
                "argument",
                "lonely",
                "social",
                "dating",
                "marriage",
                "divorce",
            ],
            "mental_health": [
                "anxiety",
                "depression",
                "therapy",
                "therapist",
                "medication",
                "panic",
                "stress",
                "overwhelmed",
                "burnout",
                "worried",
                "nervous",
                "fear",
                "anxious",
                "scared",
            ],
            "physical_health": [
                "health",
                "sleep",
                "exercise",
                "gym",
                "diet",
                "tired",
                "energy",
                "pain",
                "doctor",
                "sick",
                "headache",
                "medical",
            ],
            "personal_growth": [
                "growth",
                "learning",
                "confidence",
                "success",
                "achievement",
                "progress",
                "goal",
                "improve",
                "proud",
                "accomplished",
                "development",
                "skills",
            ],
            "daily_life": [
                "routine",
                "habits",
                "schedule",
                "home",
                "chores",
                "errands",
                "weekend",
                "morning",
                "evening",
                "daily",
            ],
        }

        # Detect themes using keyword matching
        text_lower = text.lower()
        detected_themes = []

        for theme, keywords in theme_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)

        # Default if nothing matched
        if not detected_themes:
            detected_themes = ["personal_reflection"]

        # Generate emotion descriptor
        if mood_rating >= 4:
            emotion = "positive and energized"
        elif mood_rating == 3:
            emotion = "neutral and contemplative"
        elif mood_rating == 2:
            emotion = "struggling but persisting"
        else:
            emotion = "difficult and overwhelming"

        # Refine based on detected sentiment
        if mood_analysis["detected"] == "negative" and mood_rating >= 3:
            emotion = "processing and reflecting"

        # Generate title
        primary_theme = detected_themes[0].replace("_", " ").title()

        # Check for specific keywords FIRST (more reliable)
        specific_keywords = {
            "performance review": "Performance Review",
            "quarterly review": "Review",
            "presentation": "Presentation",
            "interview": "Interview",
            "therapy": "Therapy Session",
            "conflict": "Conflict",
            "meeting": "Meeting",
            "deadline": "Deadline",
            "project": "Project",
        }

        title_subject = None
        for keyword, label in specific_keywords.items():
            if keyword in text_lower:
                title_subject = label
                break

        # If no keyword match, try extracting proper nouns
        if not title_subject:
            # Common words to exclude
            exclude_words = {
                "I",
                "The",
                "A",
                "And",
                "But",
                "So",
                "Or",
                "My",
                "This",
                "That",
                "These",
                "Those",
                "It",
                "They",
                "We",
                "He",
                "She",
                "Had",
                "Was",
                "Were",
                "Been",
                "Have",
                "Has",
                "Did",
                "Do",
            }

            words = text.split()
            specific_topics = [
                w.strip(".,!?")
                for w in words
                if w and w[0].isupper() and len(w) > 2 and w not in exclude_words
            ]

            if specific_topics:
                title_subject = specific_topics[0]

        # Construct final title
        if title_subject:
            title = f"{primary_theme} - {title_subject}"
        else:
            title = f"{primary_theme} Reflection"

        return {
            "title": title,
            "themes": detected_themes[:3],
            "emotion": emotion,
        }

    def _generate_insight(
        self,
        new_entry_text: str,
        similar_entries: List[Dict],
        mood: Dict,
        all_past_entries: List[Dict],
    ) -> str:
        """
        Generate a contextual insight based on patterns.
        Quote the user to themselves!
        """

        # Case 1: First entry ever
        if len(all_past_entries) == 0:
            return (
                f"Welcome to your journaling journey! This is your first entry. "
                f"As you write more, I'll help you spot patterns in your thoughts and emotions."
            )

        # Case 2: Pattern recognition WITH QUOTES
        if len(similar_entries) > 0:
            most_similar = similar_entries[0]

            # Parse timestamp
            timestamp = datetime.fromisoformat(most_similar["timestamp"])
            days_ago = (datetime.now() - timestamp).days

            if days_ago == 0:
                time_phrase = "earlier today"
            elif days_ago == 1:
                time_phrase = "yesterday"
            elif days_ago < 7:
                time_phrase = f"{days_ago} days ago"
            elif days_ago < 30:
                weeks = days_ago // 7
                time_phrase = f"{weeks} week{'s' if weeks > 1 else ''} ago"
            else:
                months = days_ago // 30
                time_phrase = f"{months} month{'s' if months > 1 else ''} ago"

            # Extract quote
            past_text = most_similar["text"]
            sentences = past_text.split(". ")

            if len(sentences) >= 2:
                quote = f"{sentences[0]}. {sentences[1]}."
            else:
                quote = sentences[0] if sentences else past_text[:150]

            if len(quote) > 200:
                quote = quote[:197] + "..."

            # Generate insight based on mood
            if mood["detected"] == "negative":
                if most_similar.get("mood", 3) < 3:
                    insight = (
                        f"You've felt this way before. {time_phrase}, you wrote:\n\n"
                        f'"{quote}"\n\n'
                        f"This pattern seems familiar. What helped you move forward then?"
                    )
                else:
                    insight = (
                        f"You've navigated similar feelings before. {time_phrase}, you wrote:\n\n"
                        f'"{quote}"\n\n'
                        f"You found a way through. What was different that time?"
                    )
            else:
                if most_similar.get("mood", 3) >= 4:
                    insight = (
                        f"This positive feeling has happened before! {time_phrase}, you wrote:\n\n"
                        f'"{quote}"\n\n'
                        f"You're building a pattern of what works for you."
                    )
                else:
                    insight = (
                        f"You're in a better place now. {time_phrase} you wrote:\n\n"
                        f'"{quote}"\n\n'
                        f"Look at how far you've come. What changed?"
                    )

        # Case 3: No strong patterns
        else:
            entry_count = len(all_past_entries) + 1

            if mood["detected"] == "positive":
                insight = (
                    f"You're in a good headspace today. This is entry #{entry_count}. "
                    f"Keep writing - patterns become clearer over time."
                )
            else:
                insight = (
                    f"I hear that things are challenging right now. "
                    f"This is entry #{entry_count}. Writing itself is an act of courage. "
                    f"Patterns will emerge as you continue."
                )

        return insight
