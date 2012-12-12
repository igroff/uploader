.. token-service documentation master file, created by
   sphinx-quickstart on Tue Oct 30 15:16:17 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to hipflask's documentation!
=========================================

Configuration
=============

SQLITE_VFS = Used to set the VFS used during SQLite connections.  Can be any of the valid VFS choices unix-dotfile (default for portability), unix-excl, unix-none, unix-namedsem or the SQLite default 'unix' 

View Decorators
===============
@cache_my_response 
    Is used to ensure that responses from the decorated function will be cached by the application.  The default application cache is filesystem backed.  The location of the cached data stored is controled by the environment variable CACHE_ROOT.  In the case of multiple servers wanting to share cached data, they can be configured to share the filesystem location referenced by CACHE_ROOT.
     
    When serving a cached response an additional header, 'X-AppCachedResponseExpires' will be returned, the value of this header will be the expiration time of the cached response.  The time value contained in the header will be seconds since relative to the epoch.
    
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


