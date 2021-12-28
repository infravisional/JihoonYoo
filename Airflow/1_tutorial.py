##### Tutorial #####

"""
DAG definition file

Airflow python scripts is really just a config file specifying 
the DAG's structure as code. People sometimes think of the 
DAG definition file as a place where they can do some actual
data processing - that is not the case at all!
"""

"""
Importing modules

An Airflow pipeline is just a Python script that happens to 
define an Airflow DAG object. 
"""
from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator


"""
Default Arguments

We’re about to create a DAG and some tasks, and we have the choice 
to explicitly pass a set of arguments to each task’s constructor 
(which would become redundant), or (better!) we can define 
a dictionary of default parameters that we can use when 
creating tasks.
"""
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
"""
Instantiate a DAG

Here we pass a string that defines the dag_id, which serves as 
a unique identifier for your DAG. We also pass the default argument 
dictionary that we just defined and define a schedule_interval of 
1 day for the DAG.
"""
with DAG(
    'tutorial',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
"""
Tasks

Tasks are generated when instantiating operator objects. An object 
instantiated from an operator is called a task. The first argument 
task_id acts as a unique identifier for the task.

Notice how we pass a mix of operator specific arguments (bash_command)
and an argument common to all operators (retries) inherited from 
BaseOperator to the operator’s constructor. This is simpler than passing 
every argument for every constructor call. Also, notice that in the 
second task we override the retries parameter with 3.

The precedence rules for a task are as follows:
1. Explicitly passed arguments
2. Values that exist in the default_args dictionary
3. The operator’s default value, if one exists

A task must include or inherit the arguments task_id and owner, 
otherwise Airflow will raise an exception.
"""
    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    t2 = BashOperator(
        task_id='sleep',
        depends_on_past=False,
        bash_command='sleep 5',
        retries=3,
    )
"""
Templating with Jinja

Airflow leverages the power of Jinja Templating and provides 
the pipeline author with a set of built-in parameters and macros. 
Airflow also provides hooks for the pipeline author to define their 
own parameters, macros and templates.

This tutorial barely scratches the surface of what you can do with 
templating in Airflow, but the goal of this section is to let you 
know this feature exists, get you familiar with double curly brackets, 
and point to the most common template variable: 
{{ ds }} (today’s “date stamp”)

Notice that the templated_command contains code logic in {% %} 
blocks, references parameters like {{ ds }}, calls a function as in 
{{ macros.ds_add(ds, 7)}}, and references a user-defined parameter 
in {{ params.my_param }}.

The params hook in BaseOperator allows you to pass a dictionary of 
parameters and/or objects to your templates. Please take the time 
to understand how the parameter my_param makes it through to the 
template.

Files can also be passed to the bash_command argument, like 
bash_command='templated_command.sh', where the file location is 
relative to the directory containing the pipeline file (tutorial.py 
in this case). This may be desirable for many reasons, like separating 
your script’s logic and pipeline code, allowing for proper code 
highlighting in files composed in different languages, and general 
flexibility in structuring pipelines. It is also possible to define 
your template_searchpath as pointing to any folder locations in the 
DAG constructor call.

Using that same DAG constructor call, it is possible to define 
user_defined_macros which allow you to specify your own variables. 
For example, passing dict(foo='bar') to this argument allows you to 
use {{ foo }} in your templates. Moreover, specifying user_defined_filters 
allows you to register your own filters. 

For example, passing dict(hello=lambda name: 'Hello %s' % name) to 
this argument allows you to use {{ 'world' | hello }} in your templates. 
"""
    t1.doc_md = dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](http://montcs.bloomu.edu/~bobmon/Semesters/2012-01/491/import%20soul.png)

    """
    )

    dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this
    templated_command = dedent(
        """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
        echo "{{ params.my_param }}"
    {% endfor %}
    """
    )

    t3 = BashOperator(
        task_id='templated',
        depends_on_past=False,
        bash_command=templated_command,
        params={'my_param': 'Parameter I passed in'},
    )

    t1 >> [t2, t3]
    
    
""" 
Setting up Dependencies 

Let's say we have tasks t1, t2 and t3 that do not depend on each other.
Note that when executing your script, Airflow will raise exceptions 
when it finds cycles in your DAG or when a dependency is referenced more 
than once.
"""

t1.set_downstream(t2)

# This means that t2 will depend on t1
# running successfully to run.
# It is equivalent to:
t2.set_upstream(t1)

# The bit shift operator can also be
# used to chain operations:
t1 >> t2

# And the upstream dependency with the
# bit shift operator:
t2 << t1

# Chaining multiple dependencies becomes
# concise with the bit shift operator:
t1 >> t2 >> t3

# A list of tasks can also be set as
# dependencies. These operations
# all have the same effect:
t1.set_downstream([t2, t3])
t1 >> [t2, t3]
[t2, t3] << t1

""" 
Running the script

Let’s assume we are saving the code from the previous step in tutorial.py 
in the DAGs folder referenced in your airflow.cfg. The default location 
for your DAGs is ~/airflow/dags.

"""

"""
Command Line Metadata Validation

Let’s run a few commands to validate this script further.

# initialize the database tables
airflow db init

# print the list of active DAGs
airflow dags list

# prints the list of tasks in the "tutorial" DAG
airflow tasks list tutorial

# prints the hierarchy of tasks in the "tutorial" DAG
airflow tasks list tutorial --tree
"""


""" 
Testing

Let’s test by running the actual task instances for a specific date. 
The date specified in this context is called the logical date (also 
called execution date for historical reasons), which simulates the 
scheduler running your task or DAG for a specific date and time, even 
though it physically will run now (or as soon as its dependencies 
are met).

We said the scheduler runs your task *for* a specific date and time, not 
*at*. This is because each run of a DAG conceptually represents not 
a specific date and time, but an interval between two times, called 
a data interval. A DAG run’s logical date is the start of its data 
interval.

# command layout: command subcommand dag_id task_id date

# testing print_date
airflow tasks test tutorial print_date 2015-06-01

# testing sleep
airflow tasks test tutorial sleep 2015-06-01

# testing templated
airflow tasks test tutorial templated 2015-06-01

Note that the airflow tasks test command runs task instances locally, 
outputs their log to stdout (on screen), does not bother with 
dependencies, and does not communicate state (running, success, failed, …) 
to the database. It simply allows testing a single task instance.

The same applies to airflow dags test [dag_id] [logical_date], but 
on a DAG level. It performs a single DAG run of the given DAG id. 
While it does take task dependencies into account, no state is 
registered in the database. It is convenient for locally testing 
a full run of your DAG, given that e.g. if one of your tasks expects 
data at some location, it is available.
"""


"""
Backfill

Everything looks like it’s running fine so let’s run a backfill. 
backfill will respect your dependencies, emit logs into files and talk to
the database to record status. If you do have a webserver up, you will 
be able to track the progress. airflow webserver will start a web server 
if you are interested in tracking the progress visually as your backfill 
progresses.

Note that if you use depends_on_past=True, individual task instances will 
depend on the success of their previous task instance (that is, previous 
according to the logical date). Task instances with their logical dates 
equal to start_date will disregard this dependency because there would be 
no past task instances created for them.

You may also want to consider wait_for_downstream=True when using 
depends_on_past=True. While depends_on_past=True causes a task instance 
to depend on the success of its previous task_instance, wait_for_downstream=True 
will cause a task instance to also wait for all task instances immediately 
downstream of the previous task instance to succeed.

The date range in this context is a start_date and optionally an end_date, 
which are used to populate the run schedule with task instances from this dag.

# optional, start a web server in debug mode in the background
# airflow webserver --debug &

# start your backfill on a date range
airflow dags backfill tutorial \
    --start-date 2015-06-01 \
    --end-date 2015-06-07
"""

