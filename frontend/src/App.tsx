import { BrowserRouter, Route, Routes } from './router'
import { Layout } from './components/Layout/Layout'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { CampaignPage } from './pages/CampaignPage'
import { JournalistsPage } from './pages/JournalistsPage'
import { AnalysisPage } from './pages/AnalysisPage'
import { JournalistDetailsPage } from './pages/JournalistDetailsPage'
import { PitchPage } from './pages/PitchPage'
import { NotFoundPage } from './pages/NotFoundPage'
import './App.css'

export function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<CampaignPage />} />
            <Route path="/campaign" element={<CampaignPage />} />
            <Route path="/journalists" element={<JournalistsPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/journalists/details" element={<JournalistDetailsPage />} />
            <Route path="/pitch" element={<PitchPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
