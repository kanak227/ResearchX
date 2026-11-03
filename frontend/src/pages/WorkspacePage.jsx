import React, { useState, useEffect } from 'react'
import {
  FileText,
  FileSpreadsheet,
  Image as ImageIcon,
  Sigma,
  BookOpen,
  Layers,
  ChevronRight,
  ExternalLink,
  MapPin,
  Sparkles,
  Search
} from 'lucide-react'
import { api } from '../services/api'

export default function WorkspacePage({ selectedPaperId, setSelectedPaperId }) {
  const [papers, setPapers] = useState([])
  const [currentPaper, setCurrentPaper] = useState(null)
  const [elements, setElements] = useState([])
  const [activeTab, setActiveTab] = useState('all') // all, text, table, figure, equation
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getPapers().then(data => {
      setPapers(data)
      if (data.length > 0 && !selectedPaperId) {
        setSelectedPaperId(data[0].id)
      }
    })
  }, [])

  useEffect(() => {
    if (!selectedPaperId) return
    setLoading(true)
    Promise.all([
      api.getPaper(selectedPaperId),
      api.getPaperElements(selectedPaperId)
    ]).then(([pData, eData]) => {
      setCurrentPaper(pData)
      setElements(eData)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [selectedPaperId])

  const filteredElements = elements.filter(e => {
    if (activeTab !== 'all' && e.element_type !== activeTab) return false
    if (search && !e.content.toLowerCase().includes(search.toLowerCase()) && !e.section_name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const tableElements = elements.filter(e => e.element_type === 'table')
  const figureElements = elements.filter(e => e.element_type === 'figure')
  const equationElements = elements.filter(e => e.element_type === 'equation')
  const textElements = elements.filter(e => e.element_type === 'text')

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Paper Header & Selector */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Workspace</span>
              {currentPaper?.doi && (
                <span className="text-[10px] text-slate-400 font-mono">DOI: {currentPaper.doi}</span>
              )}
            </div>
            <h2 className="text-xl font-extrabold text-slate-900 dark:text-white">
              {currentPaper?.title || 'No Paper Selected'}
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 font-medium">
              {currentPaper?.authors?.join(', ') || 'Authors unknown'}
            </p>
          </div>

          <div className="shrink-0 flex items-center gap-3">
            <select
              value={selectedPaperId || ''}
              onChange={(e) => setSelectedPaperId(e.target.value)}
              className="px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {papers.map(p => (
                <option key={p.id} value={p.id}>
                  {p.title.slice(0, 45)}... ({p.page_count}p)
                </option>
              ))}
            </select>

            {selectedPaperId && (
              <a
                href={`/api/papers/${selectedPaperId}/pdf`}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-2 rounded-lg bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <ExternalLink className="w-3.5 h-3.5" /> View PDF
              </a>
            )}
          </div>
        </div>

        {/* Abstract Box */}
        {currentPaper?.abstract && (
          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/60 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            <strong className="text-slate-900 dark:text-white block mb-1">Abstract:</strong>
            {currentPaper.abstract}
          </div>
        )}

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 gap-6 pt-2">
          {[
            { id: 'all', label: `All Elements (${elements.length})`, icon: Layers },
            { id: 'text', label: `Sections & Text (${textElements.length})`, icon: FileText },
            { id: 'table', label: `Tables (${tableElements.length})`, icon: FileSpreadsheet },
            { id: 'figure', label: `Figures & Diagrams (${figureElements.length})`, icon: ImageIcon },
            { id: 'equation', label: `Equations (${equationElements.length})`, icon: Sigma },
          ].map(tab => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 text-xs font-semibold flex items-center gap-1.5 border-b-2 transition -mb-px ${
                  isActive
                    ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-slate-300'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter extracted elements by keywords..."
          className="w-full pl-10 pr-4 py-2.5 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Extracted Elements Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading extracted elements...</div>
      ) : filteredElements.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-xs text-slate-400">
          No extracted elements match the current view.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredElements.map((elem) => {
            const isTable = elem.element_type === 'table'
            const isFigure = elem.element_type === 'figure'
            const isEquation = elem.element_type === 'equation'

            // Extract image url if figure
            let imageUrl = null
            if (isFigure && elem.content.includes('*Image Path:* `')) {
              const match = elem.content.match(/\*Image Path:\* `([^`]+)`/)
              if (match) {
                imageUrl = '/' + match[1]
              }
            }

            return (
              <div
                key={elem.id}
                className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-3"
              >
                {/* Provenance Header */}
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      isTable
                        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                        : isFigure
                        ? 'bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300'
                        : isEquation
                        ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
                        : 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                    }`}>
                      {elem.element_type}
                    </span>

                    <span className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-slate-400" /> Page {elem.page_number}
                    </span>

                    <span className="text-slate-400">•</span>

                    <span className="text-slate-600 dark:text-slate-400 font-medium">
                      Section: {elem.section_name}
                    </span>
                  </div>

                  {elem.source_coordinates && (
                    <span className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-indigo-400" />
                      [{elem.source_coordinates.x0}, {elem.source_coordinates.y0}] ({elem.source_coordinates.width}x{elem.source_coordinates.height})
                    </span>
                  )}
                </div>

                {/* Content Body */}
                <div className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
                  {isFigure && imageUrl && (
                    <div className="mb-3 p-2 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-slate-200 dark:border-slate-700 flex justify-center">
                      <img
                        src={imageUrl}
                        alt="Extracted scientific figure"
                        className="max-h-72 rounded object-contain shadow-sm"
                        onError={(e) => { e.target.style.display = 'none' }}
                      />
                    </div>
                  )}

                  {isTable ? (
                    <div className="overflow-x-auto p-2 bg-slate-50 dark:bg-slate-800/30 rounded-lg border border-slate-100 dark:border-slate-800">
                      <pre className="text-[11px] font-mono whitespace-pre text-slate-700 dark:text-slate-300">
                        {elem.content}
                      </pre>
                    </div>
                  ) : isEquation ? (
                    <div className="p-3 bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/50 dark:border-amber-900/30 rounded-lg font-mono text-center text-sm text-slate-900 dark:text-amber-200">
                      {elem.content}
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{elem.content}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

