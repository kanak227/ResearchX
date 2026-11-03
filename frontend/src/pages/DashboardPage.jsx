import React, { useState, useEffect } from 'react'
import {
  BookOpen,
  FileSpreadsheet,
  Image,
  Award,
  Upload,
  BotMessageSquare,
  BarChart3,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react'
import { api } from '../services/api'

export default function DashboardPage({ setActiveTab, setSelectedPaperId }) {
  const [papers, setPapers] = useState([])
  const [evalSummary, setEvalSummary] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getPapers().catch(() => []),
      api.getBenchmarkSummary().catch(() => [])
    ]).then(([papersData, summaryData]) => {
      setPapers(papersData)
      setEvalSummary(summaryData)
      setLoading(false)
    })
  }, [])

  const totalPages = papers.reduce((acc, p) => acc + (p.page_count || 0), 0)
  const totalTables = papers.reduce((acc, p) => acc + (p.metadata_json?.total_tables || 0), 0)
  const totalFigures = papers.reduce((acc, p) => acc + (p.metadata_json?.total_figures || 0), 0)

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 text-white p-8 shadow-xl">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" /> Multimodal Scientific Research Intelligence
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">
            Scientific Paper Understanding with Strict Evidence Grounding
          </h2>
          <p className="text-sm text-indigo-100/80 leading-relaxed">
            Ingest scientific PDFs into structural text, tables, figures, and equations. Perform hybrid dense/sparse retrieval with verifiable page citations—operating completely offline with local open-weight models.
          </p>
          <div className="flex gap-3 pt-2">
            <button
              onClick={() => setActiveTab('library')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white text-xs font-semibold shadow-md transition"
            >
              <Upload className="w-3.5 h-3.5" /> Upload Papers
            </button>
            <button
              onClick={() => setActiveTab('assistant')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold backdrop-blur-sm transition"
            >
              <BotMessageSquare className="w-3.5 h-3.5" /> Launch Assistant
            </button>
            <button
              onClick={() => setActiveTab('evaluation')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-semibold backdrop-blur-sm transition"
            >
              <BarChart3 className="w-3.5 h-3.5" /> View Experiments
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{papers.length}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Research Papers</div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/60 flex items-center justify-center text-blue-600 dark:text-blue-400">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{totalPages}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Pages Indexed</div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{totalTables}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Extracted Tables</div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 dark:bg-purple-950/60 flex items-center justify-center text-purple-600 dark:text-purple-400">
            <Image className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{totalFigures}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">Figures & Diagrams</div>
          </div>
        </div>
      </div>

      {/* Recent Papers & Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-500" /> Recent Papers Ingested
            </h3>
            <button
              onClick={() => setActiveTab('library')}
              className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
            >
              View All <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {papers.length === 0 ? (
            <div className="p-8 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-xl space-y-3">
              <p className="text-xs text-slate-500 dark:text-slate-400">No research papers ingested yet.</p>
              <button
                onClick={() => setActiveTab('library')}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 transition"
              >
                Upload First Paper
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {papers.slice(0, 4).map((p) => (
                <div
                  key={p.id}
                  onClick={() => {
                    setSelectedPaperId(p.id)
                    setActiveTab('workspace')
                  }}
                  className="p-3.5 rounded-lg border border-slate-100 dark:border-slate-800 hover:border-indigo-200 dark:hover:border-indigo-900/60 bg-slate-50/50 dark:bg-slate-800/30 flex items-center justify-between cursor-pointer transition"
                >
                  <div className="space-y-1 pr-4">
                    <div className="font-semibold text-sm text-slate-800 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 line-clamp-1">
                      {p.title}
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                      <span>{p.page_count} pages</span>
                      <span>•</span>
                      <span>{p.authors?.slice(0, 2).join(', ') || 'Unknown'}</span>
                    </div>
                  </div>
                  <div className="shrink-0">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                      {p.processing_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Evaluation Snapshot */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 space-y-4">
          <h3 className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-500" /> Scientific Benchmarks
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Compare Text-Only RAG vs Multimodal Retrieval and Verification.
          </p>

          <div className="space-y-3">
            {evalSummary.map((exp) => (
              <div key={exp.config_id} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/60 space-y-1.5">
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                  <span>{exp.label}</span>
                  <span className="text-indigo-600 dark:text-indigo-400">
                    {exp.precision_at_k > 0 ? `${(exp.precision_at_k * 100).toFixed(1)}% P@K` : 'Ready'}
                  </span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full rounded-full transition-all"
                    style={{ width: `${exp.precision_at_k * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => setActiveTab('evaluation')}
            className="w-full py-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold transition"
          >
            Launch Benchmark Engine
          </button>
        </div>
      </div>
    </div>
  )
}

