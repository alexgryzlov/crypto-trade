from __future__ import annotations

import pytest
import typing as tp


@pytest.fixture
def empty_logger_mock(monkeypatch: tp.Any) -> None:
    monkeypatch.setattr('logger.logger.Logger.__init__',
                        EmptyLoggerMock.__init__)
    monkeypatch.setattr('logger.logger.Logger.__getattribute__',
                        EmptyLoggerMock.__getattribute__)


class EmptyLoggerMock:
    def __init__(self, *args: tp.Any, **kwargs: tp.Any):
        pass

    def __getattribute__(self, *args: tp.Any, **kwargs: tp.Any) -> EmptyLoggerMock:
        return EmptyLoggerMock()

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> EmptyLoggerMock:
        return EmptyLoggerMock()
