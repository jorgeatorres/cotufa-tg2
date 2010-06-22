# coding: utf-8
import json

from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import url
from tw.forms import TableForm, TextField
from tw.forms.validators import UnicodeString

class SearchMovieForm(TableForm):
    fields = [TextField(u'movie_title',
                        label_text=_(u'Movie title'),
                        validator=UnicodeString(not_empty=True, strip=True))]
    submit_text = _(u'Search')


search_movie_form = SearchMovieForm('search_movie_form',
                                    action=url('/search_do'))
