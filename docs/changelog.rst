Changelog
=========

Release 1.3.0
-------------

* Performance improvments for hierarchical clustering (at the cost of memory)
* Cluster instances are now iterable.It will iterate over each element,
  resulting in a flat list of items.
* New option to specify a progress method. This method will be called on each
  iteration for hierarchical clusters. It gives users a way to present to
  progress on screen.
* The library now also has a ``__version__`` member.
