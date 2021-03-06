Getting started
===============

.. contents::

.. warning:: WIP (final draft done, needs rereading)

Introduction
------------

Abstract
~~~~~~~~

This package can be used to simplify Django's URL pattern
definitions. It's able to generate a Django URL pattern structure from
a directed acylic graph represented using :

 - Routes (leaves in the graph), contain URL patterns
 - Routers (nodes in the graph), contain routes

Example :

.. graphviz::

   digraph intro_ex {
       size="4, 2"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "Router" -> "Route : home page"
       "Router" -> "Route : application status"

   }

A router can also contain other routers :

.. graphviz::

   digraph intro_nested {
       size="6, 3"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "Router" -> "Route : home page"
       "Router" -> "Route : application status"

       "Router" -> "Router : help"
       "Router : help" -> "Route : getting help"
       "Router : help" -> "Route : version"

   }

This allows us to define complex routing graphs using combinations of
route and router objects. The route and router objects handle :

 - URL namespaces (in routers)
 - URL regex building (with multiple parts, routers can also prefix
   the routes they contain using their own URL regex part)
 - building a Django URL pattern tree

.. warning::

   The routing graph must be **acyclic** as we parse it recursively,
   using a depth-first search. (django-crucrudile does not (yet ?)
   support infinite routing graphs)

Routes and router
~~~~~~~~~~~~~~~~~

Here, we defined a routing graph, but we never actually defined what
to point our routes to. In fact, the above structure could not be
created in django-crucrudile, because a route is an abstract object
(Python abstract class) that doesn't know what callback to use in its
generated patterns.

As the route is an abstract object, we use "implementations" of this
object (they know what callback to use in the generated patterns, they
are "concrete"). django-crucrudile provides two basic implementations
of the route class :

 - Callback route : a simple route that uses a given callback
 - View route : a route that uses a callback from a given Django view
   class.

If we take that previous example, using view routes in lieu of routes,
we get :

.. graphviz::

   digraph viewroutes {
       size="7, 3"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "Router" -> "View route : home page"
       "Router" -> "View route : application status"

       "Router" -> "Router : help"
       "Router : help" -> "View route : getting help"
       "Router : help" -> "View route : version"

   }

.. note:: The view route leaves in this example are **instances of the
          view route class**. They need a view_class to get
          instantiated. The route names (that will be used to build
          the URL regex as well as the URL name) should also be passed
          to the constructor (otherwise the route name will be built
          from the view class name, stripping of the tailing "View" if
          needed).

.. note:: The router nodes in this example are **instances of the
          router class**. They don't need anything to get
          instantantiated, but they can take a router name (used to
          build the router URL part) and a router namespace (used to
          wrap routers in Django URL namespaces).

Here is the code corresponding to that example :

.. automodule:: tests.doctests.examples.quickstart.intro

As you can see, we can pass the URL part to the help router, to prefix
the resulting URL patterns. Here are the URLs corresponding to that
example :

.. graphviz::

   digraph intro_ex_urls {
       size="4, 3"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "/" -> "/home"
       "/" -> "/status"

       "/" -> "/help/"

       "/help/" -> "/help/help"
       "/help/" -> "/help/version"

   }

The generator returned the ``patterns()`` function of the router
yields URL objects that can be used in the ``url_patterns`` attribute
of ``urls.py``.

Index URLs and redirections
---------------------------

The base route and router objects support setting an object as
"index", which means that when it is added to a router, the router set
it as its redirect target.

In the previous example, if the home route was as index, requests to
"/" would get redirected to "/home".

To achieve this, a route is added in each router that has a
rediect. This route is a view route that uses a Django generic
redirection view that points to the redirect target. If the redirect
target is itself a router, we use this router's redirect target, and
so on, until we find a route.

To mark a route or router as "index", set its ``index`` attribute to
``True``. You can also add it as index, using the ``index`` argument
of the register method : that won't alter the ``index`` attribute, but
will still add as index.

Here is what the previous example would look like, with a redirection
from "/" to "/home" and from "/help/" to "/help/help" :

.. automodule:: tests.doctests.examples.quickstart.redirections

.. graphviz::

   digraph redirs {
       size="4, 3"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "/" -> "/home"
       "/" -> "/status"

       "/" -> "/help/"

       "/help/" -> "/help/help"
       "/help/" -> "/help/version"

       subgraph redirects {
           edge[color=blue, label="redirects to"]
           "/" -> "/home"
           "/help/" -> "/help/help"
       }

   }

