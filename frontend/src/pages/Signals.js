import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const Signals = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSignals = async () => {
    try {
      const response = await axios.get(`${API}/signals?limit=50`);
      setSignals(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching signals:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'notified':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'executed':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'skipped':
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-slate-400 text-lg">Loading signals...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in" data-testid="signals-page">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Trading Signals</h1>
        <p className="text-slate-400">Real-time signals from blockchain monitoring</p>
      </div>

      {signals.length === 0 ? (
        <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
          <CardContent className="py-12 text-center">
            <p className="text-slate-400 text-lg">No signals yet. Bot is monitoring...</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {signals.map((signal, index) => (
            <Card key={signal.id || index} className="card-hover bg-slate-900/50 backdrop-blur-xl border-slate-800" data-testid={`signal-item-${index}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <CardTitle className="text-white text-lg">
                        {signal.token_symbol || 'Unknown Token'}
                      </CardTitle>
                      <Badge className={getStatusColor(signal.status)}>
                        {signal.status}
                      </Badge>
                      <Badge variant="outline" className="border-slate-700 text-slate-300">
                        {signal.blockchain?.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-slate-400 text-sm font-mono">
                      {signal.token_address}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-slate-400 text-xs">
                      {new Date(signal.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Event Type</p>
                    <p className="text-slate-200 font-medium">{signal.event_type}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Price</p>
                    <p className="text-slate-200 font-medium">${signal.price?.toFixed(6)}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Liquidity</p>
                    <p className="text-emerald-400 font-medium">
                      ${signal.liquidity?.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Volume 24h</p>
                    <p className="text-cyan-400 font-medium">
                      ${signal.volume_24h?.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Signals;