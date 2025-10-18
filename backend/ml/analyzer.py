"""
ML Analyzer for Introspect - Pattern Recognition in Journal Entries

This module handles:
1. Generating embeddings for new entries
2. Finding semantically similar past entries
3. Detecting sentiment/mood
4. Generating contextual insights based on patterns

INTEGRATION:
- Called by electron_bridge.py when user submits entry
- Receives past entries from database (with cached embeddings)
- Returns analysis results back to Electron app
"""

import sys
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from datetime import datetime


class Analyzer:
    """
    ML-powered journal entry analyzer.

    WHY THIS ARCHITECTURE?
    - Model loaded once at startup (not per-entry)
    - Uses cached embeddings from database (fast!)
    - Runs in Python subprocess (Electron integration)
    - 100% offline (no API calls)

    MODELS USED:
    - all-MiniLM-L6-v2: Fast, accurate sentence embeddings (384 dimensions)
    - Size: ~80MB, Speed: ~1 second per entry
    - Perfect balance for offline desktop app
    """

    def __init__(self):
        """
        Initialize the analyzer with ML model.

        This loads the sentence transformer model once.
        Model is cached, so subsequent calls are fast.
        """
        sys.stderr.write("🔄 Loading ML model...\n")
        sys.stderr.flush()

        # Load sentence transformer for embeddings
        # all-MiniLM-L6-v2: Good balance of speed and accuracy
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        sys.stderr.write("✅ ML model loaded successfully\n")
        sys.stderr.flush()

    def analyze_entry(self, new_entry_text: str, past_entries: List[Dict]) -> Dict:
        """
        Analyze a new journal entry by comparing to past entries.

        WORKFLOW:
        1. Generate embedding for new entry (semantic representation)
        2. Compare to past entries using cosine similarity
        3. Find top 3 most similar entries (patterns!)
        4. Detect sentiment/mood
        5. Generate contextual insight based on patterns

        Args:
            new_entry_text: The new journal entry (e.g., "I feel anxious about tomorrow")
            past_entries: List from database, each with:
                {
                    'text': str,              # Past entry content
                    'embedding': np.ndarray,  # Shape (384,) - already computed!
                    'timestamp': str          # ISO format datetime
                }

        Returns:
            {
                'embedding': np.ndarray,      # Shape (384,) for the NEW entry
                'insight': str,               # Human-readable pattern insight
                'similar_entries': [          # Top 3 most similar past entries
                    {
                        'text': str,
                        'similarity': float,  # 0-1 (1 = identical)
                        'timestamp': str
                    }
                ],
                'mood': {
                    'detected': str,          # 'positive' or 'negative'
                    'confidence': float       # 0-1
                }
            }
        """
        sys.stderr.write(f"🧠 Analyzing entry: '{new_entry_text[:50]}...'\n")
        sys.stderr.flush()

        # Step 1: Generate embedding for new entry
        new_embedding = self.model.encode(new_entry_text)

        sys.stderr.write(f"✅ Generated embedding (shape: {new_embedding.shape})\n")
        sys.stderr.flush()

        # Step 2: Find similar past entries (if any exist)
        similar_entries = []
        if len(past_entries) > 0:
            similar_entries = self._find_similar_entries(
                new_embedding, past_entries, top_k=3
            )
            sys.stderr.write(f"📊 Found {len(similar_entries)} similar entries\n")
            sys.stderr.flush()
        else:
            sys.stderr.write("📭 No past entries to compare (first entry!)\n")
            sys.stderr.flush()

        # Step 3: Detect sentiment/mood
        mood = self._detect_sentiment(new_entry_text)
        sys.stderr.write(
            f"😊 Detected mood: {mood['detected']} (confidence: {mood['confidence']:.2f})\n"
        )
        sys.stderr.flush()

        # Step 4: Generate contextual insight
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
        }

    def _find_similar_entries(
        self, new_embedding: np.ndarray, past_entries: List[Dict], top_k: int = 3
    ) -> List[Dict]:
        """
        Find the most similar past entries using cosine similarity.

        SEMANTIC SIMILARITY:
        - Not keyword matching (finds similar *meaning*)
        - "I'm anxious" matches "I feel worried" (similar meaning)
        - Doesn't match "I'm not anxious" (opposite meaning)

        Args:
            new_embedding: Embedding of new entry (384,)
            past_entries: List of past entries with embeddings
            top_k: Number of similar entries to return

        Returns:
            List of similar entries sorted by similarity score
        """
        if len(past_entries) == 0:
            return []

        # Extract embeddings from past entries
        past_embeddings = np.array([entry["embedding"] for entry in past_entries])

        # Calculate cosine similarity between new entry and all past entries
        # Shape: (1, 384) vs (N, 384) → (N,) similarities
        similarities = cosine_similarity(new_embedding.reshape(1, -1), past_embeddings)[
            0
        ]

        # Get indices of top K most similar entries
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Build result list with similarity scores
        similar = []
        for idx in top_indices:
            similarity_score = float(similarities[idx])

            # Only include if similarity is meaningful (>0.3)
            # 0.3-0.5: Somewhat similar
            # 0.5-0.7: Similar
            # 0.7+: Very similar
            if similarity_score > 0.3:
                similar.append(
                    {
                        "text": past_entries[idx]["text"],
                        "similarity": similarity_score,
                        "timestamp": past_entries[idx]["timestamp"],
                    }
                )

        return similar

    def _detect_sentiment(self, text: str) -> Dict:
        """
        Detect sentiment/mood of the entry.

        APPROACH:
        Uses the sentence transformer embedding to detect sentiment.
        We compare the entry to positive/negative reference sentences.

        Alternative: Could use a dedicated sentiment model like:
        - transformers pipeline('sentiment-analysis')
        - But that requires another model download

        Args:
            text: Journal entry text

        Returns:
            {
                'detected': 'positive' or 'negative',
                'confidence': float (0-1)
            }
        """
        # Reference sentences for sentiment
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

        # Encode reference sentences
        text_embedding = self.model.encode(text).reshape(1, -1)
        positive_embeddings = self.model.encode(positive_refs)
        negative_embeddings = self.model.encode(negative_refs)

        # Calculate similarity to positive/negative references
        positive_sim = cosine_similarity(text_embedding, positive_embeddings).mean()
        negative_sim = cosine_similarity(text_embedding, negative_embeddings).mean()

        # Determine sentiment based on which is stronger
        if positive_sim > negative_sim:
            detected = "positive"
            # Confidence is the difference between positive and negative
            confidence = float((positive_sim - negative_sim + 1) / 2)
        else:
            detected = "negative"
            confidence = float((negative_sim - positive_sim + 1) / 2)

        # Clamp confidence to [0, 1]
        confidence = max(0.0, min(1.0, confidence))

        return {"detected": detected, "confidence": confidence}

    def _generate_insight(
        self,
        new_entry_text: str,
        similar_entries: List[Dict],
        mood: Dict,
        all_past_entries: List[Dict],
    ) -> str:
        """
        Generate a contextual insight based on patterns.

        INSIGHT TYPES:
        1. First entry: Welcome message
        2. Pattern recognition: "This is similar to when you..."
        3. Mood progression: "Your mood has been improving/declining"
        4. Encouragement: Based on past successes

        This is the "magic" - showing users patterns they didn't see.

        Args:
            new_entry_text: The new entry text
            similar_entries: Most similar past entries
            mood: Detected mood
            all_past_entries: All past entries (for trend analysis)

        Returns:
            Human-readable insight string
        """
        # Case 1: First entry ever
        if len(all_past_entries) == 0:
            return (
                f"Welcome to your journaling journey! This is your first entry. "
                f"As you write more, I'll help you spot patterns in your thoughts and emotions. "
                f"Detected mood: {mood['detected']}."
            )

        # Case 2: Pattern recognition (similar entries found)
        if len(similar_entries) > 0:
            most_similar = similar_entries[0]
            similarity_pct = int(most_similar["similarity"] * 100)

            # Parse timestamp to make it readable
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

            # Generate insight based on similarity and mood
            if mood["detected"] == "positive":
                if most_similar["similarity"] > 0.7:
                    insight = (
                        f"This feels similar to how you felt {time_phrase}. "
                        f"Pattern detected: {similarity_pct}% match to a past experience. "
                        f"It seems positive emotions around this theme are recurring. "
                        f"That's a good sign of consistency!"
                    )
                else:
                    insight = (
                        f"Your mood is {mood['detected']} today. "
                        f"I found a somewhat similar entry from {time_phrase} "
                        f"({similarity_pct}% match). You're experiencing similar situations "
                        f"but handling them positively."
                    )
            else:  # negative mood
                if most_similar["similarity"] > 0.7:
                    insight = (
                        f"I notice you had similar feelings {time_ago}. "
                        f"Pattern detected: {similarity_pct}% match. "
                        f"This seems to be a recurring challenge. Consider: "
                        f"What helped you move forward last time?"
                    )
                else:
                    insight = (
                        f"You're facing something difficult. "
                        f"I found a related experience from {time_phrase}, "
                        f"though not identical ({similarity_pct}% match). "
                        f"You've navigated tough situations before."
                    )

        # Case 3: No strong patterns, general encouragement
        else:
            entry_count = len(all_past_entries) + 1

            if mood["detected"] == "positive":
                insight = (
                    f"Great to see you in a {mood['detected']} state! "
                    f"This is entry #{entry_count}. Keep writing - "
                    f"patterns become clearer with more entries."
                )
            else:
                insight = (
                    f"I hear that things are challenging right now. "
                    f"This is entry #{entry_count} in your journal. "
                    f"Writing helps - keep going. Patterns will emerge."
                )

        return insight