Using with models
-----------------

The base route and router classes can be extended using "model
mixins", that implement model-related functionality. Model mixins make
the object require a model class (set as class attribute or passed in
constructor).

For a router, this means in particular that it will use the model to
get its URL part.

For a route, this implies that it will use the model to get the the
URL name.

Route mixins can be used with view mixins. If the view with a generic
view, the model argument should also be passed (a "model view route"
is provided, that already implements this). In the following example,
we naively use the model and view mixins, and assume that the views
are not generic (that they already know which model to use).

Example :

.. automodule:: tests.doctests.examples.quickstart.models

.. graphviz::

   digraph models {
       size="6, 4"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "Router" -> "View route : home page"
       "Router" -> "Model router : books"

       "Model router : books" -> "Model view route : list"
       "Model router : books" -> "Model view route : detail"

       subgraph models {
           node[color="blue"]
           "Book model"
       }
       subgraph models_rels {
           edge[dir="back", color="blue", label="uses"]
           "Model router : books" -> "Book model"
           "Model view route : list" -> "Book model"
           "Model view route : detail" -> "Book model"
       }

       subgraph views {
           node[color="green"]
           "List view"
           "Detail view"
       }
       subgraph views_rels {
           edge[dir="back", color="green", label="uses"]
           "Model view route : list" -> "List view"
           "Model view route : detail" -> "Detail view"
       }

   }

As you see, it is required to pass to model to the router **and** to
the route. It's not actually required to use the model route and in a
model router, and the model route actually supports this use case by
being able to prefix the URL itself (not relying on the parent router,
as it does by default).

.. note::

   It's not possible to automatically pass attributes from a router to
   its children, as the routes and routers are already instantiated
   when they get registered to the router.

   However, a similar pattern, that is very useful for defining
   "generic" routers (that can automatically create the router and
   routes for an object), can be achieved using "register mappings". A
   register mapping is a mapping of a type to a callable, that is used
   when registering objects in a router. If the object matches a type
   in the mapping, the object is passed to the callable value, and the
   return value of this callable is registered.  You could for example
   map ``Model`` to a view route class, and call the register function
   with the model class. The object that will be registered will be an
   instance of a view route, constructed using the model class.

   Please refer to `Register mappings`_ documentation for more
   information.

.. note::

   Predefined routers can also be defined : when they get
   instantiated, they automatically instantiate classes that are
   present in their "base store" (a class-level attribute), and
   register thems in their store. For example, you could create a
   predefined model router that contains model view route classes that
   use for Django generic views, and then instantiate that model
   router with a model class as argument. The result would be a model
   router that contains model view route instances, that use the model
   router model with Django generic views.

   Please refer to `Predefined routers`_ documentation
   for more information.


Arguments
---------

The base route class can be extended using an arguments mixin, that
allows to give the route an arguments specification, that will be used
in the URL regex.

.. note:: The arguments route mixin is included in the default
          concrete route classes

The arguments mixin uses an arguments parser, to create the possible
arguments regexs from the argument specification. The default
arguments parser uses a cartesian product to allow variants of an
arguments to be used, and allows arguments to be optional, meaning
that their separator (``/``) will be optional (``/?``).

It is absolutely not required to use these features, you can define
the arguments regex yourself as well : just use your argument regex as
a single item in the arguments spec, and it won't be processed.

For more information on how argument specifications are parsed, and
more examples of argument specifications, see
:class:`django_crucrudile.routes.mixins.arguments.ArgumentsMixin`.

The following example uses this argument specification :
 - a required argument, that can be either "<pk>" or "<slug>"
 - an optional argument, "<format>"

.. automodule:: tests.doctests.examples.quickstart.arguments

.. graphviz::

   digraph arguments {
       size="6, 3"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "/" -> "/home"
       "/" -> "/status/<pk>/<format>"
       "/" -> "/status/<slug>/<format>"

   }

Register mappings
-----------------

A router instance, when registering an object, checks if the object
matches any of the register mappings. If it finds a match, it calls
the mapping value using the object as argument, and registers the
resulting object in its store.

This allows to create routers on which you can register models, or
view classes, or any object for which you want to abstract the route
definition in a class.

