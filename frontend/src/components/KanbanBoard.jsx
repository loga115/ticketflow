import { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { Plus, Trash2, Timer } from 'lucide-react';
import './KanbanBoard.css';

const KanbanBoard = () => {
  const navigate = useNavigate();
  const [boards, setBoards] = useState([]);
  const [currentBoard, setCurrentBoard] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [taskTimeSpent, setTaskTimeSpent] = useState({});
  const [showNewBoard, setShowNewBoard] = useState(false);
  const [showNewTask, setShowNewTask] = useState(false);
  const [newBoardName, setNewBoardName] = useState('');
  const [newTaskData, setNewTaskData] = useState({ title: '', description: '', status: 'todo', priority: 'medium' });

  useEffect(() => {
    fetchBoards();
  }, []);

  useEffect(() => {
    if (currentBoard) {
      fetchTasks(currentBoard.id);
    }
  }, [currentBoard]);

  const fetchBoards = async () => {
    try {
      const response = await api.get('/boards');
      setBoards(response.data);
      if (response.data.length > 0 && !currentBoard) {
        setCurrentBoard(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching boards:', error);
    }
  };

  const fetchTasks = async (boardId) => {
    try {
      const response = await api.get(`/tasks/board/${boardId}`);
      setTasks(response.data);
      
      // Fetch time spent for each task
      const timeSpent = {};
      for (const task of response.data) {
        try {
          const timeResponse = await api.get(`/timetracker?task_id=${task.id}`);
          const entries = timeResponse.data;
          const totalMinutes = entries.reduce((sum, entry) => {
            if (entry.start_time && entry.end_time) {
              const duration = (new Date(entry.end_time) - new Date(entry.start_time)) / 1000 / 60;
              return sum + duration;
            }
            return sum;
          }, 0);
          timeSpent[task.id] = Math.round(totalMinutes);
        } catch (error) {
          console.error(`Error fetching time for task ${task.id}:`, error);
          timeSpent[task.id] = 0;
        }
      }
      setTaskTimeSpent(timeSpent);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const createBoard = async () => {
    if (!newBoardName.trim()) return;
    try {
      const response = await api.post('/boards', { name: newBoardName });
      setBoards([...boards, response.data]);
      setCurrentBoard(response.data);
      setNewBoardName('');
      setShowNewBoard(false);
    } catch (error) {
      console.error('Error creating board:', error);
    }
  };

  const createTask = async () => {
    if (!newTaskData.title.trim()) return;
    if (!currentBoard) {
      alert('Please create a board first!');
      return;
    }
    try {
      const response = await api.post('/tasks', {
        ...newTaskData,
        board_id: currentBoard.id,
      });
      setTasks([...tasks, response.data]);
      setNewTaskData({ title: '', description: '', status: 'todo', priority: 'medium' });
      setShowNewTask(false);
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Failed to create task. Please try again.');
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await api.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const startPomodoroForTask = async (task) => {
    try {
      // Navigate to Pomodoro page with task info
      navigate('/pomodoro', {
        state: {
          taskId: task.id,
          boardId: currentBoard.id
        }
      });
    } catch (error) {
      console.error('Error starting pomodoro:', error);
      alert('Failed to start Pomodoro session');
    }
  };

  const onDragEnd = async (result) => {
    if (!result.destination) return;

    const { source, destination, draggableId } = result;
    
    if (source.droppableId === destination.droppableId && source.index === destination.index) {
      return;
    }

    const newStatus = destination.droppableId;
    try {
      await api.put(`/tasks/${draggableId}`, { status: newStatus });
      const updatedTasks = tasks.map(task =>
        task.id === draggableId ? { ...task, status: newStatus } : task
      );
      setTasks(updatedTasks);
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status);
  };

  const columns = [
    { id: 'todo', title: 'To Do', color: '#3b82f6' },
    { id: 'in_progress', title: 'In Progress', color: '#f59e0b' },
    { id: 'done', title: 'Done', color: '#10b981' }
  ];

  return (
    <div className="kanban-container">
      <div className="kanban-header">
        <div className="board-selector">
          <select 
            value={currentBoard?.id || ''} 
            onChange={(e) => setCurrentBoard(boards.find(b => b.id === e.target.value))}
          >
            {boards.map(board => (
              <option key={board.id} value={board.id}>{board.name}</option>
            ))}
          </select>
          <button onClick={() => setShowNewBoard(true)} className="btn-secondary">
            <Plus size={20} /> New Board
          </button>
        </div>
        
        <button onClick={() => setShowNewTask(true)} className="btn-primary">
          <Plus size={20} /> New Task
        </button>
      </div>

      {showNewBoard && (
        <div className="modal">
          <div className="modal-content">
            <h3>Create New Board</h3>
            <input
              type="text"
              placeholder="Board name"
              value={newBoardName}
              onChange={(e) => setNewBoardName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && createBoard()}
            />
            <div className="modal-actions">
              <button onClick={createBoard} className="btn-primary">Create</button>
              <button onClick={() => setShowNewBoard(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {showNewTask && (
        <div className="modal">
          <div className="modal-content">
            <h3>Create New Task</h3>
            <input
              type="text"
              placeholder="Task title"
              value={newTaskData.title}
              onChange={(e) => setNewTaskData({ ...newTaskData, title: e.target.value })}
            />
            <textarea
              placeholder="Description (optional)"
              value={newTaskData.description}
              onChange={(e) => setNewTaskData({ ...newTaskData, description: e.target.value })}
            />
            <select
              value={newTaskData.priority}
              onChange={(e) => setNewTaskData({ ...newTaskData, priority: e.target.value })}
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
            <div className="modal-actions">
              <button onClick={createTask} className="btn-primary">Create</button>
              <button onClick={() => setShowNewTask(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {currentBoard && (
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="kanban-columns">
            {columns.map(column => (
              <div key={column.id} className="kanban-column">
                <div className="column-header" style={{ borderTopColor: column.color }}>
                  <h3>{column.title}</h3>
                  <span className="task-count">{getTasksByStatus(column.id).length}</span>
                </div>
                
                <Droppable droppableId={column.id} key={column.id}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`column-content ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                    >
                    {getTasksByStatus(column.id).map((task, index) => (
                      <Draggable key={task.id} draggableId={String(task.id)} index={index}>
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`task-card ${snapshot.isDragging ? 'dragging' : ''} priority-${task.priority}`}
                          >
                            <div className="task-header">
                              <h4>{task.title}</h4>
                              <div className="task-actions">
                                {task.status !== 'done' && (
                                  <button 
                                    onClick={(e) => { e.stopPropagation(); startPomodoroForTask(task); }} 
                                    className="btn-icon-small btn-pomodoro"
                                    title="Start Pomodoro"
                                  >
                                    <Timer size={16} />
                                  </button>
                                )}
                                <button onClick={(e) => { e.stopPropagation(); deleteTask(task.id); }} className="btn-icon-small">
                                  <Trash2 size={16} />
                                </button>
                              </div>
                            </div>
                            {task.description && <p className="task-description">{task.description}</p>}
                            <div className="task-footer">
                              <span className={`priority-badge priority-${task.priority}`}>
                                {task.priority}
                              </span>
                              {taskTimeSpent[task.id] > 0 && (
                                <span className="time-spent-badge" title="Time tracked">
                                  ⏱️ {taskTimeSpent[task.id]}m
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
      )}
    </div>
  );
};

export default KanbanBoard;
