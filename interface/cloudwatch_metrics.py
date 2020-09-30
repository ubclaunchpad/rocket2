import logging
import boto3
from config import Config


class CWMetrics:
    def __init__(self, config: Config):
        if config.aws_local:
            self.cw = None
        else:
            self.cw = boto3.client(
                service_name='cloudwatch',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_keyid,
                aws_secret_access_key=config.aws_secret_key)
        logging.info('Initialized CWMetrics')

    def submit_cmd_mstime(self, cmd_name: str, ms: float):
        if self.cw is None:
            logging.info(
                f'Command Execution Time [{cmd_name}@Rocket 2]: {ms} ms'
            )
            return

        self.cw.put_metric_data(
            Namespace='Rocket 2',
            MetricData=[
                {
                    'MetricName': 'Command Execution Time',
                    'Dimensions': [
                        {
                            'Name': 'Command type',
                            'Value': cmd_name
                        }
                    ],
                    'Value': ms,
                    'Unit': 'Milliseconds'
                }
            ]
        )
