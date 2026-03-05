'use client'

interface SidebarProps {
  modules: { id: string; name: string; icon: string }[]
  activeModule: string
  onModuleChange: (module: string) => void
  isOpen: boolean
}

export default function Sidebar({ modules, activeModule, onModuleChange, isOpen }: SidebarProps) {
  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-16'
      }`}
    >
      <nav className="p-4 space-y-2">
        {modules.map((module) => (
          <button
            key={module.id}
            onClick={() => onModuleChange(module.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
              activeModule === module.id
                ? 'bg-primary-500 text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span className="text-xl">{module.icon}</span>
            {isOpen && <span className="font-medium">{module.name}</span>}
          </button>
        ))}
      </nav>

      {isOpen && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Personal AI Command Center
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              v0.1.0
            </p>
          </div>
        </div>
      )}
    </aside>
  )
}
