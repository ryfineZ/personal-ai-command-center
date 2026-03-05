'use client'

import { useState, useEffect } from 'react'

export default function HITLPanel() {
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('pending')

  useEffect(() => {
    fetchRequests()
  }, [filter])

  const fetchRequests = async () => {
    try {
      const res = await fetch(`http://localhost:8001/api/hitl${filter ? `?status=${filter}` : ''}`)
      const data = await res.json()
      setRequests(data)
    } catch (error) {
      console.error('Failed to fetch requests:', error)
    } finally {
      setLoading(false)
    }
  }

  const approveRequest = async (requestId: number, approved: boolean) => {
    try {
      await fetch(`http://localhost:8001/api/hitl/${requestId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved, notes: '' }),
      })
      fetchRequests()
    } catch (error) {
      console.error('Failed to approve request:', error)
    }
  }

  const requestTypes = [
    { type: 'email_send', icon: '📧', name: 'Send Email', color: 'bg-blue-500' },
    { type: 'post_publish', icon: '📱', name: 'Publish Post', color: 'bg-purple-500' },
    { type: 'device_control', icon: '🏠', name: 'Control Device', color: 'bg-green-500' },
    { type: 'browser_action', icon: '🌐', name: 'Browser Action', color: 'bg-orange-500' },
    { type: 'payment', icon: '💳', name: 'Payment', color: 'bg-red-500' },
    { type: 'delete_data', icon: '🗑️', name: 'Delete Data', color: 'bg-gray-500' },
  ]

  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    approved: 'bg-green-100 text-green-700 border-green-300',
    rejected: 'bg-red-100 text-red-700 border-red-300',
    expired: 'bg-gray-100 text-gray-700 border-gray-300',
  }

  const getRequestIcon = (type: string) => {
    return requestTypes.find(r => r.type === type)?.icon || '❓'
  }

  const getRequestColor = (type: string) => {
    return requestTypes.find(r => r.type === type)?.color || 'bg-gray-500'
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Human Approval</h1>
        <div className="flex gap-2">
          {['pending', 'approved', 'rejected', 'expired'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg transition capitalize ${
                filter === status
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {requests.filter(r => r.status === 'pending').length}
              </p>
            </div>
            <span className="text-3xl">⏳</span>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Approved</p>
              <p className="text-2xl font-bold text-green-600">
                {requests.filter(r => r.status === 'approved').length}
              </p>
            </div>
            <span className="text-3xl">✅</span>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Rejected</p>
              <p className="text-2xl font-bold text-red-600">
                {requests.filter(r => r.status === 'rejected').length}
              </p>
            </div>
            <span className="text-3xl">❌</span>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Expired</p>
              <p className="text-2xl font-bold text-gray-600">
                {requests.filter(r => r.status === 'expired').length}
              </p>
            </div>
            <span className="text-3xl">⌛</span>
          </div>
        </div>
      </div>

      {/* Requests */}
      {requests.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <span className="text-6xl">✅</span>
          <p className="mt-4 text-gray-600 dark:text-gray-400">No pending requests</p>
          <p className="text-sm text-gray-500">All caught up!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((request) => (
            <div
              key={request.id}
              className={`p-4 bg-white dark:bg-gray-800 rounded-lg shadow border-l-4 ${
                statusColors[request.status]
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`w-12 h-12 ${getRequestColor(request.request_type)} rounded-lg flex items-center justify-center text-2xl text-white`}>
                    {getRequestIcon(request.request_type)}
                  </span>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white capitalize">
                      {request.request_type.replace('_', ' ')}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Request #{request.id}
                    </p>
                  </div>
                </div>
                <span className={`px-3 py-1 text-sm rounded-full border ${statusColors[request.status]} capitalize`}>
                  {request.status}
                </span>
              </div>

              <p className="text-gray-700 dark:text-gray-300 mb-3">
                {request.description}
              </p>

              {request.data && (
                <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                  <pre className="text-gray-600 dark:text-gray-300 overflow-x-auto">
                    {JSON.stringify(request.data, null, 2)}
                  </pre>
                </div>
              )}

              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center gap-4">
                  <span>Created: {new Date(request.created_at).toLocaleString()}</span>
                  {request.expires_at && (
                    <span>Expires: {new Date(request.expires_at).toLocaleString()}</span>
                  )}
                </div>
              </div>

              {request.status === 'pending' && (
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => approveRequest(request.id, true)}
                    className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition font-medium"
                  >
                    ✅ Approve
                  </button>
                  <button
                    onClick={() => approveRequest(request.id, false)}
                    className="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-medium"
                  >
                    ❌ Reject
                  </button>
                </div>
              )}

              {request.approved_at && (
                <p className="mt-2 text-sm text-gray-500">
                  {request.status === 'approved' ? 'Approved' : 'Rejected'} at:{' '}
                  {new Date(request.approved_at).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
