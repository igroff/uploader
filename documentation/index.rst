.. token-service documentation master file, created by
   sphinx-quickstart on Tue Oct 30 15:16:17 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to hipflask's documentation!
=========================================

Configuration
=============

SQLITE_VFS = Used to set the VFS used during SQLite connections.  Can be any of the valid VFS choices unix-dotfile (default for portability), unix-excl, unix-none, unix-namedsem or the SQLite default 'unix' 

Endpoints
=========


.. autoflask:: pyserver.core:app
    :include-empty-docstring:
    :undoc-endpoints: im_here_for_testing
    :undoc-static:


