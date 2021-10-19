def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "testnet: mark that the test requires access to testnet (network)"
    )
