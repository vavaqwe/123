import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import axios from 'axios';
import '@/App.css';
import Dashboard from '@/pages/Dashboard';
import Signals from '@/pages/Signals';
import Trades from '@/pages/Trades';
import Exchanges from '@/pages/Exchanges';
import Settings from '@/pages/Settings';
import { Toaster } from '@/components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function App() {
  return (
    <div className="App">
      <Toaster position="top-right" richColors />
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
          {/* Sidebar Navigation */}
          <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-900/50 backdrop-blur-xl border-r border-slate-800">
            <div className="p-6">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                💹 Crypto Bot
              </h1>
              <p className="text-slate-400 text-sm mt-1">Multi-Exchange Trading</p>
            </div>
            
            <nav className="mt-6 px-3 space-y-1">
              <NavLink
                to="/"
                data-testid="nav-dashboard"
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive
                    ? 'bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-emerald-400'
                  }`
                }
              >
                <span className="mr-3">🏛️</span>
                Dashboard
              </NavLink>
              
              <NavLink
                to="/signals"
                data-testid="nav-signals"
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive
                    ? 'bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-emerald-400'
                  }`
                }
              >
                <span className="mr-3">📡</span>
                Signals
              </NavLink>
              
              <NavLink
                to="/trades"
                data-testid="nav-trades"
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive
                    ? 'bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-emerald-400'
                  }`
                }
              >
                <span className="mr-3">💰</span>
                Trades
              </NavLink>
              
              <NavLink
                to="/exchanges"
                data-testid="nav-exchanges"
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive
                    ? 'bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-emerald-400'
                  }`
                }
              >
                <span className="mr-3">🏬</span>
                Exchanges
              </NavLink>
              
              <NavLink
                to="/settings"
                data-testid="nav-settings"
                className={({ isActive }) =>
                  `flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${isActive
                    ? 'bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : 'text-slate-300 hover:bg-slate-800/50 hover:text-emerald-400'
                  }`
                }
              >
                <span className="mr-3">⚙️</span>
                Settings
              </NavLink>
            </nav>
            
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
              <div className="text-xs text-slate-500 text-center">
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span>Bot Active</span>
                </div>
              </div>
            </div>
          </aside>
          
          {/* Main Content */}
          <main className="ml-64 p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/signals" element={<Signals />} />
              <Route path="/trades" element={<Trades />} />
              <Route path="/exchanges" element={<Exchanges />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;