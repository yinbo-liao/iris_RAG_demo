import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import ErrorBoundary from './components/ErrorBoundary';
import KnowledgePage from './pages/KnowledgePage';
import HistoryPage from './pages/HistoryPage';
import AgentPage from './pages/AgentPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 pb-12">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Navigate to="/agents" replace />} />
              <Route path="/agents" element={<AgentPage />} />
              <Route path="/knowledge" element={<KnowledgePage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route
                path="*"
                element={
                  <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center">
                      <h2 className="text-3xl font-bold text-gray-300 mb-2">404</h2>
                      <p className="text-gray-400">Page not found</p>
                    </div>
                  </div>
                }
              />
            </Routes>
          </ErrorBoundary>
        </main>

        {/* Footer */}
        <footer className="border-t border-gray-200 bg-white py-4">
          <div className="max-w-7xl mx-auto px-4 text-center text-xs text-gray-400">
            Iris RAG — Multi-Agent Analytics over the Iris Dataset (Fisher, 1936)
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
