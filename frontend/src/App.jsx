import React, { useState } from 'react'
import { ThemeProvider } from './context/ThemeContext'
import Layout from './layouts/Layout'
import DashboardPage from './pages/DashboardPage'
import LibraryPage from './pages/LibraryPage'
import WorkspacePage from './pages/WorkspacePage'
import AssistantPage from './pages/AssistantPage'
import ComparePage from './pages/ComparePage'
import GapsPage from './pages/GapsPage'
import GraphPage from './pages/GraphPage'
import EvaluationPage from './pages/EvaluationPage'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedPaperId, setSelectedPaperId] = useState(null)

  return (
    <ThemeProvider>
      <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
        {activeTab === 'dashboard' && (
          <DashboardPage
            setActiveTab={setActiveTab}
            setSelectedPaperId={setSelectedPaperId}
          />
        )}
        {activeTab === 'library' && (
          <LibraryPage
            setActiveTab={setActiveTab}
            setSelectedPaperId={setSelectedPaperId}
          />
        )}
        {activeTab === 'workspace' && (
          <WorkspacePage
            selectedPaperId={selectedPaperId}
            setSelectedPaperId={setSelectedPaperId}
          />
        )}
        {activeTab === 'assistant' && (
          <AssistantPage
            selectedPaperId={selectedPaperId}
          />
        )}
        {activeTab === 'compare' && (
          <ComparePage />
        )}
        {activeTab === 'gaps' && (
          <GapsPage />
        )}
        {activeTab === 'graph' && (
          <GraphPage />
        )}
        {activeTab === 'evaluation' && (
          <EvaluationPage />
        )}
      </Layout>
    </ThemeProvider>
  )
}

