import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import type { FeedbackRecord } from '../services/api';

interface TrendChartProps {
  feedbacks: FeedbackRecord[];
}

export const TrendChart: React.FC<TrendChartProps> = ({ feedbacks }) => {
  // Sort feedbacks chronologically (ascending order)
  const sortedFeedbacks = [...feedbacks].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );

  // Map feedbacks to line chart nodes
  const data = sortedFeedbacks.map((f) => {
    let numericSentiment = 0;
    if (f.sentiment === 'positive') numericSentiment = 1;
    else if (f.sentiment === 'negative') numericSentiment = -1;
    
    const formattedDate = new Date(f.created_at).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

    return {
      date: formattedDate,
      score: numericSentiment,
      confidence: f.confidence,
      sentiment: f.sentiment,
    };
  });

  if (feedbacks.length === 0) {
    return (
      <div className="empty-state" style={{ height: '250px' }}>
        No historical trends available. Add feedback to see trends.
      </div>
    );
  }

  // Custom tooltips to present clean sentiment labels instead of integers
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      let sentimentColor = 'var(--warning)';
      if (dataPoint.sentiment === 'positive') sentimentColor = 'var(--success)';
      if (dataPoint.sentiment === 'negative') sentimentColor = 'var(--danger)';

      return (
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            fontSize: '0.85rem',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
          }}
        >
          <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{dataPoint.date}</p>
          <p style={{ margin: '0.25rem 0 0 0', fontWeight: 'bold', color: sentimentColor }}>
            Sentiment: {dataPoint.sentiment.toUpperCase()}
          </p>
          <p style={{ margin: 0, color: 'var(--text-primary)' }}>
            Confidence: {(dataPoint.confidence * 100).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 20, left: -20, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="date"
            stroke="var(--text-muted)"
            fontSize={11}
            tickLine={false}
          />
          <YAxis
            domain={[-1, 1]}
            ticks={[-1, 0, 1]}
            tickFormatter={(tick) => {
              if (tick === 1) return 'Pos';
              if (tick === -1) return 'Neg';
              return 'Neu';
            }}
            stroke="var(--text-muted)"
            fontSize={11}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="score"
            name="Sentiment"
            stroke="url(#lineGradient)"
            strokeWidth={3}
            dot={{ r: 5, strokeWidth: 0, fill: 'var(--primary)' }}
            activeDot={{ r: 7 }}
          />
          <defs>
            <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="50%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#ec4899" />
            </linearGradient>
          </defs>
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
