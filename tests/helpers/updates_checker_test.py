import pytest

import typing as tp

from helpers.updates_checker import UpdatesChecker, handlers_name, FromClass


@pytest.fixture(scope="function")
def clear_updates_checker() -> None:
    UpdatesChecker.last_updates.clear()
    UpdatesChecker.last_executed.clear()


@UpdatesChecker.check_update('0mod3', lambda x: x is not None)
def append_0_mod_3(x: int, array: list[int]) -> tp.Optional[int]:
    if x % 3 == 0:
        array.append(x)
        return x
    return None


@UpdatesChecker.check_update('1mod3', lambda x: x is not None)
def append_1_mod_3(x: int, array: list[int]) -> tp.Optional[int]:
    if x % 3 == 1:
        array.append(x)
        return x
    return None


@UpdatesChecker.on_updates(['0mod3'], None)
def get_if_0_mod_3(array: list[int]) -> tp.Optional[list[int]]:
    return array


@pytest.mark.parametrize("values", [
    [i for i in range(0, 15, 3)],
    [i for i in range(1, 15, 3)],
    [i for i in range(2, 15, 3)],
    [i for i in range(15)],
])
def test_one_checker(values: list[int], clear_updates_checker: None) -> None:
    array: list[int] = []
    true_array: list[int] = []
    for elem in values:
        append_0_mod_3(elem, array)
        if elem % 3 == 0:
            true_array.append(elem)
            assert true_array == get_if_0_mod_3(array)
        else:
            assert get_if_0_mod_3(array) is None


@UpdatesChecker.on_updates(['0mod3', '1mod3'], None, 'any')
def get_if_0_or_1_mod_3(array: list[int]) -> tp.Optional[list[int]]:
    return array


@pytest.mark.parametrize("values", [
    [i for i in range(0, 15, 3)],
    [i for i in range(1, 15, 3)],
    [i for i in range(2, 15, 3)],
    [i for i in range(15)],
])
def test_two_checkers_any(values: list[int], clear_updates_checker: None) -> None:
    array: list[int] = []
    true_array: list[int] = []
    for elem in values:
        append_0_mod_3(elem, array)
        append_1_mod_3(elem, array)
        if elem % 3 != 2:
            true_array.append(elem)
            assert true_array == get_if_0_or_1_mod_3(array)
        else:
            assert get_if_0_or_1_mod_3(array) is None


@UpdatesChecker.on_updates(['0mod3', '1mod3'], None, 'all')
def get_if_0_or_1_mod_3_all(array: list[int]) -> tp.Optional[list[int]]:
    return array


@pytest.mark.parametrize("values", [
    [i for i in range(0, 15, 3)],
    [i for i in range(1, 15, 3)],
    [i for i in range(2, 15, 3)],
    [i for i in range(15)],
])
def test_two_checkers_all(values: list[int], clear_updates_checker: None) -> None:
    array: list[int] = []
    true_array: list[int] = []
    updated: int = 0  # mask of updated values (00 -- nothing updated, 11 -- both 0 and 1 updated)
    for elem in values:
        append_0_mod_3(elem, array)
        append_1_mod_3(elem, array)
        if elem % 3 != 2:
            true_array.append(elem)
            updated |= 2 ** (elem % 3)
        if updated == 3:
            assert true_array == get_if_0_or_1_mod_3_all(array)
            updated = 0
        else:
            assert get_if_0_or_1_mod_3_all(array) is None


class HandlerMock:
    def __init__(self) -> None:
        self.name = 'HandlerMock name'

    def get_name(self) -> str:
        return self.name

    @UpdatesChecker.check_update(handlers_name)
    def update_handler(self) -> bool:
        return True

    @UpdatesChecker.on_updates(FromClass(lambda cls: [cls.name]), False)
    def check(self) -> bool:
        return True


def test_helpers(clear_updates_checker: None) -> None:
    handler = HandlerMock()
    handler.update_handler()

    # test handlers_name
    assert len(UpdatesChecker.last_updates.keys()) == 1
    assert list(UpdatesChecker.last_updates.keys())[0] == handler.get_name()

    # test FromClass
    assert handler.check()
