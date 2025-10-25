# Crypto Trading Bot

Автоматичний торговий бот для криптовалют з підтримкою 5 бірж та моніторингом блокчейнів.

## 🚀 Особливості

- **Підтримка 5 бірж**: Bybit, BingX, Gate.io, OKX, XT.com
- **Моніторинг блокчейнів**: Ethereum, BSC, Solana
- **Автоматична торгівля**: Торгівля зі спредом 2-3%
- **Telegram бот**: Сповіщення та керування
- **Веб-дашборд**: React інтерфейс для моніторингу
- **Real-time оновлення**: WebSocket підтримка

## 📋 Встановлення

### 1. Налаштування Backend

```bash
cd /app/backend
pip install -r requirements.txt
```

### 2. Налаштування Frontend

```bash
cd /app/frontend
yarn install
```

### 3. Конфігурація .env

Відредагуйте `/app/backend/.env`:

```env
# MongoDB
MONGO_URL="mongodb://localhost:27017"
DB_NAME="crypto_trading_bot"

# Telegram
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"

# Exchange API Keys
BYBIT_API_KEY="your_bybit_key"
BYBIT_API_SECRET="your_bybit_secret"

BINGX_API_KEY="your_bingx_key"
BINGX_API_SECRET="your_bingx_secret"

GATE_API_KEY="your_gate_key"
GATE_API_SECRET="your_gate_secret"

OKX_API_KEY="your_okx_key"
OKX_API_SECRET="your_okx_secret"
OKX_PASSPHRASE="your_okx_passphrase"

XT_API_KEY="your_xt_key"
XT_API_SECRET="your_xt_secret"

# Blockchain RPC URLs (опціонально)
ETH_RPC_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
BSC_RPC_URL="https://bsc-dataseed.binance.org/"
SOL_RPC_URL="https://api.mainnet-beta.solana.com"

# Trading Mode
ALLOW_LIVE_TRADING="False"  # True для живих торгів
```

## 🎯 Запуск

### Backend API Server
```bash
sudo supervisorctl restart backend
```

### Frontend Dashboard
```bash
sudo supervisorctl restart frontend
```

### Запуск торгового бота (опціонально)
```bash
cd /app/backend
python bot_main.py
```

## 📊 Використання

1. **Веб-дашборд**: Відкрийте браузер та перейдіть до фронтенду
2. **Додайте біржі**: Натисніть "Exchanges" та додайте API ключі
3. **Налаштуйте параметри**: Перейдіть в "Settings" та встановіть:
   - Мінімальний/максимальний спред (2-3%)
   - Мінімальну ліквідність
   - Суму для торгівлі
   - Увімкніть/вимкніть автоматичну торгівлю

4. **Моніторинг**: 
   - Dashboard - загальна статистика
   - Signals - сигнали з блокчейну
   - Trades - історія торгів

## 🔧 Структура проекту

```
/app/
├── backend/
│   ├── server.py              # FastAPI сервер
│   ├── bot_main.py            # Головний бот
│   ├── exchanges/             # Інтеграції бірж
│   │   ├── bybit_exchange.py
│   │   ├── bingx_exchange.py
│   │   ├── gate_exchange.py
│   │   ├── okx_exchange.py
│   │   └── xt_exchange.py
│   └── bot/                   # Модулі бота
│       ├── blockchain_monitor.py
│       ├── trading_engine.py
│       ├── dex_client.py
│       └── telegram_notifier.py
├── frontend/
│   └── src/
│       ├── App.js
│       └── pages/
│           ├── Dashboard.js
│           ├── Signals.js
│           ├── Trades.js
│           ├── Exchanges.js
│           └── Settings.js
```

## ⚠️ Важливо

1. **Тестовий режим**: Спочатку запускайте з `ALLOW_LIVE_TRADING="False"`
2. **API ключі**: Зберігайте ключі в безпеці, не публікуйте в GitHub
3. **Ризики**: Криптовалютна торгівля має високі ризики
4. **Моніторинг**: Завжди перевіряйте логи та статистику

## 📱 Telegram бот

Отримуйте сповіщення про:
- Нові торгові сигнали
- Виконані торги
- Прибутки/збитки
- Статус системи

## 🛠️ Налаштування для продакшену

1. Використовуйте приватні RPC endpoints (Alchemy/Infura)
2. Налаштуйте SSL сертифікати
3. Увімкніть моніторинг (Sentry, Grafana)
4. Регулярні бекапи MongoDB
5. Rate limiting для API

## 📝 Ліцензія

MIT License
