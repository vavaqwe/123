import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const Trades = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrades();
    const interval = setInterval(fetchTrades, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchTrades = async () => {
    try {
      const response = await axios.get(`${API}/trades?limit=50`);
      setTrades(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching trades:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'closed':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-slate-400 text-lg">Loading trades...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in" data-testid="trades-page">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Trades</h1>
        <p className="text-slate-400">History of executed trades</p>
      </div>

      {trades.length === 0 ? (
        <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
          <CardContent className="py-12 text-center">
            <p className="text-slate-400 text-lg">No trades yet</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {trades.map((trade, index) => (
            <Card key={trade.id || index} className="card-hover bg-slate-900/50 backdrop-blur-xl border-slate-800" data-testid={`trade-item-${index}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <CardTitle className="text-white text-lg">
                        {trade.symbol}
                      </CardTitle>
                      <Badge className={getStatusColor(trade.status)}>
                        {trade.status}
                      </Badge>
                      <Badge variant="outline" className="border-slate-700 text-slate-300">
                        {trade.exchange?.toUpperCase()}
                      </Badge>
                      <Badge 
                        variant="outline" 
                        className={trade.side === 'buy' ? 'border-emerald-600 text-emerald-400' : 'border-red-600 text-red-400'}
                      >
                        {trade.side?.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-slate-400 text-xs">
                      {new Date(trade.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Entry Price</p>
                    <p className="text-slate-200 font-medium">${trade.entry_price?.toFixed(6)}</p>
                  </div>
                  {trade.exit_price && (
                    <div>
                      <p className="text-slate-500 text-xs mb-1">Exit Price</p>
                      <p className="text-slate-200 font-medium">${trade.exit_price?.toFixed(6)}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Amount</p>
                    <p className="text-slate-200 font-medium">{trade.amount?.toFixed(6)}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Spread</p>
                    <p className="text-cyan-400 font-medium">{trade.spread?.toFixed(2)}%</p>
                  </div>
                  {trade.profit !== null && trade.profit !== undefined && (
                    <div>
                      <p className="text-slate-500 text-xs mb-1">Profit/Loss</p>
                      <p className={`font-bold ${trade.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        ${trade.profit?.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
                {trade.closed_at && (
                  <div className="mt-3 pt-3 border-t border-slate-800">
                    <p className="text-slate-500 text-xs">
                      Closed at: {new Date(trade.closed_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Trades;