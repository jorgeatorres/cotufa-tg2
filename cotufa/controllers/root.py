# coding: utf-8

from imdb import IMDb
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash, override_template, response, redirect, tmpl_context, url, validate
from tg.controllers import CUSTOM_CONTENT_TYPE
from sqlalchemy.sql import select, func

from cotufa.lib.base import BaseController
from cotufa.model import DBSession, Movie, MovieRole, Person
from cotufa.controllers.error import ErrorController
from cotufa.widgets.forms import search_movie_form


__all__ = ['RootController']


class RootController(BaseController):
    
    error = ErrorController()

    @expose()
    def index(self):
        return redirect(url('/movies'))
        
    @expose('cotufa.templates.movies')
    def movies(self, format=u'list'):
        movies = DBSession.query(Movie).order_by('created_on desc')
        return {'format': format, 'movies': movies}
        
    @expose('cotufa.templates.export-html')
    def export(self):
        data = {}
        data.update(self.movies())
        data.update(self.stats())
        return data

    
    @expose('cotufa.templates.movie')
    def movie_details(self, id):
        movie = DBSession.query(Movie).filter_by(id=id).one()
        return {'movie': movie}

    @expose()
    def add(self, id):
        import urllib2
    
        movie = DBSession.query(Movie).filter_by(id=id).first()

        if movie is None:
            lw = Movie.lightweight_instance_for(IMDb(), id)
            
            # Construct Movie object
            movie = Movie(id=lw['id'], title=lw['title'], year=lw['year'])
            
            for at in lw['attributes']:
                movie.attributes.append(at)
                
            for d in lw['directors']:
                movie.people.append(MovieRole(person=Person.get_or_create(d['id'], d['name']),
                                              role_type=u'director'))
                                              
            for w in lw['writers']:
                movie.people.append(MovieRole(person=Person.get_or_create(w['id'], w['name']),
                                              role_type=u'writer'))
                                              
            for c in lw['cast']:
                movie.people.append(MovieRole(person=Person.get_or_create(c['id'], c['person']),
                                              role_type=u'cast',
                                              character=c['character']))
            
            # Fetch cover image
            if lw['cover_url'] is not None:
                cover = urllib2.urlopen(lw['cover_url'])
                movie.cover = cover.read()
                cover.close()
                
            DBSession.add(movie)

            flash(u'%s has been added to the list.' % movie.title)
            
        redirect(url('/movies'))
        
    @expose()
    def remove(self, id):
        movie = DBSession.query(Movie).filter_by(id=id).one()
        DBSession.delete(movie)
        flash(u'%s has been removed from the list.' % movie.title)
        redirect(url('/movies'))
    
    @expose('cotufa.templates.movie')
    def summary(self, id):
        movie = DBSession.query(Movie).filter_by(id=id).first()
        
        if movie is None:
            override_template(self.summary, 'genshi:cotufa.templates.movie-imdb')
            # emulate 'Movie' object with basic info
            movie = Movie.lightweight_instance_for(IMDb(), id)

        return {'movie': movie}

    @expose('cotufa.templates.search')
    def search(self, **kw):
        tmpl_context.search_form = search_movie_form
        return {}
        
    @expose('cotufa.templates.search')
    @validate(search_movie_form, error_handler=search)
    def search_do(self, **kw):
        tmpl_context.search_form = search_movie_form
        
        ih = IMDb()
        results = ih.search_movie(kw['movie_title'])
    
        return {'search_term': kw['movie_title'],
                'results': results}
        
    @expose('cotufa.templates.stats')
    def stats(self):
        query_directors = select(['persons.id', func.count('roles.person_id').label('count')],
                       from_obj=['persons', 'roles'],
                       whereclause="roles.person_id = persons.id AND roles.role_type = 'director'",
                       group_by=['persons.id'], order_by='count desc', limit=10)
        query_actors = select(['persons.id', func.count('roles.person_id').label('count')],
                       from_obj=['persons', 'roles'],
                       whereclause="roles.person_id = persons.id AND roles.role_type = 'cast'",
                       group_by=['persons.id'], order_by='count desc', limit=10)                       
        
        top_directors = DBSession.query(Person, 'count').from_statement(query_directors).all()
        top_actors = DBSession.query(Person, 'count').from_statement(query_actors).all()        
    
        ia = IMDb()

        top250_ids = [x.movieID for x in ia.get_top250_movies()]
        bottom100_ids = [x.movieID for x in ia.get_bottom100_movies()]
        
        top250_count = DBSession.query(Movie).filter(Movie.id.in_(top250_ids)).count()
        bottom100_count = DBSession.query(Movie).filter(Movie.id.in_(bottom100_ids)).count()
        total_count = DBSession.query(Movie).count()
        
        total_runtime = 1
        
        return {'top250_count': top250_count,
                'bottom100_count': bottom100_count,
                'total_count': total_count,
                'total_runtime' : total_runtime,
                'top_directors': top_directors,
                'top_actors': top_actors}
        
    @expose(content_type=CUSTOM_CONTENT_TYPE)
    def movie_cover(self, id):
        movie = DBSession.query(Movie).filter_by(id=id).one()

        if movie.cover is not None:
            response.content_type = 'image/png'
            response.headers.add('Content-Disposition:', 'inline; filename=%s-cover.jpg' % movie.id)

        return movie.cover            

