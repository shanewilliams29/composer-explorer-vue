from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from sqlalchemy.dialects.mysql import MEDIUMTEXT, LONGTEXT

favorites = db.Table('favorites',
                     db.Column('composer_id', db.Integer, db.ForeignKey('composer_list.id')),
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                     )

performer_albums = db.Table('performer_albums',
                            db.Column('performer_id', db.String(48), db.ForeignKey('performers.id')),
                            db.Column('album_id', db.String(46), db.ForeignKey('work_albums.id'))
                            )

visits = db.Table('visits',
                  db.Column('work_id', db.String(24), db.ForeignKey('work_list.id')),
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                  )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    display_name = db.Column(db.String(128), unique=True)
    img = db.Column(db.String(1024))
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    page_viewing = db.Column(db.String(1024))
    admin = db.Column(db.Boolean, default=False)
    patreon = db.Column(db.Boolean, default=False)
    country = db.Column(db.String(64))
    product = db.Column(db.String(64))
    forum_posts = db.relationship("ForumPost", backref="user", lazy='dynamic')
    forum_comments = db.relationship("ForumComment", backref="user", lazy='dynamic')
    favorited = db.relationship("ComposerList", secondary=favorites, back_populates="favorites", lazy='dynamic')
    visited = db.relationship("WorkList", secondary=visits, backref='user', lazy='dynamic')
    liked = db.relationship('AlbumLike', foreign_keys='AlbumLike.user_id', backref='user', lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    refresh_token = db.Column(db.String(1024))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        if self.img:
            return self.img
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def favorite(self, composer):
        if not self.is_favorite(composer):
            self.favorited.append(composer)

    def unfavorite(self, composer):
        if self.is_favorite(composer):
            self.favorited.remove(composer)

    def is_favorite(self, composer):
        return self.favorited.filter(
            favorites.c.composer_id == composer.id).count() > 0

    def favorited_composers(self):
        favorited = ComposerList.query.join(favorites).filter(favorites.c.user_id == self.id)
        return favorited

    def visit(self, work):
        if not self.has_visited(work):
            self.visited.append(work)

    def unvisit(self, work):
        if self.has_visited(work):
            self.visited.remove(work)

    def has_visited(self, work):
        return self.visited.filter(
            visits.c.work_id == work.id).count() > 0

    def all_visits(self):
        return self.visited.filter(visits.c.user_id == self.id).all()

    def like_album(self, album):
        if not self.has_liked_album(album):
            like = AlbumLike(user_id=self.id, album_id=album.id)
            db.session.add(like)

    def unlike_album(self, album):
        if self.has_liked_album(album):
            AlbumLike.query.filter_by(
                user_id=self.id,
                album_id=album.id).delete()

    def has_liked_album(self, album):
        return bool(AlbumLike.query.filter(
            AlbumLike.user_id == self.id,
            AlbumLike.album_id == album.id).count())

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def new_posts(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        post_count = ForumPost.query.filter(
            ForumPost.postdate > last_read_time, ForumPost.subforum_id != 10).count()
        comment_count = db.session.query(ForumComment).join(ForumPost).filter(
            ForumComment.postdate > last_read_time, ForumPost.subforum_id != 10).count()
        return post_count + comment_count

    def view_post(self, post):
        view = Views.query.filter(Views.user_id == self.id, Views.post_id == post.id).first()
        if view:
            view.timestamp = datetime.utcnow()
        else:
            view = Views(user_id=self.id, post_id=post.id)
            db.session.add(view)

    def already_viewed(self, post):
        view = Views.query.filter(Views.user_id == self.id, Views.post_id == post.id).first()
        if not view:
            return False
        if not post.last_comment_date:
            return False
        if view.timestamp < post.last_comment_date:
            return False
        else:
            return True


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


#  used in old site
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    workid = db.Column(db.String(24), db.ForeignKey('work_list.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)


@dataclass
class ComposerList(db.Model):
    id: int
    source: str
    name_short: str
    name_full: str
    name_norm: str
    born: int
    died: int
    linkname: str
    nationality: str
    region: str
    description: str
    image: str
    imgfull: str
    pageurl: str
    wordcount: int
    introduction: str
    rank: float
    spotify: str
    clicks: int
    catalogued: bool
    tier: int
    female: bool
    general: bool
    view: int
    preview_music: str

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(255))
    name_short = db.Column(db.String(255), unique=True)
    name_full = db.Column(db.String(255))
    name_norm = db.Column(db.String(255), index=True)
    born = db.Column(db.Integer, index=True)
    died = db.Column(db.Integer, index=True)
    linkname = db.Column(db.String(255))
    nationality = db.Column(db.String(255))
    region = db.Column(db.String(255), index=True)
    description = db.Column(db.String(255))
    image = db.Column(db.String(255))
    imgfull = db.Column(db.String(255))
    pageurl = db.Column(db.String(255))
    wordcount = db.Column(db.Integer)
    introduction = db.Column(db.Text)
    rank = db.Column(db.Float)
    spotify = db.Column(db.String(255))
    clicks = db.Column(db.Integer)
    catalogued = db.Column(db.Boolean)
    tier = db.Column(db.Integer)
    female = db.Column(db.Boolean)
    general = db.Column(db.Boolean)
    view = db.Column(db.Integer)
    preview_music = db.Column(db.String(255))
    favorites = db.relationship("User", secondary=favorites, back_populates="favorited", lazy='dynamic')

    def __repr__(self):
        return '<Composer {}>'.format(self.name_full)


@dataclass
class WorkList(db.Model):
    id: int
    composer: str
    genre: str
    order: float
    cat: str
    suite: str
    recommend: str
    title: str
    nickname: str
    search: str
    date: int
    openopus: bool
    duration: int

    id = db.Column(db.String(24), primary_key=True)
    composer = db.Column(db.String(48), index=True)
    genre = db.Column(db.String(128), index=True)
    order = db.Column(db.Float, index=True)
    cat = db.Column(db.String(24), index=True)
    suite = db.Column(db.String(512))
    recommend = db.Column(db.String(24))
    title = db.Column(db.String(512))
    nickname = db.Column(db.String(512))
    search = db.Column(db.String(256))
    date = db.Column(db.Integer)
    openopus = db.Column(db.Boolean)
    album_count = db.Column(db.Integer, index=True)
    duration = db.Column(db.Integer)
    spotify_loaded = db.Column(db.Boolean)
    albums = db.relationship("WorkAlbums", back_populates="work", lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.title)


class Spotify(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    composer = db.Column(db.String(48))
    results = db.Column(MEDIUMTEXT)
    updated = db.Column(db.DateTime, default=datetime.utcnow)


# Used in old site
class ArtistAlbums(db.Model):
    id = db.Column(db.String(24), primary_key=True)
    results = db.Column(MEDIUMTEXT)
    artists = db.Column(db.Text)
    updated = db.Column(db.DateTime, default=datetime.utcnow)


# Old table of artists/performers
@dataclass
class Artists(db.Model):
    id: str
    name: str
    workid: str
    album_id: float
    composer: str
    count: int
    spotify_id: str
    spotify_img: str

    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(256), index=True)
    workid = db.Column(db.String(24), db.ForeignKey('work_list.id'))
    album_id = db.Column(db.String(46), db.ForeignKey('work_albums.id'))
    composer = db.Column(db.String(48))
    work = db.relationship("WorkList")
    count = db.Column(db.Integer)
    spotify_id = db.Column(db.String(48))
    spotify_img = db.Column(db.String(128))

    def __repr__(self):
        return '<{}>'.format(self.name)


@dataclass
class Performers(db.Model):
    id: str
    name: str
    img: str
    description: str
    # google_img: str
    # wiki_link: str
    # role: str

    id = db.Column(db.String(48), primary_key=True)
    name = db.Column(db.String(256), index=True)
    img = db.Column(db.String(128))
    description = db.Column(db.String(256))
    # google_img = db.Column(db.String(128))
    # wiki_link = db.Column(db.String(128))
    # role = db.Column(db.String(48))
    hidden = db.Column(db.Boolean, default=False)
    albums = db.relationship("WorkAlbums", secondary=performer_albums, back_populates="performers", lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

    def add_album(self, album):
        #if album not in self.albums:
        self.albums.append(album)


class WorkAlbums(db.Model):
    id = db.Column(db.String(46), primary_key=True)
    workid = db.Column(db.String(24), db.ForeignKey('work_list.id'))
    album_id = db.Column(db.String(22))
    composer = db.Column(db.String(255), db.ForeignKey('composer_list.name_short'))
    score = db.Column(db.Float)
    artists = db.Column(db.Text)
    data = db.Column(MEDIUMTEXT)
    hidden = db.Column(db.Boolean, default=False)
    filled = db.Column(db.Boolean, default=False)
    got_artists = db.Column(db.Boolean, default=False)
    spotify_data = db.Column(db.Text)
    img = db.Column(db.Text)
    label = db.Column(db.String(1024))
    title = db.Column(db.String(2048))
    track_count = db.Column(db.Integer)
    work_track_count = db.Column(db.Integer)
    album_type = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    markets = db.Column(db.Text)
    likes = db.relationship('AlbumLike', backref='album', lazy='dynamic', passive_deletes=True)
    work = db.relationship("WorkList", back_populates="albums")
    performers = db.relationship("Performers", secondary=performer_albums, back_populates="albums", lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.id)


class AlbumLike(db.Model):
    __tablename__ = 'album_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    album_id = db.Column(db.String(46), db.ForeignKey('work_albums.id', ondelete='CASCADE'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sender_visible = db.Column(db.Boolean, default=True)
    recipient_visible = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    comments = db.relationship("ForumComment", backref="post")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subforum_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    postdate = db.Column(db.DateTime)
    last_comment_date = db.Column(db.DateTime)
    last_comment_username = db.Column(db.String(64))
    last_commenter = db.Column(db.String(128))

    def __init__(self, title, content, postdate):
        self.title = title
        self.content = content
        self.postdate = postdate


class Subforum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    posts = db.relationship("ForumPost", backref="subforum")
    path = None
    hidden = db.Column(db.Boolean, default=False)

    def __init__(self, title, description):
        self.title = title
        self.description = description


class ForumComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    postdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey("forum_post.id"))

    def __init__(self, content, postdate):
        self.content = content
        self.postdate = postdate


class Views(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class ComposerCron(db.Model):
    id = db.Column(db.String(255), primary_key=True)


class ArtistList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(LONGTEXT)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)