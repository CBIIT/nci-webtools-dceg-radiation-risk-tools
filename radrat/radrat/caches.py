from django.core.cache.backends.filebased import FileBasedCache

# Django's FileBasedCache calls _cull on every set, which in turn calls os.walk
# on the cache directory. This is OK on a real local disk, but sucks on network
# disk. NoCullFileBasedCache will simply not cull the cache, meaning you need
# to do it yourself at some interval.

class NoCullFileBasedCache (FileBasedCache):
    def _cull(self):
        pass
