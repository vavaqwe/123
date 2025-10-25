# 🔍 Як працює моніторинг сигналів

## Два режими роботи:

### 1️⃣ DEXScreener API (Рекомендовано для початку) ✅

**Що це:**
- Використовує готовий API від DEXScreener.com
- Найпростіший та найнадійніший спосіб
- Не потребує RPC endpoints
- Дані вже агреговані та відфільтровані

**Як працює:**
```
DEXScreener API → Trending токени + Нові пари
       ↓
Фільтрація (ліквідність > $5000, volume > $10000)
       ↓
Створення сигналу в MongoDB
       ↓
Telegram сповіщення
```

**Що моніторимо:**
- 🔥 **Trending токени** - топ токени по Ethereum, BSC, Solana
- 🆕 **Нові пари** - пари створені менше 24 годин тому
- 📊 **Дані**: ціна, ліквідність, об'єм 24h, зміна ціни

**Оновлення:**
- Trending: кожну 1 хвилину
- Нові пари: кожні 2 хвилини

**Приклад запиту:**
```bash
curl "https://api.dexscreener.com/latest/dex/search?q=ethereum"
```

**Переваги:**
✅ Швидко працює
✅ Не потребує API ключів
✅ Готові дані про токени
✅ Підтримує всі мережі

**Недоліки:**
❌ Затримка ~30 секунд
❌ Залежність від зовнішнього сервісу

---

### 2️⃣ Web3 Events (Прямий моніторинг блокчейну)

**Що це:**
- Прямий моніторинг блокчейн подій через RPC
- Миттєве виявлення нових пар
- Повний контроль над даними

**Як працює:**
```
Ethereum/BSC RPC → Нові блоки
       ↓
Фільтрація транзакцій
       ↓
Декодування PairCreated events
       ↓
DEXScreener API (додаткова інфо)
       ↓
Створення сигналу
```

**Що відстежуємо:**
- 🏭 **PairCreated** - нові пари на Uniswap/PancakeSwap
- 💱 **Swap** - великі свапи (> $50,000)
- 💧 **AddLiquidity** - додавання ліквідності

**Smart contracts:**
```
Uniswap V2 Factory: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
PancakeSwap Factory: 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73
```

**Вимоги:**
- Платний RPC endpoint (Alchemy/Infura/QuickNode)
- Вищі технічні вимоги
- Більше CPU/RAM

**Переваги:**
✅ Миттєве виявлення (~12s для ETH, ~3s для BSC)
✅ Повний контроль
✅ Не залежить від сторонніх сервісів

**Недоліки:**
❌ Потребує RPC ключі ($$$)
❌ Більше навантаження на сервер
❌ Складніша реалізація

---

## 🔧 Налаштування режиму

### Поточний режим: DEXScreener API ✅

Щоб змінити режим, відредагуйте `/app/backend/bot/blockchain_monitor.py`:

```python
class BlockchainMonitor:
    def __init__(self, ...):
        # DEXScreener режим (простий)
        self.use_dexscreener = True
        
        # Для Web3 режиму:
        # self.use_dexscreener = False
```

---

## 📊 Фільтри сигналів

**Мінімальні вимоги:**
- Ліквідність: ≥ $5,000
- Об'єм 24h: ≥ $10,000
- Спред: 1.5% - 4%

**Налаштування фільтрів:**
Відредагуйте у Settings сторінці веб-дашборду або `/app/backend/.env`:
- `MIN_LIQUIDITY=10000`
- `MIN_VOLUME_24H=50000`

---

## 🧪 Тестування

### Перевірка DEXScreener API:
```bash
curl "https://api.dexscreener.com/latest/dex/pairs/ethereum" | jq
```

### Запуск моніторингу:
```bash
cd /app/backend
python bot_main.py
```

### Логи:
```bash
tail -f /var/log/crypto_bot.log
```

---

## 💡 Рекомендації

**Для початку:**
1. ✅ Використовуйте DEXScreener API режим
2. ✅ Тестуйте з ALLOW_LIVE_TRADING=False
3. ✅ Налаштуйте Telegram для сповіщень

**Для продакшену:**
1. Отримайте платний RPC (Alchemy/Infura)
2. Перемкніться на Web3 Events режим
3. Налаштуйте моніторинг та алерти

---

## 🔗 Корисні посилання

- **DEXScreener API**: https://docs.dexscreener.com/api/reference
- **Alchemy RPC**: https://www.alchemy.com/
- **Infura**: https://infura.io/
- **Web3.py**: https://web3py.readthedocs.io/

---

## ❓ Питання?

**Q: Чому DEXScreener, а не прямий моніторинг?**
A: DEXScreener простіший, безкоштовний та покриває всі основні DEX. Для MVP це оптимально.

**Q: Яка затримка сигналів?**
A: DEXScreener: ~30-60 секунд. Web3: ~12 секунд (ETH), ~3 секунди (BSC).

**Q: Скільки коштує RPC?**
A: Alchemy/Infura: безкоштовно до 300М compute units/місяць. Потім від $50/місяць.

**Q: Чи можна комбінувати обидва режими?**
A: Так! Можна використовувати Web3 для швидкого виявлення + DEXScreener для додаткової інформації.
