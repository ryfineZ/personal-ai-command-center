'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'
import EmailPanel from '@/components/EmailPanel'
import SocialPanel from '@/components/SocialPanel'
import HomePanel from '@/components/HomePanel'
import BrowserPanel from '@/components/BrowserPanel'
import HITLPanel from '@/components/HITLPanel'
import AuditPanel from '@/components/AuditPanel'

export default function Home() {
  const [activeModule, setActiveModule] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const modules = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'email', name: 'Email', icon: '📧' },
    { id: 'social', name: 'Social Media', icon: '📱' },
    { id: 'home', name: 'Smart Home', icon: '🏠' },
    { id: 'browser', name: 'Browser', icon: '🌐' },
    { id: 'hitl', name: 'Approvals', icon: '✅' },
    { id: 'audit', name: 'Audit Log', icon: '📜' },
  ]

  const renderContent = () => {
    switch (activeModule) {
      case 'email':
        return <EmailPanel />
      case 'social':
        return <SocialPanel />
      case 'home':
        return <HomePanel />
      case 'browser':
        return <BrowserPanel />
      case 'hitl':
        return <HITLPanel />
      case 'audit':
        return <AuditPanel />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header 
        sidebarOpen={sidebarOpen} 
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
      />
      
      <div className="flex">
        <Sidebar
          modules={modules}
          activeModule={activeModule}
          onModuleChange={setActiveModule}
          isOpen={sidebarOpen}
        />
        
        <main className={`flex-1 p-6 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

function Dashboard() {
  const [stats, setStats] = useState({
    emails: { total: 0, unread: 0 },
    social: { scheduled: 0, posted: 0 },
    home: { devices: 0, active: 0 },
    browser: { tasks: 0, completed: 0 },
    hitl: { pending: 0, approved: 0 },
  })

  useEffect(() => {
    // Fetch stats from API
    const fetchStats = async () => {
      try {
        const [emailsRes, socialRes, homeRes, hitlRes] = await Promise.all([
          fetch('http://localhost:8001/api/email/unread/count').catch(() => ({ json: () => ({ unread_count: 0 }) })),
          fetch('http://localhost:8001/api/social?status=scheduled').catch(() => ({ json: () => [] })),
          fetch('http://localhost:8001/api/home').catch(() => ({ json: () => [] })),
          fetch('http://localhost:8001/api/hitl/pending').catch(() => ({ json: () => [] })),
        ])

        const emails = await emailsRes.json()
        const social = await socialRes.json()
        const home = await homeRes.json()
        const hitl = await hitlRes.json()

        setStats({
          emails: { total: 0, unread: emails.unread_count || 0 },
          social: { scheduled: Array.isArray(social) ? social.length : 0, posted: 0 },
          home: { devices: Array.isArray(home) ? home.length : 0, active: 0 },
          browser: { tasks: 0, completed: 0 },
          hitl: { pending: Array.isArray(hitl) ? hitl.length : 0, approved: 0 },
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }

    fetchStats()
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Emails"
          icon="📧"
          mainStat={stats.emails.unread}
          mainLabel="Unread"
          subStat={stats.emails.total}
          subLabel="Total"
          color="from-blue-500 to-cyan-500"
        />
        
        <StatCard
          title="Social Media"
          icon="📱"
          mainStat={stats.social.scheduled}
          mainLabel="Scheduled"
          subStat={stats.social.posted}
          subLabel="Posted"
          color="from-purple-500 to-pink-500"
        />
        
        <StatCard
          title="Smart Home"
          icon="🏠"
          mainStat={stats.home.devices}
          mainLabel="Devices"
          subStat={stats.home.active}
          subLabel="Active"
          color="from-green-500 to-emerald-500"
        />
        
        <StatCard
          title="Browser Tasks"
          icon="🌐"
          mainStat={stats.browser.tasks}
          mainLabel="Tasks"
          subStat={stats.browser.completed}
          subLabel="Completed"
          color="from-orange-500 to-red-500"
        />
        
        <StatCard
          title="Pending Approvals"
          icon="✅"
          mainStat={stats.hitl.pending}
          mainLabel="Pending"
          subStat={stats.hitl.approved}
          subLabel="Approved"
          color="from-yellow-500 to-orange-500"
        />
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickAction icon="📧" title="Check Email" description="View unread emails" />
          <QuickAction icon="📱" title="Post Update" description="Create social post" />
          <QuickAction icon="🏠" title="Control Home" description="Manage devices" />
          <QuickAction icon="✅" title="Review Approvals" description="Pending HITL requests" />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, icon, mainStat, mainLabel, subStat, subLabel, color }: {
  title: string
  icon: string
  mainStat: number
  mainLabel: string
  subStat: number
  subLabel: string
  color: string
}) {
  return (
    <div className={`bg-gradient-to-br ${color} p-6 rounded-xl text-white`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <span className="text-3xl">{icon}</span>
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-4xl font-bold">{mainStat}</p>
          <p className="text-sm opacity-80">{mainLabel}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-semibold">{subStat}</p>
          <p className="text-sm opacity-80">{subLabel}</p>
        </div>
      </div>
    </div>
  )
}

function QuickAction({ icon, title, description }: {
  icon: string
  title: string
  description: string
}) {
  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow hover:shadow-md transition cursor-pointer">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h4 className="font-semibold text-gray-900 dark:text-white">{title}</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        </div>
      </div>
    </div>
  )
}
