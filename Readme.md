# Google Analytics BigQuery Data Pipeline

This has been a longstanding project of mine to replicate, as closely as possible, the GA360 > BigQuery export. This readme assumes that you already have python installed on your device and have a basic understanding of python code execution and also running pipelines on Airflow.

## Why do this?
1. Data Ownership - Unlike the data in Google Analytics, you own your data. You can move it wherever you want, do whatever you want with it and analyse it however you like without worrying about API limits or restrictions
2. Price - Many medium sized companies can't afford the large price tag for the GA360 licence, but would benefit from having access to hit level analytics data, this implementation gives you that without the additional cost.
3. PII - You SHOULD NOT store PII in your analytics data. It's bad, mkay. That said, sometimes PII is accidentally ingested into your GA, through errant querystring parameters or user searches (it's amazing how many people try and search for their username…). Google's response to this is to delete all the data for the field where the PII is found, which might be all your page paths. Having the export gives you a backup of your data, so you can still perform long term analysis.
4. Unlimited Custom Dimensions/Metrics - Free GA has a limit of 20 Custom Dimensions and 20 Custom Metrics, GA360 has a limit of 200, with this you can collect an unlimited number. That doesn't mean you have to, no-one likes confetti, but with large eCommerce it's very easy to hit 200.

## Before you start
This isn't a perfect replica of GA Data. It doesn't include any filters, it doesn't include Google Ads details beyond the gclid, it only includes basic filters, it doesn't do content grouping if it's not sent in the hit, it doesn't do page timing, it doesn't do geolocation, it doesn't have channel grouping, it doesn't show the visit count… There's lots that this doesn't do. However, for slightly more advanced analytics, where hit level data is required, it's a pretty good approximation.  

## How to set it up
Before you can start looking at the pipeline, you need to have the hit level data coming in. There are multiple ways you can achieve this, the way that I used is described in this blog by [Doug Hall](https://www.conversionworks.co.uk/blog/2019/06/14/custom-data-pipeline-to-bigquery-in-realtime/), which is based on a blog by [Simo Ahava](https://www.simoahava.com/analytics/automatically-fork-google-analytics-hits-snowplow/). 

It's probably worth noting that there are other ways to do this, such as [using a pixel](https://cloud.google.com/solutions/serverless-pixel-tracking), which may be more cost effective or efficient, depending on your traffic volume, but that's for you to decide.

Whatever method you choose, you need to make sure that your pipeline query reflects how your hit level data are stored.

You'll also need to slightly modify your hits, to include the scope of all your custom definitions.

The way that I've implemented this is to send an additional custom dimension, which is offset by a certain amount, that contains the scope. So for Custom Dimension 1, there is also a Custom Dimension 101 that includes the scope, CD2 is CD102 etc. The same applies for custom metrics CM1 > CM101.

The scope is encoded as 'H', 'S', 'P' or 'U'. There are other ways that this could be done, including creating a dictionary in the pipeline, but by sending the scope with the hit it ensures that it's always accurate (asusming you remember to change it if you change the custom dimension.)

The other modification required is the device information. The device User Agent (`window.navigator.userAgent`) is required to produce the device columns. This configuration relies on it being passed as a Custom Dimension.

## Pipeline configuration
The majority of the pipeline will work without any modification, however user settings do need to be set up. 
### Environment Configuration YAML
1. Service Account - The pipeline is set up to use a service account, it will need BQ Editor and Storage Editor permissions. Once you've set up the service account, put the json file in the `google-keys` folder.
1. The Environment Configuration Files - Many of the attributes required are stored in the `ga-bq-pipeline/ga_bq_pipeline/conf` folder. In this repo there is a template file for the configuration. You'll need to fill these out for your specific use case. 
    1. The BigQuery `source_` values are for the table your hits are streamed in to.
    1. The other BigQuery values are for the destination table
    1. Storage Bucket Name is where the daily json files will be saved. This needs to be globally unique
    1. Service Account - The name of your service account file e.g. 'my-service-account.json'
    1. Save the file in the format 'envname.yaml' e.g. dev.yaml
### bq_etl.py
1. Custom Dimension Offset - As mentioned above, Along with your hit you need to send an additional custom dimension, offset by a certain value, containing hte scope. This can be whatever offset you like, you just need to update the offset.
1. User Agent Custom Dimension - The User Agent string needs to be sent as a Custom Dimension, and the index of that dimension needs to be set. 
1. Social Sources - A basic regex is used to determine if traffic came from a social source. This uses the standard social network sites, but if you have additional sites you want to track, you can add them there.

### airflow_scheduler_local.py
1. The Airflow Env Name - the environment variable that airflow uses to determine which configuration file to load. As you can use any variable name, update the variable at the top of the airflow scheduler if you use something other than 'AIRFLOW_ENV'. Also remember to update the variable you set when loading Airflow. You can also 

### Airflow conf_env.yaml files
1. pipeline > env - This is the configuration for the pipeline, not airflow (prod, dev, local-prod, local-dev)
1. dag_args > schedule_interval - You can leave this as is or update it to suit you. Remember all times are in UTC, so adjust the time to ensure your hits are processed after midnight in your timezone. 
---
Other values can be left 'as is'.

## Local Setup
If you already have Airflow set up on your device, or you're implementing this on a production airflow server, you can skip this bit.

The first step is to create a new environment 
```python
python -m virtualenv env
source env bin activate
pip -r ga-bq-pipeline/requirements.txt
```
Then launch airflow
```bash
export AIRFLOW_HOME=~/airflow
airflow variables -s airflow_env dev #or prod, if you're running in production
ln -s $(pwd) $AIRFLOW_HOME/dags/demo
airflow initdb
airflow webserver
```
You can also launch another terminal window and run 
```bash
airflow scheduler
```

That should be it. You can turn your dag on and either wait for it to run on schedule or trigger it manually.
