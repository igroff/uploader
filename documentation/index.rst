.. token-service documentation master file, created by
   sphinx-quickstart on Tue Oct 30 15:16:17 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to hipflask's documentation!
=========================================

Hipflask is a set of functionality built around the Python Flask (WSGI) Microframework.  The idea is that it provides all sorts of common functionality so that someone developing on top of this can focus on just the programming necessary to solve the problem at hand, instead of time trying to get servers to start, stop, etc.



Definitions
===========

* Local Event - Events that are emitted into the log file structure of the running application, further detail is in the 'Events' section.

* Configuration - Configuration of the system is accomplished by setting environment variables and is outlined in the 'Configuration' section.

* Handler - Corresponds to a 'view function' in flask.  Within hipflask specifically a handler is a function mapped to a particular route.  As a (theoretical) convenience, hipflask provides a directory in which it will look for handlers that you may provide.  Hipflask looks for handler files in the handlers/ directory and will load anything but __init__.py matching \*.py.  In practice multiple handlers will occur in a single file, and they will look something like this:

::

  @app.route("/respond_to")
  def say_hi():
    return "hi"

* Another thing - something


Controlling Hipflask
====================

The primary interface for interaction with Hipflask is make.  As such all of the following are invoked as 'make <cmd>' where <cmd> is one of the below:

* debug - Starts the application using the standard Flask debug server.
* build - Builds Hipflask as needed, primarily this is the setup of a virtual environment and the installation of the proper python packages.
* start - Starts the application in 'production' mode.  This simply starts the app using gunicorn.
* test  - Runs the unit tests (see testing for more information).
* clean - Cleans up var/ and tmp/ directories as well as deleting the virtual environment.  You'll want to ( make clean ; make test ) to make sure everything has the highest likelihood of working.
* docs  - Uses sphinx to build the documentation for hipflask.  See 'Documenting Hipflask'

In the non development case of using hipflask it may be the case that mutliple instances of Hipflask are needed to run concurrently, to assist in this and avoid redundant environment setup a script 'start' is provided.  The sole purpose is to synchronize the build stage so multiple instances don't try to setup the (virtual) environment simultaneously.


Documenting Hipflask
====================



Testing
=======

Talk about unit tests


Extending Hipflask
==================

Talk about package installation and the freeze file


Configuration
=============

Configuration of the system is managed by setting environment variables.
The following list specifies the behavior of the common settings.

SQLITE_VFS = Used to set the VFS used during SQLite connections.  Can be any of the valid VFS choices unix-dotfile (default for portability), unix-excl, unix-none, unix-namedsem or the SQLite default 'unix' 

PORT = Sets the port on which the WSGI server will listen, affects both standard and debug environments. (make start, make debug)

LOG_LEVEL = Valid values are those from the python logging module (DEBUG, INFO, WARNING, etc.), note that these map to the constants in the logging module so case matters.

LOCAL_EVENT_SOURCES = A comma delimited list of sources for which Local Events will be emitted, see Events section for more info.


Events
======

The system support the raising of events providing data about various actions that have taken place.  Currently the only events emitted are 'Local Events'.  Local Events are events that are emitted into the output stream of the running application.  In a normal production environment these events will end up in a log file and are available for consumption from there.



Handler Decorators
===============
It's possible to change the way output from a handler is interpereted.  This is managed by applying decorators to a handler.  Available decorators are:

@cache_my_response 
    Is used to ensure that responses from the decorated function will be cached by the application.  The default application cache is filesystem backed.  The location of the cached data stored is controled by the environment variable CACHE_ROOT.  In the case of multiple servers wanting to share cached data, they can be configured to share the filesystem location referenced by CACHE_ROOT.
     
    When serving a cached response an Expires header will be added to the response indicating the expiration time of the cached item. 
    
    <vary_by=None> - an optional list of request parameters the values of which  will
    control the variance in the cache.  This is to say the values of these parameters
    will be used to define the cache key used to cache the response.
    
    <expiration_seconds=900> - The number of seconds for which the cached response
    will be considered valid.  This doesn't affect any cache headers in the response
    this is purely for controling the lifetime of the cached value within the
    application.

@make_my_response_json
    Causes the response from the view to be formatted as json.  The Content-Type in the response will be set to application/json, and support for a callback parameter in the request will be made available (JSONP).

    In the case that the inbound request has a callback parameter, any status code of 404 will be converted to a 200.  This is to ease handling of not found conditions by the browser, which in the case of encountering a 404 in a 'JSONP request' can lead to undesireable behavior.  The rest of the response will be unchanged.

Endpoints
=========


.. autoflask:: pyserver.core:app
    :include-empty-docstring:
    :undoc-endpoints: im_here_for_testing
    :undoc-static:


