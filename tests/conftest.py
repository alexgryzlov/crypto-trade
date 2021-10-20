def pytest_addoption(parser):
    parser.addoption(
        "--testnet",
        action="store_true",
        default=False,
        help="Run tests with testnet",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "testnet: mark that the test requires access to testnet (network)"
    )


def pytest_collection_modifyitems(config, items):
    run_testnet = config.getoption("testnet")

    if not run_testnet:
        for item in items.copy():
            if item.get_closest_marker(name="testnet"):
                items.remove(item)
                continue

    # hacky magic to ensure the correct number of tests is shown in collection report
    config.pluginmanager.get_plugin("terminalreporter")._numcollected = len(items)
