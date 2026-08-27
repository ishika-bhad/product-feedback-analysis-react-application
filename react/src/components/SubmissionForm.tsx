import React, { useState } from 'react';
import { Send, AlertCircle, CheckCircle, ThumbsUp, ThumbsDown, HelpCircle } from 'lucide-react';
import { apiService } from '../services/api';
import type { FeedbackData } from '../services/api';

interface SubmissionFormProps {
  onSubmissionSuccess: (submittedProduct: string) => void;
}

export const SubmissionForm: React.FC<SubmissionFormProps> = ({ onSubmissionSuccess }) => {
  const [productName, setProductName] = useState('');
  const [feedbackText, setFeedbackText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<FeedbackData | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName.trim() || !feedbackText.trim()) return;

    setLoading(true);
    setError(null);
    setSuccess(null);
    setResult(null);

    try {
      const data = await apiService.submitFeedback(
        productName.trim(),
        feedbackText.trim()
      );
      
      setResult(data);
      setSuccess('Feedback analyzed and cataloged successfully.');
      setProductName('');
      setFeedbackText('');
      // Signal parent of new entry to refresh metrics and history
      onSubmissionSuccess(data.product_name);
    } catch (err: any) {
      setError(err.message || 'An error occurred while submitting feedback.');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentDetails = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return {
          color: 'var(--success)',
          bg: 'var(--success-bg)',
          icon: <ThumbsUp size={16} />
        };
      case 'negative':
        return {
          color: 'var(--danger)',
          bg: 'var(--danger-bg)',
          icon: <ThumbsDown size={16} />
        };
      default:
        return {
          color: 'var(--warning)',
          bg: 'var(--warning-bg)',
          icon: <HelpCircle size={16} />
        };
    }
  };

  return (
    <div className="glass-card">
      <h2 className="card-title">
        <Send size={18} style={{ color: 'var(--primary)' }} /> Submit Feedback
      </h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="product_name" className="form-label">
            Product Name
          </label>
          <input
            type="text"
            id="product_name"
            className="form-input"
            placeholder="e.g. Cloud Database Engine"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="feedback_text" className="form-label">
            Feedback Text
          </label>
          <textarea
            id="feedback_text"
            className="form-input form-textarea"
            placeholder="Provide customer feedback details..."
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <button 
          type="submit" 
          className="btn btn-primary" 
          disabled={loading || !productName.trim() || !feedbackText.trim()}
        >
          {loading ? (
            <>
              <span className="btn-loader" /> Submitting...
            </>
          ) : (
            'Analyze Sentiment'
          )}
        </button>
      </form>

      {error && (
        <div className="alert alert-danger" style={{ marginTop: '1.25rem' }}>
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert alert-success" style={{ marginTop: '1.25rem' }}>
          <CheckCircle size={16} style={{ flexShrink: 0 }} />
          <span>{success}</span>
        </div>
      )}

      {result && (
        <div className="sentiment-indicator-card">
          <div className="indicator-row">
            <span className="indicator-title">Sentiment Tag</span>
            <span className={`badge badge-${result.sentiment}`}>
              {getSentimentDetails(result.sentiment).icon} {result.sentiment}
            </span>
          </div>
          
          <div>
            <div className="indicator-row">
              <span className="indicator-title">Confidence Level</span>
              <span style={{ fontWeight: 700, color: getSentimentDetails(result.sentiment).color }}>
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="confidence-bar-bg">
              <div
                className="confidence-bar-fill"
                style={{
                  width: `${result.confidence * 100}%`,
                  backgroundColor: getSentimentDetails(result.sentiment).color,
                }}
              />
            </div>
          </div>
          
          <div className="sentiment-quote">
            "{result.feedback}"
          </div>
        </div>
      )}
    </div>
  );
};
