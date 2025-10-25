import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_signals: 0,
    total_trades: 0,
    open_trades: 0,
    total_profit: 0,
    today_profit: 0,
    success_rate: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <Card className="card-hover bg-slate-900/50 backdrop-blur-xl border-slate-800" data-testid={`stat-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-slate-400">{title}</CardTitle>
          <span className="text-2xl">{icon}</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`text-3xl font-bold ${color}`}>{value}</div>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-slate-400 text-lg">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in" data-testid="dashboard-page">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Overview of your trading bot performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          title="Total Signals"
          value={stats.total_signals}
          icon="📡"
          color="text-cyan-400"
        />
        
        <StatCard
          title="Total Trades"
          value={stats.total_trades}
          icon="📊"
          color="text-purple-400"
        />
        
        <StatCard
          title="Open Trades"
          value={stats.open_trades}
          icon="🔄"
          color="text-yellow-400"
        />
        
        <StatCard
          title="Total Profit"
          value={`$${stats.total_profit.toFixed(2)}`}
          icon="💰"
          color={stats.total_profit >= 0 ? 'text-emerald-400' : 'text-red-400'}
        />
        
        <StatCard
          title="Today's Profit"
          value={`$${stats.today_profit.toFixed(2)}`}
          icon="📈"
          color={stats.today_profit >= 0 ? 'text-emerald-400' : 'text-red-400'}
        />
        
        <StatCard
          title="Success Rate"
          value={`${stats.success_rate.toFixed(1)}%`}
          icon="🎯"
          color="text-blue-400"
        />
      </div>

      {/* Recent Activity */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">System Status</CardTitle>
          <CardDescription className="text-slate-400">
            Bot is monitoring blockchains and exchanges
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300">Blockchain Monitor</span>
              </div>
              <span className="text-emerald-400 text-sm">Active</span>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300">Trading Engine</span>
              </div>
              <span className="text-emerald-400 text-sm">Active</span>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-slate-300">Exchange Connections</span>
              </div>
              <span className="text-emerald-400 text-sm">Connected</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;