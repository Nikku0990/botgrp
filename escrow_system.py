"""
🤝 ESCROW SYSTEM
Ultimate Group King Bot - Secure Deal Layer
Author: Nikhil Mehra (NikkuAi09)
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database import Database
from payment_system import payment_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EscrowSystem:
    """Manages secure escrow transactions"""
    
    def __init__(self):
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    def create_deal(self, buyer_id: int, seller_id: int, amount: float, description: str) -> Tuple[bool, str]:
        """Create a new escrow deal"""
        if amount <= 0:
            return False, "Invalid amount!"
            
        if buyer_id == seller_id:
            return False, "You cannot trade with yourself!"
            
        try:
            deal_id = str(uuid.uuid4())[:8]
            
            escrow_collection = self.db.get_collection('escrow_deals')
            if escrow_collection:
                escrow_collection.insert_one({
                    'deal_id': deal_id,
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'amount': amount,
                    'description': description,
                    'status': 'PENDING',
                    'created_at': datetime.now().isoformat()
                })
                
            return True, deal_id
        except Exception as e:
            logger.error(f"❌ Error creating deal: {e}")
            return False, "System error creating deal."

    def get_deal(self, deal_id: str) -> Optional[Dict]:
        """Get deal details"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM escrow_deals WHERE deal_id = ?', (deal_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'deal_id': row[0],
                        'buyer_id': row[1],
                        'seller_id': row[2],
                        'amount': row[3],
                        'description': row[4],
                        'status': row[5],
                        'created_at': row[6]
                    }
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching deal {deal_id}: {e}")
            return None

    def accept_deal(self, deal_id: str, user_id: int) -> Tuple[bool, str]:
        """Seller accepts the deal"""
        deal = self.get_deal(deal_id)
        if not deal:
            return False, "Deal not found!"
            
        if deal['seller_id'] != user_id:
            return False, "You are not the seller!"
            
        if deal['status'] != 'PENDING':
            return False, f"Deal is already {deal['status']}!"
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE escrow_deals 
                    SET status = 'ACCEPTED', updated_at = CURRENT_TIMESTAMP 
                    WHERE deal_id = ?
                ''', (deal_id,))
                conn.commit()
            return True, "Deal accepted! Waiting for buyer to pay."
        except Exception as e:
            logger.error(f"❌ Error accepting deal {deal_id}: {e}")
            return False, "System error."

    def pay_deal(self, deal_id: str, user_id: int) -> Tuple[bool, str]:
        """Buyer pays for the deal (Funds held in Escrow)"""
        deal = self.get_deal(deal_id)
        if not deal:
            return False, "Deal not found!"
            
        if deal['buyer_id'] != user_id:
            return False, "You are not the buyer!"
            
        if deal['status'] != 'ACCEPTED':
            return False, "Deal must be ACCEPTED by seller first!"
            
        # Check balance
        wallet = payment_system.get_wallet(user_id)
        if not wallet or wallet['balance'] < deal['amount']:
            return False, "Insufficient balance! Please /deposit funds."
            
        try:
            # Deduct from buyer
            if not payment_system.deduct_balance(user_id, deal['amount'], f"Escrow Payment: {deal_id}"):
                return False, "Payment failed!"
                
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE escrow_deals 
                    SET status = 'FUNDED', updated_at = CURRENT_TIMESTAMP 
                    WHERE deal_id = ?
                ''', (deal_id,))
                conn.commit()
                
            return True, "Payment successful! Funds are now held in Escrow."
        except Exception as e:
            logger.error(f"❌ Error paying deal {deal_id}: {e}")
            return False, "System error."

    def release_funds(self, deal_id: str, user_id: int) -> Tuple[bool, str]:
        """Buyer releases funds to seller"""
        deal = self.get_deal(deal_id)
        if not deal:
            return False, "Deal not found!"
            
        if deal['buyer_id'] != user_id:
            return False, "Only buyer can release funds!"
            
        if deal['status'] != 'FUNDED':
            return False, "Deal is not funded yet!"
            
        try:
            # Credit to seller
            if not payment_system.add_balance(deal['seller_id'], deal['amount'], f"Escrow Release: {deal_id}"):
                return False, "Transfer failed!"
                
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE escrow_deals 
                    SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP 
                    WHERE deal_id = ?
                ''', (deal_id,))
                conn.commit()
                
            return True, "Funds released to seller! Deal completed. 🎉"
        except Exception as e:
            logger.error(f"❌ Error releasing funds {deal_id}: {e}")
            return False, "System error."

    def dispute_deal(self, deal_id: str, user_id: int) -> Tuple[bool, str]:
        """Raise a dispute"""
        deal = self.get_deal(deal_id)
        if not deal:
            return False, "Deal not found!"
            
        if user_id not in [deal['buyer_id'], deal['seller_id']]:
            return False, "You are not part of this deal!"
            
        if deal['status'] not in ['FUNDED', 'ACCEPTED']:
            return False, "Cannot dispute this deal state!"
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE escrow_deals 
                    SET status = 'DISPUTED', updated_at = CURRENT_TIMESTAMP 
                    WHERE deal_id = ?
                ''', (deal_id,))
                conn.commit()
            return True, "Dispute raised! Admin will review shortly."
        except Exception as e:
            logger.error(f"❌ Error disputing deal {deal_id}: {e}")
            return False, "System error."

# Initialize escrow system
escrow_system = EscrowSystem()
