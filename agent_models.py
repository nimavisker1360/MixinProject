from new_agent_app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """User model for agent chat application"""
    __tablename__ = 'agent_users'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    language_code = db.Column(db.String(10), default='fa')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    searches = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')

class SearchHistory(db.Model):
    """Search history for tracking user queries"""
    __tablename__ = 'agent_search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('agent_users.id'), nullable=False)
    query = db.Column(db.Text, nullable=False)
    query_type = db.Column(db.String(20), default='text')  # text, voice, image
    results_count = db.Column(db.Integer, default=0)
    search_time = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float, nullable=True)  # in seconds

class Favorite(db.Model):
    """User favorite products"""
    __tablename__ = 'agent_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('agent_users.id'), nullable=False)
    product_title = db.Column(db.String(500), nullable=False)
    product_url = db.Column(db.Text, nullable=True)
    product_image = db.Column(db.Text, nullable=True)
    product_price = db.Column(db.String(100), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSession(db.Model):
    """Chat session tracking"""
    __tablename__ = 'agent_chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('agent_users.id'), nullable=False)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime, nullable=True)
    message_count = db.Column(db.Integer, default=0)
    search_count = db.Column(db.Integer, default=0)

class ProductInteraction(db.Model):
    """Track user interactions with products"""
    __tablename__ = 'agent_product_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('agent_users.id'), nullable=False)
    product_title = db.Column(db.String(500), nullable=False)
    product_url = db.Column(db.Text, nullable=True)
    interaction_type = db.Column(db.String(50), nullable=False)  # view, click, favorite, support
    interaction_time = db.Column(db.DateTime, default=datetime.utcnow)

class SystemLog(db.Model):
    """System logs for monitoring"""
    __tablename__ = 'agent_system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    log_level = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('agent_users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility functions for user management
def get_or_create_user(telegram_id: str, username: str = None, first_name: str = None, last_name: str = None):
    """Get existing user or create new one"""
    user = User.query.filter_by(telegram_id=telegram_id).first()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update last activity
        user.last_activity = datetime.utcnow()
        if username:
            user.username = username
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        db.session.commit()
    
    return user

def log_search(user_id: int, query: str, query_type: str = 'text', results_count: int = 0, response_time: float = None):
    """Log a search query"""
    search = SearchHistory(
        user_id=user_id,
        query=query,
        query_type=query_type,
        results_count=results_count,
        response_time=response_time
    )
    db.session.add(search)
    db.session.commit()

def log_interaction(user_id: int, product_title: str, interaction_type: str, product_url: str = None):
    """Log a product interaction"""
    interaction = ProductInteraction(
        user_id=user_id,
        product_title=product_title,
        product_url=product_url,
        interaction_type=interaction_type
    )
    db.session.add(interaction)
    db.session.commit()