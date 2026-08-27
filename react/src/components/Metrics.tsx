import React from 'react';
import { MessageSquare, ThumbsUp, ThumbsDown, HelpCircle, ShieldCheck } from 'lucide-react';
import type { FeedbackRecord } from '../services/api';

interface MetricsProps {
  feedbacks: FeedbackRecord[];
}

export const Metrics: React.FC<MetricsProps> = ({ feedbacks }) => {
  const total = feedbacks.length;
  
  const positive = feedbacks.filter((f) => f.sentiment === 'positive').length;
  const negative = feedbacks.filter((f) => f.sentiment === 'negative').length;
  const neutral = feedbacks.filter((f) => f.sentiment === 'neutral').length;
  
  const avgConfidence = total > 0 
    ? feedbacks.reduce((acc, curr) => acc + curr.confidence, 0) / total 
    : 0;

  return (
    <div className="metrics-row">
      <div className="metric-card">
        <div className="metric-label" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
          <MessageSquare size={14} /> Total
        </div>
        <div className="metric-value">{total}</div>
      </div>
      
      <div className="metric-card" style={{ borderLeft: '2px solid rgba(16, 185, 129, 0.3)' }}>
        <div className="metric-label" style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
          <ThumbsUp size={14} /> Positive
        </div>
        <div className="metric-value" style={{ color: 'var(--success)' }}>{positive}</div>
      </div>
      
      <div className="metric-card" style={{ borderLeft: '2px solid rgba(244, 63, 94, 0.3)' }}>
        <div className="metric-label" style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
          <ThumbsDown size={14} /> Negative
        </div>
        <div className="metric-value" style={{ color: 'var(--danger)' }}>{negative}</div>
      </div>
      
      <div className="metric-card" style={{ borderLeft: '2px solid rgba(245, 158, 11, 0.3)' }}>
        <div className="metric-label" style={{ color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
          <HelpCircle size={14} /> Neutral
        </div>
        <div className="metric-value" style={{ color: 'var(--warning)' }}>{neutral}</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-label" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}>
          <ShieldCheck size={14} /> Avg Conf.
        </div>
        <div className="metric-value">{(avgConfidence * 100).toFixed(1)}%</div>
      </div>
    </div>
  );
};
