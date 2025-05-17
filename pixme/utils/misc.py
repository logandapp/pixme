def find_partition(arr: list[int], to_search: int):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == to_search:
            return mid
        elif arr[mid] > to_search:
            right = mid - 1
        else:
            left = mid + 1
    return left
