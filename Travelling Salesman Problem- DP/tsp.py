import math


def tsp_dp(dist):
    """
    Solves the Travelling Salesman Problem using Dynamic Programming (Held-Karp algorithm).

    Parameters:
        dist (list of list of int/float): Distance matrix where dist[i][j] is the cost to travel from city i to j.

    Returns:
        min_cost (float): Minimum travel cost to complete the tour.
        path (list): The path of cities in the optimal tour.
    """
    n = len(dist)
    # dp[mask][i] = minimum cost to reach set of cities in mask, ending at city i
    dp = [[math.inf] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    # Start from city 0
    dp[1][0] = 0

    for mask in range(1 << n):
        for u in range(n):
            if not (mask & (1 << u)):
                continue
            for v in range(n):
                if mask & (1 << v):  # if v is already visited
                    continue
                new_mask = mask | (1 << v)
                new_cost = dp[mask][u] + dist[u][v]
                if new_cost < dp[new_mask][v]:
                    dp[new_mask][v] = new_cost
                    parent[new_mask][v] = u

    # Final step: return to city 0
    full_mask = (1 << n) - 1
    min_cost = math.inf
    last_city = -1
    for i in range(1, n):
        cost = dp[full_mask][i] + dist[i][0]
        if cost < min_cost:
            min_cost = cost
            last_city = i

    # Reconstruct path
    path = []
    mask = full_mask
    cur = last_city
    while cur != -1:
        path.append(cur)
        temp = parent[mask][cur]
        mask = mask ^ (1 << cur)
        cur = temp
    path.append(0)
    path.reverse()

    return min_cost, path


if __name__ == "__main__":
    # Example distance matrix (symmetric TSP)
    dist = [
        [0, 29,20],
        [29,9,15],
        [20,15,0]
    ]

    min_cost, path = tsp_dp(dist)
    print("Minimum cost:", min_cost)
    print("Optimal path:", path)
