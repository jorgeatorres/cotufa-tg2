# coding: utf-8
import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import backref, relation, synonym
from sqlalchemy.types import Binary, DateTime, Integer, Unicode, UnicodeText, String

from cotufa.model import DBSession, DeclarativeBase


class Movie(DeclarativeBase):
    __tablename__ = 'movies'

    id = Column(String(255), primary_key=True)
    title = Column(Unicode(255), nullable=False)
    year = Column(Integer, nullable=False)
    cover = Column(Binary, nullable=True, default=None)

    created_on = Column(DateTime, default=datetime.datetime.now, nullable=False)

    @property
    def directors(self):
        return [x.person for x in self.people if x.role_type == 'director']

    @property
    def writers(self):
        return [x.person for x in self.people if x.role_type == 'writer']

    @property
    def cast(self):
        return [x for x in self.people if x.role_type == 'cast']

    def __repr__(self):
        return '<%s: %s (%s)>' % (self.id, self.title, self.year)

    @classmethod
    def lightweight_instance_for(cls, imdb, imdb_id):
        imovie = imdb.get_movie(imdb_id)
        imdb.update(imovie, info=['taglines'])
        
        res = {}
        res['id'] = imdb_id
        res['cover_url'] = imovie.get('cover url', None)
        res['imdb_url'] = 'http://www.imdb.com/title/tt%s' % imdb_id
        res['title'] = imovie['title']
        res['year'] = None if imovie['year'] == '????' else imovie['year']
        res['directors'] = [{'id': x.personID, 'name': x['name']} for x in imovie.get('director')]
        
        writers_ = {}
        for w in imovie.get('writer'):
            if w.personID not in writers_:
                writers_[w.personID] = w
        
        res['writers'] = [{'id': x.personID, 'name': x['name']} for x in writers_.values()]
        
        cast = []
        for c in imovie.get('cast'):
            chars = c.currentRole if isinstance(c.currentRole, list) else [c.currentRole]
            
            for ch in chars:
                cast.append({'person': c['name'], 'id': c.personID,
                             'character': ch.get('name')})
        res['cast'] = cast
        res['attributes'] = []
        
        if imovie.has_key('taglines'):
            for tl in imovie.get('taglines'):
                res['attributes'].append(MovieAttribute(key='tagline', value=tl))

        if imovie.has_key('plot'):
            plots = imovie.get('plot')

            if plots:
                res['attributes'].append(MovieAttribute(key='plot', value=plots[0]))        
        
        return res

    @property
    def imdb_url(self):
        return 'http://www.imdb.com/title/tt%s' % self.id


class MovieAttribute(DeclarativeBase):
    __tablename__ = 'movies_attributes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    movie_id = Column(String(255), ForeignKey(Movie.id), nullable=False)
    key = Column(Unicode(255), nullable=False)
    value = Column(UnicodeText, nullable=False, default=None)

    movie = relation('Movie', backref=backref('attributes', cascade='all, delete-orphan'))


class Person(DeclarativeBase):
    __tablename__ = 'persons'

    id = Column(String(255), primary_key=True)
    name = Column(Unicode(255), nullable=False)

    @classmethod
    def get_or_create(cls, id, name):
        from sqlalchemy.orm.exc import NoResultFound
    
        try:
            p = DBSession.query(cls).filter_by(id=id).one()
            return p
        except NoResultFound, e:
            p = cls(id=id, name=name)
            DBSession.add(p)
            return p
            
    @property
    def imdb_url(self):
        return 'http://www.imdb.com/name/nm%s/' % self.id


class MovieRole(DeclarativeBase):
    __tablename__ = 'roles'

    id = Column(Integer, autoincrement=True, primary_key=True)
    person_id = Column(String(255), ForeignKey(Person.id), nullable=False)
    movie_id = Column(String(255), ForeignKey(Movie.id), nullable=False)
    role_type = Column(Unicode(10), nullable=False, default=u'cast') # writer, director, cast
    character = Column(Unicode(255), nullable=True, default=None)

    movie = relation('Movie', backref=backref('people', cascade='all, delete-orphan'))
    person = relation('Person', backref=backref('roles', cascade='all, delete-orphan'))
