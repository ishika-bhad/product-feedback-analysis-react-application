import axios from 'axios';

// TypeScript interfaces matching backend models
export interface APIResponse<T> {
  success: boolean;
  status_code: number;
  message: string;
  error_message: string | null;
  data: T | null;
}

export interface FeedbackData {
  request_id: string;
  product_name: string;
  product_id: number;
  feedback: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  created_at: string;
}

export interface FeedbackRecord {
  request_id: string;
  feedback: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  created_at: string;
}

export interface HistoricalData {
  request_id: string;
  product_id: number;
  product_name: string;
  feedbacks: FeedbackRecord[];
}

export interface ProductItem {
  id: number;
  name: string;
}

/**
 * Generates a standard UUID-format request ID on the frontend.
 */
export function generateUUID(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  // Fallback for older browsers
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

const apiURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const apiToken = import.meta.env.VITE_API_BEARER_TOKEN || '';

const client = axios.create({
  baseURL: apiURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Configure Request interceptor to attach bearer token
client.interceptors.request.use(
  (config) => {
    if (apiToken) {
      config.headers.Authorization = `Bearer ${apiToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const apiService = {
  /**
   * Submits product feedback to the FastAPI backend.
   * Generates a UUID request_id and validates the returned request_id.
   */
  async submitFeedback(productName: string, feedbackText: string): Promise<FeedbackData> {
    const generatedId = generateUUID();

    const response = await client.post<APIResponse<FeedbackData>>('/api/feedback', {
      request_id: generatedId,
      product_name: productName,
      product_feedback: feedbackText,
    });

    const resEnvelope = response.data;
    if (!resEnvelope.success || !resEnvelope.data) {
      throw new Error(
        resEnvelope.error_message || resEnvelope.message || 'Failed to analyze feedback.'
      );
    }

    // Verify request ID matches
    if (resEnvelope.data.request_id !== generatedId) {
      throw new Error(
        `Security Alert: Request ID integrity breach. Sent: ${generatedId}, Received: ${resEnvelope.data.request_id}`
      );
    }

    return resEnvelope.data;
  },

  /**
   * Lists all products already recorded in the backend.
   */
  async getProducts(): Promise<ProductItem[]> {
    const response = await client.get<APIResponse<ProductItem[]>>('/api/feedback/products');
    const resEnvelope = response.data;
    if (!resEnvelope.success || !resEnvelope.data) {
      throw new Error(
        resEnvelope.error_message || resEnvelope.message || 'Failed to list products.'
      );
    }
    return resEnvelope.data;
  },

  /**
   * Retrieves historical analysis results for a specific product ID.
   * Generates a UUID request_id, sends in header, and validates the response request_id.
   */
  async getHistoricalSentiment(productId: number): Promise<HistoricalData> {
    const generatedId = generateUUID();

    const response = await client.get<APIResponse<HistoricalData>>(`/api/feedback/historical/${productId}`, {
      headers: {
        'x-request-id': generatedId,
      },
    });

    const resEnvelope = response.data;
    if (!resEnvelope.success || !resEnvelope.data) {
      throw new Error(
        resEnvelope.error_message || resEnvelope.message || 'Failed to get history.'
      );
    }

    // Verify request ID matches
    if (resEnvelope.data.request_id !== generatedId) {
      throw new Error(
        `Security Alert: Retrieval Request ID integrity breach. Sent: ${generatedId}, Received: ${resEnvelope.data.request_id}`
      );
    }

    return resEnvelope.data;
  },
};
