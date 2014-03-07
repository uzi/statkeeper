# StatKeeper
============

Overview
--------

At [Rdio](http://rdio.com/), we have a ping pong table and some folks who like to talk a big game.  This was hacked up in order to keep a record of the fierce office competition we have going.  The code can support more than the one game and even rudimentary team sports like doubles ping pong.

An example can be seen at http://oidr.net/.

Instructions
------------

It's just a Django app.  Recommended for running it are pip, virtualenv and [npm](https://www.npmjs.org/).  Set up your python virtual environment and then do a

```pip install -r requirements.txt```

to install the required python libraries, and an

```npm install```

to install helpers for the css and js on the frontend.  The rest of it is the usual Django stuff, though site-specific settings can be managed via a localsettings.py file in the statkeeper directory.  In production, I use something like:

```python
SECRET_KEY = 'YOUR SECRET KEY HERE'
DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['example.com', 'example.com.']

# Note that this is disabled currently because of js bugs.
PIPELINE_ENABLED = False

# Your DB info here
#DATABASES = { ... }
```

Then static files can be deployed with a

```./manage.py collectstatic -c```

and should be served separately from the rest of the app.  A few lines in urls.py can be uncommented to allow production style deployment in testing.

Credits
-------

Written by Joshua "uzi" Uziel in a few nights for fun.  Later extended and polished up as a Hackday project by Joshua "uzi" Uziel, Joe Gasiorek, Nod Raber and Mike Towber.
