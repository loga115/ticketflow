import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Play, Pause, RotateCcw } from 'lucide-react';
import api from '../lib/api';
import './Pomodoro.css';

const Pomodoro = () => {
  const location = useLocation();
  const [customDuration, setCustomDuration] = useState(25);
  const [breakDuration, setBreakDuration] = useState(5);
  const [longBreakDuration, setLongBreakDuration] = useState(15);
  const [sessionsBeforeLongBreak, setSessionsBeforeLongBreak] = useState(4);
  const [completedSessions, setCompletedSessions] = useState(0);
  const [minutes, setMinutes] = useState(25);
  const [seconds, setSeconds] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const [isLongBreak, setIsLongBreak] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [stats, setStats] = useState({ totalSessions: 0, totalMinutes: 0 });
  const [boards, setBoards] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [showCustomSettings, setShowCustomSettings] = useState(false);
  const [presets, setPresets] = useState(() => {
    const savedPresets = localStorage.getItem('pomodoro_presets');
    if (savedPresets) {
      return JSON.parse(savedPresets);
    }
    return [
      { name: 'Classic', work: 25, break: 5, longBreak: 15, sessions: 4 },
      { name: 'Short', work: 15, break: 3, longBreak: 10, sessions: 4 },
      { name: 'Long', work: 50, break: 10, longBreak: 30, sessions: 3 }
    ];
  });
  const [newPreset, setNewPreset] = useState({
    name: '',
    work: 25,
    break: 5,
    longBreak: 15,
    sessions: 4
  });

  useEffect(() => {
    fetchStats();
    fetchBoards();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
    
    // Handle pre-selected task from navigation state
    if (location.state?.taskId && location.state?.boardId) {
      setSelectedBoard(location.state.boardId);
      setSelectedTask(location.state.taskId);
    }
  }, []);

  useEffect(() => {
    // Save presets to localStorage whenever they change
    localStorage.setItem('pomodoro_presets', JSON.stringify(presets));
  }, [presets]);

  useEffect(() => {
    if (selectedBoard) {
      fetchTasks(selectedBoard);
    }
  }, [selectedBoard]);

  useEffect(() => {
    let interval = null;

    if (isActive) {
      interval = setInterval(() => {
        if (seconds === 0) {
          if (minutes === 0) {
            // Timer completed
            handleTimerComplete();
          } else {
            setMinutes(minutes - 1);
            setSeconds(59);
          }
        } else {
          setSeconds(seconds - 1);
        }
      }, 1000);
    } else {
      clearInterval(interval);
    }

    return () => clearInterval(interval);
  }, [isActive, minutes, seconds]);

  const fetchStats = async () => {
    try {
      const response = await api.get('/pomodoro/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchBoards = async () => {
    try {
      const response = await api.get('/boards');
      setBoards(response.data);
      if (response.data.length > 0) {
        setSelectedBoard(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching boards:', error);
    }
  };

  const fetchTasks = async (boardId) => {
    try {
      const response = await api.get(`/tasks/board/${boardId}`);
      setTasks(response.data.filter(t => t.status !== 'done'));
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const startSession = async () => {
    try {
      const sessionDuration = isLongBreak ? longBreakDuration : (isBreak ? breakDuration : customDuration);
      const pomodoroData = {
        duration: sessionDuration,
        completed: false
      };
      
      if (selectedTask && !isBreak && !isLongBreak) {
        pomodoroData.task_id = selectedTask;
        // Move task to in_progress
        await api.put(`/tasks/${selectedTask}`, { status: 'in_progress' });
      }
      
      const response = await api.post('/pomodoro', pomodoroData);
      setSessionId(response.data.id);
      setSessionStartTime(new Date().toISOString());
      setIsActive(true);
    } catch (error) {
      console.error('Error starting session:', error);
    }
  };

  const playChime = () => {
    // Create a pleasant chime using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const now = audioContext.currentTime;
    
    // Play three notes in succession (C-E-G chord)
    [523.25, 659.25, 783.99].forEach((freq, i) => {
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = freq;
      oscillator.type = 'sine';
      
      const startTime = now + (i * 0.15);
      gainNode.gain.setValueAtTime(0, startTime);
      gainNode.gain.linearRampToValueAtTime(0.3, startTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + 0.5);
      
      oscillator.start(startTime);
      oscillator.stop(startTime + 0.5);
    });
  };

  const showNotification = (title, body) => {
    playChime();
    
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: body,
        icon: '🍅',
        badge: '⏱️',
        requireInteraction: false
      });
    }
  };

  const handleTimerComplete = async () => {
    setIsActive(false);
    
    if (sessionId) {
      try {
        await api.put(`/pomodoro/${sessionId}`, { completed: true });
        
        // Create time tracker entry for completed work sessions
        if (!isBreak && !isLongBreak && sessionStartTime) {
          const taskName = selectedTask ? 
            tasks.find(t => t.id === selectedTask)?.title || 'Pomodoro' : 
            'Pomodoro';
          
          await api.post('/timetracker', {
            task_id: selectedTask || null,
            description: taskName,
            start_time: sessionStartTime,
            end_time: new Date().toISOString()
          });
        }
        
        fetchStats();
      } catch (error) {
        console.error('Error completing session:', error);
      }
    }

    // Switch between work and break
    if (isBreak || isLongBreak) {
      setMinutes(customDuration);
      setIsBreak(false);
      setIsLongBreak(false);
      showNotification('Break Complete! ☕', 'Ready for another session?');
    } else {
      const newCompletedSessions = completedSessions + 1;
      setCompletedSessions(newCompletedSessions);
      
      if (newCompletedSessions % sessionsBeforeLongBreak === 0) {
        setMinutes(longBreakDuration);
        setIsLongBreak(true);
        showNotification('Great Work! 🎉', `You've completed ${sessionsBeforeLongBreak} sessions! Time for a ${longBreakDuration}-minute long break!`);
      } else {
        setMinutes(breakDuration);
        setIsBreak(true);
        showNotification('Great Work! 🍅', `Time for a ${breakDuration}-minute break!`);
      }
    }
    setSeconds(0);
  };

  const toggleTimer = () => {
    if (!isActive && !sessionId) {
      startSession();
    } else {
      setIsActive(!isActive);
    }
  };

  const resetTimer = () => {
    setIsActive(false);
    setSessionId(null);
    setSessionStartTime(null);
    setMinutes(isBreak ? breakDuration : (isLongBreak ? longBreakDuration : customDuration));
    setSeconds(0);
  };

  const handleDurationChange = (newDuration) => {
    setCustomDuration(newDuration);
    if (!isActive && !isBreak && !isLongBreak) {
      setMinutes(newDuration);
      setSeconds(0);
    }
  };

  const applyPreset = (preset) => {
    if (isActive) return;
    setCustomDuration(preset.work);
    setBreakDuration(preset.break);
    setLongBreakDuration(preset.longBreak);
    setSessionsBeforeLongBreak(preset.sessions);
    setMinutes(preset.work);
    setSeconds(0);
    setCompletedSessions(0);
  };

  const saveCustomPreset = () => {
    if (!newPreset.name.trim()) {
      alert('Please enter a preset name');
      return;
    }
    if (presets.some(p => p.name.toLowerCase() === newPreset.name.toLowerCase())) {
      alert('A preset with this name already exists');
      return;
    }
    setPresets([...presets, { ...newPreset }]);
    applyPreset(newPreset);
    setShowCustomSettings(false);
    setNewPreset({ name: '', work: 25, break: 5, longBreak: 15, sessions: 4 });
    alert('Preset saved successfully!');
  };

  const formatTime = (mins, secs) => {
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const currentDuration = isLongBreak ? longBreakDuration : (isBreak ? breakDuration : customDuration);
  const progress = (currentDuration * 60 - (minutes * 60 + seconds)) / (currentDuration * 60) * 100;

  return (
    <div className="pomodoro-container">
      <div className="pomodoro-card">
        <h2>{isLongBreak ? 'Long Break Time' : (isBreak ? 'relax.' : 'focus.')}</h2>
        
        {!isBreak && !isLongBreak && !isActive && (
          <>
            <div className="task-selector">
              <label>Pomodoro Presets</label>
              <div className="duration-options">
                {presets.map(preset => (
                  <button
                    key={preset.name}
                    onClick={() => applyPreset(preset)}
                    className={`duration-btn ${customDuration === preset.work && breakDuration === preset.break ? 'active' : ''}`}
                    title={`${preset.work}min work / ${preset.break}min break / ${preset.longBreak}min long break / ${preset.sessions} sessions`}
                  >
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="task-selector">
              <label>Sessions Before Long Break</label>
              <div className="duration-options">
                {[2, 3, 4, 5].map(num => (
                  <button
                    key={num}
                    onClick={() => setSessionsBeforeLongBreak(num)}
                    className={`duration-btn ${sessionsBeforeLongBreak === num ? 'active' : ''}`}
                  >
                    {num}
                  </button>
                ))}
              </div>
              <div className="session-tracker">
                Sessions completed: {completedSessions} / {sessionsBeforeLongBreak}
              </div>
            </div>

            <div className="custom-settings-section">
              <button 
                onClick={() => setShowCustomSettings(!showCustomSettings)} 
                className="btn-toggle-custom"
              >
                {showCustomSettings ? '▼ Hide Custom Settings' : '▶ Create Custom Preset'}
              </button>
              
              {showCustomSettings && (
                <div className="custom-settings">
                  <input
                    type="text"
                    placeholder="Preset name (e.g., My Flow)"
                    value={newPreset.name}
                    onChange={(e) => setNewPreset({ ...newPreset, name: e.target.value })}
                    className="preset-name-input"
                  />
                  
                  <div className="custom-input-group">
                    <label>Work Duration (min)</label>
                    <input
                      type="number"
                      min="1"
                      max="120"
                      value={newPreset.work}
                      onChange={(e) => setNewPreset({ ...newPreset, work: parseInt(e.target.value) || 25 })}
                      className="custom-number-input"
                    />
                  </div>

                  <div className="custom-input-group">
                    <label>Short Break (min)</label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={newPreset.break}
                      onChange={(e) => setNewPreset({ ...newPreset, break: parseInt(e.target.value) || 5 })}
                      className="custom-number-input"
                    />
                  </div>

                  <div className="custom-input-group">
                    <label>Long Break (min)</label>
                    <input
                      type="number"
                      min="1"
                      max="60"
                      value={newPreset.longBreak}
                      onChange={(e) => setNewPreset({ ...newPreset, longBreak: parseInt(e.target.value) || 15 })}
                      className="custom-number-input"
                    />
                  </div>

                  <div className="custom-input-group">
                    <label>Sessions Before Long Break</label>
                    <input
                      type="number"
                      min="2"
                      max="10"
                      value={newPreset.sessions}
                      onChange={(e) => setNewPreset({ ...newPreset, sessions: parseInt(e.target.value) || 4 })}
                      className="custom-number-input"
                    />
                  </div>

                  <button onClick={saveCustomPreset} className="btn-save-preset">
                    Save Preset
                  </button>
                </div>
              )}
            </div>
            
            <div className="task-selector">
              <label>Link to Task (Optional)</label>
            <select 
              value={selectedBoard || ''} 
              onChange={(e) => setSelectedBoard(e.target.value)}
              className="task-select"
            >
              <option value="">Select a board...</option>
              {boards.map(board => (
                <option key={board.id} value={board.id}>{board.name}</option>
              ))}
            </select>
            {selectedBoard && (
              <select 
                value={selectedTask || ''} 
                onChange={(e) => setSelectedTask(e.target.value)}
                className="task-select"
              >
                <option value="">No task selected</option>
                {tasks.map(task => (
                  <option key={task.id} value={task.id}>
                    {task.title} ({task.status})
                  </option>
                ))}
              </select>
            )}
            </div>
          </>
        )}
        
        <div className="timer-circle" style={{ background: `conic-gradient(#f37335 ${progress}%, #f0f0f0 ${progress}%)` }}>
          <div className="timer-inner">
            <div className="timer-display">
              {formatTime(minutes, seconds)}
            </div>
            <div className="timer-label">
              {isBreak ? 'Break' : 'Work'}
            </div>
          </div>
        </div>

        <div className="timer-controls">
          <button onClick={toggleTimer} className="btn-timer primary">
            {isActive ? <Pause size={24} /> : <Play size={24} />}
            <span>{isActive ? 'Pause' : 'Start'}</span>
          </button>
          <button onClick={resetTimer} className="btn-timer secondary">
            <RotateCcw size={24} />
            <span>Reset</span>
          </button>
        </div>

        <div className="pomodoro-stats">
          <div className="stat-item">
            <div className="stat-value">{stats.totalSessions}</div>
            <div className="stat-label">Sessions</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.totalMinutes}</div>
            <div className="stat-label">Minutes</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.averagePerDay || 0}</div>
            <div className="stat-label">Avg/Day</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pomodoro;
