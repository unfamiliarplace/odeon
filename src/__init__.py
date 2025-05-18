#===============================================================================
# PyDev wants there to be an __init__.py to consider a folder a package...
# Even though Python wants there to be a __main__.py.
# So here's it is!
#===============================================================================

exec(open('__main__.py').read(), globals())
