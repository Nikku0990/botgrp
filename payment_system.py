"""
💰 PAYMENT SYSTEM & ECONOMY
Ultimate Group King Bot - Economy Layer
Author: Nikhil Mehra (NikkuAi09)
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentSystem:
    """Manages all economy and payment related operations"""
    
    def __init__(self):
        self.currency_name = "BotCoins"
        self.currency_symbol = "🪙"
        self.admin_upi = "nikhilop09@ibl"  # Admin UPI for deposits
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
    def create_wallet(self, user_id: int) -> bool:
        """Create a wallet for a user if not exists"""
        try:
            # Check if wallet exists
            wallet = self.get_wallet(user_id)
            if wallet:
                return True
                
            # Create new wallet in DB
            wallets_collection = self.db.get_collection('wallets')
            if wallets_collection:
                wallets_collection.insert_one({
                    'user_id': user_id,
                    'balance': 0.0,
                    'created_at': datetime.now().isoformat()
                })
            return True
        except Exception as e:
            logger.error(f"❌ Error creating wallet for {user_id}: {e}")
            return False
            
    def get_wallet(self, user_id: int) -> Optional[Dict]:
        """Get user wallet details"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM wallets WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'user_id': row[0],
                        'balance': row[1],
                        'created_at': row[2],
                        'updated_at': row[3]
                    }
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching wallet for {user_id}: {e}")
            return None

    def add_balance(self, user_id: int, amount: float, description: str = "Deposit") -> bool:
        """Add balance to user wallet"""
        if amount <= 0:
            return False
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Update wallet
                cursor.execute('''
                    UPDATE wallets 
                    SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (amount, user_id))
                
                # Log transaction
                cursor.execute('''
                    INSERT INTO transactions (
                        transaction_id, user_id, type, amount, description, status, created_at
                    ) VALUES (?, ?, 'CREDIT', ?, ?, 'COMPLETED', CURRENT_TIMESTAMP)
                ''', (str(uuid.uuid4()), user_id, amount, description))
                
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error adding balance for {user_id}: {e}")
            return False

    def deduct_balance(self, user_id: int, amount: float, description: str = "Withdrawal") -> bool:
        """Deduct balance from user wallet"""
        if amount <= 0:
            return False
            
        wallet = self.get_wallet(user_id)
        if not wallet or wallet['balance'] < amount:
            return False
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Update wallet
                cursor.execute('''
                    UPDATE wallets 
                    SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (amount, user_id))
                
                # Log transaction
                cursor.execute('''
                    INSERT INTO transactions (
                        transaction_id, user_id, type, amount, description, status, created_at
                    ) VALUES (?, ?, 'DEBIT', ?, ?, 'COMPLETED', CURRENT_TIMESTAMP)
                ''', (str(uuid.uuid4()), user_id, amount, description))
                
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error deducting balance for {user_id}: {e}")
            return False

    def generate_payment_link(self, user_id: int, amount: float) -> str:
        """Generate a UPI payment link for deposit"""
        # Format: upi://pay?pa={upi_id}&pn={name}&am={amount}&tn={note}
        # Note: This is a standard UPI deep link format
        
        transaction_ref = str(uuid.uuid4())[:8]
        note = f"Deposit-{user_id}-{transaction_ref}"
        
        link = f"upi://pay?pa={self.admin_upi}&pn=UltimateBot&am={amount}&tn={note}&cu=INR"
        
        # Log pending deposit
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transactions (
                    ) VALUES (?, ?, 'DEPOSIT_PENDING', ?, ?, 'PENDING', CURRENT_TIMESTAMP)
                ''', (transaction_ref, user_id, amount, f"UPI Deposit: {link}"))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Error logging pending deposit: {e}")
            
        return link

    def request_withdrawal(self, user_id: int, amount: float, upi_id: str) -> Tuple[bool, str]:
        """Request a withdrawal to user's UPI"""
        wallet = self.get_wallet(user_id)
        if not wallet or wallet['balance'] < amount:
            return False, "Insufficient balance!"
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Deduct balance immediately (hold it)
                cursor.execute('''
                    UPDATE wallets 
                    SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE user_id = ?
                ''', (amount, user_id))
                
                # Log withdrawal request
                cursor.execute('''
                    INSERT INTO transactions (
                        transaction_id, user_id, type, amount, description, status, created_at
                    ) VALUES (?, ?, 'WITHDRAWAL_REQUEST', ?, ?, 'PENDING', CURRENT_TIMESTAMP)
                ''', (str(uuid.uuid4()), user_id, amount, f"Withdrawal to {upi_id}"))
                
                conn.commit()
            return True, "Withdrawal request submitted! Admin will process it shortly."
        except Exception as e:
            logger.error(f"❌ Error requesting withdrawal for {user_id}: {e}")
            return False, "System error processing withdrawal."

    def get_pending_withdrawals(self) -> List[Dict]:
        """Get all pending withdrawal requests (for Admin Dashboard)"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM transactions 
                    WHERE type = 'WITHDRAWAL_REQUEST' AND status = 'PENDING'
                ''')
                rows = cursor.fetchall()
                
                withdrawals = []
                for row in rows:
                    withdrawals.append({
                        'transaction_id': row[0],
                        'user_id': row[1],
                        'amount': row[3],
                        'description': row[4],
                        'created_at': row[6]
                    })
                return withdrawals
        except Exception as e:
            logger.error(f"❌ Error fetching pending withdrawals: {e}")
            return []

# Initialize payment system
payment_system = PaymentSystem()
