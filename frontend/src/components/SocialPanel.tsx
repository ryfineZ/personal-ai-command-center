'use client'

import { useState, useEffect } from 'react'

export default function SocialPanel() {
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [newPost, setNewPost] = useState({ platform: 'twitter', content: '' })

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/social')
      const data = await res.json()
      setPosts(data)
    } catch (error) {
      console.error('Failed to fetch posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const createPost = async () => {
    if (!newPost.content.trim()) return

    try {
      await fetch('http://localhost:8001/api/social', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPost),
      })
      setNewPost({ platform: 'twitter', content: '' })
      fetchPosts()
    } catch (error) {
      console.error('Failed to create post:', error)
    }
  }

  const platforms = [
    { id: 'twitter', name: 'Twitter/X', icon: '🐦', color: 'bg-blue-500' },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼', color: 'bg-blue-700' },
    { id: 'bluesky', name: 'Bluesky', icon: '🦋', color: 'bg-sky-500' },
    { id: 'farcaster', name: 'Farcaster', icon: '🔮', color: 'bg-purple-500' },
  ]

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    scheduled: 'bg-yellow-100 text-yellow-700',
    posted: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Social Media</h1>
        <div className="flex gap-2">
          {platforms.map((platform) => (
            <button
              key={platform.id}
              className={`px-3 py-1.5 ${platform.color} text-white text-sm rounded-lg`}
            >
              {platform.icon}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Post */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Create Post</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Platform
              </label>
              <select
                value={newPost.platform}
                onChange={(e) => setNewPost({ ...newPost, platform: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                {platforms.map((platform) => (
                  <option key={platform.id} value={platform.id}>
                    {platform.icon} {platform.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Content
              </label>
              <textarea
                value={newPost.content}
                onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 resize-none"
                placeholder="What's on your mind?"
              />
              <p className="mt-1 text-xs text-gray-500">
                {newPost.content.length} characters
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={createPost}
                className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
              >
                Save Draft
              </button>
              <button
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
              >
                Schedule
              </button>
            </div>
          </div>
        </div>

        {/* Posts List */}
        <div className="lg:col-span-2 space-y-4">
          {posts.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <span className="text-6xl">📱</span>
              <p className="mt-4 text-gray-600 dark:text-gray-400">No posts yet</p>
              <p className="text-sm text-gray-500">Create your first post to get started</p>
            </div>
          ) : (
            posts.map((post) => (
              <div
                key={post.id}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {platforms.find(p => p.id === post.platform)?.icon}
                    </span>
                    <span className="font-medium text-gray-900 dark:text-white capitalize">
                      {post.platform}
                    </span>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${statusColors[post.status]}`}>
                    {post.status}
                  </span>
                </div>
                <p className="text-gray-700 dark:text-gray-300 mb-2">
                  {post.content}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>
                    {post.scheduled_at
                      ? `Scheduled: ${new Date(post.scheduled_at).toLocaleString()}`
                      : 'Not scheduled'}
                  </span>
                  <span>{new Date(post.created_at).toLocaleDateString()}</span>
                </div>
                {post.status === 'draft' && (
                  <div className="mt-3 flex gap-2">
                    <button className="px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition">
                      Publish Now
                    </button>
                    <button className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition">
                      Schedule
                    </button>
                    <button className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition">
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
