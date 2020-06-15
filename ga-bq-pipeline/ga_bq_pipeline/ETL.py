from google.cloud import bigquery, storage
import argparse
from abc import ABCMeta
import yaml
import os
from ga_bq_pipeline.logger import Logger
from pathlib import Path

GOOGLE_APP_CREDENTIALS_ENV_NAME = 'GOOGLE_APPLICATION_CREDENTIALS'

GOOGLE_CREDENTIALS_PATH = '/google-keys/'

ROOT = str(Path(os.path.dirname(os.path.abspath(__file__))).parent.parent)

class ETL(metaclass=ABCMeta):
    """
    Skeleton of a generic ETL pipeline.

    This class take care of parsing and loading environment and arguments

    A concrete ETL MUST inherit from this class and implements the 3 abstract
    methods

     def pre_execution_cleansing(self):
        pass

     def pipeline(self)
        pass

     def post_execution_cleanup(self):
        pass

    This methods are called by the execute() method and they run in sequence.

    """
    def __init__(self, app_name, conf_file_path, args_file_name, logger_name, env_name=None):
        """
        Configure the ETL class
        :param app_name: application name used for logging references
        :param conf_file_path:  environment configuration directory path
        :param args_file_name: arguments definition file path
        :param logger_name: logger name
        """
        self.__get_arguments(args_file_name)

        # configure the logging
        self._logger = Logger(app_name, logger_name)

        env_name = self.__args.get('environment', None) if env_name is None else env_name
        # get the environment variables from env configuration file
        self.__get_env_vars(conf_file_path, env_name)

        prefix = ROOT if env_name in ['local', 'local-dev'] else ''
        # Google key credentials file path
        if not os.environ.get(GOOGLE_APP_CREDENTIALS_ENV_NAME):
            os.environ[GOOGLE_APP_CREDENTIALS_ENV_NAME] = prefix + GOOGLE_CREDENTIALS_PATH + self.env['service_account']

    @property
    def logger(self):
        """
        Get the logger
        :return: logger
        """
        return self._logger

    @property
    def args(self):
        """
        Get the arguments
        :return: arguments
        """
        return self.__args

    @property
    def env(self):
        """
        Get the environment
        :return: environment variables
        """
        return self.__env

    @property
    def service_account(self):
        """
        Get the Service Account
        :return: Service Account File Location
        """
        return os.environ.get(GOOGLE_APP_CREDENTIALS_ENV_NAME)

    @property
    def bq_client(self):
        """
        Creates a BigQuery Client
        :return: BigQuery Client
        """
        return bigquery.Client()

    @property
    def gs_client(self):
        """
        Creates a Cloud Storage Client
        :return: Cloud Storage Client
        """
        return storage.Client()

    @property
    def bigquery(self):
        """
        Get BigQuery properties
        """
        return self.env['bigquery']

    @property
    def storage(self):
        """
        Get BigQuery properties
        """
        return self.env['storage']

    def __get_arguments(self, args_file_name):
        """
        Get all arguments from the arg configuration file and parse them.
        :param args_file_name: arguments definition file path
        """

        if args_file_name is None:
            self.__args = {}
            return

        try:
            with open(args_file_name) as args_file:
                args_data = yaml.load(args_file.read(), Loader=yaml.FullLoader)
        except IOError as ex:
            self.logger.critical('Fail to read configuration file: {0}'.format(ex))
            return

        try:
            description = args_data['description']
        except KeyError:
            print("Argument description is required.")
            return

        parser = argparse.ArgumentParser(description=description)

        try:
            args = args_data['args']
        except KeyError:
            print("No arguments is found!")
            return

        for arg in args:
            try:
                short = args[arg]['short']
            except KeyError:
                print("Short name is required for an argument!")
                return

            arg_required = args[arg].get('required', False)
            arg_choices = args[arg].get('choices', None)
            arg_help = args[arg].get('help', None)
            arg_type = int if args[arg].get('type', None) == 'int' else None

            parser.add_argument(
                '-{0}'.format(short),
                '--{0}'.format(arg),
                required=arg_required,
                help=arg_help,
                choices=arg_choices,
                type=arg_type
            )

        self.__args = vars(parser.parse_args())

    def __get_env_vars(self, env_path, env_name):
        """
        Get the environment variables from env configuration file
        :param env_path: environment configuration directory path
        :param env_name: environment name
        """

        conf_file_name = '{env_path}/{env_name}.yaml'.format(
            env_path=env_path,
            env_name=env_name
        )

        try:
            with open(conf_file_name) as conf:
                env = yaml.load(conf.read(), Loader=yaml.FullLoader)
        except IOError as ex:
            self.logger.critical('Fail to read environment variables: {0}'.format(ex))
            return

        self.__env = env