In the following example, we give view classes as arguments to the
register functions, also passing the arguments to pass when calling
the mapping value :

.. automodule:: tests.doctests.examples.quickstart.register_mappings

.. graphviz::

   digraph arguments {
       size="6, 3"
       bgcolor="transparent"
       edge[fontsize=10]
       node[fontsize=12]

       "/" -> "/home"
       "/" -> "/status"
       "/" -> "/testmodel/list"
       "/" -> "/help/"

       "/help/" -> "/help/help"
       "/help/" -> "/help/app-version"
   }

As shown here, some register mappings are already defined in the base
router, they allow to transform view classes in view routes, model
view classes in model view routes, and model classes in a generic
model router (see `Predefined routers`_).

To provide your own register mappings, just override the corresponding
function (see :class:`django_crucrudile.routers.Router`).

Predefined routers
------------------

It is also possible for router classes to contain classes in a "base
store" (the base store is specific to each subclass). When the router
is instantiated, these classes will be instantiated and registered.

This base store uses "register functions", as the standard store : to
add a class, call the class register method. The base store supports
register mappings, as the standard store. These mappings are separate
from the standard register mappings, and usually called "class
register mappings".

.. automodule:: tests.doctests.examples.quickstart.base_store

This allows easily creating generic, reusable routers that
automatically implement specific features (as routes, or even other
routers).

This feature is used in django-crucrudile to provide a generic model
router, that requires a model and creates routes for Django generic
views. The following example shows how such a generic model router can
be created. **The implementation in django-crucrudile is actually very
similar (if not identical) to this code, and in most cases you should
be able to directly use the generic model router provided by
django-crucrudile.**

This example also shows another route : the generic model view
route. This route uses a mixin that provides automatic URL arguments
based on the generic view class. By making the transformed view
classes use this generic model view route, instead of the default
model view route, it also shows how to add a register class mapping to
the router.

   .. automodule:: tests.doctests.examples.quickstart.generic_model_router

Quick routes and routers reference
----------------------------------

These two tables show the objects used the most frequently in django-crucrudile.

.. note:: There are many other classes though, as functionality is
          splitted into specific classes and mixins. For more
          information, see the :ref:`reference`.

Routers
~~~~~~~

.. note:: These classes are stored in the ``routers`` module. For more
          information, see :mod:`django_crucrudile.routers`

+--------------------+------------------+------------------------------------+
| Router class       | Mixins           | Description                        |
+====================+==================+====================================+
| ``Router``         | None             | Base router, is a container for    |
|                    |                  | other routers and routes.          |
+--------------------+------------------+------------------------------------+
| ``ModelRouter``    | ``ModelMixin``   | Model router, passes model when    |
|                    |                  | instantiating routed entities      |
+--------------------+------------------+------------------------------------+


Routes
~~~~~~

.. note:: These classes are stored in the ``routes`` module. For more
          information, see :mod:`django_crucrudile.routes`.

+---------------------------+------------------------------+------------------------------------+
| Router class              | Mixins                       | Description                        |
+===========================+==============================+====================================+
| ``CallbackRoute``         | - ``ArgumentsMixin``         | Route that points to a             |
|                           | - ``CallbackMixin``          | given callback                     |
+---------------------------+------------------------------+------------------------------------+
| ``ViewRoute``             | - ``ArgumentsMixin``         | Route that points to a callback    |
|                           | - ``ViewMixin``              | obtained from a given view class   |
+---------------------------+------------------------------+------------------------------------+
| ``ModelViewRoute``        | - ``ArgumentsMixin``         | Route that points to a callback    |
|                           | - ``ModelMixin``             | obtained from a given view class   |
|                           | - ``ViewMixin``              | obtained, and that uses a given    |
|                           |                              | model class                        |
+---------------------------+------------------------------+------------------------------------+
| ``GenericModelViewRoute`` | - ``ArgumentsMixin``         | Same as ``ModelViewRoute``, but    |
|                           | - ``ModelMixin``             | guesses URL arguments from the     |
|                           | - ``ViewMixin``              | class, that should be a Django     |
|                           | - ``GenericViewArgsMixin``   | generic view.                      |
+---------------------------+------------------------------+------------------------------------+

More examples
-------------

Bookstore example
~~~~~~~~~~~~~~~~~

.. automodule:: tests.doctests.examples.bookstore
