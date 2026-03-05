'use client'

import { useState, useEffect } from 'react'

export default function BrowserPanel() {
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [newTask, setNewTask] = useState({
    name: '',
    task_type: 'screenshot',
    config: {},
    schedule: '',
  })

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/browser')
      const data = await res.json()
      setTasks(data)
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const createTask = async () => {
    if (!newTask.name.trim()) return

    try {
      await fetch('http://localhost:8001/api/browser', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask),
      })
      setNewTask({ name: '', task_type: 'screenshot', config: {}, schedule: '' })
      fetchTasks()
    } catch (error) {
      console.error('Failed to create task:', error)
    }
  }

  const executeTask = async (taskId: number) => {
    try {
      await fetch(`http://localhost:8001/api/browser/${taskId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ params: {} }),
      })
      fetchTasks()
    } catch (error) {
      console.error('Failed to execute task:', error)
    }
  }

  const taskTypes = [
    { type: 'form_fill', icon: '📝', name: 'Form Filling' },
    { type: 'price_monitor', icon: '💰', name: 'Price Monitor' },
    { type: 'scheduled_check', icon: '⏰', name: 'Scheduled Check' },
    { type: 'screenshot', icon: '📸', name: 'Screenshot' },
    { type: 'data_extraction', icon: '📊', name: 'Data Extraction' },
    { type: 'login', icon: '🔐', name: 'Auto Login' },
  ]

  const statusColors: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    paused: 'bg-yellow-100 text-yellow-700',
    completed: 'bg-blue-100 text-blue-700',
    manual: 'bg-gray-100 text-gray-700',
  }

  const getTaskIcon = (type: string) => {
    return taskTypes.find(t => t.type === type)?.icon || '🌐'
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Browser Automation</h1>
        <button
          onClick={fetchTasks}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
        >
          Refresh Tasks
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Task */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4">New Task</h3>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Task Name
              </label>
              <input
                type="text"
                value={newTask.name}
                onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="My automation task"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Task Type
              </label>
              <select
                value={newTask.task_type}
                onChange={(e) => setNewTask({ ...newTask, task_type: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                {taskTypes.map((type) => (
                  <option key={type.type} value={type.type}>
                    {type.icon} {type.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Schedule (Optional)
              </label>
              <input
                type="text"
                value={newTask.schedule}
                onChange={(e) => setNewTask({ ...newTask, schedule: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="cron expression (e.g., 0 9 * * *)"
              />
            </div>

            <button
              onClick={createTask}
              className="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
            >
              Create Task
            </button>

            {/* Quick Actions */}
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Quick Actions</h4>
              <div className="space-y-2">
                <button className="w-full px-3 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition text-sm">
                  📸 Take Screenshot
                </button>
                <button className="w-full px-3 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition text-sm">
                  📝 Fill Form
                </button>
                <button className="w-full px-3 py-2 text-left bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition text-sm">
                  💰 Monitor Price
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Tasks List */}
        <div className="lg:col-span-2 space-y-4">
          {tasks.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <span className="text-6xl">🌐</span>
              <p className="mt-4 text-gray-600 dark:text-gray-400">No tasks yet</p>
              <p className="text-sm text-gray-500">Create your first automation task</p>
            </div>
          ) : (
            tasks.map((task) => (
              <div
                key={task.id}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{getTaskIcon(task.task_type)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {task.name}
                      </h3>
                      <p className="text-sm text-gray-500 capitalize">
                        {task.task_type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${statusColors[task.status]}`}>
                    {task.status}
                  </span>
                </div>

                {task.schedule && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    ⏰ Schedule: {task.schedule}
                  </p>
                )}

                {task.last_run && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Last run: {new Date(task.last_run).toLocaleString()}
                  </p>
                )}

                {task.result && (
                  <div className="mb-3 p-2 bg-gray-50 dark:bg-gray-700 rounded text-sm">
                    <span className="text-gray-600 dark:text-gray-300">Result: </span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {task.result.status}
                    </span>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => executeTask(task.id)}
                    className="flex-1 px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
                  >
                    ▶️ Run
                  </button>
                  {task.status === 'active' ? (
                    <button className="px-3 py-1.5 text-sm bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition">
                      ⏸️ Pause
                    </button>
                  ) : (
                    <button className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition">
                      ▶️ Resume
                    </button>
                  )}
                  <button className="px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition">
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
