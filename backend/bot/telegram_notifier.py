import os
import logging
from telegram import Bot
from telegram.error import TelegramError
import asyncio

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Handle Telegram notifications"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.bot = None
        
        if self.bot_token:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram bot initialized")
            except Exception as e:
                logger.error(f"Error initializing Telegram bot: {e}")
    
    async def send_message(self, message: str, parse_mode: str = 'HTML'):
        """Send a message via Telegram"""
        if not self.bot or not self.chat_id:
            logger.warning("Telegram not configured")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def send_signal_notification(self, signal: dict):
        """Send a signal notification"""
        message = f"""
🔔 <b>New Trading Signal</b>

<b>Blockchain:</b> {signal.get('blockchain', 'N/A').upper()}
<b>Token:</b> {signal.get('token_symbol', 'Unknown')}
<b>Address:</b> <code>{signal.get('token_address', 'N/A')}</code>
<b>Event:</b> {signal.get('event_type', 'N/A')}
<b>Price:</b> ${signal.get('price', 0):.6f}
<b>Liquidity:</b> ${signal.get('liquidity', 0):,.2f}
<b>Volume 24h:</b> ${signal.get('volume_24h', 0):,.2f}
<b>Spread:</b> {signal.get('spread', 0):.2f}%
        """
        
        await self.send_message(message)
    
    async def send_trade_notification(self, trade: dict):
        """Send a trade notification"""
        status_emoji = "✅" if trade.get('status') == 'closed' else "🔄"
        
        message = f"""
{status_emoji} <b>Trade {trade.get('status', 'N/A').upper()}</b>

<b>Exchange:</b> {trade.get('exchange', 'N/A').upper()}
<b>Symbol:</b> {trade.get('symbol', 'N/A')}
<b>Side:</b> {trade.get('side', 'N/A').upper()}
<b>Entry Price:</b> ${trade.get('entry_price', 0):.6f}
<b>Amount:</b> {trade.get('amount', 0):.6f}
<b>Spread:</b> {trade.get('spread', 0):.2f}%
        """
        
        if trade.get('status') == 'closed':
            message += f"""
<b>Exit Price:</b> ${trade.get('exit_price', 0):.6f}
<b>Profit:</b> ${trade.get('profit', 0):.2f}
            """
        
        await self.send_message(message)
    
    async def send_status_update(self, stats: dict):
        """Send status update with statistics"""
        message = f"""
📊 <b>Bot Status Update</b>

<b>Total Signals:</b> {stats.get('total_signals', 0)}
<b>Total Trades:</b> {stats.get('total_trades', 0)}
<b>Open Trades:</b> {stats.get('open_trades', 0)}
<b>Total Profit:</b> ${stats.get('total_profit', 0):.2f}
<b>Today's Profit:</b> ${stats.get('today_profit', 0):.2f}
<b>Success Rate:</b> {stats.get('success_rate', 0):.1f}%
        """
        
        await self.send_message(message)