'use client'

import { useState, useEffect } from 'react'

export default function HomePanel() {
  const [devices, setDevices] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [rooms, setRooms] = useState<string[]>([])

  useEffect(() => {
    fetchDevices()
  }, [])

  const fetchDevices = async () => {
    try {
      const [devicesRes, roomsRes] = await Promise.all([
        fetch('http://localhost:8001/api/home').catch(() => ({ json: () => [] })),
        fetch('http://localhost:8001/api/home/rooms/list').catch(() => ({ json: () => ({ rooms: [] }) })),
      ])

      const devicesData = await devicesRes.json()
      const roomsData = await roomsRes.json()

      setDevices(Array.isArray(devicesData) ? devicesData : [])
      setRooms(roomsData.rooms || [])
    } catch (error) {
      console.error('Failed to fetch devices:', error)
    } finally {
      setLoading(false)
    }
  }

  const controlDevice = async (deviceId: number, action: string) => {
    try {
      await fetch(`http://localhost:8001/api/home/${deviceId}/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      })
      fetchDevices()
    } catch (error) {
      console.error('Failed to control device:', error)
    }
  }

  const deviceTypes = [
    { type: 'light', icon: '💡', name: 'Light' },
    { type: 'thermostat', icon: '🌡️', name: 'Thermostat' },
    { type: 'camera', icon: '📹', name: 'Camera' },
    { type: 'sensor', icon: '📡', name: 'Sensor' },
    { type: 'switch', icon: '🔌', name: 'Switch' },
    { type: 'lock', icon: '🔒', name: 'Lock' },
  ]

  const getDeviceIcon = (type: string) => {
    return deviceTypes.find(d => d.type === type)?.icon || '📱'
  }

  const scenes = [
    { id: 'morning', name: 'Good Morning', icon: '🌅', actions: ['lights on', 'thermostat 72'] },
    { id: 'night', name: 'Good Night', icon: '🌙', actions: ['lights off', 'thermostat 68'] },
    { id: 'away', name: 'Away Mode', icon: '🚗', actions: ['all off', 'lock doors'] },
    { id: 'movie', name: 'Movie Time', icon: '🎬', actions: ['dim lights', 'tv on'] },
  ]

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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Smart Home</h1>
        <button
          onClick={fetchDevices}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition"
        >
          Sync Devices
        </button>
      </div>

      {/* Scenes */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Scenes</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {scenes.map((scene) => (
            <button
              key={scene.id}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition text-center"
            >
              <span className="text-4xl mb-2 block">{scene.icon}</span>
              <span className="font-medium text-gray-900 dark:text-white">{scene.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Rooms */}
      {rooms.length > 0 && (
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Rooms</h2>
          <div className="flex gap-2 flex-wrap">
            {rooms.map((room) => (
              <button
                key={room}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition capitalize"
              >
                {room}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Devices */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Devices ({devices.length})
        </h2>
        
        {devices.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
            <span className="text-6xl">🏠</span>
            <p className="mt-4 text-gray-600 dark:text-gray-400">No devices yet</p>
            <p className="text-sm text-gray-500">Connect your Home Assistant to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {devices.map((device) => (
              <div
                key={device.id}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{getDeviceIcon(device.device_type)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {device.name}
                      </h3>
                      <p className="text-sm text-gray-500 capitalize">
                        {device.device_type}
                      </p>
                    </div>
                  </div>
                  <span className={`w-3 h-3 rounded-full ${
                    device.state?.power ? 'bg-green-500' : 'bg-gray-400'
                  }`}></span>
                </div>

                {device.room && (
                  <p className="text-sm text-gray-500 mb-3">
                    📍 {device.room}
                  </p>
                )}

                <div className="flex gap-2">
                  {device.device_type === 'light' && (
                    <>
                      <button
                        onClick={() => controlDevice(device.id, 'on')}
                        className="flex-1 px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
                      >
                        On
                      </button>
                      <button
                        onClick={() => controlDevice(device.id, 'off')}
                        className="flex-1 px-3 py-1.5 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition"
                      >
                        Off
                      </button>
                    </>
                  )}
                  {device.device_type === 'thermostat' && (
                    <button
                      onClick={() => controlDevice(device.id, 'set')}
                      className="flex-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition"
                    >
                      Set Temp
                    </button>
                  )}
                  {device.device_type === 'lock' && (
                    <>
                      <button
                        onClick={() => controlDevice(device.id, 'lock')}
                        className="flex-1 px-3 py-1.5 text-sm bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition"
                      >
                        Lock
                      </button>
                      <button
                        onClick={() => controlDevice(device.id, 'unlock')}
                        className="flex-1 px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition"
                      >
                        Unlock
                      </button>
                    </>
                  )}
                </div>

                {device.last_updated && (
                  <p className="text-xs text-gray-400 mt-3">
                    Last updated: {new Date(device.last_updated).toLocaleString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
