import os
import requests

from simple_salesforce import Salesforce
from aws_lambda_powertools import Logger

SALESFORCE_TIMEOUT_SECONDS = 15

logger = Logger()

user = os.environ["SalesforceUser"]
password = os.environ["SalesforcePass"]
security_token = os.environ["SalesforceSecurityToken"]
consumer_key = os.environ["SalesforceConsumerKey"]
consumer_secret = os.environ["SalesforceConsumerSecret"]
TEST_LOCAL = os.getenv("TEST_LOCAL", "false").lower() == "true"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


class TimeoutAdapter(requests.adapters.HTTPAdapter):
    """Custom adapter to add a timeout to Salesforce API requests"""

    def send(self, *args, **kwargs):
        kwargs["timeout"] = SALESFORCE_TIMEOUT_SECONDS
        return super().send(*args, **kwargs)


def build_request_session() -> requests.Session:
    """Return a requests session with a timeout adapter

    Returns:
        requests.Session: the requests session with a timeout adapter
    """
    requests_session = requests.Session()
    # Add a timeout to Salesforce API requests
    requests_session.mount("https://", TimeoutAdapter())
    requests_session.mount("http://", TimeoutAdapter())
    return requests_session


def open_session() -> Salesforce:
    """Return an authenticated Salesforce session

    Returns:
        Salesforce: the authenticated Salesforce session.
    """
    session = get_session(
        username=user,
        password=password,
        security_token=security_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
    )
    return session


def get_session(
    username: str,
    password: str,
    security_token: str,
    consumer_key: str,
    consumer_secret: str,
) -> Salesforce:
    """Return an authenticated Salesforce session

    Args:
      username (str): The username to use for authentication.  This users permissions will be used for the session.
      password (str): The password of the user that is authenticating.
      security_token (str): The security token of the user that is authenticating.
      consumer_key (str): The name of the Salesforce connected app.
      url (str): The domain of the Salesforce instance.  Use `test` for the QA instance.

      Returns:
        Salesforce: the authenticated Salesforce session.
    """

    logger.debug(f"Salesforce login: {username}")
    logger.debug(f"Salesforce domain: {'test' if DEBUG else None}")
    logger.debug(f"Test local: {TEST_LOCAL}")

    try:
        return Salesforce(
            client_id="Notify",
            username=username,
            password=password,
            security_token=security_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            session=build_request_session(),
            domain="test" if DEBUG else None,
        )
    except Exception as ex:
        logger.error(f"Salesforce login failed: {ex}")
        return None


def end_session(session: Salesforce):
    """Logout of a Salesforce session

    Args:
        session (Salesforce): The session to revoke.
    """
    try:
        if session and session.session_id:
            session.oauth2("revoke", {"token": session.session_id}, method="POST")
    except Exception as ex:
        logger.error(f"Salesforce logout failed: {ex}")
