import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Terminal, Play, Pause, Square, Monitor, Cpu, MemoryStick, 
  HardDrive, Network, Users, FileText, Code, Settings,
  ChevronRight, Activity, Zap, AlertCircle
} from 'lucide-react';

interface VMInstance {
  id: string;
  name: string;
  environment: 'python' | 'javascript' | 'cpp' | 'java' | 'rust' | 'go' | 'linux_full';
  status: 'running' | 'stopped' | 'paused' | 'initializing';
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  uptime: string;
  collaborators: number;
  lastActivity: string;
}

interface ExecutionHistory {
  id: string;
  language: string;
  status: 'completed' | 'failed' | 'running';
  executionTime: number;
  timestamp: string;
  output: string;
}

const WebVMDashboard: React.FC = () => {
  const [vmInstances, setVmInstances] = useState<VMInstance[]>([]);
  const [selectedInstance, setSelectedInstance] = useState<string | null>(null);
  const [executionHistory, setExecutionHistory] = useState<ExecutionHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadVMData = async () => {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setVmInstances([
        {
          id: 'vm-1',
          name: 'Python ML Environment',
          environment: 'python',
          status: 'running',
          cpuUsage: 45,
          memoryUsage: 78,
          diskUsage: 23,
          uptime: '2h 34m',
          collaborators: 0,
          lastActivity: '5 minutes ago'
        },
        {
          id: 'vm-2',
          name: 'JavaScript Development',
          environment: 'javascript',
          status: 'paused',
          cpuUsage: 12,
          memoryUsage: 34,
          diskUsage: 45,
          uptime: '1h 12m',
          collaborators: 2,
          lastActivity: '15 minutes ago'
        },
        {
          id: 'vm-3',
          name: 'Rust Systems Programming',
          environment: 'rust',
          status: 'stopped',
          cpuUsage: 0,
          memoryUsage: 0,
          diskUsage: 67,
          uptime: '0m',
          collaborators: 0,
          lastActivity: '2 hours ago'
        }
      ]);

      setExecutionHistory([
        {
          id: 'exec-1',
          language: 'python',
          status: 'completed',
          executionTime: 1250,
          timestamp: '2 minutes ago',
          output: 'Model trained successfully - Accuracy: 94.5%'
        },
        {
          id: 'exec-2',
          language: 'javascript',
          status: 'completed',
          executionTime: 340,
          timestamp: '8 minutes ago',
          output: 'React component rendered successfully'
        },
        {
          id: 'exec-3',
          language: 'python',
          status: 'failed',
          executionTime: 0,
          timestamp: '15 minutes ago',
          output: 'ImportError: No module named numpy'
        }
      ]);

      setLoading(false);
    };

    loadVMData();
  }, []);

  const getEnvironmentColor = (env: string) => {
    const colors = {
      python: 'text-yellow-400 bg-yellow-500/20',
      javascript: 'text-yellow-300 bg-yellow-600/20',
      cpp: 'text-blue-400 bg-blue-500/20',
      java: 'text-red-400 bg-red-500/20',
      rust: 'text-orange-400 bg-orange-500/20',
      go: 'text-cyan-400 bg-cyan-500/20',
      linux_full: 'text-purple-400 bg-purple-500/20'
    };
    return colors[env as keyof typeof colors] || 'text-gray-400 bg-gray-500/20';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      running: 'text-green-400 bg-green-500/20',
      stopped: 'text-red-400 bg-red-500/20',
      paused: 'text-yellow-400 bg-yellow-500/20',
      initializing: 'text-blue-400 bg-blue-500/20'
    };
    return colors[status as keyof typeof colors] || 'text-gray-400 bg-gray-500/20';
  };

  const createNewVM = () => {
    // Simulate VM creation
    const newVM: VMInstance = {
      id: `vm-${Date.now()}`,
      name: `New Environment ${vmInstances.length + 1}`,
      environment: 'python',
      status: 'initializing',
      cpuUsage: 0,
      memoryUsage: 0,
      diskUsage: 0,
      uptime: '0m',
      collaborators: 0,
      lastActivity: 'Just created'
    };
    
    setVmInstances([...vmInstances, newVM]);
    
    // Simulate initialization process
    setTimeout(() => {
      setVmInstances(prev => 
        prev.map(vm => 
          vm.id === newVM.id 
            ? { ...vm, status: 'running' as const, cpuUsage: 15, memoryUsage: 25 }
            : vm
        )
      );
    }, 3000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Monitor className="w-16 h-16 text-blue-400 animate-pulse mx-auto mb-4" />
          <p className="text-gray-400">Loading WebVM dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          className="flex items-center justify-between mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
              <Terminal className="w-8 h-8 text-blue-400" />
              WebVM Dashboard
            </h1>
            <p className="text-gray-400">
              Manage your browser-based development environments
            </p>
          </div>
          <button
            onClick={createNewVM}
            className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center gap-2"
          >
            <Play className="w-5 h-5" />
            Create VM
          </button>
        </motion.div>

        {/* VM Instances Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          <AnimatePresence>
            {vmInstances.map((vm, index) => (
              <motion.div
                key={vm.id}
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                onClick={() => setSelectedInstance(selectedInstance === vm.id ? null : vm.id)}
              >
                {/* VM Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      vm.status === 'running' ? 'bg-green-400 animate-pulse' :
                      vm.status === 'paused' ? 'bg-yellow-400' :
                      vm.status === 'stopped' ? 'bg-red-400' : 'bg-blue-400 animate-pulse'
                    }`} />
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(vm.status)}`}>
                      {vm.status.toUpperCase()}
                    </span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${getEnvironmentColor(vm.environment)}`}>
                    {vm.environment}
                  </span>
                </div>

                <h3 className="text-lg font-semibold mb-2">{vm.name}</h3>
                <p className="text-gray-400 text-sm mb-4">Uptime: {vm.uptime}</p>

                {/* Resource Usage */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-blue-400" />
                      <span className="text-sm">CPU</span>
                    </div>
                    <span className="text-sm text-gray-300">{vm.cpuUsage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-700"
                      style={{ width: `${vm.cpuUsage}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MemoryStick className="w-4 h-4 text-purple-400" />
                      <span className="text-sm">Memory</span>
                    </div>
                    <span className="text-sm text-gray-300">{vm.memoryUsage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-700"
                      style={{ width: `${vm.memoryUsage}%` }}
                    />
                  </div>
                </div>

                {/* VM Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    {vm.collaborators > 0 && (
                      <span className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {vm.collaborators}
                      </span>
                    )}
                    <span>Last: {vm.lastActivity}</span>
                  </div>
                  <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${
                    selectedInstance === vm.id ? 'rotate-90' : ''
                  }`} />
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {selectedInstance === vm.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-4 pt-4 border-t border-white/10"
                    >
                      <div className="grid grid-cols-3 gap-3 mb-4">
                        <button className="bg-green-500/20 hover:bg-green-500/30 text-green-400 p-2 rounded-lg transition-colors flex items-center justify-center gap-1">
                          <Play className="w-4 h-4" />
                          <span className="text-xs">Start</span>
                        </button>
                        <button className="bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-400 p-2 rounded-lg transition-colors flex items-center justify-center gap-1">
                          <Pause className="w-4 h-4" />
                          <span className="text-xs">Pause</span>
                        </button>
                        <button className="bg-red-500/20 hover:bg-red-500/30 text-red-400 p-2 rounded-lg transition-colors flex items-center justify-center gap-1">
                          <Square className="w-4 h-4" />
                          <span className="text-xs">Stop</span>
                        </button>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Disk Usage</span>
                        <span className="text-gray-300">{vm.diskUsage}%</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Execution History */}
        <motion.div
          className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-6 h-6 text-green-400" />
            <h2 className="text-xl font-bold">Recent Executions</h2>
          </div>
          
          <div className="space-y-4">
            {executionHistory.map((execution, index) => (
              <motion.div
                key={execution.id}
                className="flex items-center gap-4 p-4 bg-white/5 rounded-xl"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getEnvironmentColor(execution.language)}`}>
                  <Code className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold capitalize">{execution.language}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      execution.status === 'completed' ? 'text-green-400 bg-green-500/20' :
                      execution.status === 'failed' ? 'text-red-400 bg-red-500/20' :
                      'text-blue-400 bg-blue-500/20'
                    }`}>
                      {execution.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm truncate">{execution.output}</p>
                </div>
                <div className="text-right text-sm text-gray-500">
                  <div>{execution.executionTime}ms</div>
                  <div>{execution.timestamp}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default WebVMDashboard;