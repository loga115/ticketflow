import { useState, useEffect, useRef } from 'react';
import { Plus, Search, Edit2, Trash2, X, Users } from 'lucide-react';
import api from '../lib/api';
import { useApiNotifications } from '../hooks/useApiNotifications';
import './EmployeeManager.css';

const EmployeeManager = () => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [showModal, setShowModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    position: '',
    department: '',
    phone: '',
    salary: '',
    specializations: []
  });
  
  const { notifySuccess, notifyError } = useApiNotifications();
  const previousEmployeesRef = useRef([]);

  useEffect(() => {
    fetchEmployees();
    
    // Auto-refresh every 3 seconds
    const interval = setInterval(() => {
      fetchEmployees();
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  // Detect employee changes and trigger notifications
  useEffect(() => {
    const previousEmployees = previousEmployeesRef.current;
    
    if (previousEmployees.length === 0) {
      // First load, just store the employees
      previousEmployeesRef.current = employees;
      return;
    }

    // Check for new employees
    employees.forEach(employee => {
      const existed = previousEmployees.find(e => e.id === employee.id);
      if (!existed) {
        notifySuccess('New Employee Added', `${employee.name} has joined the team`);
      }
    });

    // Check for deleted employees
    previousEmployees.forEach(oldEmployee => {
      const stillExists = employees.find(e => e.id === oldEmployee.id);
      if (!stillExists) {
        notifySuccess('Employee Removed', `${oldEmployee.name} has been removed from the team`);
      }
    });

    // Update the ref
    previousEmployeesRef.current = employees;
  }, [employees, notifySuccess]);

  useEffect(() => {
    filterEmployees();
  }, [employees, searchTerm, departmentFilter]);

  const fetchEmployees = async () => {
    try {
      const response = await api.get('/employees');
      setEmployees(response.data?.employees || response.employees || []);
    } catch (error) {
      console.error('Error fetching employees:', error);
      setEmployees([]);
    }
  };

  const filterEmployees = () => {
    let filtered = employees;

    if (searchTerm) {
      filtered = filtered.filter(emp =>
        emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        emp.position.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (departmentFilter !== 'all') {
      filtered = filtered.filter(emp => emp.department === departmentFilter);
    }

    setFilteredEmployees(filtered);
  };

  const getDepartments = () => {
    const depts = [...new Set(employees.map(emp => emp.department).filter(Boolean))];
    return depts.sort();
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      position: '',
      department: '',
      phone: '',
      salary: '',
      specializations: []
    });
    setEditingEmployee(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Convert specializations to array if it's still a string
      let specializations = formData.specializations;
      if (typeof specializations === 'string') {
        specializations = specializations.split(',').map(s => s.trim()).filter(Boolean);
      }
      
      const submitData = {
        ...formData,
        salary: formData.salary ? parseFloat(formData.salary) : null,
        specializations: specializations || []
      };

      console.log('Submitting employee data:', submitData);

      if (editingEmployee) {
        await api.put(`/employees/${editingEmployee.id}`, submitData);
        notifySuccess('Employee Updated', `${submitData.name} has been updated successfully`);
      } else {
        await api.post('/employees', submitData);
        notifySuccess('Employee Created', `${submitData.name} has been added to the team`);
      }

      fetchEmployees();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Error saving employee:', error);
      notifyError('Save Failed', 'Failed to save employee. Please try again.');
    }
  };

  const handleEdit = (employee) => {
    setEditingEmployee(employee);
    setFormData({
      name: employee.name,
      email: employee.email,
      position: employee.position,
      department: employee.department || '',
      phone: employee.phone || '',
      salary: employee.salary || '',
      specializations: employee.specializations || []
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this employee?')) return;

    try {
      const employee = employees.find(e => e.id === id);
      await api.delete(`/employees/${id}`);
      
      if (employee) {
        notifySuccess('Employee Deleted', `${employee.name} has been removed`);
      }
      
      fetchEmployees();
    } catch (error) {
      console.error('Error deleting employee:', error);
      notifyError('Delete Failed', 'Failed to delete employee. Please try again.');
    }
  };

  const formatSalary = (salary) => {
    if (!salary) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(salary);
  };

  return (
    <div className="employee-manager">
      <div className="employee-header">
        <div className="header-title">
          <Users size={32} />
          <h2>Employee Management</h2>
        </div>
        <button onClick={() => { resetForm(); setShowModal(true); }} className="btn-add-employee">
          <Plus size={20} />
          Add Employee
        </button>
      </div>

      <div className="employee-filters">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search employees..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <select
          value={departmentFilter}
          onChange={(e) => setDepartmentFilter(e.target.value)}
          className="department-filter"
        >
          <option value="all">All Departments</option>
          {getDepartments().map(dept => (
            <option key={dept} value={dept}>{dept}</option>
          ))}
        </select>
      </div>

      <div className="employee-stats">
        <div className="stat-card">
          <div className="stat-value">{employees.length}</div>
          <div className="stat-label">Total Employees</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{getDepartments().length}</div>
          <div className="stat-label">Departments</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{filteredEmployees.length}</div>
          <div className="stat-label">Showing</div>
        </div>
      </div>

      <div className="employees-grid">
        {filteredEmployees.map(employee => (
          <div key={employee.id} className="employee-card">
            <div className="employee-card-header">
              <h3>{employee.name}</h3>
              <div className="employee-actions">
                <button onClick={() => handleEdit(employee)} className="btn-icon">
                  <Edit2 size={18} />
                </button>
                <button onClick={() => handleDelete(employee.id)} className="btn-icon btn-delete">
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
            <div className="employee-details">
              <div className="detail-row">
                <span className="label">Position:</span>
                <span className="value">{employee.position}</span>
              </div>
              {employee.department && (
                <div className="detail-row">
                  <span className="label">Department:</span>
                  <span className="value">{employee.department}</span>
                </div>
              )}
              <div className="detail-row">
                <span className="label">Email:</span>
                <span className="value email">{employee.email}</span>
              </div>
              {employee.phone && (
                <div className="detail-row">
                  <span className="label">Phone:</span>
                  <span className="value">{employee.phone}</span>
                </div>
              )}
              {employee.salary && (
                <div className="detail-row">
                  <span className="label">Salary:</span>
                  <span className="value salary">{formatSalary(employee.salary)}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredEmployees.length === 0 && (
        <div className="empty-state">
          <Users size={64} />
          <h3>No employees found</h3>
          <p>Add your first employee to get started</p>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingEmployee ? 'Edit Employee' : 'Add New Employee'}</h2>
              <button onClick={() => setShowModal(false)} className="btn-close">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Position *</label>
                <input
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Department</label>
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Specializations (comma-separated)</label>
                <input
                  type="text"
                  name="specializations"
                  value={Array.isArray(formData.specializations) ? formData.specializations.join(', ') : formData.specializations || ''}
                  onChange={(e) => {
                    setFormData(prev => ({ ...prev, specializations: e.target.value }));
                  }}
                  onBlur={(e) => {
                    const value = e.target.value;
                    const specs = value.split(',').map(s => s.trim()).filter(Boolean);
                    setFormData(prev => ({ ...prev, specializations: specs }));
                  }}
                  placeholder="e.g., Python, React, Backend Development"
                />
              </div>

              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>Salary</label>
                <input
                  type="number"
                  name="salary"
                  value={formData.salary}
                  onChange={handleInputChange}
                  step="0.01"
                  min="0"
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingEmployee ? 'Update' : 'Create'} Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeeManager;
