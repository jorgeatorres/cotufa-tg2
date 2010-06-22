About Cotufa
======================

- Source code: http://github.com/nichohel/cotufa
- Author: Jorge Torres <jorge@0xfee1dead.org>


Cotufa allows you to store the list of movies you have seen
including data such as cover, cast, etc. gathered from IMDB.
It also shows you some unuseful stats about your preferences.

Cotufa is licensed under the Do What The Fuck You Want To
Public License (WTFPL).


Requirements
======================

 - Turbogears2 environment (including ToscaWidgets, SQLAlchemy)
 - IMDBPy


Installation and Setup (Standard TG2 cruft)
===========================================

Create the project database for any model classes defined::

    $ paster setup-app development.ini

Start the paste http server::

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.
