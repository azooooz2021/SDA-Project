import sqlite3
from datetime import datetime

DB_FILE = 'chat_history.db'

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY, title TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, conversation_id INTEGER, 
                  role TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def create_conversation(title):
    """Create a new conversation and return its ID."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO conversations (title, timestamp) VALUES (?, ?)", (title, timestamp))
    conversation_id = c.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def update_conversation_title(conversation_id, new_title):
    """Update the title of a conversation."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE conversations SET title = ? WHERE id = ?", (new_title, conversation_id))
    conn.commit()
    conn.close()

def get_conversations():
    """Retrieve a list of all conversations, sorted by timestamp (newest first)."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, timestamp FROM conversations ORDER BY timestamp DESC")
    conversations = c.fetchall()
    conn.close()
    return conversations

def get_messages(conversation_id):
    """Retrieve all messages for a specific conversation, sorted by ID."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id", 
              (conversation_id,))
    messages = c.fetchall()
    conn.close()
    return messages

def save_message(conversation_id, role, content, timestamp):
    """Save a message to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (conversation_id, role, content, timestamp))
    conn.commit()
    conn.close()