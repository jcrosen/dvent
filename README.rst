Dvent
~~~~~
.. image:: https://img.shields.io/pypi/v/dvent.svg
    :target: https://pypi.python.org/pypi/dvent
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/dvent.svg
    :target: https://pypi.python.org/pypi/dvent/
    :alt: License

**Dvent** is a minimal set of simple, immutable, and functional models and tools
intended to support `Domain Driven Design`_ (DDD) and function as the
source-of-truth data model in a CQRS_ / `Event sourcing`_ architecture pattern.

Installation
------------

  ::

    pip install dvent

Dvent is
--------
A library
  A set of tools from which to build rich solutions, not a solution which you
  may easily apply to an existing problem.  It aims to guide your development
  of models that are robust, simple, scalable, easy to reason about, and easy
  to test.  While opinionated about the manner in which you model event
  orchestration it is still up to you to implement that model.

Minimal
  Only include what is necessary and eschew that which is not;
  allow for easy expansion and composition

Simple
  Aim for simplicity over ease of use; this generally manifests in very
  explicit code with consistent naming, loose-coupling, composition, and no "magic"

Immutable
  With help from the *excellent* pyrsistent_ library all data structures and
  patterns follow and reinforce immutable best-practices; so all state
  transitions require reassignment and all entities (Events, Commands,
  Aggregates) are hashable.

Functional
  Prefer functional patterns to classic OOP while retaining a style that is
  approachable for developers familiar with more classic Python idioms.

Fully Specified and Tested
  Dvent is developed with DDD itself and features living documentation in the
  form of Gherkin features.  Long-term plans include implementation of multiple
  languages against the same specification.

Beta Software
  While Dvent is currently in use in an enterprise-level setting, it is still
  provided as Beta software until further scaling and consistency guarantees are
  tested.

Dvent is not
------------
A framework
  Dvent implements no "real-world" or practical data persistence and because it
  knows nothing about your problem domain it does not attempt to provide a
  solution.  Instead it aims to guide your development of models that are robust,
  simple, scalable, easy to reason about, and easy to test.  For something more
  fully-featured and "out-of-the-box" take a look at the excellently documented
  eventsourcing_ project which implements many of the same (and more) patterns.

Usage
-----
**Coming Soon - for now check out the sample notebook(s)!**

Exploring
---------
Dvent includes integration with the Jupyter_ project via a docker image. To use the notebook(s) you'll need docker version :code:`17.09.0+` and can simply run

  ::

    DVENT_JUPYTER_TOKEN=<password-or-token-value> docker-compose up -d dvent-notebook

*Note: this will download and build the images which may require a good internet connection*

Then in your browser visit `your personal notebook <http://localhost:8288/>`_, enter your
password/token from above, browse to the "notebooks" folder, and open any you like.

Testing
-------
All tests are currently done via behave_ and gherkin feature files.  To run the test
suite you can use docker via :code:`docker-compose run --rm dvent-test`

Why make "Dvent"?
-----------------
I was leading a team at Discogs_ building a new "greenfield" project which needed a basic
set of event-sourcing models which were immutable, unopinionated about implementation
details, and enabled basic functional patterns.  I couldn't find anything that quite
fit the need, so I made one over an intense weekend and we've been using it without
any major modifications for over 15 months as of release :code:`0.1.0` (May 2018).

It's very plausible that without Discogs_ I would never have written Dvent and even so not
considered it as viable enterprise-level software.  I consider it the birthplace and indirect
sponsor of the project.

Why the name "Dvent"?
---------------------
An *extreme* portmanteau of:

- **Domain Driven Design**
- Discogs_
- **Event**

Obligatory `naming things`_ is hard reference ;)

Special Thanks
--------------
- Discogs_ and my team members (you know who you are)!
- The excellent pyrsistent_ library which makes working with data structures in
  Python almost as joyful as in Clojure
- `Greg Young`_ for his many helpful talks, posts, etc. which inform much of this
  library's patterns
- `Rich Hickey`_ and the broader Clojure_ community for the inspiration in
  building practical, immutable, functional solutions

.. _Domain Driven Design: https://en.wikipedia.org/wiki/Domain-driven_design
.. _CQRS: https://en.wikipedia.org/wiki/Command%E2%80%93query_separation#Command_query_responsibility_segregation
.. _Event sourcing: https://docs.microsoft.com/en-us/azure/architecture/patterns/event-sourcing
.. _Discogs: https://www.discogs.com
.. _pyrsistent: https://github.com/tobgu/pyrsistent
.. _eventsourcing: https://github.com/johnbywater/eventsourcing
.. _naming things: https://martinfowler.com/bliki/TwoHardThings.html
.. _Greg Young: https://twitter.com/gregyoung
.. _Rich Hickey: https://twitter.com/richhickey
.. _Clojure: https://clojure.org
.. _Jupyter: https://jupyter.org/index.html
.. _behave: https://github.com/behave/behave
