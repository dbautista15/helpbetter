"""
ML Analyzer for Introspect - Multi-Factor Pattern Recognition & Composite Mental State Scoring
Enhanced with RAG LLM Pipeline for Natural Language Insights
"""

import sys
import re
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import Counter, defaultdict

# NEW: LLM inference for RAG pipeline
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    sys.stderr.write("⚠️  llama-cpp-python not available. Using template-based insights.\n")


class Analyzer:
    """ML-powered journal entry analyzer with composite mental state scoring and RAG LLM."""

    def __init__(self, use_llm: bool = True):
        """Initialize the analyzer with ML model and optional LLM."""
        sys.stderr.write("📦 Loading ML model...\n")
        sys.stderr.flush()
        
        # Load embedding model (always needed for semantic search)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        sys.stderr.write("✅ ML model loaded successfully\n")
        sys.stderr.flush()
        
        # Load LLM for insight generation (optional)
        self.llm = None
        self.use_llm = use_llm and LLAMA_AVAILABLE
        
        if self.use_llm:
            try:
                sys.stderr.write("🤖 Loading GGUF model for LLM insights...\n")
                sys.stderr.flush()
                
                # Get model path from environment or use default
                resources_path = os.getenv("RESOURCES_PATH", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                model_path = os.path.join(resources_path, "backend", "scripts", "models", "gemma-2b-Q4_K_M.gguf")
                
                if not os.path.exists(model_path):
                    sys.stderr.write(f"⚠️  GGUF model not found at: {model_path}\n")
                    sys.stderr.write("⚠️  Falling back to template-based insights.\n")
                    sys.stderr.flush()
                    self.use_llm = False
                else:
                    self.llm = Llama(
                        model_path=model_path,
                        n_ctx=2048,  # Context window
                        n_threads=4,  # CPU threads
                        n_gpu_layers=0,  # Use 0 for CPU-only, increase if GPU available
                        verbose=False,
                    )
                    sys.stderr.write("✅ LLM loaded successfully (RAG mode enabled)\n")
                    sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"⚠️  Failed to load LLM: {e}\n")
                sys.stderr.write("⚠️  Falling back to template-based insights.\n")
                sys.stderr.flush()
                self.llm = None
                self.use_llm = False
        else:
            sys.stderr.write("📝 Using template-based insights (LLM disabled)\n")
            sys.stderr.flush()

    def analyze_entry(
        self, new_entry_text: str, past_entries: List[Dict], mood_rating: int = 3
    ) -> Dict:
        """Analyze a new journal entry with multi-factor composite scoring."""
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
                new_embedding, past_entries, top_k=5
            )
            sys.stderr.write(f"📊 Found {len(similar_entries)} similar entries\n")
            sys.stderr.flush()
        else:
            sys.stderr.write("🔭 No past entries to compare (first entry!)\n")
            sys.stderr.flush()

        # MULTI-FACTOR ANALYSIS

        # 1. Writing intensity analysis
        writing_intensity = self._analyze_writing_intensity(new_entry_text)
        sys.stderr.write(
            f"✍️  Writing intensity: {writing_intensity['intensity']} "
            f"({writing_intensity['word_count']} words)\n"
        )
        sys.stderr.flush()

        # 2. Nuanced sentiment detection
        sentiment = self._detect_nuanced_sentiment(new_entry_text)
        secondary_text = (
            f" + {sentiment['secondary_emotion']}" if sentiment["is_mixed"] else ""
        )
        sys.stderr.write(
            f"🎭 Emotional state: {sentiment['primary_emotion']}{secondary_text}\n"
        )
        sys.stderr.flush()

        # 3. Reflection depth analysis
        reflection = self._analyze_reflection_depth(new_entry_text)
        sys.stderr.write(
            f"🤔 Processing mode: {reflection['mode']} "
            f"({reflection['question_count']} questions asked)\n"
        )
        sys.stderr.flush()

        # 4. Theme analysis (existing + co-occurrence)
        summary = self._generate_summary_label(new_entry_text, mood_rating, sentiment)
        theme_context = None
        if len(past_entries) >= 3:
            theme_context = self._analyze_theme_cooccurrence(
                summary["themes"], past_entries
            )
            if theme_context:
                sys.stderr.write(
                    f"🔗 Theme pattern detected: {theme_context['combination']} "
                    f"(appears {theme_context['frequency']}x)\n"
                )
                sys.stderr.flush()

        # 5. Writing frequency analysis
        frequency_pattern = None
        if len(past_entries) >= 2:
            frequency_pattern = self._analyze_writing_frequency(past_entries)
            sys.stderr.write(f"📅 Writing pattern: {frequency_pattern['pattern']}\n")
            sys.stderr.flush()

        # 6. COMPOSITE MENTAL STATE SCORE
        mental_state = self._calculate_mental_state_score(
            mood_rating=mood_rating,
            writing_intensity=writing_intensity,
            sentiment=sentiment,
            reflection=reflection,
        )
        sys.stderr.write(
            f"🎯 Composite mental state: {mental_state['composite_score']}/5 "
            f"(mood rating: {mood_rating}/5)\n"
        )
        sys.stderr.flush()

        # Legacy mood field (kept for backwards compatibility)
        mood = {
            "detected": (
                "positive" if mental_state["composite_score"] >= 3 else "negative"
            ),
            "confidence": mental_state["confidence"],
        }

        # Generate insight with all available signals
        insight = self._generate_insight(
            new_entry_text=new_entry_text,
            similar_entries=similar_entries,
            mood_rating=mood_rating,
            mental_state=mental_state,
            writing_intensity=writing_intensity,
            sentiment=sentiment,
            reflection=reflection,
            theme_context=theme_context,
            frequency_pattern=frequency_pattern,
            all_past_entries=past_entries,
        )
        sys.stderr.write(f"💡 Generated multi-factor insight\n")
        sys.stderr.flush()

        return {
            "embedding": new_embedding,
            "insight": insight,
            "similar_entries": similar_entries[:3],
            "mood": mood,  # Legacy field
            "mental_state": mental_state,  # NEW: Composite score
            "summary": summary,
            "writing_intensity": writing_intensity,  # NEW
            "sentiment": sentiment,  # NEW
            "reflection": reflection,  # NEW
        }

    def _find_similar_entries(
        self, new_embedding: np.ndarray, past_entries: List[Dict], top_k: int = 5
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

    # ============== NEW: MULTI-FACTOR ANALYSIS METHODS ==============

    def _analyze_writing_intensity(self, text: str) -> Dict:
        """
        Analyze writing engagement through length and structure.

        Why it matters: Word count reveals emotional processing depth.
        - Short entries: Low energy, avoidance, or quick check-in
        - Long entries: Deep processing, crisis, or breakthrough
        """
        words = text.split()
        word_count = len(words)
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Categorize intensity
        if word_count > 400:
            intensity = "high"
            interpretation = "deep processing"
        elif word_count > 200:
            intensity = "medium"
            interpretation = "engaged reflection"
        elif word_count > 75:
            intensity = "moderate"
            interpretation = "standard check-in"
        else:
            intensity = "low"
            interpretation = "brief note"

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "intensity": intensity,
            "interpretation": interpretation,
        }

    def _detect_nuanced_sentiment(self, text: str) -> Dict:
        """
        Detect emotional nuance beyond binary positive/negative.

        Why it matters: "Anxious but hopeful" is very different from "anxious and defeated".
        Captures the complexity of human emotion.
        """
        emotion_refs = {
            "hopeful": [
                "feeling hopeful",
                "things might improve",
                "I'm optimistic",
                "looking forward",
            ],
            "defeated": ["giving up", "nothing works", "hopeless", "can't do this"],
            "anxious": ["worried", "nervous", "anxious", "scared", "afraid"],
            "calm": ["peaceful", "calm", "relaxed", "at ease", "tranquil"],
            "energized": ["motivated", "energized", "excited", "driven", "inspired"],
            "exhausted": ["tired", "drained", "exhausted", "burnt out", "depleted"],
            "grateful": ["thankful", "grateful", "blessed", "appreciate", "fortunate"],
            "angry": ["frustrated", "angry", "irritated", "furious", "mad"],
            "sad": ["sad", "depressed", "down", "unhappy", "miserable"],
            "content": ["content", "satisfied", "okay", "fine", "stable"],
        }

        text_embedding = self.model.encode(text).reshape(1, -1)

        emotion_scores = {}
        for emotion, refs in emotion_refs.items():
            ref_embeddings = self.model.encode(refs)
            similarity = cosine_similarity(text_embedding, ref_embeddings).mean()
            emotion_scores[emotion] = float(similarity)

        # Get top 2 emotions
        top_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)[
            :2
        ]

        primary = top_emotions[0][0]
        secondary = top_emotions[1][0] if len(top_emotions) > 1 else None

        # Check if emotions are mixed (similar scores)
        is_mixed = False
        if secondary and abs(top_emotions[0][1] - top_emotions[1][1]) < 0.08:
            is_mixed = True

        return {
            "primary_emotion": primary,
            "secondary_emotion": secondary,
            "is_mixed": is_mixed,
            "emotion_scores": emotion_scores,
            "top_score": top_emotions[0][1],
        }

    def _analyze_reflection_depth(self, text: str) -> Dict:
        """
        Measure active processing vs. passive venting.

        Why it matters: Questions and reflective language signal growth mindset.
        Venting without reflection can indicate being stuck.
        """
        # Count questions
        question_count = text.count("?")

        # Detect reflective language
        reflective_phrases = [
            "i wonder",
            "i realize",
            "i realized",
            "i noticed",
            "i learned",
            "maybe",
            "perhaps",
            "what if",
            "i think",
            "i believe",
            "i understand",
            "i see now",
            "looking back",
        ]

        text_lower = text.lower()
        reflection_count = sum(
            1 for phrase in reflective_phrases if phrase in text_lower
        )

        # Detect venting/stuck language
        venting_phrases = [
            "i hate",
            "i can't",
            "i cant",
            "nothing",
            "never works",
            "always",
            "why does",
            "why do",
            "sick of",
            "so tired of",
        ]

        venting_count = sum(1 for phrase in venting_phrases if phrase in text_lower)

        # Determine mode
        if reflection_count > venting_count and question_count > 0:
            mode = "active_processing"
        elif reflection_count > venting_count:
            mode = "reflecting"
        elif venting_count > reflection_count * 2:
            mode = "venting"
        else:
            mode = "mixed"

        return {
            "mode": mode,
            "question_count": question_count,
            "reflection_markers": reflection_count,
            "venting_markers": venting_count,
            "processing_ratio": reflection_count / max(venting_count, 1),
        }

    def _analyze_theme_cooccurrence(
        self, current_themes: List[str], past_entries: List[Dict]
    ) -> Optional[Dict]:
        """
        Find which themes appear together and what that predicts.

        Why it matters: "work" + "sleep" often = burnout.
        "anxiety" + "relationships" = social stress.
        Co-occurrence reveals underlying patterns.
        """
        if len(current_themes) < 2:
            return None

        # Build co-occurrence patterns from history
        cooccurrence = defaultdict(lambda: {"count": 0, "moods": []})

        for entry in past_entries:
            entry_text = entry.get("text", "")
            entry_mood = entry.get("mood", 3)

            # Quick theme detection for past entries (simplified)
            text_lower = entry_text.lower()
            entry_themes = []

            theme_keywords = {
                "work": ["work", "job", "meeting", "deadline", "project"],
                "sleep": ["sleep", "tired", "exhausted", "insomnia"],
                "anxiety": ["anxiety", "anxious", "worried", "stress"],
                "relationships": ["relationship", "partner", "friend", "family"],
                "exercise": ["exercise", "gym", "workout", "run"],
                "mental_health": ["therapy", "depression", "mental"],
            }

            for theme, keywords in theme_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    entry_themes.append(theme)

            # Track combinations
            if len(entry_themes) >= 2:
                # Sort for consistent key
                combo = "+".join(sorted(entry_themes[:2]))
                cooccurrence[combo]["count"] += 1
                cooccurrence[combo]["moods"].append(entry_mood)

        # Find relevant pattern for current entry
        current_combo_key = "+".join(sorted(current_themes[:2]))

        if current_combo_key in cooccurrence:
            data = cooccurrence[current_combo_key]
            if data["count"] >= 3:  # Significant pattern
                return {
                    "combination": current_combo_key.replace("+", " + "),
                    "frequency": data["count"],
                    "typical_mood": round(np.mean(data["moods"]), 1),
                }

        return None

    def _analyze_writing_frequency(self, past_entries: List[Dict]) -> Dict:
        """
        Understand the user's journaling rhythm and recent changes.

        Why it matters: Writing frequency reveals crisis vs. practice.
        - Daily entries for days = processing something urgent
        - Sporadic = reactive journaling (only writes when struggling)
        """
        if len(past_entries) < 2:
            return {"pattern": "new_user"}

        # Calculate days between entries
        timestamps = sorted(
            [datetime.fromisoformat(e["timestamp"]) for e in past_entries]
        )
        timestamps.append(datetime.now())  # Include current entry

        gaps = [
            (timestamps[i + 1] - timestamps[i]).days for i in range(len(timestamps) - 1)
        ]

        avg_gap = np.mean(gaps)

        # Classify pattern
        if avg_gap <= 1.5:
            pattern = "daily_practice"
            description = "writing almost daily"
        elif avg_gap <= 4:
            pattern = "regular_practice"
            description = "writing several times per week"
        elif avg_gap <= 10:
            pattern = "weekly_practice"
            description = "writing weekly"
        else:
            pattern = "reactive_journaling"
            description = "writing when needed"

        # Detect recent acceleration (writing more often lately)
        recent_gaps = gaps[-5:] if len(gaps) >= 5 else gaps
        is_accelerating = len(recent_gaps) >= 3 and np.mean(recent_gaps) < avg_gap * 0.5

        return {
            "pattern": pattern,
            "description": description,
            "avg_gap_days": round(avg_gap, 1),
            "is_accelerating": is_accelerating,
            "total_entries": len(past_entries) + 1,
        }

    def _calculate_mental_state_score(
        self,
        mood_rating: int,
        writing_intensity: Dict,
        sentiment: Dict,
        reflection: Dict,
    ) -> Dict:
        """
        Calculate composite mental state score from multiple signals.

        WHY THIS MATTERS:
        A user might rate themselves 3/5, but if they're:
        - Writing long, engaged entries (+)
        - Asking reflective questions (+)
        - Processing rather than venting (+)

        Their composite score might be 3.8/5 - they're doing better than they think!

        Conversely, a 4/5 with:
        - Very short entry (-)
        - Pure venting, no reflection (-)
        - Mixed, confused emotions (-)

        Might be a 3.2/5 - something's being suppressed.
        """
        score = float(mood_rating)
        adjustments = []

        # Factor 1: Writing engagement (± 0.5)
        if writing_intensity["intensity"] == "high":
            score += 0.5
            adjustments.append("deep engagement (+0.5)")
        elif writing_intensity["intensity"] == "moderate":
            score += 0.1
            adjustments.append("moderate engagement (+0.1)")
        elif writing_intensity["intensity"] == "low":
            score -= 0.3
            adjustments.append("brief entry (-0.3)")

        # Factor 2: Reflection mode (± 0.4)
        if reflection["mode"] == "active_processing":
            score += 0.4
            adjustments.append("active processing (+0.4)")
        elif reflection["mode"] == "reflecting":
            score += 0.2
            adjustments.append("reflective mode (+0.2)")
        elif reflection["mode"] == "venting":
            score -= 0.3
            adjustments.append("venting mode (-0.3)")

        # Factor 3: Emotional clarity (± 0.2)
        if sentiment["is_mixed"]:
            score -= 0.2
            adjustments.append("mixed emotions (-0.2)")
        elif sentiment["primary_emotion"] in ["hopeful", "grateful", "content", "calm"]:
            score += 0.2
            adjustments.append(f"{sentiment['primary_emotion']} (+0.2)")
        elif sentiment["primary_emotion"] in ["defeated", "exhausted"]:
            score -= 0.2
            adjustments.append(f"{sentiment['primary_emotion']} (-0.2)")

        # Factor 4: Question-asking (curiosity signal) (± 0.1)
        if reflection["question_count"] >= 3:
            score += 0.1
            adjustments.append("asking questions (+0.1)")

        # Normalize to 1-5 scale
        score = max(1.0, min(5.0, score))

        # Calculate confidence based on how much data we have
        confidence = min(0.85, 0.5 + (len(adjustments) * 0.1))

        is_different = abs(score - mood_rating) >= 0.5

        return {
            "composite_score": round(score, 1),
            "mood_rating": mood_rating,
            "is_different_from_mood": is_different,
            "adjustments": adjustments,
            "confidence": confidence,
            "interpretation": self._interpret_composite_score(
                score, mood_rating, adjustments
            ),
        }

    def _interpret_composite_score(
        self, composite: float, mood_rating: int, adjustments: List[str]
    ) -> str:
        """Generate human-readable interpretation of composite score."""
        diff = composite - mood_rating

        if abs(diff) < 0.3:
            return "Your self-assessment aligns with your overall state"
        elif diff > 0.5:
            return "You're doing better than your mood rating suggests"
        elif diff < -0.5:
            return "There may be underlying challenges beyond your mood rating"
        else:
            return "Your overall state is close to your mood rating"

    # ============== LEGACY SENTIMENT (kept for backwards compatibility) ==============

    def _detect_sentiment(self, text: str) -> Dict:
        """Legacy sentiment detection - now just calls nuanced version."""
        sentiment = self._detect_nuanced_sentiment(text)

        # Convert to legacy format
        positive_emotions = {"hopeful", "calm", "energized", "grateful", "content"}
        detected = (
            "positive"
            if sentiment["primary_emotion"] in positive_emotions
            else "negative"
        )

        return {
            "detected": detected,
            "confidence": sentiment["top_score"],
        }

    # ============== SUMMARY LABEL (unchanged) ==============

    def _generate_summary_label(
        self, text: str, mood_rating: int, sentiment: Dict
    ) -> Dict:
        """Generate a summary label for timeline display."""
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

        text_lower = text.lower()
        detected_themes = []

        for theme, keywords in theme_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)

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

        # Use nuanced sentiment if available
        if isinstance(sentiment, dict) and "primary_emotion" in sentiment:
            primary = sentiment["primary_emotion"]
            if sentiment.get("is_mixed") and sentiment.get("secondary_emotion"):
                emotion = f"{primary} and {sentiment['secondary_emotion']}"
            else:
                emotion = primary

        primary_theme = detected_themes[0].replace("_", " ").title()

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

        if not title_subject:
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

        if title_subject:
            title = f"{primary_theme} - {title_subject}"
        else:
            title = f"{primary_theme} Reflection"

        return {
            "title": title,
            "themes": detected_themes[:3],
            "emotion": emotion,
        }

    # ============== ENHANCED INSIGHT GENERATION ==============

    def _generate_insight(
        self,
        new_entry_text: str,
        similar_entries: List[Dict],
        mood_rating: int,
        mental_state: Dict,
        writing_intensity: Dict,
        sentiment: Dict,
        reflection: Dict,
        theme_context: Optional[Dict],
        frequency_pattern: Optional[Dict],
        all_past_entries: List[Dict],
    ) -> str:
        """
        Generate deeply personalized insights.
        Routes to LLM-based RAG pipeline or template-based fallback.
        """
        
        # Route to LLM if available
        if self.use_llm:
            return self._generate_llm_insight(
                new_entry_text, similar_entries, mood_rating, mental_state,
                writing_intensity, sentiment, reflection, theme_context,
                frequency_pattern, all_past_entries
            )
        else:
            # Fallback to template-based insights
            return self._generate_insight_template(
                new_entry_text, similar_entries, mood_rating, mental_state,
                writing_intensity, sentiment, reflection, theme_context,
                frequency_pattern, all_past_entries
            )

    def _generate_llm_insight(
        self,
        new_entry_text: str,
        similar_entries: List[Dict],
        mood_rating: int,
        mental_state: Dict,
        writing_intensity: Dict,
        sentiment: Dict,
        reflection: Dict,
        theme_context: Optional[Dict],
        frequency_pattern: Optional[Dict],
        all_past_entries: List[Dict],
    ) -> str:
        """
        Generate insight using RAG LLM pipeline.
        
        RAG Architecture:
        1. RETRIEVE: Use embeddings to find similar past entries (already done)
        2. AUGMENT: Build context-rich prompt with retrieved entries
        3. GENERATE: Use LLM to create personalized insight
        """
        
        if not self.use_llm or self.llm is None:
            # Fallback to template-based insights
            return self._generate_insight_template(
                new_entry_text, similar_entries, mood_rating, mental_state,
                writing_intensity, sentiment, reflection, theme_context,
                frequency_pattern, all_past_entries
            )
        
        # Build RAG prompt
        prompt = self._build_rag_prompt(
            new_entry_text=new_entry_text,
            similar_entries=similar_entries,
            mood_rating=mood_rating,
            mental_state=mental_state,
            writing_intensity=writing_intensity,
            sentiment=sentiment,
            reflection=reflection,
            theme_context=theme_context,
            frequency_pattern=frequency_pattern,
            entry_count=len(all_past_entries),
        )
        
        # Generate insight using LLM
        try:
            sys.stderr.write("🤖 Generating LLM insight...\n")
            sys.stderr.flush()
            
            response = self.llm(
                prompt,
                max_tokens=300,
                temperature=0.7,
                top_p=0.9,
                stop=["User:", "Assistant:", "\n\n\n"],
                echo=False,
            )
            
            insight = response["choices"][0]["text"].strip()
            
            sys.stderr.write(f"✅ LLM insight generated ({len(insight)} chars)\n")
            sys.stderr.flush()
            
            return insight
            
        except Exception as e:
            sys.stderr.write(f"⚠️  LLM generation failed: {e}\n")
            sys.stderr.write("⚠️  Falling back to template-based insight.\n")
            sys.stderr.flush()
            
            # Fallback to templates
            return self._generate_insight_template(
                new_entry_text, similar_entries, mood_rating, mental_state,
                writing_intensity, sentiment, reflection, theme_context,
                frequency_pattern, all_past_entries
            )

    def _build_rag_prompt(
        self,
        new_entry_text: str,
        similar_entries: List[Dict],
        mood_rating: int,
        mental_state: Dict,
        writing_intensity: Dict,
        sentiment: Dict,
        reflection: Dict,
        theme_context: Optional[Dict],
        frequency_pattern: Optional[Dict],
        entry_count: int,
    ) -> str:
        """
        Build a context-rich prompt for the LLM using retrieved entries.
        
        This is the "Augmented" part of RAG - we provide the LLM with:
        1. User's current entry
        2. Retrieved similar past entries (semantic search)
        3. Analytical context (mood, patterns, themes)
        """
        
        # Format similar entries as context
        context_entries = []
        if similar_entries:
            for i, entry in enumerate(similar_entries[:3], 1):
                time_ago = self._format_time_ago(entry["timestamp"])
                context_entries.append(
                    f"Past Entry #{i} ({time_ago}, mood: {entry.get('mood', 3)}/5, "
                    f"{int(entry['similarity']*100)}% similar):\n\"{entry['text'][:200]}...\""
                )
        
        context_block = "\n\n".join(context_entries) if context_entries else "No similar past entries found."
        
        # Build analytical context
        composite = mental_state["composite_score"]
        composite_diff = composite - mood_rating
        
        analysis_context = f"""
Current Analysis:
- User's mood rating: {mood_rating}/5
- Composite mental state: {composite}/5 (AI-analyzed from multiple signals)
- Primary emotion: {sentiment['primary_emotion']}
- Secondary emotion: {sentiment.get('secondary_emotion', 'none')}
- Writing intensity: {writing_intensity['intensity']} ({writing_intensity['word_count']} words)
- Processing mode: {reflection['mode']} ({reflection['question_count']} questions asked)
- Entry count: #{entry_count + 1}
"""
        
        # Add pattern context if available
        if theme_context:
            analysis_context += f"- Recurring theme pattern: {theme_context['combination']} (appears {theme_context['frequency']}x)\n"
        
        if frequency_pattern:
            analysis_context += f"- Writing pattern: {frequency_pattern['pattern']}\n"
        
        # Special insights
        insights_to_mention = []
        if abs(composite_diff) >= 0.7:
            if composite_diff > 0:
                insights_to_mention.append(f"The user rated themselves {mood_rating}/5, but their actual state seems better ({composite}/5). They may be being too hard on themselves.")
            else:
                insights_to_mention.append(f"The user rated themselves {mood_rating}/5, but their actual state may be more challenging ({composite}/5). They might be masking their struggles.")
        
        if sentiment.get("is_mixed"):
            insights_to_mention.append(f"The user is experiencing mixed emotions: {sentiment['primary_emotion']} and {sentiment['secondary_emotion']}.")
        
        special_insights = "\n- ".join(insights_to_mention) if insights_to_mention else "None"
        
        # Build the full prompt
        prompt = f"""You are a compassionate journaling companion helping someone process their emotions. You have access to their current journal entry and past similar entries.

## Retrieved Past Entries (Most Similar):
{context_block}

## Current Journal Entry:
"{new_entry_text}"

{analysis_context}

## Special Insights to Consider:
- {special_insights}

TASK:
Analyze connections between the current entry and past entries. Identify:

1. **Recurring Themes**: Topics, concerns, or situations that appear across entries
2. **Behavioral Patterns**: Repeated actions, reactions, or coping mechanisms
3. **Emotional Trajectories**: How feelings about similar situations have evolved
4. **Cognitive Patterns**: Thought processes, decision-making styles, or mental frameworks
5. **Progress Indicators**: Growth, stagnation, or regression in specific areas
6. **Blind Spots**: Patterns the writer may not be aware of

GUIDELINES:
- Be specific, citing dates and examples
- Note both positive patterns and areas for reflection
- Avoid being judgmental; focus on observation
- Highlight growth and positive changes
- Ask thought-provoking questions when appropriate
- Keep insights actionable

Talk to the person Provide 3-5 key insights, prioritizing the most meaningful patterns. Do not make insights up if there are no past similar entries.

Be conversational, empathetic, and specific to their experiences. Avoid generic advice.

In the first paragraph, state all of the context you were given. In the second paragraph, tell the user the patterns you have found."""

        return prompt

    def _generate_insight_template(
        self,
        new_entry_text: str,
        similar_entries: List[Dict],
        mood_rating: int,
        mental_state: Dict,
        writing_intensity: Dict,
        sentiment: Dict,
        reflection: Dict,
        theme_context: Optional[Dict],
        frequency_pattern: Optional[Dict],
        all_past_entries: List[Dict],
    ) -> str:
        """
        Generate deeply personalized insights using template-based logic.
        This is the fallback when LLM is not available.
        """

        # Case 1: First entry
        if len(all_past_entries) == 0:
            return self._first_entry_insight()

        # Case 2: Early journey (fewer than 3 entries)
        if len(all_past_entries) < 3:
            return self._early_journey_insight(
                len(all_past_entries), mental_state, writing_intensity
            )

        # Case 3: Not enough similar entries for pattern detection
        if len(similar_entries) < 2:
            return self._sparse_pattern_insight(
                len(all_past_entries),
                mental_state,
                writing_intensity,
                sentiment,
                similar_entries,
            )

        # Case 4: Rich pattern analysis (3+ entries, 2+ similar matches)
        patterns = self._analyze_patterns(similar_entries, all_past_entries)

        # Priority 1: Composite score reveals hidden truth
        if mental_state["is_different_from_mood"]:
            return self._generate_composite_insight(
                mental_state,
                writing_intensity,
                reflection,
                sentiment,
                similar_entries,
                patterns,
            )

        # Priority 2: Theme co-occurrence pattern
        if theme_context:
            return self._generate_theme_cooccurrence_insight(
                theme_context, mental_state, similar_entries
            )

        # Priority 3: Writing frequency pattern
        if frequency_pattern and frequency_pattern.get("is_accelerating"):
            return self._generate_frequency_insight(
                frequency_pattern, mental_state, sentiment
            )

        # Priority 4: Growth narrative
        if patterns["has_growth_story"] or patterns["has_decline"]:
            return self._generate_growth_narrative(
                similar_entries, mental_state, patterns
            )

        # Priority 5: Temporal patterns
        if patterns["temporal_pattern"]:
            return self._generate_temporal_insight(
                patterns, similar_entries, mental_state
            )

        # Priority 6: Enhanced contextual comparison
        return self._generate_contextual_comparison(
            similar_entries, mental_state, patterns, reflection
        )

    def _analyze_patterns(
        self, similar_entries: List[Dict], all_entries: List[Dict]
    ) -> Dict:
        """Detect patterns across multiple entries for personalization."""

        # Temporal clustering
        timestamps = [datetime.fromisoformat(e["timestamp"]) for e in similar_entries]
        weekdays = [t.strftime("%A") for t in timestamps]
        weekday_counts = Counter(weekdays)
        dominant_weekday = weekday_counts.most_common(1)[0] if weekday_counts else None

        # Mood trajectory analysis
        sorted_by_time = sorted(similar_entries, key=lambda x: x["timestamp"])
        moods = [e.get("mood", 3) for e in sorted_by_time]

        # Detect growth or decline
        has_growth = False
        has_decline = False
        if len(moods) >= 3:
            earliest_avg = np.mean(moods[:2])
            latest_avg = np.mean(moods[-2:])
            if latest_avg > earliest_avg + 0.5:
                has_growth = True
            elif latest_avg < earliest_avg - 0.5:
                has_decline = True

        # Extract user's personal phrases
        user_phrases = self._extract_key_phrases(all_entries)

        # Find action patterns in past entries
        actions_taken = self._extract_actions(similar_entries)

        return {
            "has_growth_story": has_growth,
            "has_decline": has_decline,
            "temporal_pattern": (
                dominant_weekday
                if dominant_weekday and dominant_weekday[1] >= 2
                else None
            ),
            "mood_trajectory": moods,
            "user_phrases": user_phrases,
            "actions_taken": actions_taken,
        }

    def _extract_key_phrases(
        self, entries: List[Dict], min_count: int = 2
    ) -> List[str]:
        """Extract frequently used 2-3 word phrases from user's entries."""
        if len(entries) < 3:
            return []

        all_text = " ".join([e["text"].lower() for e in entries])
        words = re.findall(r"\b\w+\b", all_text)

        # Extract bigrams and trigrams
        phrases = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            phrases.append(bigram)

            if i < len(words) - 2:
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                phrases.append(trigram)

        phrase_counts = Counter(phrases)

        # Filter out generic phrases
        generic_stopwords = {
            "i feel",
            "i am",
            "i was",
            "i have",
            "i want",
            "i think",
            "i need",
            "i can",
            "i will",
            "i would",
            "i should",
            "it is",
            "it was",
            "to be",
            "in the",
            "of the",
            "and i",
        }

        meaningful_phrases = [
            phrase
            for phrase, count in phrase_counts.items()
            if count >= min_count
            and phrase not in generic_stopwords
            and len(phrase) > 5
        ]

        return meaningful_phrases[:5]

    def _extract_actions(self, entries: List[Dict]) -> List[str]:
        """Extract action-oriented phrases (what user did in past to cope/improve)."""
        actions = []

        action_patterns = [
            r"talked to (\w+)",
            r"went for a (\w+)",
            r"decided to ([\w\s]{3,20})",
            r"started ([\w\s]{3,20})",
            r"tried ([\w\s]{3,20})",
            r"called (\w+)",
            r"reached out to (\w+)",
        ]

        for entry in entries:
            text = entry["text"].lower()
            for pattern in action_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    action = match.strip()
                    if len(action) > 2:
                        actions.append(action)

        return list(set(actions))[:3]

    def _extract_meaningful_quote(
        self, text: str, prioritize_actions: bool = False
    ) -> str:
        """Extract the most meaningful sentence(s) from a past entry."""
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        if len(sentences) == 0:
            return text[:200]

        # Score sentences by meaningfulness
        scored_sentences = []

        action_keywords = [
            "decided",
            "tried",
            "started",
            "realized",
            "learned",
            "talked",
            "called",
            "went",
            "made",
            "chose",
        ]
        emotion_keywords = [
            "feel",
            "felt",
            "feeling",
            "emotion",
            "mood",
            "happy",
            "sad",
            "anxious",
            "relieved",
            "grateful",
        ]

        for sent in sentences:
            score = 0
            sent_lower = sent.lower()
            word_count = len(sent.split())

            # Prioritize action sentences
            if any(word in sent_lower for word in action_keywords):
                score += 4

            # Value emotional content
            if any(word in sent_lower for word in emotion_keywords):
                score += 2

            # Prefer substantial sentences (not too short, not too long)
            if 8 <= word_count <= 20:
                score += 2
            elif word_count > 20:
                score += 1

            scored_sentences.append((score, sent))

        # Sort by score and take best 1-2 sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])

        if len(scored_sentences) >= 2 and scored_sentences[0][0] > 0:
            best = [scored_sentences[0][1], scored_sentences[1][1]]
            quote = ". ".join(best) + "."
        else:
            quote = scored_sentences[0][1] + "."

        # Truncate if too long
        if len(quote) > 200:
            quote = quote[:197] + "..."

        return quote

    def _format_time_ago(self, timestamp: str) -> str:
        """Format timestamp as human-readable 'time ago' string."""
        ts = datetime.fromisoformat(timestamp)
        days_ago = (datetime.now() - ts).days

        if days_ago == 0:
            return "earlier today"
        elif days_ago == 1:
            return "yesterday"
        elif days_ago < 7:
            return f"{days_ago} days ago"
        elif days_ago < 30:
            weeks = days_ago // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days_ago < 365:
            months = days_ago // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = days_ago // 365
            return f"{years} year{'s' if years > 1 else ''} ago"

    # ============== NEW: COMPOSITE SCORE INSIGHT METHODS ==============

    def _generate_composite_insight(
        self,
        mental_state: Dict,
        writing_intensity: Dict,
        reflection: Dict,
        sentiment: Dict,
        similar_entries: List[Dict],
        patterns: Dict,
    ) -> str:
        """
        Generate insight when composite score reveals hidden truth.

        This is the MOST IMPACTFUL new feature - telling users they're doing
        better (or worse) than they think based on multiple signals.
        """
        composite = mental_state["composite_score"]
        mood_rating = mental_state["mood_rating"]
        diff = composite - mood_rating

        # Build context from past similar entries
        context = ""
        if len(similar_entries) > 0:
            most_similar = similar_entries[0]
            time_ago = self._format_time_ago(most_similar["timestamp"])
            context = f" {time_ago.capitalize()}, you felt similarly."

        if diff >= 0.7:
            # Composite score is MUCH better than mood rating
            # They're being too hard on themselves
            reasons = []
            if writing_intensity["intensity"] in ["high", "medium"]:
                reasons.append(
                    f"you're writing {writing_intensity['word_count']} words of engaged reflection"
                )
            if reflection["mode"] in ["active_processing", "reflecting"]:
                reasons.append(
                    f"you're asking yourself {reflection['question_count']} questions"
                )
            if sentiment["primary_emotion"] in ["hopeful", "grateful", "calm"]:
                reasons.append(f"your emotional tone is {sentiment['primary_emotion']}")

            reasons_text = (
                ", ".join(reasons)
                if reasons
                else "you're engaging deeply with your thoughts"
            )

            return (
                f"You rated yourself {mood_rating}/5, but your composite wellbeing score is {composite}/5. "
                f"Why the difference? Because {reasons_text}. "
                f"The number you gave yourself doesn't capture the work you're doing here.{context} "
                f"You're processing, not just surviving. That's growth."
            )

        elif diff >= 0.4:
            # Modestly better than mood rating
            return (
                f"You rated yourself {mood_rating}/5, but looking at the full picture—"
                f"your {writing_intensity['word_count']}-word entry, your {reflection['mode']} mode, "
                f"your {sentiment['primary_emotion']} emotional state—I'd say you're closer to {composite}/5. "
                f"{mental_state['interpretation']}.{context} "
                f"You're doing better than you might feel in this moment."
            )

        elif diff <= -0.7:
            # Composite score is MUCH worse than mood rating
            # Something's being suppressed or avoided
            warning_signs = []
            if writing_intensity["intensity"] == "low":
                warning_signs.append("this is a very brief entry")
            if reflection["mode"] == "venting":
                warning_signs.append("you're venting without reflection")
            if sentiment["is_mixed"]:
                warning_signs.append(
                    f"you're feeling both {sentiment['primary_emotion']} and {sentiment['secondary_emotion']}"
                )

            signs_text = (
                " and ".join(warning_signs)
                if warning_signs
                else "there are underlying signals"
            )

            return (
                f"You rated yourself {mood_rating}/5, but I'm noticing something beneath the surface. "
                f"Your composite score is {composite}/5 because {signs_text}. "
                f"{context} Sometimes we minimize our struggles. "
                f"What's being left unsaid here?"
            )

        elif diff <= -0.4:
            # Modestly worse than mood rating
            return (
                f"You rated yourself {mood_rating}/5, but reading between the lines—"
                f"the brevity of your words ({writing_intensity['word_count']} words), "
                f"the {sentiment['primary_emotion']} undertone—suggests you might be at {composite}/5. "
                f"{mental_state['interpretation']}. "
                f"What are you not letting yourself feel right now?"
            )

        else:
            # Should not reach here, but fallback
            return self._generate_contextual_comparison(
                similar_entries, mental_state, patterns, reflection
            )

    def _generate_theme_cooccurrence_insight(
        self,
        theme_context: Dict,
        mental_state: Dict,
        similar_entries: List[Dict],
    ) -> str:
        """Generate insight when theme co-occurrence pattern is detected."""

        combination = theme_context["combination"]
        frequency = theme_context["frequency"]
        typical_mood = theme_context["typical_mood"]

        most_similar = similar_entries[0]
        time_ago = self._format_time_ago(most_similar["timestamp"])
        quote = self._extract_meaningful_quote(most_similar["text"])

        composite = mental_state["composite_score"]

        return (
            f"I'm seeing a familiar pattern. When you write about {combination}, "
            f"it's happened {frequency} times before, and your typical state is around {typical_mood}/5. "
            f"Today you're at {composite}/5. {time_ago.capitalize()}, you wrote:\n"
            f'"{quote}"\n\n'
            f"This combination of themes tends to cluster together for you. "
            f"What is it about {combination.split(' + ')[0]} and {combination.split(' + ')[1]} "
            f"that brings them up at the same time? Understanding this connection might reveal something important."
        )

    def _generate_frequency_insight(
        self,
        frequency_pattern: Dict,
        mental_state: Dict,
        sentiment: Dict,
    ) -> str:
        """Generate insight when writing frequency has changed dramatically."""

        pattern = frequency_pattern["description"]
        total = frequency_pattern["total_entries"]
        composite = mental_state["composite_score"]

        return (
            f"You're entry #{total}, and I've noticed something: you've accelerated your writing recently. "
            f"Usually you're {pattern}, but lately you've been writing much more often. "
            f"This acceleration often signals you're processing something significant. "
            f"Today you're at {composite}/5 and feeling {sentiment['primary_emotion']}. "
            f"When you write this frequently, what's usually driving it? "
            f"What are you working through right now?"
        )

    def _generate_growth_narrative(
        self,
        similar_entries: List[Dict],
        mental_state: Dict,
        patterns: Dict,
    ) -> str:
        """Generate insight highlighting growth or decline trajectory."""

        sorted_entries = sorted(similar_entries, key=lambda x: x["timestamp"])
        earliest = sorted_entries[0]
        latest = sorted_entries[-1]

        earliest_time = self._format_time_ago(earliest["timestamp"])
        latest_time = self._format_time_ago(latest["timestamp"])

        earliest_mood = earliest.get("mood", 3)
        latest_mood = latest.get("mood", 3)
        composite = mental_state["composite_score"]

        # Extract meaningful quote from the journey
        quote = self._extract_meaningful_quote(
            earliest["text"], prioritize_actions=True
        )

        if patterns["has_growth_story"]:
            # User is improving over time
            if composite >= latest_mood:
                return (
                    f"You're making real progress with this. Looking at your journey:\n\n"
                    f"{earliest_time.capitalize()}, you were at {earliest_mood}/5 and wrote:\n"
                    f'"{quote}"\n\n'
                    f"{latest_time.capitalize()}, you reached {latest_mood}/5. "
                    f"Today your composite state is {composite}/5. "
                    f"This upward trajectory isn't luck—it's the result of how you're showing up for yourself. "
                    f"What's working for you?"
                )
            else:
                return (
                    f"You've navigated this before, and you've grown through it. {earliest_time.capitalize()}, "
                    f"you were at {earliest_mood}/5. By {latest_time}, you'd moved to {latest_mood}/5. "
                    f"Today feels like {composite}/5, a step back perhaps, but your history shows you know how to move forward. "
                    f"What helped you before?"
                )

        else:  # has_decline
            # User is struggling more over time
            if patterns["actions_taken"]:
                actions = ", ".join(patterns["actions_taken"][:2])
                return (
                    f"This theme has been more challenging lately. {earliest_time.capitalize()}, "
                    f"you were at {earliest_mood}/5. Now you're at {composite}/5. "
                    f"Looking back, I see you tried {actions}. "
                    f"Sometimes what worked before needs adjustment. What feels different now, "
                    f"and what might you need that you didn't before?"
                )
            else:
                return (
                    f"I notice this has been weighing on you more over time. "
                    f"{earliest_time.capitalize()} you wrote:\n"
                    f'"{quote}"\n\n'
                    f"You were at {earliest_mood}/5 then, and you're at {composite}/5 now. "
                    f"The fact that you keep showing up to write about this shows strength. "
                    f"What support do you need right now?"
                )

    def _generate_temporal_insight(
        self,
        patterns: Dict,
        similar_entries: List[Dict],
        mental_state: Dict,
    ) -> str:
        """Generate insight about temporal patterns."""

        weekday, count = patterns["temporal_pattern"]
        most_similar = similar_entries[0]
        time_ago = self._format_time_ago(most_similar["timestamp"])
        composite = mental_state["composite_score"]

        quote = self._extract_meaningful_quote(most_similar["text"])

        if count >= 3:
            pattern_strength = "consistently"
        else:
            pattern_strength = "often"

        return (
            f"I'm noticing a pattern: you {pattern_strength} write about this on {weekday}s. "
            f"{time_ago.capitalize()}, you wrote:\n"
            f'"{quote}"\n\n'
            f"Today you're at {composite}/5. Is there something about {weekday}s "
            f"that brings this up? Sometimes awareness of timing reveals what triggers these feelings."
        )

    def _generate_contextual_comparison(
        self,
        similar_entries: List[Dict],
        mental_state: Dict,
        patterns: Dict,
        reflection: Dict,
    ) -> str:
        """Enhanced single-entry comparison with added context."""

        most_similar = similar_entries[0]
        time_ago = self._format_time_ago(most_similar["timestamp"])
        past_mood = most_similar.get("mood", 3)
        composite = mental_state["composite_score"]

        # Extract meaningful quote
        quote = self._extract_meaningful_quote(
            most_similar["text"], prioritize_actions=(past_mood >= 3 and composite < 3)
        )

        # Add personalization from user's phrases if available
        personalization = ""
        if patterns.get("user_phrases"):
            phrase = patterns["user_phrases"][0]
            personalization = f"I notice you often write about '{phrase}'. "

        # Determine tone based on composite score
        if composite < 3:
            # Current state is difficult
            if past_mood < 3:
                # Both entries are difficult
                if patterns.get("actions_taken"):
                    action = patterns["actions_taken"][0]
                    return (
                        f"{personalization}You've felt this way before. {time_ago.capitalize()}, "
                        f"you were also at {past_mood}/5 and wrote:\n"
                        f'"{quote}"\n\n'
                        f"I see that in the past you {action}. Did that help? "
                        f"Today you're at {composite}/5. Do you need to try something different this time?"
                    )
                else:
                    return (
                        f"{personalization}This feeling is familiar. {time_ago.capitalize()}, "
                        f"you wrote:\n"
                        f'"{quote}"\n\n'
                        f"You were at {past_mood}/5 then, and {composite}/5 now. "
                        f"What did you need then? Is it the same now, or has something shifted?"
                    )
            else:
                # Past was better, now struggling
                return (
                    f"{personalization}You've been in a better place with this before. "
                    f"{time_ago.capitalize()}, you were at {past_mood}/5 and wrote:\n"
                    f'"{quote}"\n\n'
                    f"Today you're at {composite}/5. You've navigated this territory before. "
                    f"What was different then that supported you?"
                )
        else:
            # Current state is positive or neutral
            if past_mood >= 4:
                # Both entries are positive
                return (
                    f"{personalization}This positive feeling is becoming a pattern! "
                    f"{time_ago.capitalize()}, you were at {past_mood}/5 and wrote:\n"
                    f'"{quote}"\n\n'
                    f"Today you're at {composite}/5. You're learning what works for you. "
                    f"What are the common threads between then and now?"
                )
            else:
                # Growth from difficult to positive
                return (
                    f"{personalization}Look at how far you've come. {time_ago.capitalize()}, "
                    f"you were at {past_mood}/5 and wrote:\n"
                    f'"{quote}"\n\n'
                    f"Today you're at {composite}/5. That's real progress. "
                    f"What changed? Understanding this can help you recreate it when you need it."
                )

    # ============== BASIC INSIGHT METHODS (simplified, use composite score) ==============

    def _first_entry_insight(self) -> str:
        """Welcoming message for the very first entry."""
        return (
            "Welcome to your journaling journey! This is your first entry. "
            "As you continue writing, I'll analyze not just your mood, but how you're writing—"
            "your engagement level, emotional complexity, and processing style. "
            "Together, these create a complete picture of your mental state over time. "
            "Every entry is a step toward deeper self-understanding."
        )

    def _early_journey_insight(
        self, entry_count: int, mental_state: Dict, writing_intensity: Dict
    ) -> str:
        """Encouraging message for entries 2-3."""
        composite = mental_state["composite_score"]
        interpretation = mental_state["interpretation"]

        if composite >= 3.5:
            return (
                f"You're building a meaningful practice. This is entry #{entry_count + 1}. "
                f"Your composite wellbeing score is {composite}/5—{interpretation.lower()}. "
                f"I'm tracking not just your mood, but your writing patterns, emotional complexity, "
                f"and how you process thoughts. Keep going, patterns will emerge."
            )
        else:
            return (
                f"Thank you for showing up, even when things are difficult. "
                f"This is entry #{entry_count + 1}. Your composite score is {composite}/5. "
                f"You wrote {writing_intensity['word_count']} words today—"
                f"that act of putting feelings into words is powerful. "
                f"Keep going. Insights will emerge as your journal grows."
            )

    def _sparse_pattern_insight(
        self,
        entry_count: int,
        mental_state: Dict,
        writing_intensity: Dict,
        sentiment: Dict,
        similar_entries: List[Dict],
    ) -> str:
        """Insight when not enough similar entries exist."""
        composite = mental_state["composite_score"]

        if len(similar_entries) == 1:
            most_similar = similar_entries[0]
            time_ago = self._format_time_ago(most_similar["timestamp"])

            return (
                f"This reminds me of something you wrote {time_ago}. "
                f"You're at entry #{entry_count + 1} now (composite score: {composite}/5). "
                f"Themes are starting to emerge. A few more entries and I'll be able to show you "
                f"deeper patterns in how you process these experiences."
            )
        else:
            if composite >= 3.5:
                return (
                    f"Entry #{entry_count + 1}. Your composite score is {composite}/5—"
                    f"you're {sentiment['primary_emotion']} and writing with {writing_intensity['intensity']} engagement. "
                    f"This is a fresh perspective compared to recent entries. These shifts are worth noticing."
                )
            else:
                return (
                    f"Entry #{entry_count + 1}. I can sense you're processing something new here. "
                    f"Your composite score is {composite}/5, shaped by your {sentiment['primary_emotion']} state "
                    f"and {writing_intensity['interpretation']}. "
                    f"As you continue, connections to past experiences may reveal themselves."
                )
