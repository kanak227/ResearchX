import React, { useState, useEffect } from 'react'
import {
  Compass,
  AlertTriangle,
  Lightbulb,
  HelpCircle,
  TrendingUp,
  GitBranch,
  BookOpen,
  Sparkles,
  Loader2,
  CheckSquare,
  Square,
  ShieldAlert
} from 'lucide-react'
import { api } from '../services/api'

export default function GapsPage() {
  const [papers, setPapers] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getPapers().then(data => {
      setPapers(data)
      if (data.length > 0) {
        setSelectedIds(data.map(p => p.id))
      }
    })
    api.listGaps().then(data => {
      if (data.length > 0) {
        setReport(data[0])
      }
    }).catch(() => {})
  }, [])

  const toggleSelect = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    )
  }

  const handleAnalyze = async () => {
    if (selectedIds.length === 0) {
      alert('Select at least one paper to analyze research gaps.')
      return
    }
    setLoading(true)
    try {
      const res = await api.analyzeGaps(selectedIds)
      setReport(res)
    } catch (err) {
      alert(err.response?.data?.detail || 'Gap analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Controls */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Compass className="w-4 h-4 text-indigo-500" /> Research Gap Discovery & Opportunity Mapping
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Discovers unaddressed problem formulations, recurring author-stated limitations, and unexplored research questions.
            </p>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={selectedIds.length === 0 || loading}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm transition"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            <span>{loading ? 'Discovering Gaps...' : `Analyze (${selectedIds.length}) Papers`}</span>
          </button>
        </div>

        {/* Paper Checklist */}
        <div className="flex flex-wrap gap-2 pt-1">
          {papers.map(p => {
            const isChecked = selectedIds.includes(p.id)
            return (
              <button
                key={p.id}
                onClick={() => toggleSelect(p.id)}
                className={`px-3 py-1.5 rounded-lg border text-xs flex items-center gap-1.5 transition ${
                  isChecked
                    ? 'border-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold'
                    : 'border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                }`}
              >
                {isChecked ? <CheckSquare className="w-3.5 h-3.5 text-indigo-600" /> : <Square className="w-3.5 h-3.5 text-slate-400" />}
                <span className="truncate max-w-[200px]">{p.title}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Mandatory Scope Notice Banner */}
      {report && (
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 flex items-center gap-3 text-xs text-amber-900 dark:text-amber-200 font-medium">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <strong>Scope Notice:</strong> {report.scope_notice} Findings represent gaps strictly unaddressed in the selected papers and should not be inferred as global novelty without broader literature review.
          </div>
        </div>
      )}

      {/* Report Cards Grid */}
      {report && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Trends & Common Methods */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-500" /> Observed Research Trends
            </h3>
            <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-300">
              {report.trends?.map((t, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                  <span>{t}</span>
                </li>
              ))}
            </ul>

            <h4 className="font-bold text-xs text-slate-800 dark:text-slate-200 pt-2 flex items-center gap-2">
              <GitBranch className="w-3.5 h-3.5 text-blue-500" /> Common Methodologies
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {report.common_methodologies?.map((m, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[11px] font-medium">
                  {m}
                </span>
              ))}
            </div>
          </div>

          {/* Frequently Reported Limitations */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" /> Frequently Reported Limitations
            </h3>
            <div className="space-y-3">
              {report.frequently_reported_limitations?.map((lim, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-rose-50/40 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/40 text-xs space-y-1">
                  <div className="flex justify-between items-start gap-2">
                    <span className="font-semibold text-rose-900 dark:text-rose-200">{lim.category}</span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-300 shrink-0">
                      {lim.type}
                    </span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 italic">"{lim.finding}"</p>
                  <div className="text-[10px] text-slate-400">
                    Source: {lim.paper_title} (Page {lim.page}, {lim.section})
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Unexplored Combinations */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-amber-500" /> Unexplored Combinations & Hypotheses
            </h3>
            <div className="space-y-3">
              {report.unexplored_combinations?.map((u, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-amber-50/30 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 text-xs space-y-1.5">
                  <div className="flex justify-between items-start gap-2">
                    <span className="font-bold text-slate-900 dark:text-white">{u.gap_title}</span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300">
                      {u.relevance} Priority
                    </span>
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{u.description}</p>
                  <div className="text-[10px] font-semibold text-indigo-500 uppercase">{u.status}</div>
                </div>
              ))}
            </div>
          </div>

          {/* High Potential Research Questions */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-indigo-500" /> Potential Research Questions
            </h3>
            <div className="space-y-3">
              {report.potential_research_questions?.map((q, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-indigo-50/40 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-xs space-y-1.5">
                  <div className="font-bold text-indigo-950 dark:text-indigo-200 leading-snug">
                    {idx + 1}. {q.question}
                  </div>
                  <p className="text-slate-600 dark:text-slate-300 text-[11px]">{q.rationale}</p>
                  {q.candidate_benchmarks && (
                    <div className="text-[10px] text-slate-500 dark:text-slate-400">
                      Candidate Benchmarks: {q.candidate_benchmarks.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

