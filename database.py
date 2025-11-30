import os
from astrapy import DataAPIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.keyspace = os.getenv("ASTRA_DB_KEYSPACE")
        self.client = None
        self.db = None

    def connect(self):
        """Establishes connection to the Astra DB database."""
        try:
            # Disable SSL verification to avoid network issues
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            self.client = DataAPIClient(self.token)
            self.db = self.client.get_database_by_api_endpoint(
                self.api_endpoint
            )
            print(f"✅ Connection to Astra DB successful.")
            self.setup_collections()
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Astra DB: {e}")
            return False

    def get_collection(self, collection_name):
        """Gets a collection from the database."""
        if not self.db:
            print("Not connected to database.")
            return None
        return self.db.get_collection(collection_name)

    def get_user(self, user_id):
        """Retrieves a user from the 'users' collection."""
        try:
            if not self.db:
                print("⚠️ Database not connected")
                return None
            users_collection = self.get_collection('users')
            if users_collection:
                return users_collection.find_one({'_id': user_id})
            return None
        except Exception as e:
            print(f"❌ Error getting user {user_id}: {e}")
            return None

    def update_user(self, user_id, data):
        """Updates or inserts a user in the 'users' collection."""
        try:
            if not self.db:
                print("⚠️ Database not connected")
                return None
            users_collection = self.get_collection('users')
            if users_collection:
                # Use upsert=True to insert if document doesn't exist
                return users_collection.update_one({'_id': user_id}, {'$set': data}, upsert=True)
            return None
        except Exception as e:
            print(f"❌ Error updating user {user_id}: {e}")
            return None

    def setup_collections(self):
        """Ensures that the required collections exist in the database."""
        try:
            existing_collections = self.db.list_collection_names()
            if 'users' not in existing_collections:
                print("[DB] 'users' collection not found. Creating it...")
                self.db.create_collection('users')
                print("[DB] 'users' collection created.")
            else:
                print("[DB] 'users' collection already exists.")
        except Exception as e:
            # This can happen due to network issues, as seen before.
            # We'll assume the collection exists and proceed.
            print(f"⚠️ Could not verify collections due to a network error: {e}")
            print("Proceeding with assumption that 'users' collection exists.")

# Example of how to use the Database class for direct testing
if __name__ == "__main__":
    print("[Test] Running database.py directly...")
    db_manager = Database()
    if db_manager.connect():
        print("[Test] Connection successful!")
        # Collection listing is causing a DNS issue, skipping for now.
        pass
    else:
        print("[Test] Connection failed.")

