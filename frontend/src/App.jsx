import React, { useState, useEffect } from 'react';


const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December'];

function App() {
  const [hierarchyData, setHierarchyData] = useState({});
  const [years, setYears] = useState([]);
  const [expandedYears, setExpandedYears] = useState(new Set());
  const [expandedMonths, setExpandedMonths] = useState(new Set());
  const [expandedWeeks, setExpandedWeeks] = useState(new Set());
  const [entryTitles, setEntryTitles] = useState({});
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [selectedMood, setSelectedMood] = useState(3);
  const [entryContent, setEntryContent] = useState('');
  const [statusMessage, setStatusMessage] = useState({ text: '', type: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHierarchy();
  }, []);

  const loadHierarchy = async () => {
    try {
      const data = await window.electronAPI.getDateHierarchy();
      setHierarchyData(data.hierarchy);
      setYears(data.years);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load hierarchy:', error);
      setLoading(false);
    }
  };

  const toggleYear = async (year) => {
    const newExpanded = new Set(expandedYears);
    if (newExpanded.has(year)) {
      newExpanded.delete(year);
    } else {
      newExpanded.add(year);
      // Load titles for this year
      await loadTitlesForYear(year);
    }
    setExpandedYears(newExpanded);
  };

  const toggleMonth = (year, month) => {
    const key = `${year}-${month}`;
    const newExpanded = new Set(expandedMonths);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedMonths(newExpanded);
  };

  const toggleWeek = (year, month, week) => {
    const key = `${year}-${month}-${week}`;
    const newExpanded = new Set(expandedWeeks);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedWeeks(newExpanded);
  };

  const loadTitlesForYear = async (year) => {
    try {
      const result = await window.electronAPI.getEntriesByYear(year);
      const newTitles = { ...entryTitles };
      result.entries.forEach(entry => {
        const key = `${entry.year}-${entry.month}-${entry.day}`;
        newTitles[key] = {
          title: entry.title,
          mood_emoji: entry.mood_emoji
        };
      });
      setEntryTitles(newTitles);
    } catch (error) {
      console.error('Failed to load titles:', error);
    }
  };

  const loadEntry = async (year, month, day) => {
    try {
      const result = await window.electronAPI.getEntriesByDate(year, month, day);
      if (result.entries && result.entries.length > 0) {
        setSelectedEntry(result.entries[0]);
      }
    } catch (error) {
      console.error('Failed to load entry:', error);
      showStatus('Failed to load entry', 'error');
    }
  };

  const saveEntry = async () => {
    if (!entryContent.trim()) {
      showStatus('Please write something first', 'error');
      return;
    }

    try {
      showStatus('Saving entry...', 'info');
      
      await window.electronAPI.createEntry({
        content: entryContent,
        mood_rating: selectedMood
      });

      showStatus('Entry saved successfully! 🎉', 'success');
      setEntryContent('');
      setSelectedMood(3);
      
      // Reload hierarchy
      await loadHierarchy();
      
    } catch (error) {
      console.error('Failed to save entry:', error);
      showStatus('Failed to save entry: ' + error.message, 'error');
    }
  };

  const showStatus = (text, type) => {
    setStatusMessage({ text, type });
    if (type === 'success') {
      setTimeout(() => setStatusMessage({ text: '', type: '' }), 3000);
    }
  };

  const renderDays = (year, month, week, days) => {
    if (!days) return null;

    return days.sort((a, b) => b - a).map(day => {
      const key = `${year}-${month}-${day}`;
      const dateStr = `${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}`;
      const titleData = entryTitles[key];

      return (
        <div 
          key={key}
          className="day-entry" 
          onClick={() => loadEntry(year, month, day)}
        >
          <span className="date">{dateStr}</span>
          <span className="title">
            {titleData ? titleData.title : 'Loading...'}
          </span>
          <span className="mood">
            {titleData ? titleData.mood_emoji : ''}
          </span>
        </div>
      );
    });
  };

  const renderWeeks = (year, month, weeks) => {
    if (!weeks) return null;

    return Object.keys(weeks).sort((a, b) => b - a).map(week => {
      const weekKey = `${year}-${month}-${week}`;
      const isExpanded = expandedWeeks.has(weekKey);

      return (
        <div key={weekKey} className="week-item">
          <div 
            className={`week-header ${isExpanded ? 'expanded' : ''}`}
            onClick={() => toggleWeek(year, month, parseInt(week))}
          >
            <span>Week {week}</span>
            <span className="arrow">▶</span>
          </div>
          <div className={`days-container ${isExpanded ? 'show' : ''}`}>
            {renderDays(year, month, parseInt(week), weeks[week])}
          </div>
        </div>
      );
    });
  };

  const renderMonths = (year, months) => {
    if (!months) return null;

    return Object.keys(months).sort((a, b) => b - a).map(month => {
      const monthKey = `${year}-${month}`;
      const isExpanded = expandedMonths.has(monthKey);
      const monthName = MONTHS[parseInt(month) - 1];

      return (
        <div key={monthKey} className="month-item">
          <div 
            className={`month-header ${isExpanded ? 'expanded' : ''}`}
            onClick={() => toggleMonth(year, parseInt(month))}
          >
            <span>{monthName}</span>
            <span className="arrow">▶</span>
          </div>
          <div className={`weeks-container ${isExpanded ? 'show' : ''}`}>
            {renderWeeks(year, parseInt(month), months[month])}
          </div>
        </div>
      );
    });
  };

  const renderYears = () => {
    if (loading) {
      return <div className="loading">Loading entries...</div>;
    }

    if (!years || years.length === 0) {
      return (
        <div className="empty-state">
          <div className="icon">📝</div>
          <p>No entries yet. Start writing!</p>
        </div>
      );
    }

    return years.map(year => {
      const isExpanded = expandedYears.has(year);

      return (
        <div key={year} className="year-item">
          <div 
            className={`year-header ${isExpanded ? 'expanded' : ''}`}
            onClick={() => toggleYear(year)}
          >
            <span>{year}</span>
            <span className="arrow">▶</span>
          </div>
          <div className={`months-container ${isExpanded ? 'show' : ''}`}>
            {renderMonths(year, hierarchyData[year])}
          </div>
        </div>
      );
    });
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>📔 Introspect</h1>
          <p>Your Personal Journal</p>
        </div>
        
        <div className="journal-entries-section">
          <div className="section-title">My Journal Entries</div>
          <div id="timeline-hierarchy">
            {renderYears()}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="content-header">
          <h2>Welcome to Your Journal</h2>
          <p>Reflect, grow, and discover patterns in your thoughts</p>
        </div>

        {/* New Entry Form */}
        <div className="new-entry-card">
          <h3>✍️ New Journal Entry</h3>
          
          <textarea
            id="entry-content"
            value={entryContent}
            onChange={(e) => setEntryContent(e.target.value)}
            placeholder="Write your thoughts here..."
          />
          
          <div className="mood-selector">
            <label>How are you feeling?</label>
            <div className="mood-options">
              {[
                { value: 1, emoji: '😢', label: 'Struggling' },
                { value: 2, emoji: '😔', label: 'Low' },
                { value: 3, emoji: '😐', label: 'Neutral' },
                { value: 4, emoji: '🙂', label: 'Good' },
                { value: 5, emoji: '😊', label: 'Great' }
              ].map(mood => (
                <div
                  key={mood.value}
                  className={`mood-option ${selectedMood === mood.value ? 'selected' : ''}`}
                  onClick={() => setSelectedMood(mood.value)}
                >
                  <span className="emoji">{mood.emoji}</span>
                  <span className="label">{mood.label}</span>
                </div>
              ))}
            </div>
          </div>

          <button className="primary" onClick={saveEntry}>
            Save Entry
          </button>
          
          {statusMessage.text && (
            <div className={`status-message ${statusMessage.type}`}>
              {statusMessage.text}
            </div>
          )}
        </div>

        {/* Selected Entry Display */}
        {selectedEntry && (
          <div className="entry-display">
            <h4>
              <span>{selectedEntry.title}</span>
              <span>{selectedEntry.mood_emoji}</span>
            </h4>
            <div className="entry-content">{selectedEntry.content}</div>
            <div className="entry-meta">
              {new Date(selectedEntry.timestamp).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;