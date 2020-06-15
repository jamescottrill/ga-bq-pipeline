import sys
from ga_bq_pipeline.bq_etl import PYTHON_MIN_VERSION, PIPELINE, APP_NAME, CONF_FILE_PATH, ARGS_FILE_NAME, LOGGER_NAME

if __name__ == "__main__":
    assert tuple(sys.version_info) >= PYTHON_MIN_VERSION, "Please update to Python {}.{}".format(
        PYTHON_MIN_VERSION[0], PYTHON_MIN_VERSION[1])

    etl = PIPELINE(
        app_name=APP_NAME,
        conf_file_path=CONF_FILE_PATH,
        args_file_name=ARGS_FILE_NAME,
        logger_name=LOGGER_NAME
    )
    etl.execute()