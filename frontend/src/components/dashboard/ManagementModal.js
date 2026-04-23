import React, { useState, useEffect } from 'react';
import './ManagementModal.css';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ManagementModal({ isOpen, onClose, onRefresh }) {
  const [activeTab, setActiveTab] = useState('feature');
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Form states
  const [featureForm, setFeatureForm] = useState({
    name: '',
    model_provider: 'openai',
    model_name: '',
    cost_per_1k_input_tokens: 0.01,
    cost_per_1k_output_tokens: 0.03,
  });

  const [usageForm, setUsageForm] = useState({
    feature_id: '',
    model_used: '',
    input_tokens: 100,
    output_tokens: 50,
  });

  const [metricForm, setMetricForm] = useState({
    feature_id: '',
    user_id: 'user_' + Math.floor(Math.random() * 1000),
    engagement_score: 5,
    retention_flag: false,
    conversion_flag: false,
  });

  useEffect(() => {
    if (isOpen) {
      fetchFeatures();
      setNotification(null);
    }
  }, [isOpen]);

  const fetchFeatures = async () => {
    try {
      const res = await fetch(`${API_BASE}/features`);
      if (res.ok) {
        const data = await res.json();
        setFeatures(data);
        if (data.length > 0 && !usageForm.feature_id) {
          setUsageForm(prev => ({ ...prev, feature_id: data[0].id }));
          setMetricForm(prev => ({ ...prev, feature_id: data[0].id }));
        }
      }
    } catch (err) {
      console.error("Failed to fetch features", err);
    }
  };

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleFeatureSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/features`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(featureForm)
      });
      
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create feature');
      
      showNotification('Feature registered successfully! 🚀');
      fetchFeatures();
      setFeatureForm({ ...featureForm, name: '', model_name: '' });
      if (onRefresh) onRefresh();
    } catch (err) {
      showNotification(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUsageSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...usageForm,
        user_id: 'user_' + Math.floor(Math.random() * 1000),
        total_tokens: parseInt(usageForm.input_tokens || 0) + parseInt(usageForm.output_tokens || 0)
      };
      
      const res = await fetch(`${API_BASE}/usage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error('Failed to log usage');
      
      showNotification('Usage logged successfully! 💸');
      if (onRefresh) onRefresh();
    } catch (err) {
      showNotification(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleMetricSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...metricForm,
        engagement_score: (parseFloat(metricForm.engagement_score) || 0) / 10.0
      };

      const res = await fetch(`${API_BASE}/metrics`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error('Failed to log metric');
      
      showNotification('Metric logged successfully! 📈');
      setMetricForm({ ...metricForm, user_id: 'user_' + Math.floor(Math.random() * 1000) });
      if (onRefresh) onRefresh();
    } catch (err) {
      showNotification(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">⚙️ Management Console</h2>
          <button className="btn-close" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-tabs">
          <button 
            className={`modal-tab ${activeTab === 'feature' ? 'active' : ''}`}
            onClick={() => setActiveTab('feature')}
          >
            Register Feature
          </button>
          <button 
            className={`modal-tab ${activeTab === 'usage' ? 'active' : ''}`}
            onClick={() => setActiveTab('usage')}
          >
            Log Usage
          </button>
          <button 
            className={`modal-tab ${activeTab === 'metric' ? 'active' : ''}`}
            onClick={() => setActiveTab('metric')}
          >
            Log Metrics
          </button>
        </div>

        <div className="modal-body">
          {notification && (
            <div className={`notification ${notification.type}`}>
              {notification.msg}
            </div>
          )}

          {activeTab === 'feature' && (
            <form onSubmit={handleFeatureSubmit}>
              <div className="form-group">
                <label className="form-label">Feature Name</label>
                <input 
                  type="text" 
                  className="form-input" 
                  required
                  placeholder="e.g. Chat Assistant"
                  value={featureForm.name}
                  onChange={e => setFeatureForm({...featureForm, name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Model Provider</label>
                <select 
                  className="form-select"
                  value={featureForm.model_provider}
                  onChange={e => setFeatureForm({...featureForm, model_provider: e.target.value})}
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google">Google</option>
                  <option value="custom">Custom / Open Source</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Cost per 1k Input Tokens ($)</label>
                <input 
                  type="number" 
                  step="0.0001"
                  className="form-input" 
                  required
                  value={featureForm.cost_per_1k_input_tokens}
                  onChange={e => setFeatureForm({...featureForm, cost_per_1k_input_tokens: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Cost per 1k Output Tokens ($)</label>
                <input 
                  type="number" 
                  step="0.0001"
                  className="form-input" 
                  required
                  value={featureForm.cost_per_1k_output_tokens}
                  onChange={e => setFeatureForm({...featureForm, cost_per_1k_output_tokens: e.target.value})}
                />
              </div>
              <div className="form-actions">
                <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Registering...' : 'Register Feature'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'usage' && (
            <form onSubmit={handleUsageSubmit}>
              <div className="form-group">
                <label className="form-label">Target Feature</label>
                <select 
                  className="form-select"
                  required
                  value={usageForm.feature_id}
                  onChange={e => setUsageForm({...usageForm, feature_id: parseInt(e.target.value)})}
                >
                  <option value="">-- Select a feature --</option>
                  {features.map(f => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Input Tokens</label>
                <input 
                  type="number" 
                  className="form-input" 
                  required
                  value={usageForm.input_tokens}
                  onChange={e => setUsageForm({...usageForm, input_tokens: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Output Tokens</label>
                <input 
                  type="number" 
                  className="form-input" 
                  required
                  value={usageForm.output_tokens}
                  onChange={e => setUsageForm({...usageForm, output_tokens: e.target.value})}
                />
              </div>
              <div className="form-actions">
                <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Logging...' : 'Log Usage'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'metric' && (
            <form onSubmit={handleMetricSubmit}>
              <div className="form-group">
                <label className="form-label">Target Feature</label>
                <select 
                  className="form-select"
                  required
                  value={metricForm.feature_id}
                  onChange={e => setMetricForm({...metricForm, feature_id: parseInt(e.target.value)})}
                >
                  <option value="">-- Select a feature --</option>
                  {features.map(f => (
                    <option key={f.id} value={f.id}>{f.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Engagement Score (1-10)</label>
                <input 
                  type="number" 
                  min="1" max="10"
                  className="form-input" 
                  required
                  value={metricForm.engagement_score}
                  onChange={e => setMetricForm({...metricForm, engagement_score: e.target.value})}
                />
              </div>
              <div className="form-group checkbox-group">
                <input 
                  type="checkbox" 
                  id="retention"
                  className="form-checkbox" 
                  checked={metricForm.retention_flag}
                  onChange={e => setMetricForm({...metricForm, retention_flag: e.target.checked})}
                />
                <label htmlFor="retention" className="form-label" style={{marginBottom: 0}}>
                  User was Retained
                </label>
              </div>
              <div className="form-group checkbox-group">
                <input 
                  type="checkbox" 
                  id="conversion"
                  className="form-checkbox" 
                  checked={metricForm.conversion_flag}
                  onChange={e => setMetricForm({...metricForm, conversion_flag: e.target.checked})}
                />
                <label htmlFor="conversion" className="form-label" style={{marginBottom: 0}}>
                  User Converted (Paid)
                </label>
              </div>
              <div className="form-actions">
                <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Logging...' : 'Log Metric'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
