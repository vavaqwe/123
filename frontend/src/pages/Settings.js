import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { Slider } from '@/components/ui/slider';

const Settings = () => {
  const [config, setConfig] = useState({
    min_spread: 2.0,
    max_spread: 3.0,
    min_liquidity: 10000,
    min_volume_24h: 50000,
    trade_amount: 100,
    auto_trading: false,
    active_blockchains: ['eth', 'bsc', 'solana'],
    active_exchanges: ['bybit', 'binance', 'gate', 'okx', 'xt']
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API}/config`);
      setConfig(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching config:', error);
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await axios.put(`${API}/config`, config);
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Error saving config:', error);
      toast.error('Failed to save settings');
    }
  };

  const toggleBlockchain = (blockchain) => {
    setConfig(prev => ({
      ...prev,
      active_blockchains: prev.active_blockchains.includes(blockchain)
        ? prev.active_blockchains.filter(b => b !== blockchain)
        : [...prev.active_blockchains, blockchain]
    }));
  };

  const toggleExchange = (exchange) => {
    setConfig(prev => ({
      ...prev,
      active_exchanges: prev.active_exchanges.includes(exchange)
        ? prev.active_exchanges.filter(e => e !== exchange)
        : [...prev.active_exchanges, exchange]
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-slate-400 text-lg">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in" data-testid="settings-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-slate-400">Configure your trading bot parameters</p>
        </div>
        <Button 
          className="bg-emerald-500 hover:bg-emerald-600 text-white" 
          onClick={handleSave}
          data-testid="save-settings-btn"
        >
          Save Settings
        </Button>
      </div>

      {/* Trading Parameters */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Trading Parameters</CardTitle>
          <CardDescription className="text-slate-400">
            Configure spread range and trading thresholds
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="text-slate-300">Minimum Spread (%)</Label>
              <div className="mt-3 space-y-3">
                <Slider
                  value={[config.min_spread]}
                  onValueChange={(value) => setConfig({ ...config, min_spread: value[0] })}
                  min={0.5}
                  max={5}
                  step={0.1}
                  className="w-full"
                />
                <Input
                  type="number"
                  data-testid="min-spread-input"
                  value={config.min_spread}
                  onChange={(e) => setConfig({ ...config, min_spread: parseFloat(e.target.value) })}
                  className="bg-slate-800 border-slate-700 text-white"
                  step="0.1"
                />
              </div>
            </div>

            <div>
              <Label className="text-slate-300">Maximum Spread (%)</Label>
              <div className="mt-3 space-y-3">
                <Slider
                  value={[config.max_spread]}
                  onValueChange={(value) => setConfig({ ...config, max_spread: value[0] })}
                  min={0.5}
                  max={10}
                  step={0.1}
                  className="w-full"
                />
                <Input
                  type="number"
                  data-testid="max-spread-input"
                  value={config.max_spread}
                  onChange={(e) => setConfig({ ...config, max_spread: parseFloat(e.target.value) })}
                  className="bg-slate-800 border-slate-700 text-white"
                  step="0.1"
                />
              </div>
            </div>

            <div>
              <Label className="text-slate-300">Minimum Liquidity ($)</Label>
              <Input
                type="number"
                data-testid="min-liquidity-input"
                value={config.min_liquidity}
                onChange={(e) => setConfig({ ...config, min_liquidity: parseFloat(e.target.value) })}
                className="mt-2 bg-slate-800 border-slate-700 text-white"
              />
            </div>

            <div>
              <Label className="text-slate-300">Minimum 24h Volume ($)</Label>
              <Input
                type="number"
                data-testid="min-volume-input"
                value={config.min_volume_24h}
                onChange={(e) => setConfig({ ...config, min_volume_24h: parseFloat(e.target.value) })}
                className="mt-2 bg-slate-800 border-slate-700 text-white"
              />
            </div>

            <div>
              <Label className="text-slate-300">Trade Amount ($)</Label>
              <Input
                type="number"
                data-testid="trade-amount-input"
                value={config.trade_amount}
                onChange={(e) => setConfig({ ...config, trade_amount: parseFloat(e.target.value) })}
                className="mt-2 bg-slate-800 border-slate-700 text-white"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Auto Trading */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Auto Trading</CardTitle>
          <CardDescription className="text-slate-400">
            Enable or disable automatic trade execution
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50">
            <div>
              <p className="text-white font-medium">Automatic Trading</p>
              <p className="text-slate-400 text-sm mt-1">
                {config.auto_trading ? 'Bot will execute trades automatically' : 'Bot will only notify about opportunities'}
              </p>
            </div>
            <Switch
              checked={config.auto_trading}
              onCheckedChange={(checked) => setConfig({ ...config, auto_trading: checked })}
              data-testid="auto-trading-switch"
            />
          </div>
        </CardContent>
      </Card>

      {/* Active Blockchains */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Active Blockchains</CardTitle>
          <CardDescription className="text-slate-400">
            Select which blockchains to monitor
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['eth', 'bsc', 'solana'].map((blockchain) => (
              <div
                key={blockchain}
                className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50"
              >
                <span className="text-white capitalize">{blockchain}</span>
                <Switch
                  checked={config.active_blockchains.includes(blockchain)}
                  onCheckedChange={() => toggleBlockchain(blockchain)}
                  data-testid={`blockchain-${blockchain}-switch`}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Active Exchanges */}
      <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
        <CardHeader>
          <CardTitle className="text-white">Active Exchanges</CardTitle>
          <CardDescription className="text-slate-400">
            Select which exchanges to use for trading
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['bybit', 'binance', 'gate', 'okx', 'xt'].map((exchange) => (
              <div
                key={exchange}
                className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50"
              >
                <span className="text-white capitalize">{exchange}</span>
                <Switch
                  checked={config.active_exchanges.includes(exchange)}
                  onCheckedChange={() => toggleExchange(exchange)}
                  data-testid={`exchange-${exchange}-switch`}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;