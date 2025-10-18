# Introspect 🧠

> **AI-powered pattern recognition for your journal entries—completely private, completely offline**

Introspect is a privacy-first desktop journaling application that uses local AI to detect emotional patterns and provide personalized insights based on your own history. Unlike cloud-based alternatives, everything runs on your device—your thoughts stay yours.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Electron](https://img.shields.io/badge/Electron-Desktop-47848F?logo=electron)](https://www.electronjs.org/)

---

## 🎯 The Problem

Journaling improves mental health, but most people never extract insights from their writing. Therapists provide invaluable pattern recognition—remembering when you felt this way before and what helped—but cost $200-400/month and aren't accessible to everyone.

**Most journaling apps fail in two ways:**

1. **Cloud-based apps** store your most vulnerable thoughts on someone else's servers
2. **Traditional journals** provide no pattern recognition—your insights stay trapped in the past

---

## 💡 The Solution

Introspect brings therapeutic pattern recognition to everyone through:

- **🔍 Pattern Recognition**: Automatically detects emotional patterns across journal entries
- **🎯 Contextual Insights**: Surfaces relevant past experiences when you're struggling
- **💬 Self-Reflection**: Quotes your own words back: _"Last time you felt this way, you wrote..."_
- **🔒 Privacy by Design**: 100% offline—no servers, no cloud, complete privacy
- **📊 Smart Categorization**: Auto-tags entries with themes and emotions

---

## ✨ Key Features

### 🧠 Intelligent Pattern Detection

Uses semantic similarity (sentence transformers) to find emotionally similar entries, even when you use different words.

**Example:**

- Today: _"Nervous about tomorrow's client meeting"_
- 2 weeks ago: _"Anxious about the big presentation"_
- **Pattern detected**: Both are work-related anxiety before important events

### 💭 Personalized Insights

Instead of generic advice, get insights from YOUR history:

> _"You've felt this way before. 2 weeks ago, you wrote: 'Feeling really anxious about tomorrow's team presentation...' Preparation with Sarah helped then. What's different this time?"_

### 📋 Auto-Categorization & Timeline

New entries are automatically summarized:

```
Work - Performance Review
[work] [mental_health] [personal_growth]
struggling but persisting
Mood: 2/5 • Oct 18, 2025
```

Click to expand and see full entry. Spot recurring patterns at a glance.

### 🔐 Privacy-First Architecture

- **No internet required** - Works 100% offline
- **Local database** - SQLite file on your device
- **No tracking** - Zero analytics, zero telemetry
- **User control** - Delete the app → delete all data

### ⚡ Fast Local AI

- **2-5 second analysis** - Proves local AI is viable
- **Semantic embeddings** - 384-dimensional vectors for similarity matching
- **Efficient storage** - Pickled NumPy arrays in SQLite

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                YOUR DEVICE ONLY                      │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │          Electron (UI Layer)               │    │
│  │  ┌──────────────────────────────────────┐  │    │
│  │  │    React + Vite + Tailwind CSS       │  │    │
│  │  └──────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────┘    │
│                       ↕ IPC                         │
│  ┌────────────────────────────────────────────┐    │
│  │     Python Subprocess (Backend)            │    │
│  │  ┌──────────────────────────────────────┐  │    │
│  │  │  SQLite DB    │   ML Pipeline        │  │    │
│  │  │  (Local)      │   (Sentence Trans.)  │  │    │
│  │  └──────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│           NO INTERNET • NO SERVERS • NO CLOUD       │
└─────────────────────────────────────────────────────┘
```

### Tech Stack

**Frontend:**

- React 18 - UI framework
- Vite - Build tool & dev server
- Tailwind CSS - Styling
- Electron - Desktop wrapper

**Backend:**

- Python 3.9+ - Core logic
- SQLite - Local database
- sentence-transformers - Semantic embeddings
- NumPy - Vector operations
- scikit-learn - Cosine similarity

**Architecture:**

- Electron ↔ Python subprocess via stdin/stdout (JSON protocol)
- No HTTP server required
- Offline-first by design

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm** or **yarn**

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/introspect.git
cd introspect
```

2. **Set up the backend**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Set up the frontend**

```bash
cd ../electron

# Install dependencies
npm install

# Build React app
npm run build
```

4. **Optional: Load demo data**

```bash
cd ../backend
python load_demo_data.py
```

### Running the App

From the `electron` directory:

```bash
npm start
```

The app will:

1. Start Python subprocess (loads ML model ~5 seconds)
2. Open Electron window
3. Be ready to use!

---

## 📖 Usage Guide

### Writing Your First Entry

1. **Open the app** - Electron window launches
2. **Write freely** - No minimum length, just express yourself
3. **Set your mood** - Rate 1-5 (Struggling → Great)
4. **Click "Find Patterns"** - AI analyzes in 2-5 seconds
5. **Read your insight** - See similar past entries and patterns

### Understanding Analysis

**After clicking "Find Patterns", you'll see:**

📊 **Pattern Detection**

- Timeline showing: Past similar entry → Today → Future outlook
- Similarity percentage
- Mood comparison

💡 **Personalized Insight**

- Quotes from your own past entries
- When you felt this way before
- What helped (if applicable)

📖 **Similar Entries**

- Expandable list of past entries with similar emotional patterns
- Semantic matching (not just keyword matching)

### Viewing Timeline

Click **"📚 View Past Entries"** to see:

- Chronological list of all entries
- Auto-generated summaries (for new entries)
- Theme tags and emotions
- Click any entry to expand and read full content

### Demo Offline Capability

**To prove it works offline:**

1. Disconnect from WiFi/Ethernet
2. Write a journal entry
3. Get full AI analysis (still works!)
4. This proves everything runs locally

---

## 🔒 Privacy & Security

### Data Storage

**Where your data lives:**

- SQLite database: `backend/journal.db`
- Location: Project directory (development) or `~/Library/Application Support/Introspect/` (production)
- Format: Single file, human-readable with SQLite tools

**What's stored:**

- Journal entry text
- Mood ratings (1-5)
- ML embeddings (384-dimensional vectors)
- Analysis results (insights, summaries)
- Timestamps

**What's NOT stored:**

- No user accounts
- No IP addresses
- No device identifiers
- No telemetry
- No analytics

### How to Delete Your Data

**Complete deletion:**

```bash
rm backend/journal.db
```

That's it. Your data is gone forever. No cloud backup to worry about.

### Encryption

**Current state (Hackathon MVP):**

- Data stored unencrypted locally
- No network transmission (nothing to encrypt in transit)

**Production recommendations:**

- Encrypt database file with user password
- Use SQLCipher for transparent encryption
- Implement secure export/backup

---

## 🎨 Demo Data

Load realistic demo entries to test pattern recognition:

```bash
cd backend
python load_demo_data.py
```

**Demo dataset includes:**

- 12 entries over 2 weeks
- Recurring themes: work anxiety, therapy, personal growth
- Pattern: Anxiety → Preparation → Success
- Tests semantic similarity with varied wording

---

## 🛠️ Development

### Project Structure

```
introspect/
├── electron/               # Electron app
│   ├── main.js            # Electron main process
│   ├── preload.js         # IPC bridge (context isolation)
│   ├── dist/              # Built React app
│   └── package.json
│
├── electron/src/          # React source
│   ├── App.jsx            # Main component
│   ├── main.jsx           # Entry point
│   └── index.css          # Tailwind styles
│
├── backend/               # Python backend
│   ├── electron_bridge.py # Subprocess entry point
│   ├── database.py        # SQLite operations
│   ├── ml/
│   │   └── analyzer.py    # ML pipeline
│   ├── load_demo_data.py  # Demo data loader
│   └── requirements.txt
│
└── README.md
```

### Key Files Explained

**`electron/main.js`**

- Spawns Python subprocess
- Manages IPC communication
- Handles window lifecycle

**`electron/preload.js`**

- Exposes safe IPC methods to renderer
- Context isolation bridge

**`backend/electron_bridge.py`**

- Reads commands from stdin (JSON)
- Processes via database + ML
- Writes responses to stdout (JSON)

**`backend/database.py`**

- SQLite wrapper
- Stores embeddings as pickled BLOBs
- JSON serialization for analysis

**`backend/ml/analyzer.py`**

- Loads sentence-transformers model
- Generates 384-dim embeddings
- Finds similar entries via cosine similarity
- Generates insights and summaries

### Development Workflow

**Terminal 1 - Backend (optional for testing):**

```bash
cd backend
source venv/bin/activate
python electron_bridge.py
# Reads stdin, writes stdout
```

**Terminal 2 - Frontend:**

```bash
cd electron
npm run dev  # Vite dev server (React hot reload)
```

**Terminal 3 - Electron:**

```bash
cd electron
npm start  # Launches Electron
```

### Building for Production

```bash
cd electron

# Build React app
npm run build

# Package Electron app (coming soon)
# npm run package
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

### Database Tests

```bash
cd backend
python database.py  # Runs built-in tests
```

### Frontend Tests

```bash
cd electron
npm test
```

### Manual Testing Checklist

- [ ] Create entry with mood 1-5
- [ ] Verify analysis completes (2-5 seconds)
- [ ] Check similar entries appear
- [ ] Verify insight quotes past entry
- [ ] View timeline
- [ ] Expand entry details
- [ ] Test with WiFi OFF (offline mode)
- [ ] Create multiple entries
- [ ] Verify pattern detection improves over time

---

## 📊 Key Technical Concepts

### Why Sentence Transformers?

**Traditional keyword matching:**

```
Entry 1: "I'm anxious about my presentation"
Entry 2: "Nervous about tomorrow's talk"
Match: ❌ No common words
```

**Semantic embeddings:**

```
Entry 1: [0.832, -0.421, 0.156, ...]  # 384 dimensions
Entry 2: [0.841, -0.389, 0.162, ...]
Similarity: ✅ 89% (cosine similarity)
```

### Why Offline?

**Privacy:** Your journal is deeply personal. Cloud storage means trusting a company with your most vulnerable thoughts.

**Control:** With Introspect, you physically own your data. No terms of service can change that.

**Permanence:** Companies shut down, services change. Local-first means your journal outlasts any startup.

**Trust:** No need to trust us. The code is open source. Audit it yourself.

### Why Electron + Python?

**Electron:** Cross-platform desktop apps with web tech (React)

**Python:** ML ecosystem (transformers, NumPy, scikit-learn)

**IPC via stdin/stdout:** Simple, reliable, no HTTP overhead

**Alternative considered:** Pure JavaScript with TensorFlow.js

- **Rejected because:** sentence-transformers ecosystem is richer, Python ML libraries more mature

---

## 🗺️ Roadmap

### Post-Hackathon (v1.0)

- [ ] Database encryption (SQLCipher)
- [ ] Password protection on app launch
- [ ] Export/import functionality (JSON)
- [ ] Better LLM integration (Ollama for richer insights)
- [ ] Advanced pattern visualization (mood trends over time)
- [ ] Search functionality

### Future Vision (v2.0+)

- [ ] Cross-platform (Windows, Mac, Linux)
- [ ] Mobile version (iOS/Android with local sync)
- [ ] Themes & customization
- [ ] Multi-language support
- [ ] Voice journaling (speech-to-text locally)
- [ ] Portable USB edition (run from flash drive)
- [ ] Optional E2E encrypted cloud backup (user-controlled)

### Never Planned

- ❌ Cloud-required features
- ❌ User accounts / authentication
- ❌ Analytics / tracking
- ❌ Ads / monetization via data
- ❌ Social features

**Philosophy:** Your journal is yours. Period.

---

## 🤝 Contributing

We welcome contributions! This project was built during a hackathon and there's lots of room for improvement.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Principles

- **Privacy first**: No features that require cloud
- **Simple over clever**: Readable code > premature optimization
- **User agency**: User controls everything
- **Open source**: No proprietary lock-in

### Areas Needing Help

- [ ] Windows testing & packaging
- [ ] UI/UX improvements
- [ ] Database encryption implementation
- [ ] Export/import features
- [ ] Documentation improvements
- [ ] More ML model options (smaller/faster alternatives)

---

## 🐛 Troubleshooting

### Python subprocess won't start

**Error:** `Python failed to start`

**Solutions:**

```bash
# Verify Python version
python3 --version  # Should be 3.9+

# Check dependencies
cd backend
pip install -r requirements.txt

# Test manually
python electron_bridge.py
# Should print: ✅ Python subprocess ready
```

### ML model fails to load

**Error:** `Failed to load sentence-transformers`

**Solutions:**

```bash
# Install transformers dependencies
pip install sentence-transformers torch

# Download model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Database locked error

**Error:** `database is locked`

**Solution:**
Close all Electron windows and restart. SQLite doesn't handle concurrent writes well.

### Entries not showing summaries

**Cause:** Entries created before summary feature was added

**Solution:**

- Old entries show text preview (expected)
- New entries will show summaries
- To regenerate: Delete `journal.db` and reload demo data

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

**In short:** Use it, modify it, distribute it. Just don't blame us if something breaks. And keep it open source.

---

## 👥 Team

Built with ❤️ during [Hackathon Name] by:

- **[Your Name]** - Full-stack, Integration, Architecture
- **[DS Friend 1]** - ML Pipeline, Pattern Recognition
- **[DS Friend 2]** - Database, Data Engineering

---

## 🙏 Acknowledgments

- **[sentence-transformers](https://www.sbert.net/)** for semantic embeddings
- **[Electron](https://www.electronjs.org/)** for cross-platform desktop apps
- **[React](https://react.dev/)** for the UI framework
- **[Tailwind CSS](https://tailwindcss.com/)** for styling
- The open-source community for making privacy-first AI possible

---

## ⚖️ Disclaimer

**Introspect is not a replacement for professional mental health care.**

If you're experiencing a mental health crisis, please contact:

- **National Suicide Prevention Lifeline:** 988
- **Crisis Text Line:** Text HOME to 741741
- **International Association for Suicide Prevention:** https://www.iasp.info/resources/Crisis_Centres/

Journaling is a tool for self-reflection, not clinical treatment.

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/introspect/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/introspect/discussions)
- **Email:** your.email@example.com

---

## 🌟 Star Us!

If you find Introspect valuable, please star the repository! It helps others discover privacy-first mental health tools.

---

**Built with ❤️ for mental health and privacy**

_"Your thoughts, your device, your control"_
