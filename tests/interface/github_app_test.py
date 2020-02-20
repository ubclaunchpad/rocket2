"""Tests for Github App interface."""
from unittest.mock import patch
from unittest import TestCase
import jwt

from interface.exceptions.github import GithubAPIException
from interface.github_app import GithubAppInterface, \
    DefaultGithubAppAuthFactory

PRIVATE_KEY = \
    "-----BEGIN PRIVATE KEY-----\n" \
    "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCWqqwmhlqFnYFH\n" \
    "AYCOHzj8tItvWLpFuUjH93lE7hDVNOGrpc5Ooh0NH3cBSHxgLpPZ6/ZTgtF8sBZu\n" \
    "E8NcRIkDs6ZbdKZs2TnRqZSAvAMLVAEmvwri+Lq+bFYRAit8IrdyRD/x89cBF+WS\n" \
    "UYjStLhVCyvHpRykAwLr2w//7+VtLiZycJO07ZkcXZxc4QK5Y2tunFFCDTEPUP+Z\n" \
    "MQngvxdt1Ytm1YspKOLgYat7gT8Uv7LdhMAWdcoy8lZiU+qF0YVLX4/5xpjqvtps\n" \
    "mKhMfa2vibxtKlcSL1WcYYMNYQ3uMn3ER9dOWHnbr7QoCfrbpTZXyXehN8x6YwbG\n" \
    "3LzsZw9LAgMBAAECggEAMkj6Nc1njuq3h+xPbJ+tFGJpmxsA6F5jlSHaXpAaHB6P\n" \
    "JwuqpIHkskmLHWmE4VEKVZQ0XUDvC+91PP3pmPTiydJ+tk1jcja53mj7wE9/sJsz\n" \
    "2yutxX0ATqe3vet8eezYTxHKScV5P8sq+r+tq61XTELzNKm9uluq8O7nEyOM7fgT\n" \
    "EHZBteEJDsdnAyDuwKNmP120XyNYZuOvangXF3SlswlxDKhdiS8POIRXujhiHGGb\n" \
    "cQ5Q5PO9B30haTHKpei7xL+tVMAcABvYHE7XbtX5MCNckYc4cCjOLbn32cz7NXCZ\n" \
    "uy+R/6tD/f1swjXBMZzt1LoUMlLyWmSHIwg60CbJWQKBgQDGkrMlwIBz2hEdPKuN\n" \
    "6SGU8Y6pXGQepR1Bpmo0khA4Y0eR38UBAFemHkc5oV4mPMJA0BWRSIriY8wPzD4l\n" \
    "SX6bRkE0mHS7xcmQ/+JGjHKZsK+pFz3ounQesVdAQRETXn+/9I5UJBPmSn3as8WP\n" \
    "daNA3/JLyPLVNKxEmAdpUvSJnwKBgQDCPT0nBwPhk8yxMGJgmxieMgIha7tz1emP\n" \
    "FYIN7LBtEnP9sWqQZCY2/j5Bgh9NFMKWqpL2Wmp0gtmIxKcQmcl3jMkIzc9eM3YN\n" \
    "BNcz4uGQYjA4SUYqWaLdzFbGQmIzn+8MvsYah3mQZ3Qht+7w5p7kQXQTNAzHdTK4\n" \
    "Z1LpWMCy1QKBgEr/PQoVGm6m/a+9Kk3+ruBCG097xZSNZ+9TmukgAWBKns1JZm5q\n" \
    "YrAq31u0xopKiFNSQ9MLQukeKAQPb6lFiLu8XQQwUGZa3TYWbq+We/Hv+Wgzjv5G\n" \
    "7XRqJjnuWTSnjDhDdT3yIlHn8ICZRRRZqb7m1ewpiQ1dR3LguGvfGNyhAoGAZNQt\n" \
    "Pmkh1qNGimQ3bTaVnOkQuhCWihbs2t2rWVcYbkY59+N1Eecq/zkTUCYf4X95U4TQ\n" \
    "LRnaUQjrq1eJ8dAjCPAIG43aq2fDTBbLL6ACv1R4+37t8WX+aWx9TwV+vJW1HcSa\n" \
    "SYMx04ggfLBiVKMisBJaEu3eBFwOLDNWktMDlNECgYBSKqw3GO0EfX2FkxvG0HIY\n" \
    "iGzd5+bqxv69LQiqkKENJ3Lj4qmFCXa4iZh5LH8qq/W34Ow4R3pNTUzcAGXh2SLY\n" \
    "5dlbqr6UPEVGChdKV7tXWlOUxxxb20RHl2ganwpvILjElivG7+02+9H3Lkaa9QwV\n" \
    "Gc6OQWnZIEVhIxyjXotpPQ==\n" \
    "-----END PRIVATE KEY-----\n"
