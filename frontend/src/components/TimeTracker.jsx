import { useState, useEffect } from 'react';
import { Play, Square, Trash2, Clock } from 'lucide-react';
import api from '../lib/api';
import './TimeTracker.css';

const TimeTracker = () => {
  const [entries, setEntries] = useState([]);
  const [activeEntry, setActiveEntry] = useState(null);
  const [description, setDescription] = useState('');
  const [stats, setStats] = useState({ totalHours: 0, totalEntries: 0 });
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    fetchEntries();
    fetchActiveEntry();
    fetchStats();
  }, []);

  useEffect(() => {
    let interval = null;
    if (activeEntry) {
      interval = setInterval(() => {
        const start = new Date(activeEntry.start_time);
        const now = new Date();
        const diff = Math.floor((now - start) / 1000);
        setElapsedTime(diff);
      }, 1000);
    } else {
      setElapsedTime(0);
    }
    return () => clearInterval(interval);
  }, [activeEntry]);

  const fetchEntries = async () => {
    try {
      const response = await api.get('/timetracker');
      setEntries(response.data);
    } catch (error) {
      console.error('Error fetching entries:', error);
    }
  };

  const fetchActiveEntry = async () => {
    try {
      const response = await api.get('/timetracker/active');
      setActiveEntry(response.data);
    } catch (error) {
      console.error('Error fetching active entry:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/timetracker/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const startTracking = async () => {
    if (!description.trim()) {
      alert('Please enter a description');
      return;
    }

    try {
      const response = await api.post('/timetracker/start', {
        description: description.trim()
      });
      setActiveEntry(response.data);
      setDescription('');
    } catch (error) {
      console.error('Error starting tracker:', error);
      alert(error.response?.data?.error || 'Failed to start tracking');
    }
  };

  const stopTracking = async () => {
    if (!activeEntry) return;

    try {
      await api.put(`/timetracker/stop/${activeEntry.id}`);
      setActiveEntry(null);
      fetchEntries();
      fetchStats();
    } catch (error) {
      console.error('Error stopping tracker:', error);
    }
  };

  const deleteEntry = async (id) => {
    if (!confirm('Delete this time entry?')) return;

    try {
      await api.delete(`/timetracker/${id}`);
      setEntries(entries.filter(e => e.id !== id));
      fetchStats();
    } catch (error) {
      console.error('Error deleting entry:', error);
    }
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const calculateDuration = (start, end) => {
    const startTime = new Date(start);
    const endTime = end ? new Date(end) : new Date();
    return Math.floor((endTime - startTime) / 1000);
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="timetracker-container">
      <div className="tracker-header">
        <div className="tracker-input-section">
          <input
            type="text"
            placeholder="What are you working on?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !activeEntry && startTracking()}
            disabled={!!activeEntry}
            className="tracker-input"
          />
          {activeEntry ? (
            <div className="active-timer">
              <span className="timer-display">{formatDuration(elapsedTime)}</span>
              <button onClick={stopTracking} className="btn-stop">
                <Square size={20} fill="currentColor" />
                <span>Stop</span>
              </button>
            </div>
          ) : (
            <button onClick={startTracking} className="btn-start">
              <Play size={20} />
              <span>Start</span>
            </button>
          )}
        </div>

        <div className="tracker-stats">
          <div className="stat-box">
            <Clock size={24} />
            <div>
              <div className="stat-value">{stats.totalHours}h</div>
              <div className="stat-label">Total Time</div>
            </div>
          </div>
          <div className="stat-box">
            <div className="stat-value">{stats.totalEntries}</div>
            <div className="stat-label">Entries</div>
          </div>
        </div>
      </div>

      <div className="entries-list">
        <h3>Recent Time Entries</h3>
        {entries.length === 0 ? (
          <div className="empty-state">
            <Clock size={48} />
            <p>No time entries yet</p>
            <p className="empty-hint">Start tracking your time to see entries here</p>
          </div>
        ) : (
          <div className="entries-grid">
            {entries.map(entry => (
              <div key={entry.id} className="entry-card">
                <div className="entry-header">
                  <div className="entry-description">
                    {entry.description || 'No description'}
                  </div>
                  <button onClick={() => deleteEntry(entry.id)} className="btn-delete">
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="entry-details">
                  <div className="entry-time">
                    <span className="time-badge">{formatTime(entry.start_time)}</span>
                    {entry.end_time && (
                      <>
                        <span>→</span>
                        <span className="time-badge">{formatTime(entry.end_time)}</span>
                      </>
                    )}
                  </div>
                  <div className="entry-duration">
                    {formatDuration(calculateDuration(entry.start_time, entry.end_time))}
                  </div>
                </div>
                <div className="entry-date">
                  {formatDate(entry.start_time)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeTracker;
