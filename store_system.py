"""
🏪 STORE SYSTEM
Ultimate Group King Bot - E-commerce Layer
Author: Nikhil Mehra (NikkuAi09)
"""

import logging
import uuid
from typing import Dict, List, Optional, Tuple
from database import Database
from payment_system import payment_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoreSystem:
    """Manages user stores and items"""
    
    def __init__(self):
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    def create_store(self, user_id: int, name: str, description: str) -> Tuple[bool, str]:
        """Create a new store for user"""
        try:
            stores_collection = self.db.get_collection('stores')
            if not stores_collection:
                return False, "Database error."
            
            # Check if user already has a store
            existing = stores_collection.find_one({'owner_id': user_id})
            if existing:
                return False, "You already have a store!"
            
            store_id = str(uuid.uuid4())[:8]
            stores_collection.insert_one({
                'store_id': store_id,
                'owner_id': user_id,
                'name': name,
                'description': description,
                'created_at': datetime.now().isoformat()
            })
                
            return True, "Store created successfully!"
        except Exception as e:
            logger.error(f"❌ Error creating store: {e}")
            return False, "System error."

    def add_item(self, user_id: int, name: str, price: float, description: str, content: str = None) -> Tuple[bool, str]:
        """Add item to user's store"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Get store ID
                cursor.execute('SELECT store_id FROM stores WHERE owner_id = ?', (user_id,))
                row = cursor.fetchone()
                if not row:
                    return False, "You don't have a store! Use /createstore first."
                
                store_id = row[0]
                item_id = str(uuid.uuid4())[:8]
                
                cursor.execute('''
                    INSERT INTO store_items (
                        item_id, store_id, name, price, description, content, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', CURRENT_TIMESTAMP)
                ''', (item_id, store_id, name, price, description, content))
                conn.commit()
                
            return True, f"Item '{name}' added to your store!"
        except Exception as e:
            logger.error(f"❌ Error adding item: {e}")
            return False, "System error."

    def get_store(self, user_id: int) -> Optional[Dict]:
        """Get user's store details"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM stores WHERE owner_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'store_id': row[0],
                        'owner_id': row[1],
                        'name': row[2],
                        'description': row[3],
                        'created_at': row[4]
                    }
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching store: {e}")
            return None

    def get_store_items(self, store_id: str) -> List[Dict]:
        """Get all active items in a store"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM store_items WHERE store_id = ? AND status = "ACTIVE"', (store_id,))
                rows = cursor.fetchall()
                
                items = []
                for row in rows:
                    items.append({
                        'item_id': row[0],
                        'store_id': row[1],
                        'name': row[2],
                        'price': row[3],
                        'description': row[4],
                        'content': row[5]
                    })
                return items
        except Exception as e:
            logger.error(f"❌ Error fetching items: {e}")
            return []

    def buy_item(self, buyer_id: int, item_id: str) -> Tuple[bool, str, Optional[str]]:
        """Buy an item from a store"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Get item details
                cursor.execute('SELECT * FROM store_items WHERE item_id = ?', (item_id,))
                item = cursor.fetchone()
                
                if not item:
                    return False, "Item not found!", None
                    
                price = item[3]
                store_id = item[1]
                content = item[5]
                
                # Get store owner
                cursor.execute('SELECT owner_id FROM stores WHERE store_id = ?', (store_id,))
                store = cursor.fetchone()
                if not store:
                    return False, "Store not found!", None
                
                owner_id = store[0]
                
                if buyer_id == owner_id:
                    return False, "You cannot buy from your own store!", None
                
                # Check balance and transfer
                if not payment_system.deduct_balance(buyer_id, price, f"Bought item: {item[2]}"):
                    return False, "Insufficient balance!", None
                    
                if not payment_system.add_balance(owner_id, price, f"Sale: {item[2]}"):
                    # Rollback deduction (simplified)
                    payment_system.add_balance(buyer_id, price, "Refund: Failed purchase")
                    return False, "Transaction failed!", None
                
                # Record purchase (optional, can be added to transactions table)
                
                return True, f"Successfully bought '{item[2]}'!", content
                
        except Exception as e:
            logger.error(f"❌ Error buying item: {e}")
            return False, "System error.", None

# Initialize store system
store_system = StoreSystem()
