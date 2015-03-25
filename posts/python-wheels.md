.. title: Stats for Strategy Quiz 4 Review
.. date: 2014-02-27 20:00
.. slug: python-wheels
.. tags: stats for strategy, review
.. status: draft

I'm working on getting a OS X pandas wheel going. I'll document my findings here.

Links
-----


Tools
-----

-twinse (note about needing '~/.pypic'). I made mine through python setup.py register but that may be insecure?

Commands
---------

- `python setup.py bdist_wheel` : create a wheel and place it under `./dist`

Wheels with binary extensions are platform specific, but `whl` isn't (yet) able to handle/determine that(?) It can handle py2 / py3 as the naming of the `whl` file contains the python version (See http://lucumr.pocoo.org/2014/1/27/python-on-wheels/.


setup.py
--------

- install_requires = ['pypi dependency names']


Building
--------

`python setup.py sdist`  (does the python 2 vs 3 version matter here?)
`python setup.py bdist_wheel` python does matter here since 2 and 3 get written to separate wheel zips.

Uploading to PyPI
-----------------
