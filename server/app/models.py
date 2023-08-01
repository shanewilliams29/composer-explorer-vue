from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from app.search import add_to_index, remove_from_index, query_index

performer_albums = db.Table('performer_albums',
                            db.Column('performer_id', db.String(48), db.ForeignKey('performers.id')),
                            db.Column('album_id', db.String(46), db.ForeignKey('work_albums.id', ondelete='CASCADE'))
                            )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    display_name = db.Column(db.String(128), unique=True)
    img = db.Column(db.String(1024))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    page_viewing = db.Column(db.String(1024))
    admin = db.Column(db.Boolean, default=False)
    patreon = db.Column(db.Boolean, default=False)
    country = db.Column(db.String(64))
    product = db.Column(db.String(64))
    forum_posts = db.relationship("ForumPost", backref="user", lazy='dynamic')
    forum_comments = db.relationship("ForumComment", backref="user", lazy='dynamic')
    liked = db.relationship('AlbumLike', foreign_keys='AlbumLike.user_id', backref='user', lazy='dynamic')
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


# class SearchableMixin(object):
#     @classmethod
#     def elasticsearch(cls, expression, page, per_page, sort_column=None):
#         ids, scores, total = query_index(cls.__tablename__, expression, page, per_page)
#         if total == 0:
#             return cls.query.filter_by(id=None), 0
#         when = []
#         for i, _id in enumerate(ids):
#             when.append((cls.id == _id, scores[i]))
#             print(_id, scores[i])
#         # return cls.query.filter(cls.id.in_(ids)).order_by(
#         #     db.case(when, value=cls.id)), total
#         query = cls.query.filter(cls.id.in_(ids))
        
#         # If a sort_column is provided, apply the sorting
#         if sort_column:
#             sort_column_attr = getattr(cls, sort_column)
#             query = query.order_by(db.case(when, value=cls.id), desc(sort_column_attr))
#         else:
#             query = query.order_by(db.case(when, value=cls.id))

#         return query, total

class SearchableMixin(object):
    @classmethod
    def elasticsearch(cls, expression, page, per_page, sort_column=None):
        ids, scores, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0

        # Retrieve the results without any specific ordering
        if sort_column == 'score':  # for albums table, do not include compilation albums
            query = cls.query.filter(cls.id.in_(ids), cls.album_type != 'compilation').all()
        elif sort_column == 'album_count':  # for works table, do not include works without albums
            query = cls.query.filter(cls.id.in_(ids), cls.album_count > 0).all()
        else:
            query = cls.query.filter(cls.id.in_(ids)).all()

        # Create a dictionary to map ids to their corresponding scores
        score_mapping = {id: score for id, score in zip(ids, scores)}

        # Sort the results by the scores and the sort_column if provided
        if sort_column:
            sorted_results = sorted(query, key=lambda x: (score_mapping.get(x.id, 0), getattr(x, sort_column)), reverse=True)
        else:
            sorted_results = sorted(query, key=lambda x: score_mapping.get(x.id, 0), reverse=True)  # Added default value 0

        return sorted_results, total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


@dataclass
class ComposerList(SearchableMixin, db.Model):
    __searchable__ = ['name_norm', 'name_full', 'name_short']
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
    name_short = db.Column(db.String(255), unique=True, index=True)
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
    works = db.relationship("WorkList", lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name_full)


@dataclass
class WorkList(SearchableMixin, db.Model):
    __searchable__ = ['composer', 'genre', 'cat', 'title', 'nickname', 'search']
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
    composer = db.Column(db.String(48), db.ForeignKey('composer_list.name_short'))
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
    last_refresh = db.Column(db.DateTime)
    albums = db.relationship("WorkAlbums", back_populates="work", lazy='dynamic')

    def __repr__(self):
        return '<{}|{}>'.format(self.composer, self.title)


@dataclass
class Performers(SearchableMixin, db.Model):
    __searchable__ = ['name']
    id: str
    name: str
    img: str
    description: str
    google_img: str
    wiki_link: str

    id = db.Column(db.String(48), primary_key=True)
    name = db.Column(db.String(256), index=True)
    img = db.Column(db.String(128))
    description = db.Column(db.String(256))
    google_img = db.Column(db.String(128))
    wiki_link = db.Column(db.String(256))
    hidden = db.Column(db.Boolean, default=False)
    albums = db.relationship("WorkAlbums", secondary=performer_albums, back_populates="performers", lazy='dynamic')

    def __repr__(self):
        return '<{}>'.format(self.name)

    def add_album(self, album):
        # if album not in self.albums:
        self.albums.append(album)


@dataclass
class WorkAlbums(SearchableMixin, db.Model):
    __searchable__ = ['composer', 'title', 'artists', 'label']
    id: str
    album_id: str
    artists: str
    img: str
    title: str

    id = db.Column(db.String(46), primary_key=True)
    workid = db.Column(db.String(24), db.ForeignKey('work_list.id'))
    album_id = db.Column(db.String(22), index=True)
    composer = db.Column(db.String(255), db.ForeignKey('composer_list.name_short'))
    score = db.Column(db.Float, index=True)
    artists = db.Column(db.Text)
    data = db.Column(MEDIUMTEXT)
    hidden = db.Column(db.Boolean, default=False)
    img = db.Column(db.Text)
    label = db.Column(db.String(1024))
    title = db.Column(db.String(2048))
    track_count = db.Column(db.Integer)
    work_track_count = db.Column(db.Integer)
    album_type = db.Column(db.String(255), index=True)
    duration = db.Column(db.Integer)
    likes = db.relationship('AlbumLike', backref='album', lazy='dynamic', passive_deletes=True)
    work = db.relationship("WorkList", back_populates="albums")
    performers = db.relationship("Performers", secondary=performer_albums, back_populates="albums", lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return '<{}>'.format(self.title)


class AlbumLike(db.Model):
    __tablename__ = 'album_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    album_id = db.Column(db.String(46), db.ForeignKey('work_albums.id', ondelete='CASCADE'))


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
