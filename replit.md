# Crypto Trading Bot - Multi-Exchange Trading Platform

## Overview

This is a comprehensive crypto trading bot that monitors multiple blockchains (Ethereum, BSC, Solana) and executes trades across 5 major cryptocurrency exchanges (Bybit, BingX, Gate.io, OKX, XT.com). The application features:

- **Backend**: Python FastAPI server with MongoDB database
- **Frontend**: React dashboard with real-time updates
- **Trading Bot**: Automated trading engine with blockchain monitoring

## Project Status

✅ Fully configured and running on Replit
- All three workflows (MongoDB, Backend, Frontend) are running successfully
- Frontend accessible on port 5000
- Backend API running on port 8000
- MongoDB running on localhost:27017

## Recent Changes

**Date: October 25, 2025**
- Initial Replit setup completed
- Installed Python 3.11 and Node.js 20
- Installed MongoDB 7.0.16 for local database
- Configured all environment variables for Replit deployment
- Set up CORS to allow frontend-backend communication
- Updated React dev server to allow all hosts (required for Replit proxy)
- Configured deployment settings for autoscale deployment

## Project Architecture

### Backend (Python/FastAPI)
- **Location**: `/backend`
- **Port**: 8000 (bound to 0.0.0.0 for external access)
- **Database**: MongoDB (localhost:27017)
- **API Endpoints**:
  - `GET /api/stats` - Trading statistics
  - `GET /api/signals` - Trading signals from blockchain monitoring
  - `GET /api/trades` - Trade history
  - `GET /api/exchanges` - Exchange configurations
  - `POST /api/exchanges` - Add new exchange
  - `GET /api/config` - Bot configuration
  - `PUT /api/config` - Update bot configuration
  - `WebSocket /ws` - Real-time updates

### Frontend (React/Create React App with CRACO)
- **Location**: `/frontend`
- **Port**: 5000 (bound to 0.0.0.0:5000)
- **Framework**: React 19 with Tailwind CSS
- **UI Components**: Radix UI component library
- **Routes**:
  - `/` - Dashboard (overview and stats)
  - `/signals` - Trading signals
  - `/trades` - Trade history
  - `/exchanges` - Exchange management
  - `/settings` - Bot configuration

### Database (MongoDB)
- **Version**: 7.0.16
- **Data Directory**: `~/mongodb/data`
- **Collections**:
  - `exchanges` - Exchange API credentials
  - `signals` - Trading signals from blockchain
  - `trades` - Trade execution history
  - `bot_config` - Bot configuration settings

## Environment Configuration

### Backend Environment (`/backend/.env`)
- `MONGO_URL`: MongoDB connection string
- `DB_NAME`: Database name
- `CORS_ORIGINS`: Allowed origins for CORS
- Exchange API keys (Bybit, BingX, Gate.io, OKX, XT)
- Blockchain RPC URLs (ETH, BSC, Solana)
- Telegram bot configuration
- `ALLOW_LIVE_TRADING`: Safety flag for production trading

### Frontend Environment (`/frontend/.env`)
- `REACT_APP_BACKEND_URL`: Backend API URL (Replit domain:8000)
- `WDS_SOCKET_PORT`: WebSocket port for hot reload
- `REACT_APP_ENABLE_VISUAL_EDITS`: Visual editing mode
- `DISABLE_HOT_RELOAD`: Hot reload configuration

## User Preferences

None yet specified.

## Development Notes

### Important Replit-Specific Configurations

1. **Frontend Proxy Configuration** (`frontend/craco.config.js`):
   - CRITICAL: `allowedHosts: 'all'` is required because users access the site through Replit's proxy
   - Frontend must bind to `0.0.0.0:5000` for the proxy to work
   - Without this, users will see a blank page

2. **Backend Configuration**:
   - Backend must bind to `0.0.0.0:8000` (not localhost) so the frontend can access it
   - CORS must include the Replit domain and localhost origins

3. **MongoDB**:
   - Runs locally on port 27017 (only accessible within the Replit environment)
   - Automatically started via workflow

### Workflows

Three workflows are configured to run the application:

1. **MongoDB**: Starts the MongoDB database server
   - Command: `mongod --dbpath=$HOME/mongodb/data --bind_ip 127.0.0.1`
   - Output: Console

2. **Backend**: Starts the FastAPI server
   - Command: `cd backend && uvicorn server:app --host 0.0.0.0 --port 8000`
   - Port: 8000
   - Output: Console

3. **Frontend**: Starts the React development server
   - Command: `cd frontend && PORT=5000 npm start`
   - Port: 5000
   - Output: Webview (primary interface users see)

### Dependencies

**Backend (Python)**:
- FastAPI & Uvicorn (API framework)
- Motor (async MongoDB driver)
- python-dotenv (environment management)
- Web3.py (blockchain interaction)
- python-telegram-bot (notifications)
- Exchange SDKs (aiohttp for API calls)

**Frontend (Node.js)**:
- React 19
- React Router (navigation)
- Axios (API calls)
- Tailwind CSS (styling)
- Radix UI (component library)
- CRACO (Create React App Configuration Override)

### Security Notes

⚠️ **Important Security Considerations**:

1. `.env` files are in `.gitignore` to prevent committing secrets
2. `ALLOW_LIVE_TRADING` is set to `False` by default - change carefully in production
3. Exchange API keys should have minimal permissions (read + trade, no withdrawal)
4. MongoDB has no authentication enabled (local development only)
5. For production deployment, enable MongoDB authentication and use environment secrets

## Trading Bot Features

### Blockchain Monitoring
- Monitors Ethereum, BSC, and Solana blockchains
- Detects pool creation, large swaps, and liquidity events
- Filters signals based on:
  - Minimum/maximum spread (2-3%)
  - Minimum liquidity ($10,000)
  - Minimum 24h volume ($50,000)

### Supported Exchanges
1. **Bybit** - Spot and derivatives trading
2. **BingX** - Multi-asset trading
3. **Gate.io** - Comprehensive exchange
4. **OKX** - Global crypto exchange
5. **XT.com** - Digital asset exchange

### Auto-Trading
- Configurable trading parameters
- Risk management with spread limits
- Real-time WebSocket updates
- Telegram notifications (when configured)

## Getting Started

The application is already running! To use it:

1. **View the Dashboard**: The frontend is automatically displayed
2. **Add Exchange Keys**: Navigate to "Exchanges" and add your API credentials
3. **Configure Settings**: Go to "Settings" to adjust trading parameters
4. **Monitor Signals**: Check "Signals" for blockchain opportunities
5. **Review Trades**: View trade history in "Trades"

## Troubleshooting

### Frontend not loading?
- Check that the Frontend workflow is running
- Verify port 5000 is accessible
- Check browser console for errors

### Backend API errors?
- Ensure Backend workflow is running on port 8000
- Verify MongoDB is running
- Check backend logs for detailed errors

### Database connection errors?
- Confirm MongoDB workflow is running
- Check MongoDB logs for startup errors
- Verify data directory exists: `~/mongodb/data`

## Future Enhancements

Potential improvements:
- Add database authentication for production
- Implement user authentication system
- Add more blockchain networks
- Support additional exchanges
- Enhanced risk management features
- Historical data analytics
- Paper trading mode for testing strategies
