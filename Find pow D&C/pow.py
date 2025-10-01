def superPow(a, b):
    base = 1337

    def powerMod(x, n):
        """Optimized modular exponentiation using recursion"""
        if n == 0:
            return 1
        if n % 2 == 0:
            half = powerMod(x, n // 2)
            return (half * half) % base
        else:
            return (x * powerMod(x, n - 1)) % base

    def dfs(digits):
        if not digits:
            return 1

        # Process from the end (but don't modify original array)
        last_digit = digits[-1]
        remaining_digits = digits[:-1]

        part1 = powerMod(a, last_digit)
        part2 = powerMod(dfs(remaining_digits), 10)

        return (part1 * part2) % base

    return dfs(b)


# Alternative iterative version (more space-efficient)
def superPow_iterative(a, b):
    base = 1337
    result = 1

    def powerMod(x, n):
        """Iterative version of modular exponentiation"""
        res = 1
        x = x % base
        while n > 0:
            if n % 2 == 1:
                res = (res * x) % base
            x = (x * x) % base
            n = n // 2
        return res

    for digit in b:
        result = (powerMod(result, 10) * powerMod(a, digit)) % base

    return result


# Test cases
print(superPow(2, [3]))  # Expected: 8
print(superPow(2, [1, 0]))  # Expected: 1024
