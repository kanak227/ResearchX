import React, { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  BotMessageSquare,
  Scale,
  Compass,
  Network,
  BarChart3,
  Sun,
  Moon,
  Cpu,
  Layers,
  Database,
  CheckCircle2
} from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { api } from '../services/api'

export default function Layout({ activeTab, setActiveTab, children }) {
  const { theme, toggleTheme } = useTheme()
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api.getHealth()
      .then(data => setHealth(data))
      .catch(() => setHealth({ status: 'offline', ollama_model: 'llama3.2:1b' }))
  }, [])

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'library', label: 'Paper Library', icon: BookOpen },
    { id: 'workspace', label: 'Paper Workspace', icon: FileText },
    { id: 'assistant', label: 'Research Assistant', icon: BotMessageSquare },
    { id: 'compare', label: 'Compare Papers', icon: Scale },
    { id: 'gaps', label: 'Research Gaps', icon: Compass },
    { id: 'graph', label: 'Knowledge Graph', icon: Network },
    { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: BarChart3 },
  ]

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800 gap-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 dark:text-white tracking-tight flex items-center gap-1.5">
                Research<span className="text-indigo-600 dark:text-indigo-400">X</span>
              </span>
              <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400 uppercase tracking-widest block -mt-1">
                Intelligence
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-semibold shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* System Hardware & Status Pill */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
          <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-2.5 border border-slate-200/80 dark:border-slate-700/60 text-xs space-y-1.5">
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
              <span className="flex items-center gap-1.5 font-medium">
                <Cpu className="w-3.5 h-3.5 text-indigo-500" /> Model
              </span>
              <span className="font-semibold text-slate-700 dark:text-slate-200">
                {health?.ollama_model || 'llama3.2:1b'}
              </span>
            </div>
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
              <span className="flex items-center gap-1.5 font-medium">
                <Database className="w-3.5 h-3.5 text-emerald-500" /> Vector Index
              </span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Qdrant Local
              </span>
            </div>
          </div>

          {/* Theme Toggle */}
          <div className="flex items-center justify-between pt-1">
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Theme</span>
            <button
              onClick={toggleTheme}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
              title="Toggle Dark/Light Mode"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-slate-50 dark:bg-slate-950">
        {/* Header bar */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm px-8 flex items-center justify-between shrink-0">
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-white capitalize">
              {activeTab.replace('_', ' ')}
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Multimodal Evidence-Grounded Scientific Intelligence System
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              100% Zero Paid API / Local
            </span>
          </div>
        </header>

        {/* View Content */}
        <div className="flex-1 overflow-y-auto p-8">
          {children}
        </div>
      </main>
    </div>
  )
}

