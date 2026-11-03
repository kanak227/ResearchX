import React, { useState, useEffect, useRef } from 'react'
import {
  Send,
  BotMessageSquare,
  User,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  BookOpen,
  MapPin,
  Clock,
  Sparkles,
  SlidersHorizontal,
  ChevronDown,
  Layers,
  FileSpreadsheet,
  Image as ImageIcon,
  Sigma
} from 'lucide-react'
import { api } from '../services/api'

export default function AssistantPage({ selectedPaperId }) {
  const [papers, setPapers] = useState([])
  const [targetPaperId, setTargetPaperId] = useState(selectedPaperId || '')
  const [retrievalMode, setRetrievalMode] = useState('multimodal') // text_only, hybrid, multimodal
  const [topK, setTopK] = useState(5)
  const [enableVerification, setEnableVerification] = useState(true)
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Welcome to ResearchX Assistant. Ask any technical, mathematical, architectural, or empirical question about your ingested papers. Every response is strictly grounded in retrieved evidence with verified citations.',
      claims: [],
      citations: [],
      latency: null,
      mode: 'multimodal'
    }
  ])
  const [loading, setLoading] = useState(false)
  const [showConfig, setShowConfig] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    api.getPapers().then(data => {
      setPapers(data)
      if (selectedPaperId) {
        setTargetPaperId(selectedPaperId)
      }
    })
  }, [selectedPaperId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (qText = null) => {
    const textToSend = qText || query
    if (!textToSend.trim() || loading) return

    const userMessage = { role: 'user', content: textToSend }
    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setLoading(true)

    try {
      const res = await api.askChat({
        query: textToSend,
        paper_id: targetPaperId || null,
        retrieval_mode: retrievalMode,
        top_k: topK,
        enable_verification: enableVerification
      })

      const botMessage = {
        role: 'assistant',
        content: res.answer,
        claims: res.claims || [],
        citations: res.citations || [],
        latency: res.latency_seconds,
        mode: res.retrieval_mode,
        model: res.model_used
      }

      setMessages(prev => [...prev, botMessage])
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'An error occurred during evidence retrieval or answer synthesis. Please verify that Ollama or backend service is running.',
          claims: [],
          citations: [],
          latency: null
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const promptSuggestions = [
    "Explain the methodology used in this paper.",
    "What is the significance of the empirical results in the main table?",
    "Explain the architecture diagram in the paper figures.",
    "What mathematical equations and loss functions are formulated?",
    "What are the major limitations stated by the authors?"
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-6xl mx-auto space-y-4">
      {/* Configuration Header */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-300">
            <BookOpen className="w-4 h-4 text-indigo-500" />
            <span>Corpus:</span>
          </div>
          <select
            value={targetPaperId}
            onChange={(e) => setTargetPaperId(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-medium focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">All Uploaded Papers (Cross-Corpus)</option>
            {papers.map(p => (
              <option key={p.id} value={p.id}>
                {p.title.slice(0, 40)}...
              </option>
            ))}
          </select>

          {/* Mode Switcher */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg">
            {[
              { id: 'text_only', label: 'Text-Only' },
              { id: 'hybrid', label: 'Hybrid (Dense+BM25)' },
              { id: 'multimodal', label: 'Multimodal' },
            ].map(m => (
              <button
                key={m.id}
                onClick={() => setRetrievalMode(m.id)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition ${
                  retrievalMode === m.id
                    ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-sm'
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-600 dark:text-slate-400 font-medium">
            <input
              type="checkbox"
              checked={enableVerification}
              onChange={(e) => setEnableVerification(e.target.checked)}
              className="rounded text-indigo-600 focus:ring-indigo-500"
            />
            <span>Evidence Verification</span>
          </label>

          <span className="text-slate-300 dark:text-slate-700">|</span>

          <span className="text-slate-500 font-medium">Top-K:</span>
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="px-2 py-1 rounded border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium"
          >
            <option value={3}>3 elements</option>
            <option value={5}>5 elements</option>
            <option value={8}>8 elements</option>
          </select>
        </div>
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user'

          return (
            <div key={idx} className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}>
              {!isUser && (
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shrink-0 mt-1 shadow-sm">
                  <BotMessageSquare className="w-4 h-4" />
                </div>
              )}

              <div className={`space-y-3 max-w-3xl ${isUser ? 'items-end' : 'items-start'}`}>
                {/* Bubble */}
                <div className={`p-4 rounded-2xl text-xs leading-relaxed shadow-sm ${
                  isUser
                    ? 'bg-indigo-600 text-white rounded-tr-none font-medium'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none font-sans'
                }`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* Latency & Mode pill */}
                  {!isUser && msg.latency !== null && (
                    <div className="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center gap-3 text-[10px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" /> {msg.latency}s latency
                      </span>
                      <span>•</span>
                      <span className="uppercase font-semibold tracking-wider text-indigo-500">
                        {msg.mode}
                      </span>
                      <span>•</span>
                      <span>Model: {msg.model || 'llama3.2:1b'}</span>
                    </div>
                  )}
                </div>

                {/* Verified Claims Card (Module G) */}
                {!isUser && msg.claims && msg.claims.length > 0 && (
                  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 text-xs space-y-2.5 shadow-sm">
                    <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
                      <span className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <ShieldCheck className="w-4 h-4 text-emerald-500" />
                        Grounded Claim Verification ({msg.claims.length} assertions analyzed)
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">Deterministic Validation</span>
                    </div>

                    <div className="space-y-2">
                      {msg.claims.map((c, cIdx) => {
                        const isVerified = c.status === 'verified'
                        const isPartial = c.status === 'partially_supported'

                        return (
                          <div
                            key={cIdx}
                            className={`p-2.5 rounded-lg border text-[11px] space-y-1.5 ${
                              isVerified
                                ? 'bg-emerald-50/40 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/60 text-slate-800 dark:text-slate-200'
                                : isPartial
                                ? 'bg-amber-50/40 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800/60 text-slate-800 dark:text-slate-200'
                                : 'bg-rose-50/40 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800/60 text-slate-800 dark:text-slate-200'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <span className="font-medium leading-relaxed">{c.claim}</span>
                              <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold shrink-0 uppercase ${
                                isVerified
                                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300'
                                  : isPartial
                                  ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300'
                                  : 'bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-300'
                              }`}>
                                {c.status.replace('_', ' ')} ({(c.confidence_score * 100).toFixed(0)}%)
                              </span>
                            </div>

                            {c.supporting_citations && c.supporting_citations.length > 0 && (
                              <div className="text-[10px] text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-200/50 dark:border-slate-800/50 flex flex-wrap gap-2">
                                {c.supporting_citations.map((sc, scIdx) => (
                                  <span key={scIdx} className="inline-flex items-center gap-1 font-medium text-indigo-600 dark:text-indigo-400">
                                    <BookOpen className="w-3 h-3" /> Page {sc.page_number} ({sc.section_name})
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Evidence Citations Drawer */}
                {!isUser && msg.citations && msg.citations.length > 0 && (
                  <div className="bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-xs space-y-2">
                    <span className="font-semibold text-slate-700 dark:text-slate-300 block text-[11px]">
                      Source Provenance References:
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {msg.citations.slice(0, 4).map((cit, cIdx) => (
                        <div key={cIdx} className="p-2 bg-white dark:bg-slate-800/80 rounded border border-slate-200 dark:border-slate-700 text-[10px] space-y-1">
                          <div className="font-semibold text-slate-800 dark:text-slate-200 line-clamp-1">
                            {cit.paper_title}
                          </div>
                          <div className="text-slate-500 flex items-center justify-between">
                            <span>Page {cit.page_number} • {cit.section_name}</span>
                            <span className="uppercase text-[9px] font-bold text-indigo-500">{cit.element_type}</span>
                          </div>
                          <p className="text-slate-400 italic line-clamp-2">"{cit.snippet}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-lg bg-slate-200 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300 shrink-0 mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          )
        })}
        {loading && (
          <div className="flex gap-3.5 items-center text-xs text-slate-400">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/50 animate-pulse flex items-center justify-center text-white">
              <Sparkles className="w-4 h-4" />
            </div>
            <span>Analyzing research evidence across modalities...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Pre-built Prompt Suggestions */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-[11px]">
        {promptSuggestions.map((s, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(s)}
            className="px-2.5 py-1 rounded-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-indigo-400 dark:hover:border-indigo-600 hover:text-indigo-600 dark:hover:text-indigo-300 shrink-0 transition"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input Field */}
      <div className="relative bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-1.5 flex items-center gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a scientific question, cite a table/figure, or compare methodologies..."
          className="flex-1 px-3 py-2 text-xs bg-transparent text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
        />
        <button
          onClick={() => handleSend()}
          disabled={!query.trim() || loading}
          className="p-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50 disabled:cursor-not-allowed transition shadow-sm"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

