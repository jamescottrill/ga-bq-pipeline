import os
import yaml
from pathlib import Path
from datetime import timedelta, datetime
from airflow.models import DAG, Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator


AIRFLOW_ENV_VAR = 'airflow_env'
ENV = Variable.get(AIRFLOW_ENV_VAR)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = "config_{}.yaml".format(ENV)
ROOT = str(Path(CURRENT_DIR).parent)

with open(os.path.join(CURRENT_DIR, CONFIG_FILE)) as config:
    conf = yaml.load(config, Loader=yaml.FullLoader)
    pipeline_conf = conf['pipeline']
    dag_args = conf['dag_args']

STARTDATE = datetime.strptime(dag_args['start_date'], '%Y%m%d')

YESTERDAY = (datetime.now() - timedelta(1)).strftime('%Y%m%d')

default_dag_args = {
    'dag_id': pipeline_conf['name'],
    'start_date': STARTDATE,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': dag_args['retries'],
    'retry_delay': timedelta(minutes=dag_args['delay']),
    'catchup': dag_args['catchup']
}

dag = DAG(
    dag_id=pipeline_conf['name'],
    default_args=default_dag_args,
    schedule_interval=dag_args['schedule_interval'])

start = DummyOperator(task_id='start', dag=dag)

run_pipeline = BashOperator(
    task_id='run_pipeline',
    bash_command='python ' + ROOT + '/ga-bq-pipeline/run_pipeline.py -e '+ pipeline_conf['env'] +' -d ' + YESTERDAY,
    dag=dag
)
start >> run_pipeline
