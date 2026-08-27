import React from 'react';
import { History, ThumbsUp, ThumbsDown, HelpCircle, Calendar, Shield } from 'lucide-react';
import type { ProductItem, HistoricalData } from '../services/api';
import { TrendChart } from '../charts/TrendChart';

interface HistoricalViewProps {
  products: ProductItem[];
  selectedProductId: number | null;
  onSelectProduct: (id: number) => void;
  historicalData: HistoricalData | null;
  loading: boolean;
  error: string | null;
}

export const HistoricalView: React.FC<HistoricalViewProps> = ({
  products,
  selectedProductId,
  onSelectProduct,
  historicalData,
  loading,
  error,
}) => {
  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <ThumbsUp size={12} />;
      case 'negative':
        return <ThumbsDown size={12} />;
      default:
        return <HelpCircle size={12} />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="glass-card historical-container">
      <div>
        <div className="history-header">
          <h2 className="card-title" style={{ margin: 0 }}>
            <History size={18} style={{ color: 'var(--primary)' }} /> Product History
          </h2>
          
          <div style={{ minWidth: '220px' }}>
            <select
              className="form-input form-select"
              value={selectedProductId || ''}
              onChange={(e) => {
                const val = e.target.value;
                if (val) onSelectProduct(Number(val));
              }}
              disabled={loading}
            >
              <option value="" disabled>Select a product...</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} (ID: {p.id})
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <div className="alert alert-danger" style={{ marginTop: '1rem' }}>
            {error}
          </div>
        )}
      </div>

      {loading ? (
        <div className="loader-container">
          <span className="loader" />
          <p>Retrieving historical logs...</p>
        </div>
      ) : !selectedProductId ? (
        <div className="empty-state">
          <History size={40} className="empty-state-icon" />
          <h3>No Product Selected</h3>
          <p>Select a product from the list to display sentiment metrics and analysis trends over time.</p>
        </div>
      ) : historicalData && historicalData.feedbacks.length === 0 ? (
        <div className="empty-state">
          <History size={40} className="empty-state-icon" />
          <h3>No Records Found</h3>
          <p>No feedbacks recorded yet for <strong>{historicalData.product_name}</strong>.</p>
        </div>
      ) : historicalData ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div>
            <h3 style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontWeight: 600 }}>
              Sentiment Trend Timeline
            </h3>
            <TrendChart feedbacks={historicalData.feedbacks} />
          </div>

          <div>
            <h3 style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '1rem', fontWeight: 600 }}>
              Feedback Entries ({historicalData.feedbacks.length})
            </h3>
            
            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Feedback Text</th>
                    <th>Sentiment</th>
                    <th>Confidence</th>
                    <th>Date & Time</th>
                  </tr>
                </thead>
                <tbody>
                  {historicalData.feedbacks.map((fb) => (
                    <tr key={fb.request_id}>
                      <td className="feedback-text-cell" title={fb.feedback}>
                        {fb.feedback}
                      </td>
                      <td>
                        <span className={`badge badge-${fb.sentiment}`}>
                          {getSentimentIcon(fb.sentiment)} {fb.sentiment}
                        </span>
                      </td>
                      <td>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', fontFamily: 'var(--font-mono)' }}>
                          <Shield size={12} className="text-muted" /> {(fb.confidence * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="metadata-cell">
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                          <Calendar size={12} /> {formatDate(fb.created_at)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
