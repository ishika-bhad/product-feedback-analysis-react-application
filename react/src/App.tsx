import './App.css';
import { useState, useEffect, useRef } from 'react';
import { BarChart3 } from 'lucide-react';
import { apiService } from './services/api';
import type { ProductItem, HistoricalData } from './services/api';
import { Metrics } from './components/Metrics';
import { SubmissionForm } from './components/SubmissionForm';
import { HistoricalView } from './components/HistoricalView';

function App() {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [historicalData, setHistoricalData] = useState<HistoricalData | null>(null);

  const [productsLoading, setProductsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [productsError, setProductsError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // Ref to track current selectedProductId inside async callbacks without stale closure
  const selectedProductIdRef = useRef<number | null>(null);
  selectedProductIdRef.current = selectedProductId;

  // Load products list from database
  const loadProducts = async (autoSelectName?: string) => {
    setProductsLoading(true);
    setProductsError(null);
    try {
      const data = await apiService.getProducts();
      setProducts(data);

      if (data.length > 0) {
        if (autoSelectName) {
          const matched = data.find(
            (p) => p.name.toLowerCase() === autoSelectName.toLowerCase()
          );
          if (matched) {
            setSelectedProductId(matched.id);
            return;
          }
        }

        // Do NOT auto-select on initial load — the user must choose a product
        // or submit feedback to trigger history. This prevents 404 errors for
        // stale product IDs that may no longer exist in the database.
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load products listing.';
      setProductsError(message);
    } finally {
      setProductsLoading(false);
    }
  };

  // Load historical feedback records for a specific product
  const loadHistory = async (id: number) => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const data = await apiService.getHistoricalSentiment(id);
      setHistoricalData(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to retrieve historical data.';
      setHistoryError(message);
      setHistoricalData(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Load product list on initial mount
  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch history whenever selected product changes
  useEffect(() => {
    if (selectedProductId !== null) {
      loadHistory(selectedProductId);
    } else {
      setHistoricalData(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProductId]);

  const handleSubmissionSuccess = (submittedProduct: string) => {
    loadProducts(submittedProduct);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="brand-title">
          <BarChart3 size={24} style={{ color: 'var(--primary)' }} /> SENTIMENT ANALYTICS
        </h1>
        <div className="status-badge">
          <span className="status-dot" /> Backend Online
        </div>
      </header>

      {/* Overview Analytics Metrics — driven by currently selected product's feedbacks */}
      <Metrics feedbacks={historicalData?.feedbacks || []} />

      <main className="dashboard-grid">
        {/* Left column: Feedback submission form */}
        <section>
          <SubmissionForm onSubmissionSuccess={handleSubmissionSuccess} />
        </section>

        {/* Right column: Historical analytics and trend chart */}
        <section>
          <HistoricalView
            products={products}
            selectedProductId={selectedProductId}
            onSelectProduct={setSelectedProductId}
            historicalData={historicalData}
            loading={historyLoading || productsLoading}
            error={historyError || productsError}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
