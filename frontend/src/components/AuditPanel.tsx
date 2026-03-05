'use client'

import { useState, useEffect } from 'react'

export default function AuditPanel() {
  const [logs, setLogs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<any>({})
  const [filter, setFilter] = useState({ resource: '', action: '' })

  useEffect(() => {
    fetchLogs()
    fetchStats()
  }, [filter])

  const fetchLogs = async () => {
    try {
      const params = new URLSearchParams()
      if (filter.resource) params.append('resource', filter.resource)
      if (filter.action) params.append('action', filter.action)
      
      const res = await fetch(`http://localhost:8001/api/audit?${params.toString()}`)
      const data = await res.json()
      setLogs(data)
    } catch (error) {
      console.error('Failed to fetch logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/audit/stats')
      const data = await res.json()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const exportLogs = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/audit/export')
      const data = await res.json()
      
      // Download as JSON
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export logs:', error)
    }
  }

  const resources = ['email', 'social', 'home', 'browser', 'hitl']
  const actions = ['create', 'update', 'delete', 'execute', 'approve', 'reject']

  const resourceColors: Record<string, string> = {
    email: 'bg-blue-100 text-blue-700',
    social: 'bg-purple-100 text-purple-700',
    home: 'bg-green-100 text-green-700',
    browser: 'bg-orange-100 text-orange-700',
    hitl: 'bg-yellow-100 text-yellow-700',
  }

  const actionIcons: Record<string, string> = {
    create: '➕',
    update: '✏️',
    delete: '🗑️',
    execute: '▶️',
    approve: '✅',
    reject: '❌',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Audit Log</h1>
        <button
          onClick={exportLogs}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
        >
          📥 Export
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total || 0}</p>
        </div>
        {Object.entries(stats.by_resource || {}).slice(0, 4).map(([resource, count]) => (
          <div key={resource} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{resource}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{count as number}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Resource
            </label>
            <select
              value={filter.resource}
              onChange={(e) => setFilter({ ...filter, resource: e.target.value })}
              className="px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Resources</option>
              {resources.map((resource) => (
                <option key={resource} value={resource}>
                  {resource.charAt(0).toUpperCase() + resource.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Action
            </label>
            <select
              value={filter.action}
              onChange={(e) => setFilter({ ...filter, action: e.target.value })}
              className="px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Actions</option>
              {actions.map((action) => (
                <option key={action} value={action}>
                  {action.charAt(0).toUpperCase() + action.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Logs */}
      {logs.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <span className="text-6xl">📜</span>
          <p className="mt-4 text-gray-600 dark:text-gray-400">No audit logs yet</p>
          <p className="text-sm text-gray-500">Actions will be logged here</p>
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div
              key={log.id}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{actionIcons[log.action] || '📝'}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white capitalize">
                      {log.action}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 text-xs rounded-full ${resourceColors[log.resource] || 'bg-gray-100 text-gray-700'}`}>
                        {log.resource}
                      </span>
                      {log.resource_id && (
                        <span className="text-xs text-gray-500">
                          #{log.resource_id}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(log.created_at).toLocaleString()}
                </span>
              </div>

              {log.details && Object.keys(log.details).length > 0 && (
                <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                  <pre className="text-gray-600 dark:text-gray-300 overflow-x-auto">
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                </div>
              )}

              {log.ip_address && (
                <p className="mt-2 text-xs text-gray-400">
                  IP: {log.ip_address}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Load More */}
      {logs.length >= 50 && (
        <div className="mt-6 text-center">
          <button
            className="px-6 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  )
}
