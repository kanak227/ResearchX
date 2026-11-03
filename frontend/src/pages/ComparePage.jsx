import React, { useState, useEffect } from 'react'
import {
  Scale,
  Download,
  BookOpen,
  CheckSquare,
  Square,
  Layers,
  ChevronDown,
  ChevronUp,
  FileSpreadsheet,
  AlertCircle,
  Loader2,
  Sparkles
} from 'lucide-react'
import { api } from '../services/api'

export default function ComparePage() {
  const [papers, setPapers] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [comparison, setComparison] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [expandedRow, setExpandedRow] = useState(null)

  useEffect(() => {
    api.getPapers().then(data => {
      setPapers(data)
      if (data.length >= 2) {
        setSelectedIds([data[0].id, data[1].id])
      }
    })
    api.listComparisons().then(data => setHistory(data)).catch(() => {})
  }, [])

  const toggleSelect = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    )
  }

  const handleCompare = async () => {
    if (selectedIds.length < 2) {
      alert('Please select at least 2 papers for comparison.')
      return
    }
    setLoading(true)
    try {
      const res = await api.comparePapers({ paper_ids: selectedIds })
      setComparison(res)
      setHistory(prev => [res, ...prev.filter(h => h.id !== res.id)])
    } catch (err) {
      alert(err.response?.data?.detail || 'Comparison failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadCsv = () => {
    if (!comparison) return
    window.open(api.getComparisonCsvUrl(comparison.id), '_blank')
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Selector & Actions */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Scale className="w-4 h-4 text-indigo-500" /> Cross-Paper Comparative Analysis
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Select multiple research papers to generate structured matrices across methodologies, architectures, and empirical findings.
            </p>
          </div>

          <div className="flex gap-2.5">
            {comparison && (
              <button
                onClick={handleDownloadCsv}
                className="px-3.5 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" /> Export CSV
              </button>
            )}
            <button
              onClick={handleCompare}
              disabled={selectedIds.length < 2 || loading}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm transition"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>{loading ? 'Synthesizing...' : `Compare (${selectedIds.length}) Papers`}</span>
            </button>
          </div>
        </div>

        {/* Paper Selection Checklist */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-2">
          {papers.map((p) => {
            const isChecked = selectedIds.includes(p.id)
            return (
              <div
                key={p.id}
                onClick={() => toggleSelect(p.id)}
                className={`p-3 rounded-lg border text-xs cursor-pointer flex items-start gap-2.5 transition ${
                  isChecked
                    ? 'border-indigo-400 bg-indigo-50/50 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <div className="mt-0.5 shrink-0">
                  {isChecked ? (
                    <CheckSquare className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  ) : (
                    <Square className="w-4 h-4 text-slate-400" />
                  )}
                </div>
                <div className="space-y-0.5 flex-1 min-w-0">
                  <div className="font-semibold line-clamp-1">{p.title}</div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-1">
                    {p.authors?.slice(0, 2).join(', ') || 'Unknown'} • {p.page_count}p
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Comparison Results Table */}
      {comparison && (
        <div className="space-y-6">
          {/* Synthesis Card */}
          <div className="bg-indigo-50/60 dark:bg-indigo-950/30 border border-indigo-200/80 dark:border-indigo-800/60 rounded-xl p-5 text-xs text-indigo-950 dark:text-indigo-200 space-y-2 leading-relaxed">
            <div className="font-bold text-sm text-indigo-900 dark:text-indigo-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-500" /> Multi-Paper Synthesis
            </div>
            <p className="whitespace-pre-wrap">{comparison.synthesis}</p>
          </div>

          {/* Matrix Grid */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300">
                    <th className="py-3 px-4 font-bold w-1/5">Comparative Criterion</th>
                    {comparison.paper_ids.map(pid => {
                      const paper = papers.find(p => p.id === pid)
                      return (
                        <th key={pid} className="py-3 px-4 font-bold">
                          <div className="line-clamp-1 text-slate-900 dark:text-white">{paper?.title || pid}</div>
                          <div className="text-[10px] font-normal text-slate-500 dark:text-slate-400">ID: {pid}</div>
                        </th>
                      )
                    })}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-800 dark:text-slate-200">
                  {comparison.matrix.map((row, rIdx) => {
                    const isExpanded = expandedRow === rIdx

                    return (
                      <React.Fragment key={rIdx}>
                        <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition">
                          <td className="py-3 px-4 font-semibold text-slate-900 dark:text-slate-100 align-top flex items-center justify-between">
                            <span>{row.criterion}</span>
                            <button
                              onClick={() => setExpandedRow(isExpanded ? null : rIdx)}
                              className="text-slate-400 hover:text-indigo-600 p-1 rounded"
                              title="Inspect Supporting Evidence"
                            >
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </button>
                          </td>
                          {comparison.paper_ids.map(pid => (
                            <td key={pid} className="py-3 px-4 align-top leading-relaxed">
                              {row.values[pid] || 'N/A'}
                            </td>
                          ))}
                        </tr>

                        {/* Evidence Sub-row */}
                        {isExpanded && (
                          <tr className="bg-slate-50/70 dark:bg-slate-800/50">
                            <td colSpan={comparison.paper_ids.length + 1} className="p-4 space-y-2">
                              <span className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 block uppercase tracking-wider">
                                Grounded Evidence & Page Citations for: {row.criterion}
                              </span>
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                {comparison.paper_ids.map(pid => {
                                  const cits = row.evidence[pid] || []
                                  const paper = papers.find(p => p.id === pid)
                                  return (
                                    <div key={pid} className="p-2.5 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700 text-[11px] space-y-1.5">
                                      <div className="font-semibold text-slate-900 dark:text-slate-100 line-clamp-1">
                                        {paper?.title || pid}
                                      </div>
                                      {cits.length === 0 ? (
                                        <p className="text-slate-400 italic text-[10px]">No explicit citation snippet found.</p>
                                      ) : (
                                        cits.map((c, cIdx) => (
                                          <div key={cIdx} className="space-y-0.5 border-t border-slate-100 dark:border-slate-800 pt-1 text-[10px]">
                                            <div className="font-medium text-indigo-500">
                                              Page {c.page_number} • {c.section_name}
                                            </div>
                                            <p className="text-slate-600 dark:text-slate-400 italic line-clamp-2">"{c.snippet}"</p>
                                          </div>
                                        ))
                                      )}
                                    </div>
                                  )
                                })}
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

