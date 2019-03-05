"""Tests for Github App interface."""
from interface.github_app import GithubAppInterface
from datetime import datetime
import jwt

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


def test_github_app_auth():
    """Test GithubAppAuth internal class."""
    app_id = "test_app_id"
    auth = GithubAppInterface.GithubAppAuth(app_id, PRIVATE_KEY)
    token = jwt.decode(auth.token, PUBLIC_KEY, algorithms='RS256')
    assert token['exp'] == auth.expiry
    assert token['iss'] == app_id
    assert not auth.is_expired()
