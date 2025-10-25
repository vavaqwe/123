import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '@/App';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';

const Exchanges = () => {
  const [exchanges, setExchanges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: 'bybit',
    api_key: '',
    api_secret: '',
    is_active: true
  });

  useEffect(() => {
    fetchExchanges();
  }, []);

  const fetchExchanges = async () => {
    try {
      const response = await axios.get(`${API}/exchanges`);
      setExchanges(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching exchanges:', error);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/exchanges`, formData);
      toast.success('Exchange added successfully');
      setIsDialogOpen(false);
      setFormData({ name: 'bybit', api_key: '', api_secret: '', is_active: true });
      fetchExchanges();
    } catch (error) {
      console.error('Error adding exchange:', error);
      toast.error('Failed to add exchange');
    }
  };

  const handleDelete = async (exchangeId) => {
    if (!window.confirm('Are you sure you want to delete this exchange?')) return;
    
    try {
      await axios.delete(`${API}/exchanges/${exchangeId}`);
      toast.success('Exchange deleted successfully');
      fetchExchanges();
    } catch (error) {
      console.error('Error deleting exchange:', error);
      toast.error('Failed to delete exchange');
    }
  };

  const exchangeIcons = {
    bybit: '🔵',
    binance: '🟡',
    bingx: '🟠',
    gate: '🟢',
    okx: '⚫',
    xt: '🔴'
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-slate-400 text-lg">Loading exchanges...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in" data-testid="exchanges-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Exchanges</h1>
          <p className="text-slate-400">Manage your exchange connections</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-emerald-500 hover:bg-emerald-600 text-white" data-testid="add-exchange-btn">
              + Add Exchange
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-800">
            <DialogHeader>
              <DialogTitle className="text-white">Add New Exchange</DialogTitle>
              <DialogDescription className="text-slate-400">
                Connect a new exchange to your trading bot
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="exchange-name" className="text-slate-300">Exchange</Label>
                  <select
                    id="exchange-name"
                    data-testid="exchange-name-select"
                    className="w-full mt-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-white"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  >
                    <option value="bybit">Bybit</option>
                    <option value="binance">BingX</option>
                    <option value="gate">Gate.io</option>
                    <option value="okx">OKX</option>
                    <option value="xt">XT.com</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="api-key" className="text-slate-300">API Key</Label>
                  <Input
                    id="api-key"
                    data-testid="api-key-input"
                    type="text"
                    className="mt-2 bg-slate-800 border-slate-700 text-white"
                    value={formData.api_key}
                    onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="api-secret" className="text-slate-300">API Secret</Label>
                  <Input
                    id="api-secret"
                    data-testid="api-secret-input"
                    type="password"
                    className="mt-2 bg-slate-800 border-slate-700 text-white"
                    value={formData.api_secret}
                    onChange={(e) => setFormData({ ...formData, api_secret: e.target.value })}
                    required
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is-active"
                    checked={formData.is_active}
                    onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                  />
                  <Label htmlFor="is-active" className="text-slate-300">Active</Label>
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="bg-emerald-500 hover:bg-emerald-600" data-testid="submit-exchange-btn">
                  Add Exchange
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {exchanges.length === 0 ? (
        <Card className="bg-slate-900/50 backdrop-blur-xl border-slate-800">
          <CardContent className="py-12 text-center">
            <p className="text-slate-400 text-lg mb-4">No exchanges connected</p>
            <p className="text-slate-500 text-sm">Add your first exchange to start trading</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exchanges.map((exchange) => (
            <Card key={exchange.id} className="card-hover bg-slate-900/50 backdrop-blur-xl border-slate-800" data-testid={`exchange-card-${exchange.name}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-3xl">{exchangeIcons[exchange.name] || '🏬'}</span>
                    <div>
                      <CardTitle className="text-white capitalize">{exchange.name}</CardTitle>
                      <Badge 
                        className={exchange.is_active 
                          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30 mt-1' 
                          : 'bg-slate-500/20 text-slate-400 border-slate-500/30 mt-1'
                        }
                      >
                        {exchange.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <p className="text-slate-500 text-xs">API Key</p>
                    <p className="text-slate-300 text-sm font-mono truncate">
                      {exchange.api_key.substring(0, 20)}...
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs">Added</p>
                    <p className="text-slate-300 text-sm">
                      {new Date(exchange.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  className="w-full mt-4"
                  onClick={() => handleDelete(exchange.id)}
                  data-testid={`delete-exchange-${exchange.name}`}
                >
                  Remove
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Exchanges;