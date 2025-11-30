"""
🆔 IDENTITY SYSTEM
Ultimate Group King Bot - User Identity Layer
Author: Nikhil Mehra (NikkuAi09)
"""

import logging
from typing import Dict, Optional, Tuple
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdentitySystem:
    """Manages user identities (Custom ID, Bio, Business)"""
    
    def __init__(self):
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    def set_custom_id(self, user_id: int, custom_id: str) -> Tuple[bool, str]:
        """Set a custom ID (handle) for the user"""
        if not custom_id.startswith("@"):
            return False, "Custom ID must start with @ (e.g., @King)"
            
        if len(custom_id) < 4 or len(custom_id) > 20:
            return False, "Custom ID must be between 4 and 20 characters!"
            
        try:
            identities_collection = self.db.get_collection('identities')
            if not identities_collection:
                return False, "Database error."
                
            # Check if ID is taken
            existing = identities_collection.find_one({'custom_id': custom_id})
            if existing and existing['user_id'] != user_id:
                return False, "This Custom ID is already taken!"
                
            # Upsert identity
            identities_collection.update_one(
                {'user_id': user_id},
                {'$set': {'custom_id': custom_id, 'updated_at': datetime.now().isoformat()}},
                upsert=True
            )
                
            return True, f"Custom ID set to {custom_id}!"
        except Exception as e:
            logger.error(f"❌ Error setting custom ID: {e}")
            return False, "System error."

    def set_bio(self, user_id: int, bio: str) -> Tuple[bool, str]:
        """Set user bio"""
        if len(bio) > 200:
            return False, "Bio must be under 200 characters!"
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO identities (user_id, bio, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                    bio = excluded.bio,
                    updated_at = CURRENT_TIMESTAMP
                ''', (user_id, bio))
                conn.commit()
                
            return True, "Bio updated successfully!"
        except Exception as e:
            logger.error(f"❌ Error setting bio: {e}")
            return False, "System error."

    def set_business_name(self, user_id: int, name: str) -> Tuple[bool, str]:
        """Set business/store name"""
        if len(name) > 50:
            return False, "Business name must be under 50 characters!"
            
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO identities (user_id, business_name, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                    business_name = excluded.business_name,
                    updated_at = CURRENT_TIMESTAMP
                ''', (user_id, name))
                conn.commit()
                
            return True, f"Business name set to '{name}'!"
        except Exception as e:
            logger.error(f"❌ Error setting business name: {e}")
            return False, "System error."

    def get_identity(self, user_id: int) -> Dict:
        """Get user identity details"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT custom_id, bio, business_name FROM identities WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'custom_id': row[0],
                        'bio': row[1],
                        'business_name': row[2]
                    }
            return {}
        except Exception as e:
            logger.error(f"❌ Error fetching identity: {e}")
            return {}

# Initialize identity system
identity_system = IdentitySystem()
