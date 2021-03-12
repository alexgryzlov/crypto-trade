import pytest


@pytest.fixture
def empty_logger_mock(monkeypatch):
    monkeypatch.setattr('logger.logger.Logger.__init__', EmptyLoggerMock.__init__)
    monkeypatch.setattr('logger.logger.Logger.__getattribute__', EmptyLoggerMock.__getattribute__)


class EmptyLoggerMock:
    def __init__(self, *args, **kwargs):
        pass

    def __getattribute__(self, *args, **kwargs):
        return EmptyLoggerMock()

    def __call__(self, *args, **kwargs):
        return EmptyLoggerMock()
