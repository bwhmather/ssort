def bubble_sort(array, swap):
    n = len(array)
    while n > 1:
        next_n = 0
        for i in range(1, n):
            if swap(array[i - 1], array[i]):
                array[i - 1], array[i] = array[i], array[i - 1]
                next_n = i
        n = next_n
