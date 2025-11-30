"""
🗳️ POLITICS SYSTEM
Ultimate Group King Bot - Election & Voting Layer
Author: Nikhil Mehra (NikkuAi09)
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoliticsSystem:
    """Manages elections and voting"""
    
    def __init__(self):
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    def check_expired_elections(self) -> List[str]:
        """Check and end expired elections (older than 5 days)"""
        ended_elections = []
        try:
            elections_collection = self.db.get_collection('elections')
            if not elections_collection:
                return ended_elections
                
            # Find active elections older than 5 days
            cutoff_date = datetime.now() - timedelta(days=5)
            expired = elections_collection.find({
                'status': 'ACTIVE',
                'created_at': {'$lt': cutoff_date.isoformat()}
            })
            
            for election in expired:
                self.end_election(election['chat_id'])
                ended_elections.append(f"{election['title']} (Chat ID: {election['chat_id']})")
                    
        except Exception as e:
            logger.error(f"❌ Error checking expired elections: {e}")
            
        return ended_elections

    def create_election(self, chat_id: int, title: str, duration_hours: int = 120) -> Tuple[bool, str]:
        """Create a new election (Default 5 days)"""
        # First check for expired ones
        self.check_expired_elections()
        
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Check if active election exists
                cursor.execute('''
                    SELECT election_id FROM elections 
                    WHERE chat_id = ? AND status = 'ACTIVE'
                ''', (chat_id,))
                if cursor.fetchone():
                    return False, "An election is already active in this group!"
                
                election_id = str(uuid.uuid4())[:8]
                end_time = datetime.now() + timedelta(hours=duration_hours)
                
                cursor.execute('''
                    INSERT INTO elections (
                        election_id, chat_id, title, status, end_time, created_at
                    ) VALUES (?, ?, ?, 'ACTIVE', ?, CURRENT_TIMESTAMP)
                ''', (election_id, chat_id, title, end_time))
                conn.commit()
                
            return True, f"Election '{title}' started! Use /nominate to run."
        except Exception as e:
            logger.error(f"❌ Error creating election: {e}")
            return False, "System error."

    def nominate_candidate(self, chat_id: int, user_id: int, manifesto: str = "") -> Tuple[bool, str]:
        """Nominate a user for the active election"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Get active election
                cursor.execute('''
                    SELECT election_id FROM elections 
                    WHERE chat_id = ? AND status = 'ACTIVE'
                ''', (chat_id,))
                row = cursor.fetchone()
                if not row:
                    return False, "No active election in this group!"
                
                election_id = row[0]
                
                # Check if already nominated
                cursor.execute('''
                    SELECT candidate_id FROM candidates 
                    WHERE election_id = ? AND user_id = ?
                ''', (election_id, user_id))
                if cursor.fetchone():
                    return False, "You are already a candidate!"
                
                candidate_id = str(uuid.uuid4())[:8]
                cursor.execute('''
                    INSERT INTO candidates (
                        candidate_id, election_id, user_id, manifesto, votes, created_at
                    ) VALUES (?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                ''', (candidate_id, election_id, user_id, manifesto))
                conn.commit()
                
            return True, "You have been nominated! Good luck! 🗳️"
        except Exception as e:
            logger.error(f"❌ Error nominating: {e}")
            return False, "System error."

    def vote(self, chat_id: int, voter_id: int, candidate_id: str) -> Tuple[bool, str]:
        """Vote for a candidate"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Get active election
                cursor.execute('''
                    SELECT election_id FROM elections 
                    WHERE chat_id = ? AND status = 'ACTIVE'
                ''', (chat_id,))
                row = cursor.fetchone()
                if not row:
                    return False, "No active election!"
                election_id = row[0]
                
                # Check if candidate belongs to this election
                cursor.execute('''
                    SELECT user_id FROM candidates 
                    WHERE candidate_id = ? AND election_id = ?
                ''', (candidate_id, election_id))
                if not cursor.fetchone():
                    return False, "Invalid candidate!"
                
                # Check if already voted
                cursor.execute('''
                    SELECT vote_id FROM votes 
                    WHERE election_id = ? AND voter_id = ?
                ''', (election_id, voter_id))
                if cursor.fetchone():
                    return False, "You have already voted!"
                
                # Record vote
                vote_id = str(uuid.uuid4())[:8]
                cursor.execute('''
                    INSERT INTO votes (vote_id, election_id, voter_id, candidate_id, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (vote_id, election_id, voter_id, candidate_id))
                
                # Update candidate count
                cursor.execute('''
                    UPDATE candidates 
                    SET votes = votes + 1 
                    WHERE candidate_id = ?
                ''', (candidate_id,))
                
                conn.commit()
                
            return True, "Vote cast successfully! 🗳️"
        except Exception as e:
            logger.error(f"❌ Error voting: {e}")
            return False, "System error."

    def get_election_results(self, chat_id: int) -> Tuple[bool, str, List[Dict]]:
        """Get results of active or last election"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                # Get latest election
                cursor.execute('''
                    SELECT election_id, title, status FROM elections 
                    WHERE chat_id = ? 
                    ORDER BY created_at DESC LIMIT 1
                ''', (chat_id,))
                election = cursor.fetchone()
                
                if not election:
                    return False, "No elections found!", []
                
                election_id, title, status = election
                
                # Get candidates and votes
                cursor.execute('''
                    SELECT c.candidate_id, u.first_name, c.votes, c.manifesto 
                    FROM candidates c
                    JOIN users u ON c.user_id = u.user_id
                    WHERE c.election_id = ?
                    ORDER BY c.votes DESC
                ''', (election_id,))
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'candidate_id': row[0],
                        'name': row[1],
                        'votes': row[2],
                        'manifesto': row[3]
                    })
                    
                return True, f"Results for: {title} ({status})", results
        except Exception as e:
            logger.error(f"❌ Error fetching results: {e}")
            return False, "System error.", []

    def end_election(self, chat_id: int) -> Tuple[bool, str]:
        """End the active election"""
        try:
            with db.connect() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE elections 
                    SET status = 'COMPLETED', end_time = CURRENT_TIMESTAMP 
                    WHERE chat_id = ? AND status = 'ACTIVE'
                ''', (chat_id,))
                
                if cursor.rowcount == 0:
                    return False, "No active election to end!"
                
                conn.commit()
            return True, "Election ended! Use /results to see the winner."
        except Exception as e:
            logger.error(f"❌ Error ending election: {e}")
            return False, "System error."

# Initialize politics system
politics_system = PoliticsSystem()
