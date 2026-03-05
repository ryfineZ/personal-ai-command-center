'use client'

import { useState, useEffect } from 'react'

export default function EmailPanel() {
  const [emails, setEmails] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedEmail, setSelectedEmail] = useState<any>(null)

  useEffect(() => {
    fetchEmails()
  }, [])

  const fetchEmails = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/email')
      const data = await res.json()
      setEmails(data)
    } catch (error) {
      console.error('Failed to fetch emails:', error)
    } finally {
      setLoading(false)
    }
  }

  const categorizeEmail = async (emailId: number, category: string) => {
    try {
      await fetch(`http://localhost:8001/api/email/${emailId}/categorize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category }),
      })
      fetchEmails()
    } catch (error) {
      console.error('Failed to categorize email:', error)
    }
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Email Management</h1>
        <button
          onClick={fetchEmails}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
        >
          Sync Emails
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Email List */}
        <div className="lg:col-span-2 space-y-4">
          {emails.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <span className="text-6xl">📭</span>
              <p className="mt-4 text-gray-600 dark:text-gray-400">No emails yet</p>
              <p className="text-sm text-gray-500">Sync your inbox to get started</p>
            </div>
          ) : (
            emails.map((email) => (
              <div
                key={email.id}
                className={`p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition cursor-pointer ${
                  selectedEmail?.id === email.id ? 'ring-2 ring-primary-500' : ''
                }`}
                onClick={() => setSelectedEmail(email)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {email.sender}
                      </span>
                      {!email.processed && (
                        <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                          New
                        </span>
                      )}
                    </div>
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                      {email.subject}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {email.body}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(email.created_at).toLocaleDateString()}
                  </span>
                </div>
                {email.category && (
                  <div className="mt-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      email.category === 'important' ? 'bg-red-100 text-red-700' :
                      email.category === 'notification' ? 'bg-yellow-100 text-yellow-700' :
                      email.category === 'promotion' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {email.category}
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Actions */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition">
                📥 Sync Inbox
              </button>
              <button className="w-full px-4 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition">
                ✉️ Compose
              </button>
              <button className="w-full px-4 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition">
                🏷️ Auto-Categorize
              </button>
              <button className="w-full px-4 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition">
                🤖 AI Reply
              </button>
            </div>
          </div>

          {selectedEmail && (
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Categorize</h3>
              <div className="grid grid-cols-2 gap-2">
                {['important', 'notification', 'promotion', 'social'].map((category) => (
                  <button
                    key={category}
                    onClick={() => categorizeEmail(selectedEmail.id, category)}
                    className="px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition capitalize"
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
