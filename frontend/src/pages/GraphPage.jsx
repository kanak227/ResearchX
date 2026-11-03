import React, { useState, useEffect } from 'react'
import {
  Network,
  BookOpen,
  User,
  Cpu,
  Database,
  BarChart,
  Filter,
  Layers,
  Sparkles,
  Info
} from 'lucide-react'
import { api } from '../services/api'

export default function GraphPage() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [], stats: {} })
  const [selectedNode, setSelectedNode] = useState(null)
  const [filterType, setFilterType] = useState('all') // all, paper, author, model, dataset, metric
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getKnowledgeGraph()
      .then(data => {
        setGraphData(data)
        if (data.nodes.length > 0) {
          setSelectedNode(data.nodes[0])
        }
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filteredNodes = graphData.nodes.filter(n =>
    filterType === 'all' ? true : n.type === filterType
  )

  const nodeColor = (type) => {
    switch (type) {
      case 'paper': return 'bg-indigo-600 text-white border-indigo-700'
      case 'author': return 'bg-emerald-600 text-white border-emerald-700'
      case 'model': return 'bg-purple-600 text-white border-purple-700'
      case 'dataset': return 'bg-blue-600 text-white border-blue-700'
      case 'metric': return 'bg-amber-600 text-white border-amber-700'
      default: return 'bg-slate-600 text-white border-slate-700'
    }
  }

  const nodeIcon = (type) => {
    switch (type) {
      case 'paper': return BookOpen
      case 'author': return User
      case 'model': return Cpu
      case 'dataset': return Database
      case 'metric': return BarChart
      default: return Network
    }
  }

  // Connected links for selected node
  const connectedLinks = selectedNode
    ? graphData.links.filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
    : []

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Network className="w-4 h-4 text-indigo-500" /> Research Knowledge Graph
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Constructed with NetworkX. Visualizes semantic interconnections across papers, authors, algorithms, datasets, and evaluation metrics.
          </p>
        </div>

        {/* Filter Badges */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-400 font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Filter:
          </span>
          {['all', 'paper', 'author', 'model', 'dataset', 'metric'].map(t => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-2.5 py-1 rounded-md text-xs font-semibold capitalize transition ${
                filterType === t
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Main Graph Grid & Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Nodes Canvas / Grid */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-3">
            <span className="font-semibold text-slate-700 dark:text-slate-300">
              Graph Entities ({filteredNodes.length} nodes, {graphData.links.length} edges)
            </span>
            <span>Density: {graphData.stats?.density || '0.00'}</span>
          </div>

          {filteredNodes.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400">
              No knowledge graph entities found. Ingest papers to build the graph.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[520px] overflow-y-auto pr-1">
              {filteredNodes.map(node => {
                const Icon = nodeIcon(node.type)
                const isSelected = selectedNode?.id === node.id

                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`p-3 rounded-lg border cursor-pointer transition flex items-start gap-3 ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/40 shadow-sm'
                        : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/40 dark:bg-slate-800/20'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${nodeColor(node.type)}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="space-y-0.5 min-w-0 flex-1">
                      <div className="font-semibold text-xs text-slate-900 dark:text-white truncate">
                        {node.label}
                      </div>
                      <div className="text-[10px] uppercase font-bold text-slate-400">
                        {node.type}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Node Inspector */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            <Info className="w-4 h-4 text-indigo-500" /> Entity Inspector
          </h3>

          {selectedNode ? (
            <div className="space-y-4 text-xs">
              <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800/60 space-y-1.5">
                <div className="text-[10px] uppercase font-bold text-indigo-500">
                  {selectedNode.type} Entity
                </div>
                <div className="font-bold text-sm text-slate-900 dark:text-white">
                  {selectedNode.properties?.full_title || selectedNode.label}
                </div>
                {selectedNode.properties?.year && (
                  <div className="text-slate-500 font-medium">Year: {selectedNode.properties.year}</div>
                )}
                {selectedNode.properties?.venue && (
                  <div className="text-slate-400">Venue: {selectedNode.properties.venue}</div>
                )}
              </div>

              {/* Connected Relationships */}
              <div className="space-y-2">
                <span className="font-bold text-slate-700 dark:text-slate-300 block text-[11px]">
                  Connected Edges ({connectedLinks.length}):
                </span>
                {connectedLinks.length === 0 ? (
                  <p className="text-slate-400 italic text-[11px]">No direct edges recorded.</p>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                    {connectedLinks.map((link, idx) => (
                      <div key={idx} className="p-2 rounded bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 text-[11px] space-y-0.5">
                        <div className="font-semibold text-indigo-600 dark:text-indigo-400 uppercase text-[9px] tracking-wider">
                          {link.relationship}
                        </div>
                        <div className="text-slate-600 dark:text-slate-300 flex items-center justify-between">
                          <span>{link.source === selectedNode.id ? link.target : link.source}</span>
                          <span className="text-[10px] text-slate-400">Weight: {link.weight}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-xs text-slate-400">
              Select a node in the graph to inspect its properties and relationships.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