# ============================================================================
# TESTING CODE - Run this file directly to test the analyzer
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing ML Analyzer")
    print("=" * 70 + "\n")

    # Initialize analyzer
    print("📦 Initializing analyzer...")
    analyzer = Analyzer()
    print()

    # Test 1: First entry (no past entries)
    print("📝 Test 1: First entry (no history)")
    print("-" * 70)
    result = analyzer.analyze_entry(
        new_entry_text="Today I feel anxious about my presentation tomorrow.",
        past_entries=[],
    )
    print(f"Embedding shape: {result['embedding'].shape}")
    print(
        f"Mood: {result['mood']['detected']} (confidence: {result['mood']['confidence']:.2f})"
    )
    print(f"Similar entries: {len(result['similar_entries'])}")
    print(f"Insight: {result['insight']}")
    print()

    # Test 2: Entry with past history
    print("📝 Test 2: Entry with similar past entry")
    print("-" * 70)

    # Create a fake past entry for testing
    past_text = "I was worried about the meeting but it went well after preparation."
    past_embedding = analyzer.model.encode(past_text)

    past_entries = [
        {
            "text": past_text,
            "embedding": past_embedding,
            "timestamp": "2025-10-10T10:30:00",
        }
    ]

    result = analyzer.analyze_entry(
        new_entry_text="Nervous about tomorrow's presentation. Need to prepare well.",
        past_entries=past_entries,
    )

    print(f"Embedding shape: {result['embedding'].shape}")
    print(
        f"Mood: {result['mood']['detected']} (confidence: {result['mood']['confidence']:.2f})"
    )
    print(f"Similar entries found: {len(result['similar_entries'])}")
    if result["similar_entries"]:
        print(f"  - Similarity: {result['similar_entries'][0]['similarity']:.2f}")
        print(f"  - Text: {result['similar_entries'][0]['text'][:60]}...")
    print(f"Insight: {result['insight']}")
    print()

    # Test 3: Positive entry
    print("📝 Test 3: Positive mood detection")
    print("-" * 70)
    result = analyzer.analyze_entry(
        new_entry_text="Amazing day! Everything went perfectly. I feel so grateful and happy.",
        past_entries=past_entries,
    )
    print(
        f"Mood: {result['mood']['detected']} (confidence: {result['mood']['confidence']:.2f})"
    )
    print(f"Insight: {result['insight']}")
    print()

    print("=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print("\n💡 Integration notes:")
    print("  • Analyzer loads model once (cached)")
    print("  • Each analysis takes ~1 second")
    print("  • Embeddings are shape (384,)")
    print("  • Works 100% offline")
    print("  • Ready for Electron integration!\n")
