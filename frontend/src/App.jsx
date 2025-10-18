import { useState, useEffect } from "react";

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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-3">
            Introspect
          </h1>
          <p className="text-gray-600 mb-3">
            AI-powered pattern recognition in your journal entries
          </p>
          <div className="flex items-center justify-center gap-3 text-sm flex-wrap">
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-green-100 text-green-800">
              <span>✅</span>
              <span>Running Offline</span>
            </span>
            <span className="text-gray-400">•</span>
            <span className="text-gray-600">100% local processing</span>
            <span className="text-gray-400">•</span>
            <span className="text-gray-600">Privacy-first</span>
          </div>
        </header>

        {/* Main Content */}
        {!insight && !showTimeline ? (
          // Writing State
          <div className="bg-white rounded-2xl shadow-xl p-8 backdrop-blur-sm bg-white/90">
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-semibold mb-3">
                  What's on your mind?
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Write freely... I'll help you spot patterns in your thoughts and emotions."
                  className="w-full h-48 px-4 py-3 border-2 border-gray-200 rounded-xl 
                           focus:ring-2 focus:ring-indigo-500 focus:border-transparent
                           resize-none text-gray-700 placeholder-gray-400
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
                <label className="block text-gray-700 text-sm font-semibold mb-3">
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
                            ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg scale-105"
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200 hover:scale-102"
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
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 rounded-xl
                         font-semibold hover:shadow-lg transition-all duration-200
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transform hover:scale-102"
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
                  "🔍 Find Patterns"
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
              className="w-full mt-4 bg-gray-100 text-gray-700 py-3 rounded-xl
                       font-medium hover:bg-gray-200 transition-all duration-200"
            >
              📚 View Past Entries
            </button>
          </div>
        ) : showTimeline ? (
          // Timeline View
          <div>
            <button
              onClick={() => setShowTimeline(false)}
              className="mb-4 text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-2"
            >
              ← Back to writing
            </button>

            <div className="bg-white rounded-2xl shadow-xl p-8">
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
                    <div
                      key={entry.id || idx}
                      className="border-l-4 border-indigo-200 pl-4 py-3 hover:bg-indigo-50 
                               rounded-r-lg transition-colors duration-200"
                    >
                      <p className="text-gray-700 mb-2">
                        {entry.content.substring(0, 150)}
                        {entry.content.length > 150 && "..."}
                      </p>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span className="font-semibold">
                          Mood: {entry.mood || entry.mood_rating}/5
                        </span>
                        <span>•</span>
                        <span>
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          // Insight State
          <div className="space-y-6">
            {/* Main Insight */}
            <div className="bg-white rounded-2xl shadow-xl p-8 backdrop-blur-sm bg-white/90">
              <div className="flex items-start gap-4 mb-4">
                <div
                  className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full 
                              flex items-center justify-center flex-shrink-0 shadow-lg"
                >
                  <span className="text-2xl">💡</span>
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-gray-900 mb-3">
                    Pattern Detected
                  </h2>
                  <p className="text-gray-700 leading-relaxed text-lg">
                    {insight}
                  </p>
                  <p className="text-sm text-gray-500 mt-4 italic">
                    This insight is based on your own past entries, not generic
                    advice
                  </p>
                </div>
              </div>
            </div>

            {/* Similar Entries */}
            {similar.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  Similar Past Experiences
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Found {similar.length} entries with similar emotional patterns
                  (using semantic analysis)
                </p>
                <div className="space-y-4">
                  {similar.map((entry, idx) => (
                    <div
                      key={idx}
                      className="border-l-4 border-purple-200 pl-4 py-3 bg-gradient-to-r 
                               from-purple-50 to-indigo-50 rounded-r-xl"
                    >
                      <p className="text-gray-700 mb-2">
                        "{entry.text.substring(0, 150)}..."
                      </p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="font-bold text-purple-700">
                          {Math.round(entry.similarity * 100)}% match
                        </span>
                        <span className="text-gray-500">•</span>
                        <span className="text-gray-600">
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={handleNewEntry}
                className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white 
                         py-4 rounded-xl font-semibold hover:shadow-lg transition-all duration-200
                         transform hover:scale-102"
              >
                ✍️ Write Another Entry
              </button>
              <button
                onClick={loadTimeline}
                className="flex-1 bg-gray-100 text-gray-700 py-4 rounded-xl
                         font-semibold hover:bg-gray-200 transition-all duration-200"
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
              <span>🧠</span>
              <span>Local AI processing</span>
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
