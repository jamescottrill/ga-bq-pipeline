#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )

source $DIR/../env/bin/activate
python $DIR/../ga-bq-pipeline/run_pipeline.py -d $1 -e $2
deactivate