PUBLIC_KEY = \
    "-----BEGIN PUBLIC KEY-----\n" \
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlqqsJoZahZ2BRwGAjh84\n" \
    "/LSLb1i6RblIx/d5RO4Q1TThq6XOTqIdDR93AUh8YC6T2ev2U4LRfLAWbhPDXESJ\n" \
    "A7OmW3SmbNk50amUgLwDC1QBJr8K4vi6vmxWEQIrfCK3ckQ/8fPXARflklGI0rS4\n" \
    "VQsrx6UcpAMC69sP/+/lbS4mcnCTtO2ZHF2cXOECuWNrbpxRQg0xD1D/mTEJ4L8X\n" \
    "bdWLZtWLKSji4GGre4E/FL+y3YTAFnXKMvJWYlPqhdGFS1+P+caY6r7abJioTH2t\n" \
    "r4m8bSpXEi9VnGGDDWEN7jJ9xEfXTlh526+0KAn626U2V8l3oTfMemMGxty87GcP\n" \
    "SwIDAQAB\n" \
    "-----END PUBLIC KEY-----\n"


class TestDefaultGithubAppAuthFactory(TestCase):
    """Test case for DefaultGithubAppAuthFactory class."""

    def setUp(self):
        """Set everything up for testing the class."""
        self.app_id = "test_app_id"
        self.factory = DefaultGithubAppAuthFactory(self.app_id, PRIVATE_KEY)

    def test_token_creation(self):
        """Test create() function."""
        auth = self.factory.create()
        token = jwt.decode(auth.token, PUBLIC_KEY, algorithms='RS256')
        self.assertEqual(token['iss'], self.app_id)
        self.assertFalse(auth.is_expired())


class TestGithubAppInterface(TestCase):
    """Test case for GithubAppInterface class."""

    def setUp(self):
        """Set everything up for testing the class."""
        self.app_id = 'test_app_id'
        self.default_factory = DefaultGithubAppAuthFactory(self.app_id,
                                                           PRIVATE_KEY)
        self.interface = GithubAppInterface(self.default_factory)

    @patch('requests.get')
    def test_get_app_details_bad_status(self, mock_request):
        """Test get_app_details() when status code returns non-200."""
        mock_request.return_value.status_code = 500
        with self.assertRaises(GithubAPIException):
            self.interface.get_app_details()

    @patch('requests.get')
    def test_get_app_details(self, mock_request):
        """Test get_app_details()."""
        expected_headers = {
            'Authorization': f'Bearer {self.interface.auth.token}',
            'Accept': 'application/vnd.github.machine-man-preview+json'
        }
        mock_request.return_value.status_code = 200

        self.interface.get_app_details()

        mock_request.assert_called_once_with(
            url="https://api.github.com/app",
            headers=expected_headers
        )

    @patch('requests.get')
    def test_create_api_token_get_failure(self, mock_get):
        """Test create_api_token() with failing get request."""
        mock_get.return_value.status_code = 500
        with self.assertRaises(GithubAPIException):
            self.interface.create_api_token()

    @patch('requests.get')
    @patch('requests.post')
    def test_create_api_token_post_failure(self, mock_post, mock_get):
        """Test create_api_token() with failing post request."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            'id': 7
        }]
        mock_post.return_value.status_code = 500
        with self.assertRaises(GithubAPIException):
            self.interface.create_api_token()

    @patch('requests.get')
    @patch('requests.post')
    def test_create_api_token(self, mock_post, mock_get):
        """Test create_api_token()."""
        expected_headers = {
            'Authorization': f'Bearer {self.interface.auth.token}',
            'Accept': 'application/vnd.github.machine-man-preview+json'
        }
        mock_ret_val = "token"
        mock_id = 7
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            'id': mock_id
        }]
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            'token': "token"
        }

        self.assertEqual(self.interface.create_api_token(), mock_ret_val)

        mock_get.assert_called_once_with(
            url="https://api.github.com/app/installations",
            headers=expected_headers)
        mock_post.assert_called_once_with(
            url=f"https://api.github.com/app/installations/"
                f"{mock_id}/access_tokens",
            headers=expected_headers)
