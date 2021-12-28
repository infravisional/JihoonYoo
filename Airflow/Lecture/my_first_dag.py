### my_first_dag.py ###

'''
A DAG file, which is basically a Python script, is a configuration file specifying
the DAG's structure as code.

There are only 5 steps you need to remember to write an Airflow DAG.
# Step 1 - importing modules
# Step 2 - Default arguments
# Step 3 - Instantiate a DAG
# Step 4 - Tasks
# Step 5 - Setting up dependencies
'''

# Step 1 - importing modules
from datetime import timedelta

import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator


# Step 2 - Default arguments
default_args = {
    'owner': 'airflow',    
    'start_date': airflow.utils.dates.days_ago(2),
    # 'end_date': datetime(2018, 12, 30),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    # If a task fails, retry it once after waiting
    # at least 5 minutes
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# Step 3 - Instantiate a DAG
dag = DAG(
    'tutorial',
    default_args=default_args,
    description='Tutorial DAG',
    schedule_interval=timedelta(days=1),
)


# Step 4 - Tasks
# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

t2 = BashOperator(
    task_id='sleep',
    depends_on_past=False,
    bash_command='sleep 5',
    dag=dag,
)

templated_command = """
{% for i in range(5) %}
    echo "{{ ds }}"
    echo "{{ macros.ds_add(ds, 7)}}"
    echo "{{ params.my_param }}"
{% endfor %}
"""

t3 = BashOperator(
    task_id='templated',
    depends_on_past=False,
    bash_command=templated_command,
    params={'my_param': 'Parameter I passed in'},
    dag=dag,
)


# Step 5 - Setting up dependencies
# This means that t2 will depend on t1 running successfully to run.
t1.set_downstream(t2)

# similar to above where t3 will depend on t1
t3.set_upstream(t1)

'''
# The bit shift operator can also be used to chain operations:
t1 >> t2

# And the upstream dependency with the bit shift operator:
t2 << t1

# A list of tasks can also be set as dependencies. These operations all have the same effect:
t1.set_downstream([t2, t3])
t1 >> [t2, t3]
[t2, t3] << t1
'''



