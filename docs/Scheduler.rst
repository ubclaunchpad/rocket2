Scheduler Guide
===============

So, you want to write a module and add it to the ever-growing list of
modules that run periodically for rocket 2? Well, you have come to the
right place.

A very good example module can be found in the
``app/scheduler/modules/random_channel.py`` source file. I recommend
that you read it before starting development (don’t worry, it’s very
short).

Structure
---------

All scheduler modules are to be placed in the ``app/scheduler/modules/``
directory. As Python source files, of course. These files should house
the module class. Every class must inherit ``ModuleBase``.

Since you inherit the ``ModuleBase`` class, you must implement the
following methods:

**get_job_args**: A dictionary of job configuration arguments to be
passed into the scheduler.

**do_it**: A function that actually does the thing you want to do every
time the conditions you specified in the job configuration mentioned
above.

Job arguments
-------------

As you can see from the example, the following job arguments are
returned:

.. code:: js

   {'trigger':      'cron',
    'day_of_week':  'sat',
    'hour':         12,
    'name':         self.NAME}

Our trigger type is ``cron``, meaning that it is supposed to fire once
every time the rest of the arguments fit. ``day_of_week`` means which
day it is supposed to fire. ``hour`` means which hour on that day it is
supposed to fire. And every job has to have a name, which is specified
in the ``name`` argument. For a more detailed look at the different
types of arguments and different trigger types that aren’t discussed
here, have a look at the `APScheduler
documentation <https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html?highlight=intervaltrigger#apscheduler.triggers.interval.IntervalTrigger>`__.

Firing it
---------

The function ``do_it`` is called whenever it is time to execute the job.
You can use it to periodically message people, periodically check
statistics, poll Github, you name it.

Adding your module to the scheduler
-----------------------------------

To actually have the scheduler execute and remember your module (and
job), you must add the job to the scheduler. This can be achieved by
adding your module into the scheduler via the function ``__add_job``
within the function ``__init_periodic_tasks``. You can see that we
already have initialized our beloved ``RandomChannelPromoter`` in that
function, so just follow along with your own module.

And look! That wasn’t all that bad now wasn’t it??
