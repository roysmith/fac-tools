import pytest
import pytest_socket


@pytest.fixture(autouse=True)
def disable_socket():
    """Prevent accidental network traffic leaking from tests by
    intercepting it at the network level.
    """
    pytest_socket.disable_socket()
