import React, { useState, useEffect } from 'react'
import {
  BarChart3,
  Play,
  RotateCw,
  Award,
  Clock,
  ShieldCheck,
  TrendingUp,
  Download,
  AlertCircle,
  Loader2,
  CheckCircle2
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import { api } from '../services/api'

export default function EvaluationPage() {
  const [summaryData, setSummaryData] = useState([])
  const [history, setHistory] = useState([])
  const [runningExp, setRunningExp] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      const [sumRes, histRes] = await Promise.all([
        api.getBenchmarkSummary(),
        api.getBenchmarkHistory()
      ])
      setSummaryData(sumRes)
      setHistory(histRes)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const runExperiment = async (expId) => {
    setRunningExp(expId)
    try {
      await api.runBenchmark({ experiment_id: expId, top_k: 5 })
      await fetchData()
    } catch (err) {
      alert(err.response?.data?.detail || 'Experiment execution failed.')
    } finally {
      setRunningExp(null)
    }
  }

  const runAllExperiments = async () => {
    const exps = ['exp_a_text_only', 'exp_b_hybrid', 'exp_c_multimodal', 'exp_d_multimodal_rerank']
    for (const exp of exps) {
      setRunningExp(exp)
      try {
        await api.runBenchmark({ experiment_id: exp, top_k: 5 })
      } catch (e) {
        console.error(e)
      }
    }
    setRunningExp(null)
    fetchData()
  }

  // Chart datasets
  const accuracyChartData = summaryData.map(d => ({
    name: d.config_id.replace('exp_', '').replace('_', ' ').toUpperCase(),
    'Precision@5': Math.round(d.precision_at_k * 100),
    'Recall@5': Math.round(d.recall_at_k * 100),
    'MRR': Math.round(d.mrr * 100),
    'Citation Accuracy': Math.round(d.citation_accuracy * 100),
    'Faithfulness': Math.round(d.faithfulness * 100)
  }))

  const latencyChartData = summaryData.map(d => ({
    name: d.config_id.replace('exp_', '').replace('_', ' ').toUpperCase(),
    'Retrieval (ms)': Math.round(d.avg_retrieval_latency * 1000),
    'Total Latency (s)': parseFloat(d.avg_response_latency.toFixed(2))
  }))

  const experiments = [
    { id: 'exp_a_text_only', label: 'Experiment A: Text-Only RAG', desc: 'Dense vector retrieval over text chunks only (no tables/figures).' },
    { id: 'exp_b_hybrid', label: 'Experiment B: Hybrid RAG', desc: 'Dense vector + BM25 sparse keyword fusion over text.' },
    { id: 'exp_c_multimodal', label: 'Experiment C: Multimodal RAG', desc: 'Retrieval across text, structured tables, figures & equations.' },
    { id: 'exp_d_multimodal_rerank', label: 'Experiment D: Multimodal + Rerank + Verifier', desc: 'Multimodal retrieval + Cross-encoder reranker + Claim verification.' },
  ]

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-500" /> Research Experimentation & Benchmark Suite
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Reproducible scientific benchmarking comparing conventional text-only RAG with multimodal retrieval and evidence-grounded verification.
          </p>
        </div>

        <button
          onClick={runAllExperiments}
          disabled={runningExp !== null}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold disabled:opacity-50 flex items-center gap-2 shadow-sm transition"
        >
          {runningExp ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          <span>{runningExp ? `Running ${runningExp}...` : 'Run All 4 Experiments'}</span>
        </button>
      </div>

      {/* Experiment Runner Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {experiments.map(exp => {
          const isRunning = runningExp === exp.id
          const sum = summaryData.find(s => s.config_id === exp.id)

          return (
            <div
              key={exp.id}
              className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold uppercase text-indigo-500 tracking-wider">
                  Configuration
                </span>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">
                  {exp.label}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  {exp.desc}
                </p>
              </div>

              <div className="space-y-3 pt-2">
                <div className="flex justify-between items-center text-xs font-semibold text-slate-700 dark:text-slate-300">
                  <span>Precision@5:</span>
                  <span className="text-indigo-600 dark:text-indigo-400">
                    {sum?.precision_at_k ? `${(sum.precision_at_k * 100).toFixed(1)}%` : 'Not run'}
                  </span>
                </div>

                <button
                  onClick={() => runExperiment(exp.id)}
                  disabled={runningExp !== null}
                  className="w-full py-2 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-semibold disabled:opacity-50 flex items-center justify-center gap-1.5 transition"
                >
                  {isRunning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                  <span>{isRunning ? 'Evaluating...' : 'Run Experiment'}</span>
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Benchmark Visualizations (Recharts) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Retrieval & Generation Quality Chart */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Award className="w-4 h-4 text-emerald-500" /> Retrieval & Grounding Quality (% Score)
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Precision@5, Recall@5, MRR, Citation Accuracy, and Faithfulness across configurations.
          </p>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={accuracyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', fontSize: '11px', color: '#fff' }}
                />
                <Legend wrapperStyle={{ fontSize: '10px' }} />
                <Bar dataKey="Precision@5" fill="#6366f1" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Recall@5" fill="#3b82f6" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Citation Accuracy" fill="#10b981" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Faithfulness" fill="#f59e0b" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Latency Comparison Chart */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-500" /> Latency Profile (Retrieval ms vs Total s)
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Execution overhead measured across retrieval and LLM response generation on local CPU.
          </p>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={latencyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', fontSize: '11px', color: '#fff' }}
                />
                <Legend wrapperStyle={{ fontSize: '10px' }} />
                <Bar dataKey="Retrieval (ms)" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Total Latency (s)" fill="#ec4899" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Historical Runs Table */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm space-y-2 p-6">
        <h3 className="font-bold text-sm text-slate-900 dark:text-white">
          Benchmark Execution Log ({history.length} runs recorded)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold">
                <th className="py-2.5 px-3">Configuration</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Samples</th>
                <th className="py-2.5 px-3">Precision@5</th>
                <th className="py-2.5 px-3">Recall@5</th>
                <th className="py-2.5 px-3">MRR</th>
                <th className="py-2.5 px-3">Citation Acc</th>
                <th className="py-2.5 px-3">Faithfulness</th>
                <th className="py-2.5 px-3">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400">
                    No benchmark runs completed yet. Click "Run All 4 Experiments" to evaluate.
                  </td>
                </tr>
              ) : (
                history.map(h => (
                  <tr key={h.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-semibold text-slate-900 dark:text-white uppercase text-[11px]">
                      {h.config_name.replace('exp_', '').replace('_', ' ')}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-[10px]">{h.timestamp.slice(0, 19).replace('T', ' ')}</td>
                    <td className="py-2.5 px-3">{h.sample_count}</td>
                    <td className="py-2.5 px-3 font-medium text-indigo-600 dark:text-indigo-400">{(h.precision_at_k * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3">{(h.recall_at_k * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3">{(h.mrr * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 font-medium text-emerald-600 dark:text-emerald-400">{(h.citation_accuracy * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 font-medium text-amber-600 dark:text-amber-400">{(h.faithfulness * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 text-slate-400">{h.avg_response_latency.toFixed(2)}s</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

