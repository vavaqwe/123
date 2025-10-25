#!/bin/bash

# Crypto Trading Bot - Quick Start Script
# Цей скрипт допоможе швидко запустити торговий бот

echo "🚀 Crypto Trading Bot - Запуск"
echo "================================"
echo ""

# Check if .env is configured
if ! grep -q "TELEGRAM_BOT_TOKEN=" /app/backend/.env || [ -z "$(grep TELEGRAM_BOT_TOKEN= /app/backend/.env | cut -d'=' -f2)" ]; then
    echo "⚠️  УВАГА: Налаштуйте .env файл перед запуском!"
    echo ""
    echo "Відредагуйте /app/backend/.env та додайте:"
    echo "  - TELEGRAM_BOT_TOKEN (отримайте від @BotFather в Telegram)"
    echo "  - TELEGRAM_CHAT_ID (ваш Telegram ID)"
    echo "  - API ключі від бірж (Bybit, BingX, Gate.io, OKX, XT.com)"
    echo ""
    echo "Після налаштування запустіть цей скрипт знову."
    exit 1
fi

echo "✅ .env файл знайдено"
echo ""

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB не запущено. Запускаю..."
    sudo systemctl start mongodb
    sleep 2
fi

echo "✅ MongoDB запущено"
echo ""

# Check if backend is running
if ! sudo supervisorctl status backend | grep -q "RUNNING"; then
    echo "⚠️  Backend API не запущено. Запускаю..."
    sudo supervisorctl start backend
    sleep 3
fi

echo "✅ Backend API запущено"
echo ""

# Check if frontend is running
if ! sudo supervisorctl status frontend | grep -q "RUNNING"; then
    echo "⚠️  Frontend не запущено. Запускаю..."
    sudo supervisorctl start frontend
    sleep 3
fi

echo "✅ Frontend запущено"
echo ""

# Ask about trading mode
echo "Режим роботи бота:"
echo "1. Тестовий режим (тільки сповіщення, без торгів)"
echo "2. Живі торги (автоматична торгівля з реальними коштами)"
echo ""
read -p "Оберіть режим (1 або 2): " mode

if [ "$mode" = "2" ]; then
    echo "⚠️  УВАГА: Ви обрали режим ЖИВИХ ТОРГІВ!"
    read -p "Ви впевнені? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        sed -i 's/ALLOW_LIVE_TRADING="False"/ALLOW_LIVE_TRADING="True"/' /app/backend/.env
        echo "✅ Режим живих торгів УВІМКНЕНО"
    else
        echo "✅ Залишаємось в тестовому режимі"
    fi
else
    sed -i 's/ALLOW_LIVE_TRADING="True"/ALLOW_LIVE_TRADING="False"/' /app/backend/.env
    echo "✅ Тестовий режим активовано"
fi

echo ""
echo "================================"
echo "🎉 Бот готовий до роботи!"
echo ""
echo "📊 Веб-дашборд: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8001/api"
echo ""
echo "Щоб запустити торговий бот (окремий процес):"
echo "  cd /app/backend"
echo "  python bot_main.py"
echo ""
echo "Логи:"
echo "  Backend: tail -f /var/log/supervisor/backend.err.log"
echo "  Frontend: tail -f /var/log/supervisor/frontend.out.log"
echo "  Bot: tail -f /var/log/crypto_bot.log"
echo ""
echo "================================"
