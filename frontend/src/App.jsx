import { useState, useEffect } from "react";

// Helper functions for mood visualization
function getMoodEmoji(mood) {
  if (mood >= 4) return "😊";
  if (mood === 3) return "😐";
  return "😟";
}

function getMoodColor(mood) {
  if (mood >= 4) return "bg-emerald-500";
  if (mood === 3) return "bg-amber-500";
  return "bg-rose-500";
}

function getMoodGlow(mood) {
  if (mood >= 4) return "shadow-emerald-500/50";
  if (mood === 3) return "shadow-amber-500/50";
  return "shadow-rose-500/50";
}

// Pattern Timeline Component - Visual representation of emotional patterns
function PatternTimeline({ currentMood, similarEntries, currentContent }) {
  if (similarEntries.length === 0) return null;

  // Get the most similar entry
  const mostSimilar = similarEntries[0];

  // Calculate time difference
  const pastDate = new Date(mostSimilar.timestamp);
  const now = new Date();
  const daysAgo = Math.floor((now - pastDate) / (1000 * 60 * 60 * 24));

  // Format time phrase
  let timePhrase;
  if (daysAgo === 0) timePhrase = "Earlier today";
  else if (daysAgo === 1) timePhrase = "Yesterday";
  else if (daysAgo < 7) timePhrase = `${daysAgo} days ago`;
  else if (daysAgo < 30) timePhrase = `${Math.floor(daysAgo / 7)} weeks ago`;
  else timePhrase = `${Math.floor(daysAgo / 30)} months ago`;

  // Determine if pattern improved (for "next time" suggestion)
  const patternImproved = mostSimilar.mood < currentMood;

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mt-6">
      <h3 className="text-xl font-bold text-gray-900 mb-2">
        🔄 Pattern Detected
      </h3>
      <p className="text-sm text-gray-600 mb-6">
        You've experienced similar emotions before. Here's how it unfolded:
      </p>

      {/* Timeline visualization */}
      <div className="relative">
        {/* Connection line */}
        <div
          className="absolute top-8 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-200 via-indigo-300 to-purple-200"
          style={{ zIndex: 0 }}
        ></div>

        <div
          className="relative flex items-start justify-between"
          style={{ zIndex: 1 }}
        >
          {/* Past Entry */}
          <div className="flex flex-col items-center flex-1">
            <div
              className={`w-16 h-16 ${getMoodColor(
                mostSimilar.mood
              )} rounded-full 
                            flex items-center justify-center text-3xl shadow-lg
                            transform transition-transform hover:scale-110`}
            >
              {getMoodEmoji(mostSimilar.mood)}
            </div>
            <div className="mt-3 text-center">
              <p className="text-xs font-semibold text-gray-700">
                {timePhrase}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Mood: {mostSimilar.mood}/5
              </p>
              <p className="text-xs text-indigo-600 font-medium mt-1">
                {Math.round(mostSimilar.similarity * 100)}% similar
              </p>
            </div>
            {/* Quote from past entry */}
            <div className="mt-4 p-3 bg-purple-50 rounded-lg border-l-4 border-purple-300 max-w-xs">
              <p className="text-xs text-gray-700 italic">
                "{mostSimilar.text.split(".")[0]}..."
              </p>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex items-center justify-center px-4 pt-6">
            <div className="text-3xl text-indigo-400">→</div>
          </div>

          {/* Current Entry */}
          <div className="flex flex-col items-center flex-1">
            <div
              className={`w-16 h-16 ${getMoodColor(currentMood)} rounded-full 
                            flex items-center justify-center text-3xl shadow-lg
                            ring-4 ring-indigo-200 animate-pulse`}
            >
              {getMoodEmoji(currentMood)}
            </div>
            <div className="mt-3 text-center">
              <p className="text-xs font-semibold text-gray-700">Today</p>
              <p className="text-xs text-gray-500 mt-1">
                Mood: {currentMood}/5
              </p>
              <p className="text-xs text-indigo-600 font-medium mt-1">
                Current
              </p>
            </div>
            <div className="mt-4 p-3 bg-indigo-50 rounded-lg border-l-4 border-indigo-400 max-w-xs">
              <p className="text-xs text-gray-700 italic">
                "{currentContent.split(".")[0]}..."
              </p>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex items-center justify-center px-4 pt-6">
            <div className="text-3xl text-gray-300">→</div>
          </div>

          {/* Future/Hope */}
          <div className="flex flex-col items-center flex-1">
            <div
              className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 
                            rounded-full flex items-center justify-center text-3xl 
                            shadow-lg opacity-60"
            >
              {patternImproved ? "🌟" : "💪"}
            </div>
            <div className="mt-3 text-center">
              <p className="text-xs font-semibold text-gray-700">Next time?</p>
              <p className="text-xs text-gray-500 mt-1">
                {patternImproved ? "Pattern improving" : "What helps?"}
              </p>
            </div>
            <div className="mt-4 p-3 bg-green-50 rounded-lg border-l-4 border-green-400 max-w-xs">
              <p className="text-xs text-gray-700 font-medium">
                {patternImproved
                  ? "Your mood improved from last time! Keep doing what works."
                  : "What helped you move forward before?"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pattern count */}
      <div className="mt-6 pt-6 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600">
          💡 <span className="font-semibold">Pattern Recognition:</span> Similar
          emotions detected in your history. Reflecting on past experiences can
          guide current actions.
        </p>
      </div>
    </div>
  );
}

