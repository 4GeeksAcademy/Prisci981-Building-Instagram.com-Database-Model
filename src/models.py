from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import enum

db = SQLAlchemy()


class MediaType(enum.Enum):
    image = "image"
    video = "video"
    reel = "reel"
    story = "story"


class User(db.Model):
    """
    User model for Instagram accounts
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    profile_picture_url = db.Column(db.String(255))
    website = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    is_private = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    posts = db.relationship('Post', back_populates='user',
                            lazy=True, cascade='all, delete-orphan')
    comments = db.relationship(
        'Comment', back_populates='user', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='user',
                            lazy=True, cascade='all, delete-orphan')
    stories = db.relationship(
        'Story', back_populates='user', lazy=True, cascade='all, delete-orphan')

    # Following relationships
    following = db.relationship('Follow', foreign_keys='Follow.follower_id',
                                back_populates='follower', lazy=True, cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id',
                                back_populates='followed', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "profile_picture_url": self.profile_picture_url,
            "website": self.website,
            "is_private": self.is_private,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Post(db.Model):
    """
    Post model for Instagram posts (photos, videos, reels)
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    caption = db.Column(db.Text)
    media_url = db.Column(db.String(255), nullable=False)
    media_type = db.Column(
        db.Enum(MediaType), nullable=False, default=MediaType.image)
    location = db.Column(db.String(100))
    is_archived = db.Column(db.Boolean, default=False)
    comments_disabled = db.Column(db.Boolean, default=False)
    likes_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='posts')
    comments = db.relationship(
        'Comment', back_populates='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', back_populates='post',
                            lazy=True, cascade='all, delete-orphan')
    hashtags = db.relationship(
        'PostHashtag', back_populates='post', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.id} by {self.user.username if self.user else "Unknown"}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "caption": self.caption,
            "media_url": self.media_url,
            "media_type": self.media_type.value if self.media_type else None,
            "location": self.location,
            "is_archived": self.is_archived,
            "comments_disabled": self.comments_disabled,
            "likes_hidden": self.likes_hidden,
            "likes_count": len(self.likes) if self.likes else 0,
            "comments_count": len(self.comments) if self.comments else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Comment(db.Model):
    """
    Comment model for post comments
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey(
        'comments.id'))  # For reply functionality
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')
    parent_comment = db.relationship(
        'Comment', remote_side=[id], backref='replies')
    likes = db.relationship(
        'CommentLike', back_populates='comment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Comment {self.id} by {self.user.username if self.user else "Unknown"}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "post_id": self.post_id,
            "parent_comment_id": self.parent_comment_id,
            "content": self.content,
            "is_pinned": self.is_pinned,
            "likes_count": len(self.likes) if self.likes else 0,
            "replies_count": len(self.replies) if hasattr(self, 'replies') and self.replies else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Like(db.Model):
    """
    Like model for post likes
    """
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'post_id', name='unique_user_post_like'),)

    # Relationships
    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')

    def __repr__(self):
        return f'<Like {self.id}: User {self.user_id} liked Post {self.post_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CommentLike(db.Model):
    """
    Like model for comment likes
    """
    __tablename__ = 'comment_likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey(
        'comments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'comment_id', name='unique_user_comment_like'),)

    # Relationships
    user = db.relationship('User')
    comment = db.relationship('Comment', back_populates='likes')

    def __repr__(self):
        return f'<CommentLike {self.id}: User {self.user_id} liked Comment {self.comment_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "comment_id": self.comment_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Follow(db.Model):
    """
    Follow model for user following relationships
    """
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)  # User who follows
    followed_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)  # User being followed
    # For private account follow requests
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate follows
    __table_args__ = (db.UniqueConstraint(
        'follower_id', 'followed_id', name='unique_follower_followed'),)

    # Relationships
    follower = db.relationship('User', foreign_keys=[
                               follower_id], back_populates='following')
    followed = db.relationship('User', foreign_keys=[
                               followed_id], back_populates='followers')

    def __repr__(self):
        return f'<Follow {self.follower_id} follows {self.followed_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "follower_username": self.follower.username if self.follower else None,
            "followed_id": self.followed_id,
            "followed_username": self.followed.username if self.followed else None,
            "is_approved": self.is_approved,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Story(db.Model):
    """
    Story model for Instagram stories (24-hour posts)
    """
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_url = db.Column(db.String(255), nullable=False)
    media_type = db.Column(
        db.Enum(MediaType), nullable=False, default=MediaType.image)
    caption = db.Column(db.Text)
    is_archived = db.Column(db.Boolean, default=False)  # Highlight stories
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow(
    ) + timedelta(hours=24))  # 24 hours from creation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='stories')
    views = db.relationship(
        'StoryView', back_populates='story', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Story {self.id} by {self.user.username if self.user else "Unknown"}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "media_url": self.media_url,
            "media_type": self.media_type.value if self.media_type else None,
            "caption": self.caption,
            "is_archived": self.is_archived,
            "views_count": len(self.views) if self.views else 0,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class StoryView(db.Model):
    """
    StoryView model to track who viewed stories
    """
    __tablename__ = 'story_views'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey(
        'stories.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate views from same user
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'story_id', name='unique_user_story_view'),)

    # Relationships
    user = db.relationship('User')
    story = db.relationship('Story', back_populates='views')

    def __repr__(self):
        return f'<StoryView {self.id}: User {self.user_id} viewed Story {self.story_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "story_id": self.story_id,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None
        }


class Hashtag(db.Model):
    """
    Hashtag model for post hashtags
    """
    __tablename__ = 'hashtags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True,
                     nullable=False)  # Without the # symbol
    post_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    posts = db.relationship('PostHashtag', back_populates='hashtag', lazy=True)

    def __repr__(self):
        return f'<Hashtag #{self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "post_count": self.post_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PostHashtag(db.Model):
    """
    Junction table for Post-Hashtag many-to-many relationship
    """
    __tablename__ = 'post_hashtags'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey(
        'hashtags.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate hashtag-post relationships
    __table_args__ = (db.UniqueConstraint(
        'post_id', 'hashtag_id', name='unique_post_hashtag'),)

    # Relationships
    post = db.relationship('Post', back_populates='hashtags')
    hashtag = db.relationship('Hashtag', back_populates='posts')

    def __repr__(self):
        return f'<PostHashtag Post:{self.post_id} Hashtag:{self.hashtag_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "hashtag_id": self.hashtag_id,
            "hashtag_name": self.hashtag.name if self.hashtag else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }