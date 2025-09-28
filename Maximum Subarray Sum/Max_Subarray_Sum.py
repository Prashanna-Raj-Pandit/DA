def find_max_crossing_subarray(A, low, mid, high):
    # Left side: find max sum ending at mid
    left_sum = float('-inf')
    total = 0
    max_left = mid
    for i in range(mid, low - 1, -1):
        total += A[i]
        if total > left_sum:
            left_sum = total
            max_left = i

    # Right side: find max sum starting at mid+1
    right_sum = float('-inf')
    total = 0
    max_right = mid + 1
    for j in range(mid + 1, high + 1):
        total += A[j]
        if total > right_sum:
            right_sum = total
            max_right = j

    return max_left, max_right, left_sum + right_sum


def find_maximum_subarray(A, low, high):
    # Base case: one element
    if high == low:
        return (low, high, A[low])

    mid = (low + high) // 2

    # Recursive calls
    left_low, left_high, left_sum = find_maximum_subarray(A, low, mid)
    right_low, right_high, right_sum = find_maximum_subarray(A, mid + 1, high)
    cross_low, cross_high, cross_sum = find_max_crossing_subarray(A, low, mid, high)

    # Choose the best of three
    if left_sum >= right_sum and left_sum >= cross_sum:
        return (left_low, left_high, left_sum)
    elif right_sum >= left_sum and right_sum >= cross_sum:
        return (right_low, right_high, right_sum)
    else:
        return (cross_low, cross_high, cross_sum)


# A = [2, -4, 3, 5, -1, 2, -6, 4]
A = [-2, -5, 6, -2, -3, 1, 5, -6]
low, high, max_sum = find_maximum_subarray(A, 0, len(A) - 1)
print("Input array: ", A)
print(f"Maximum subarray: {A[low:high + 1]}, Sum = {max_sum}")
