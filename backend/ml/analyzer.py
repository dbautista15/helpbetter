"""
ML Analyzer for Introspect - Pattern Recognition in Journal Entries
RAG Pipeline: Retrieval (semantic search) + Generation (Gemma2-2b)
"""

import sys
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class Analyzer:
    """ML-powered journal entry analyzer with RAG pipeline."""

    def __init__(self):
        """Initialize the analyzer with ML models."""
        sys.stderr.write("📦 Loading embedding model (sentence-transformers)...\n")
        sys.stderr.flush()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        sys.stderr.write("✅ Embedding model loaded\n")
        sys.stderr.flush()

        # Load Gemma2-2b for insight generation
        sys.stderr.write("📦 Loading Gemma2-2b LLM (this may take a moment)...\n")
        sys.stderr.flush()
        
        model_name = "google/gemma-2-2b-it"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.llm = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        
        # Move to CPU if no CUDA
        if not torch.cuda.is_available():
            self.llm = self.llm.to("cpu")
            sys.stderr.write("⚠️  Running on CPU (slower but works)\n")
        else:
            sys.stderr.write("🚀 Running on GPU\n")
        
        sys.stderr.write("✅ Gemma2-2b LLM loaded successfully\n")
        sys.stderr.flush()

    def analyze_entry(
        self, new_entry_text: str, past_entries: List[Dict], mood_rating: int = 3
    ) -> Dict:
        """Analyze a new journal entry by comparing to past entries."""
        sys.stderr.write(f"🧠 Analyzing entry: '{new_entry_text[:50]}...'\n")
        sys.stderr.flush()

        # Generate embedding
        new_embedding = self.embedding_model.encode(new_entry_text)
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

        text_embedding = self.embedding_model.encode(text).reshape(1, -1)
        positive_embeddings = self.embedding_model.encode(positive_refs)
        negative_embeddings = self.embedding_model.encode(negative_refs)

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
        Generate a contextual insight using RAG pipeline with Gemma2-2b.
        Uses retrieved past entries as context for the LLM.
        """
        sys.stderr.write("🤖 Generating LLM insight with RAG pipeline...\n")
        sys.stderr.flush()

        # Case 1: First entry ever - simple welcome message
        if len(all_past_entries) == 0:
            return (
                "Welcome to your journaling journey! This is your first entry. "
                "As you write more, I'll help you spot patterns in your thoughts and emotions."
            )

        # Case 2: Build context from similar entries for RAG
        if len(similar_entries) > 0:
            # Build context from retrieved entries
            context_entries = []
            for entry in similar_entries[:3]:  # Use top 3 similar entries
                timestamp = datetime.fromisoformat(entry["timestamp"])
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
                
                context_entries.append({
                    "text": entry["text"],
                    "time": time_phrase,
                    "mood": entry.get("mood", 3),
                    "similarity": entry["similarity"]
                })
            
            # Build the prompt for Gemma2
            prompt = self._build_rag_prompt(new_entry_text, context_entries, mood)
            
            # Generate insight using LLM
            insight = self._generate_with_llm(prompt)
            
        else:
            # Case 3: No similar entries found
            entry_count = len(all_past_entries) + 1
            prompt = f"""You are a supportive journaling companion. The user has written {entry_count} journal entries.

Current entry: "{new_entry_text}"

They are feeling {mood["detected"]} today. There are no strongly similar past entries yet. Provide brief, encouraging feedback that acknowledges their feelings and encourages continued journaling to discover patterns.

Keep your response to 2-3 sentences."""
            
            insight = self._generate_with_llm(prompt)

        return insight

    def _build_rag_prompt(
        self,
        current_entry: str,
        past_entries: List[Dict],
        mood: Dict
    ) -> str:
        """Build a RAG prompt with retrieved past entries as context."""
        
        # Build context section from past entries
        context_text = ""
        for i, entry in enumerate(past_entries, 1):
            mood_desc = "struggling" if entry["mood"] <= 2 else "neutral" if entry["mood"] == 3 else "positive"
            context_text += f"""
Past Entry {i} (from {entry["time"]}, mood: {entry["mood"]}/5 - {mood_desc}, {int(entry["similarity"]*100)}% similar):
"{entry["text"]}"
"""
        
        # Build the full prompt
        prompt = f"""You are a compassionate journaling companion helping the user recognize patterns in their emotional journey. You have access to their past journal entries.

CONTEXT - Similar Past Entries:
{context_text}

CURRENT ENTRY (mood: {mood["detected"]}):
"{current_entry}"

TASK:
Based on the similar past entries, provide a personalized, therapeutic insight that:
1. Acknowledges the pattern you notice between past and current entries
2. Quotes or references specific phrases from their past entries to show the connection
3. Asks a reflective question or provides supportive guidance
4. Keeps the tone warm, non-judgmental, and encouraging

Keep your response to 3-4 sentences. Quote the user's own words back to them."""

        return prompt

    def _generate_with_llm(self, prompt: str) -> str:
        """Generate text using Gemma2-2b LLM."""
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Move to same device as model
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate with controlled parameters
            with torch.no_grad():
                outputs = self.llm.generate(
                    **inputs,
                    max_new_tokens=200,  # Keep responses concise
                    temperature=0.7,      # Balanced creativity
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode output
            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated response (remove the prompt)
            response = full_output[len(prompt):].strip()
            
            sys.stderr.write(f"✅ LLM generated {len(response)} characters\n")
            sys.stderr.flush()
            
            return response if response else "I'm processing your thoughts and patterns."
            
        except Exception as e:
            sys.stderr.write(f"❌ LLM generation error: {e}\n")
            sys.stderr.flush()
            # Fallback to simple response
            return "I notice patterns in your entries. Continue journaling to deepen these insights."