export default function App() {
  const [content, setContent] = useState("");
  const [mood, setMood] = useState(3);
  const [insight, setInsight] = useState(null);
  const [similar, setSimilar] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isElectron, setIsElectron] = useState(false);
  const [entries, setEntries] = useState([]);
  const [showTimeline, setShowTimeline] = useState(false);

  useEffect(() => {
    // Check if running in Electron
    setIsElectron(typeof window.electronAPI !== "undefined");

    // Listen for Python errors
    if (window.electronAPI) {
      window.electronAPI.onPythonError((error) => {
        console.error("Python error:", error);
        alert("Analysis failed: " + error);
        setIsAnalyzing(false);
      });
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (content.trim().length < 10) {
      alert("Please write at least 10 characters");
      return;
    }

    setIsAnalyzing(true);

    try {
      const response = await window.electronAPI.createEntry({
        content: content.trim(),
        mood_rating: mood,
      });

      // Enhanced debug logging
      console.log("=== FULL RESPONSE ===");
      console.log(JSON.stringify(response, null, 2));

      console.log("=== SIMILAR ENTRIES CHECK ===");
      console.log("Similar entries exist?", !!response.similar_entries);
      console.log("Similar entries length:", response.similar_entries?.length);

      if (response.similar_entries && response.similar_entries.length > 0) {
        console.log("First entry:", response.similar_entries[0]);
        console.log(
          "First entry has mood?",
          "mood" in response.similar_entries[0]
        );
        console.log("Mood value:", response.similar_entries[0].mood);
        console.log("Mood type:", typeof response.similar_entries[0].mood);
      }

      setInsight(response.insight);
      setSimilar(response.similar_entries || []);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to analyze entry. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleNewEntry = () => {
    setContent("");
    setMood(3);
    setInsight(null);
    setSimilar([]);
    setShowTimeline(false);
  };

  const loadTimeline = async () => {
    try {
      const result = await window.electronAPI.getEntries(20);
      setEntries(result.entries || []);
      setShowTimeline(true);
    } catch (error) {
      console.error("Error loading entries:", error);
    }
  };

  if (!isElectron) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Introspect</h1>
          <p className="text-gray-600 mb-2">
            This app requires Electron to run
          </p>
          <p className="text-sm text-gray-500">
            Please start the app using: npm start
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-emerald-800 mb-3">
            Introspect
          </h1>
          <p className="text-gray-600 mb-3">
            AI-powered pattern recognition in your journal entries
          </p>
          <div className="flex items-center justify-center gap-3 text-sm flex-wrap">
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span>✅</span>
              <span>Running Offline</span>
            </span>
            <span className="text-gray-300">•</span>
            <span className="text-gray-600">100% local processing</span>
            <span className="text-gray-300">•</span>
            <span className="text-gray-600">Privacy-first</span>
          </div>
        </header>

        {/* Main Content */}
        {!insight && !showTimeline ? (
          // Writing State
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-gray-900 text-sm font-semibold mb-3">
                  What's on your mind?
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Write freely... I'll help you spot patterns in your thoughts and emotions."
                  className="w-full h-48 px-4 py-3 bg-gray-50 border-2 border-gray-300 rounded-xl 
                           focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500
                           resize-none text-gray-900 placeholder-gray-400
                           transition-all duration-200"
                  disabled={isAnalyzing}
                />
                <p className="text-sm text-gray-500 mt-2">
                  {content.length} characters{" "}
                  {content.length < 10 && "(minimum 10)"}
                </p>
              </div>

              {/* Mood Rating */}
              <div className="mb-6">
                <label className="block text-gray-900 text-sm font-semibold mb-3">
                  How are you feeling? ({mood}/5)
                </label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((num) => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setMood(num)}
                      className={`
                        flex-1 py-3 rounded-xl font-semibold transition-all duration-200
                        ${
                          mood === num
                            ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 scale-105"
                            : "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300"
                        }
                      `}
                    >
                      {num}
                    </button>
                  ))}
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-2 px-1">
                  <span>Struggling</span>
                  <span>Great</span>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isAnalyzing || content.length < 10}
                className="w-full bg-emerald-600 text-white py-4 rounded-xl
                         font-bold hover:bg-emerald-700 hover:shadow-lg transition-all duration-200
                         disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none
                         transform hover:scale-[1.02]"
              >
                {isAnalyzing ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    <span>Analyzing patterns...</span>
                  </span>
                ) : (
                  "🌱 Find Patterns"
                )}
              </button>

              {isAnalyzing && (
                <p className="text-sm text-gray-500 text-center mt-3">
                  All AI processing happens locally on this device • No data
                  sent to cloud
                </p>
              )}
            </form>

            {/* Timeline Button */}
            <button
              onClick={loadTimeline}
              className="w-full mt-4 bg-gray-100 text-gray-700 py-3 rounded-xl border border-gray-300
                       font-semibold hover:bg-gray-200 transition-all duration-200"
            >
              📚 View Past Entries
            </button>
          </div>
        ) : showTimeline ? (
          // Timeline View with Summary Support
          <div>
            <button
              onClick={() => setShowTimeline(false)}
              className="mb-4 text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-2"
            >
              ← Back to writing
            </button>

            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Your Journal Timeline
              </h2>

              {entries.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No entries yet. Start writing!
                </p>
              ) : (
                <div className="space-y-4">
                  {entries.map((entry, idx) => (
                    <details
                      key={entry.id || idx}
                      className="border-l-4 border-emerald-600 pl-4 py-3 hover:bg-gray-50
                               rounded-r-lg transition-colors duration-200 cursor-pointer group"
                    >
                      <summary className="cursor-pointer list-none">
                        {/* Show summary if available, otherwise fallback to text preview */}
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-gray-900 font-semibold group-hover:text-emerald-600 transition-colors">
                            {entry.summary?.title ||
                              entry.content.substring(0, 80)}
                            {!entry.summary &&
                              entry.content.length > 80 &&
                              "..."}
                          </h3>
                          <span className="text-xs text-emerald-600">▼</span>
                        </div>

                        {/* Show themes and emotion if summary exists */}
                        {entry.summary && (
                          <div className="flex items-center gap-2 text-xs mb-2 flex-wrap">
                            {entry.summary.themes.map((theme, i) => (
                              <span
                                key={i}
                                className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full font-medium"
                              >
                                {theme.replace("_", " ")}
                              </span>
                            ))}
                            <span className="text-gray-400">•</span>
                            <span className="text-gray-600 italic">
                              {entry.summary.emotion}
                            </span>
                          </div>
                        )}

                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="font-semibold flex items-center gap-1">
                            Mood: {entry.mood || entry.mood_rating}/5
                            <span className="text-base">
                              {getMoodEmoji(entry.mood || entry.mood_rating)}
                            </span>
                          </span>
                          <span>•</span>
                          <span>
                            {new Date(entry.timestamp).toLocaleDateString(
                              "en-US",
                              {
                                month: "short",
                                day: "numeric",
                                year: "numeric",
                              }
                            )}
                          </span>
                        </div>
                      </summary>

                      {/* Full content when expanded */}
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                          {entry.content}
                        </p>
                      </div>
                    </details>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          // Insight State
          <div className="space-y-6">
            {/* Main Insight */}
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
              <div className="flex items-start gap-4 mb-4">
                <div
                  className="w-12 h-12 bg-emerald-600 rounded-full 
                              flex items-center justify-center flex-shrink-0 shadow-lg"
                >
                  <span className="text-2xl">💡</span>
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-gray-900 mb-3">
                    Pattern Detected
                  </h2>
                  {/* Preserve line breaks and format quotes */}
                  <div className="text-gray-700 leading-relaxed text-lg whitespace-pre-wrap">
                    {insight}
                  </div>
                  <p className="text-sm text-gray-500 mt-4 italic bg-gray-50 p-3 rounded-lg border-l-4 border-emerald-600">
                    💭 This insight is based on your own past entries, not
                    generic advice
                  </p>
                </div>
              </div>
            </div>

            {/* NEW: Pattern Timeline Visualization */}
            <PatternTimeline
              currentMood={mood}
              similarEntries={similar}
              currentContent={content}
            />

            {/* Similar Entries - Now collapsible/secondary */}
            {similar.length > 0 && (
              <details className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
                <summary className="text-lg font-bold text-gray-900 mb-2 cursor-pointer hover:text-emerald-600 transition-colors">
                  📖 View All Similar Entries ({similar.length})
                </summary>
                <p className="text-sm text-gray-600 mb-4 mt-4">
                  Found {similar.length} entries with similar emotional patterns
                  (using semantic analysis)
                </p>
                <div className="space-y-4">
                  {similar.map((entry, idx) => (
                    <details
                      key={idx}
                      className="border-l-4 border-emerald-600 pl-4 py-3 bg-gray-50
                               rounded-r-xl cursor-pointer"
                    >
                      <summary className="text-gray-900 mb-2">
                        "{entry.text.substring(0, 150)}..."
                        <span className="text-sm text-emerald-600 ml-2">
                          {entry.text.length > 150 ? "▼ Read full entry" : ""}
                        </span>
                      </summary>

                      {/* Full entry content */}
                      {entry.text.length > 150 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                            {entry.text}
                          </p>
                        </div>
                      )}

                      <div className="flex items-center gap-4 text-sm flex-wrap mt-2">
                        <span className="font-bold text-emerald-700">
                          {Math.round(entry.similarity * 100)}% match
                        </span>
                        {entry.mood && (
                          <>
                            <span className="text-gray-300">•</span>
                            <span className="text-gray-600">
                              Mood: {entry.mood}/5 {getMoodEmoji(entry.mood)}
                            </span>
                          </>
                        )}
                        <span className="text-gray-300">•</span>
                        <span className="text-gray-600">
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </details>
                  ))}
                </div>
              </details>
            )}

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={handleNewEntry}
                className="flex-1 bg-emerald-600 text-white
                         py-4 rounded-xl font-bold hover:bg-emerald-700 hover:shadow-lg transition-all duration-200
                         transform hover:scale-[1.02]"
              >
                ✏️ Write Another Entry
              </button>
              <button
                onClick={loadTimeline}
                className="flex-1 bg-white text-gray-900 py-4 rounded-xl border-2 border-gray-300
                         font-semibold hover:bg-gray-50 transition-all duration-200"
              >
                📚 View Timeline
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500">
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <span className="flex items-center gap-1">
              <span>💻</span>
              <span>Desktop app</span>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span>🔒</span>
              <span>No HTTP server</span>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span>✈️</span>
              <span>Works offline</span>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <span>🌱</span>
              <span>Local AI processing</span>
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
