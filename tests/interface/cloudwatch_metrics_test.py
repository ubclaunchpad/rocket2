from unittest import mock, TestCase
from interface.cloudwatch_metrics import CWMetrics
from config import Config


class TestCWMetrics(TestCase):
    def setUp(self):
        self.conf_disable_metrics = mock.MagicMock(Config)
        self.conf_enable_metrics = mock.MagicMock(Config)

        self.conf_enable_metrics.aws_local = False
        self.conf_enable_metrics.aws_region = 'us-west-2'
        self.conf_enable_metrics.aws_access_keyid = 'access key id'
        self.conf_enable_metrics.aws_secret_key = 'secret key'

        self.conf_disable_metrics.aws_local = True

    @mock.patch('logging.info')
    @mock.patch('boto3.client')
    def test_disabled_metrics(self, b3client, log):
        cwm = CWMetrics(self.conf_disable_metrics)
        b3client.assert_not_called()

        cwm.submit_cmd_mstime('team', 30)
        log.assert_called_with(
            'Command Execution Time [team@Rocket 2]: 30 ms')

    @mock.patch('boto3.client')
    def test_enabled_metrics(self, b3client):
        client = mock.Mock()
        b3client.return_value = client

        cwm = CWMetrics(self.conf_enable_metrics)
        b3client.assert_called_once_with(
            service_name='cloudwatch',
            region_name=self.conf_enable_metrics.aws_region,
            aws_access_key_id=self.conf_enable_metrics.aws_access_keyid,
            aws_secret_access_key=self.conf_enable_metrics.aws_secret_key)

        cwm.submit_cmd_mstime('team', 30)
        client.put_metric_data.assert_called_once()
