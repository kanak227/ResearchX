import React, { useState, useEffect } from 'react'
import {
  Upload,
  Search,
  BookOpen,
  FileText,
  FileSpreadsheet,
  Image,
  Sigma,
  Trash2,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react'
import { api } from '../services/api'

export default function LibraryPage({ setActiveTab, setSelectedPaperId }) {
  const [papers, setPapers] = useState([])
  const [search, setSearch] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchPapers = async () => {
    try {
      const data = await api.getPapers()
      setPapers(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPapers()
  }, [])

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    setUploadStatus({ type: 'info', message: `Ingesting "${file.name}" with multimodal pipeline...` })

    try {
      const res = await api.uploadPaper(file)
      setUploadStatus({
        type: 'success',
        message: `Successfully ingested "${res.summary?.title || file.name}" (${res.summary?.page_count} pages, ${res.summary?.total_tables} tables, ${res.summary?.total_figures} figures, ${res.summary?.total_equations} equations)`
      })
      await fetchPapers()
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to ingest paper.'
      })
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (paperId) => {
    if (!window.confirm('Delete this paper and all its extracted elements?')) return
    try {
      await api.deletePaper(paperId)
      fetchPapers()
    } catch (err) {
      alert('Failed to delete paper')
    }
  }

  const filteredPapers = papers.filter(p =>
    p.title?.toLowerCase().includes(search.toLowerCase()) ||
    p.authors?.some(a => a.toLowerCase().includes(search.toLowerCase())) ||
    p.abstract?.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Upload & Action Header */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Upload className="w-4 h-4 text-indigo-500" /> Ingest Research Paper (PDF)
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Extracts text structure, figures, tables, equations, and page-level provenance.
            </p>
          </div>
          <div>
            <label className={`cursor-pointer inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold text-white shadow-md transition ${
              uploading ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
            }`}>
              {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              <span>{uploading ? 'Processing Ingestion...' : 'Select PDF Paper'}</span>
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                disabled={uploading}
                onChange={handleFileUpload}
              />
            </label>
          </div>
        </div>

        {uploadStatus && (
          <div className={`p-3 rounded-lg text-xs flex items-center gap-2.5 border ${
            uploadStatus.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
              : uploadStatus.type === 'error'
              ? 'bg-rose-50 dark:bg-rose-950/50 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800'
              : 'bg-blue-50 dark:bg-blue-950/50 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800'
          }`}>
            {uploadStatus.type === 'success' && <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />}
            {uploadStatus.type === 'error' && <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />}
            {uploadStatus.type === 'info' && <Loader2 className="w-4 h-4 shrink-0 animate-spin text-blue-600" />}
            <span>{uploadStatus.message}</span>
          </div>
        )}
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search papers by title, author, topic, or abstract keywords..."
          className="w-full pl-10 pr-4 py-2.5 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Paper Cards List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading research library...</div>
        ) : filteredPapers.length === 0 ? (
          <div className="p-12 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-white dark:bg-slate-900 space-y-2">
            <BookOpen className="w-8 h-8 text-slate-300 dark:text-slate-600 mx-auto" />
            <p className="text-xs text-slate-500 dark:text-slate-400">No matching research papers found.</p>
          </div>
        ) : (
          filteredPapers.map((paper) => (
            <div
              key={paper.id}
              className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm hover:border-indigo-300 dark:hover:border-indigo-900 transition flex flex-col md:flex-row md:items-start justify-between gap-4"
            >
              <div className="space-y-2.5 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900">
                    ID: {paper.id}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900">
                    {paper.processing_status}
                  </span>
                  {paper.published_year && (
                    <span className="text-[10px] text-slate-500 font-medium">Year: {paper.published_year}</span>
                  )}
                  {paper.doi && (
                    <span className="text-[10px] text-slate-400">DOI: {paper.doi}</span>
                  )}
                </div>

                <h3
                  onClick={() => {
                    setSelectedPaperId(paper.id)
                    setActiveTab('workspace')
                  }}
                  className="font-bold text-base text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer transition line-clamp-1"
                >
                  {paper.title}
                </h3>

                <p className="text-xs font-medium text-slate-600 dark:text-slate-400">
                  {paper.authors?.join(', ') || 'Authors unknown'}
                </p>

                {paper.abstract && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                    {paper.abstract}
                  </p>
                )}

                {/* Modality Badges */}
                <div className="flex items-center gap-4 text-xs text-slate-500 pt-1">
                  <span className="flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5 text-indigo-500" />
                    <strong>{paper.page_count}</strong> pages
                  </span>
                  <span className="flex items-center gap-1">
                    <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500" />
                    <strong>{paper.metadata_json?.total_tables || 0}</strong> tables
                  </span>
                  <span className="flex items-center gap-1">
                    <Image className="w-3.5 h-3.5 text-purple-500" />
                    <strong>{paper.metadata_json?.total_figures || 0}</strong> figures
                  </span>
                  <span className="flex items-center gap-1">
                    <Sigma className="w-3.5 h-3.5 text-amber-500" />
                    <strong>{paper.metadata_json?.total_equations || 0}</strong> equations
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex md:flex-col items-center md:items-end gap-2 shrink-0 pt-2 md:pt-0">
                <button
                  onClick={() => {
                    setSelectedPaperId(paper.id)
                    setActiveTab('workspace')
                  }}
                  className="px-3 py-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/60 dark:hover:bg-indigo-900 text-indigo-700 dark:text-indigo-300 text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <FileText className="w-3.5 h-3.5" /> Workspace
                </button>
                <button
                  onClick={() => {
                    setSelectedPaperId(paper.id)
                    setActiveTab('assistant')
                  }}
                  className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <BookOpen className="w-3.5 h-3.5" /> Ask AI
                </button>
                <button
                  onClick={() => handleDelete(paper.id)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 transition"
                  title="Delete Paper"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

