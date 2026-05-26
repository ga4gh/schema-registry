import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--api-root",
        action="store",
        default=None,
        help="Base URL of the schema registry server to test (e.g., https://schema-registry.databio.org/api)",
    )


@pytest.fixture(scope="session")
def api_root(request):
    url = request.config.getoption("--api-root")
    if not url:
        pytest.skip("--api-root not provided")
    return url.rstrip("/")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "recommended: mark test as RECOMMENDED (not REQUIRED) by spec"
    )
    config.addinivalue_line(
        "markers", "require_service: mark test as requiring a running schema registry server"
    )


def pytest_collection_modifyitems(config, items):
    api_root = config.getoption("api_root")
    if api_root is None:
        skip = pytest.mark.skip(reason="No --api-root provided")
        for item in items:
            if "require_service" in item.keywords:
                item.add_marker(skip)
