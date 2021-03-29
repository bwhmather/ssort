from ssort._bubble_sort import bubble_sort


def test_sort_empty():
    array = []
    swap = lambda a, b: a > b
    bubble_sort(array, swap)
    assert array == []


def test_sort_one_element():
    array = []
    swap = lambda a, b: a > b
    bubble_sort(array, swap)
    assert array == []


def test_three_elements():
    array = [3, 2, 1]
    swap = lambda a, b: a > b
    bubble_sort(array, swap)
    assert array == [1, 2, 3]


def test_sort_sorted():
    array = [0, 1, 3, 5, 6]
    swap = lambda a, b: a > b
    bubble_sort(array, swap)
    assert array == [0, 1, 3, 5, 6]


def test_sort_reversed():
    array = [5, 4, 3, 2, 1]
    swap = lambda a, b: a > b
    bubble_sort(array, swap)
    assert array == [1, 2, 3, 4, 5]
