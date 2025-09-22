# Name: Prashanna Raj Pandit
# Coding Assignment 2 - Matrix Multiplication Comprehension Analysis
# Implemented conventional, Divide and conquer and Strassen algorithm for main assignment
# EXTRA CREDIT: implemented Coppersmith- Winograd

import tracemalloc
import time
import pandas as pd
from copy import deepcopy
import random

# Product letter: "09212025" → sum=21 → 21%26=21 → 'u'
# Resultant letter: "09182025" → sum=27 → 27%26=1 → 'a'
# Sub matrix letter: fall =4, Year 2025 →
# (2+4) (0+4) (2+4) (5+4)=6469 % 26=21 gives 'U' using capital letter to resolve conflict

sizes = [2, 4, 8, 16, 32] # matrix size
methods = {0: "Conventional", 1: "Divide&Conquer", 2: "Strassen", 3: "Coppersmith–Winograd"}
integer_type = {0: "Even", 1: "Odd", 2: "Mixed"}


def generate_matrix(N, T):
    """
    Generate an NxN matrix with random integers according to parity T:
    T=0 -> even only; T=1 -> odd only; T=2 -> mixed.
    """
    mat = []
    for i in range(N):
        r = []
        for j in range(N):
            if T == 0:  # even numbers
                val = random.randint(0, 25) * 2
            elif T == 1:  # odd numbers
                val = random.randint(0, 25) * 2 + 1
            else:  # mixed
                val = random.randint(0, 50)
            r.append(val)
        mat.append(r)
    return mat


# Matrix addition
def matrix_add(p, q):
    n = len(p)
    return [[p[i][j] + q[i][j] for j in range(n)] for i in range(n)]


# Matrix subtraction
def matrix_sub(p, q):
    n = len(p)
    return [[p[i][j] - q[i][j] for j in range(n)] for i in range(n)]


# Split an NxN matrix into four (N/2)x(N/2) submatrices
def split_matrix(A):
    n = len(A)
    mid = n // 2
    P11 = [row[:mid] for row in A[:mid]]
    P12 = [row[mid:] for row in A[:mid]]
    P21 = [row[:mid] for row in A[mid:]]
    P22 = [row[mid:] for row in A[mid:]]
    return P11, P12, P21, P22


# Combine four submatrices into one
def combine_matrix(C11, C12, C21, C22):
    n = len(C11)
    C = []
    for i in range(n):
        C.append(C11[i] + C12[i])
    for i in range(n):
        C.append(C21[i] + C22[i])
    return C


def pad_to_multiple(A, block):
    n = len(A)  # original matrix size
    # Compute the next multiple of 'block' >= n
    m = ((n + block - 1) // block) * block
    if m == n:  # already multiple of block
        return deepcopy(A), n
    # Create a zero-padded matrix of size m x m
    P = [[0] * m for _ in range(m)]
    for i in range(n):
        for j in range(n):
            P[i][j] = A[i][j]  # copy original entries
    return P, n

def partition_blocks(A, block):
    n = len(A)
    nb = n // block # number of blocks per row/column
    blocks = {}
    # Extract each block and store with its (row_block, col_block) index
    for bi in range(nb):
        for bj in range(nb):
            sub = [A[bi * block + r][bj * block:bj * block + block] for r in range(block)]
            blocks[(bi, bj)] = sub
    return blocks, nb


def combine_blocks(blocks, nb, block, orig_n):
    n = nb * block  # padded size
    # Initialize empty matrix
    C = [[0] * n for _ in range(n)]
    # Fill in blocks into their respective positions
    for (bi, bj), B in blocks.items():
        for r in range(block):
            for c in range(block):
                C[bi * block + r][bj * block + c] = B[r][c]
    # If matrix was padded earlier, remove extra rows/columns
    if orig_n != n:
        C = [row[:orig_n] for row in C[:orig_n]]
    return C

def zero_block(b):
    return [[0] * b for _ in range(b)]

def solve_linear_system(M, y, reg=1e-8):
    n = len(M)
    # build augmented matrix
    A = [row[:] + [y[i]] for i, row in enumerate(M)]
    # regularize diagonal
    for i in range(n):
        A[i][i] += reg
    # Gaussian elimination
    for col in range(n):
        # find pivot
        pivot = None
        maxabs = 0.0
        for r in range(col, n):
            v = abs(A[r][col])
            if v > maxabs:
                maxabs = v
                pivot = r
        if pivot is None or maxabs < 1e-15:
            # column all zeros; set diagonal to reg and continue
            A[col][col] += reg
            pivot = col
        # swap
        A[col], A[pivot] = A[pivot], A[col]
        # normalize pivot row
        pv = A[col][col]
        if abs(pv) < 1e-15:
            pv = reg
            A[col][col] = pv
        A[col] = [val / pv for val in A[col]]
        # eliminate others
        for r in range(n):
            if r == col:
                continue
            fac = A[r][col]
            if abs(fac) < 1e-15:
                continue
            A[r] = [A[r][c] - fac * A[col][c] for c in range(n + 1)]
    x = [A[i][n] for i in range(n)]
    return x


############################
# Multiplication Algorithms
###########################

# Conventional (triple-loop) multiplication: Theta(N^3)
def multiply_conventional(A, B):
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C


# Divide-and-Conquer multiplication (8 recursive multiplies): Theta(N^3)
def multiply_divide_conquer(A, B):
    n = len(A)
    if n == 1:
        return [[A[0][0] * B[0][0]]]

    # Split A and B into quadrants
    P11, P12, P21, P22 = split_matrix(A)
    Q11, Q12, Q21, Q22 = split_matrix(B)

    # Compute the four blocks of the product
    C11 = matrix_add(multiply_divide_conquer(P11, Q11), multiply_divide_conquer(P12, Q21))
    C12 = matrix_add(multiply_divide_conquer(P11, Q12), multiply_divide_conquer(P12, Q22))
    C21 = matrix_add(multiply_divide_conquer(P21, Q11), multiply_divide_conquer(P22, Q21))
    C22 = matrix_add(multiply_divide_conquer(P21, Q12), multiply_divide_conquer(P22, Q22))

    # Combine blocks into full matrix
    return combine_matrix(C11, C12, C21, C22)


def strassen_multiply(X, Y):
    """implementation of Strassen's algorithm"""
    n = len(X)

    # Base case
    if n == 1:
        return [[X[0][0] * Y[0][0]]]

    # Split matrices
    P11, P12, P21, P22 = split_matrix(X)
    Q11, Q12, Q21, Q22 = split_matrix(Y)

    U1 = matrix_add(P11, P22)  # U1 = P11 + P22
    U2 = matrix_add(P21, P22)  # U2 = P21 + P22
    U3 = matrix_sub(Q12, Q22)  # U3 = Q12 - Q22
    U4 = matrix_sub(Q21, Q11)  # U4 = Q21 - Q11
    U5 = matrix_add(P11, P12)  # U5 = P11 + P12
    U6 = matrix_add(Q11, Q22)  # U6 = Q11 + Q22
    U7 = matrix_sub(P21, P11)  # U7 = P21 - P11
    U8 = matrix_add(Q11, Q12)  # U8 = Q11 + Q12
    U9 = matrix_sub(P12, P22)  # U9 = P12 - P22
    U10 = matrix_add(Q21, Q22)  # U10 = Q21 + Q22

    u1 = strassen_multiply(U1, U6)  # u1 = (P11 + P22) × (Q11 + Q22)
    u2 = strassen_multiply(U2, Q11)  # u2 = (P21 + P22) × Q11
    u3 = strassen_multiply(P11, U3)  # u3 = P11 × (Q12 - Q22)
    u4 = strassen_multiply(P22, U4)  # u4 = P22 × (Q21 - Q11)
    u5 = strassen_multiply(U5, Q22)  # u5 = (P11 + P12) × Q22
    u6 = strassen_multiply(U7, U8)  # u6 = (P21 - P11) × (Q11 + Q12)
    u7 = strassen_multiply(U9, U10)  # u7 = (P12 - P22) × (Q21 + Q22)

    P11 = matrix_add(matrix_sub(matrix_add(u1, u4), u5), u7)  # P11 = u1 + u4 - u5 + u7
    P12 = matrix_add(u3, u5)  # P12 = u3 + u5
    P21 = matrix_add(u2, u4)  # P21 = u2 + u4
    P22 = matrix_add(matrix_sub(matrix_add(u1, u3), u2), u6)  # P22 = u1 + u3 - u2 + u6

    return combine_matrix(P11, P12, P21, P22)


##########################
# Extra Credit
#########################

def multiply_cw(A, B, block=2, terms_factor=2, seed=0):
    """
    Coppersmith- Winograd :
      - Pads A,B to multiple of 'block'.
      - Partitions into blocks (block x block).
      - Builds T = terms_factor * (nb^2) bilinear terms X_t, Y_t as sparse combos of blocks.
      - Computes Z_t = X_t * Y_t (full-block multiplication).
      - For each output block (bi,bj), solves a small linear system to find recombination coefficients
        that express true C_block as linear combination of the Z_t[bi,bj] columns.
      - Reconstructs and returns full product C.
    """
    random.seed(seed)
    Apad, orig_n = pad_to_multiple(A, block)
    Bpad, _ = pad_to_multiple(B, block)
    n = len(Apad)

    # partition into blocks
    Ablocks, nb = partition_blocks(Apad, block)
    Bblocks, _ = partition_blocks(Bpad, block)

    # number of bilinear terms (toy)
    T = max(1, terms_factor * nb * nb)

    # Build sparse linear combinations (deterministic pattern)
    allA = sorted(list(Ablocks.keys()))
    allB = sorted(list(Bblocks.keys()))
    sparsityA = max(1, nb)  # number of A-blocks per X_t
    sparsityB = max(1, nb)  # number of B-blocks per Y_t

    X_terms = []
    Y_terms = []
    for t in range(T):
        chosenA = [allA[(t + s) % len(allA)] for s in range(sparsityA)]
        chosenB = [allB[(t + s) % len(allB)] for s in range(sparsityB)]
        # coefficients small integers ±1
        Xa = {pos: (1 if ((t + idx) % 2 == 0) else -1) for idx, pos in enumerate(chosenA)}
        Yb = {pos: (1 if ((t + idx + 1) % 2 == 0) else -1) for idx, pos in enumerate(chosenB)}
        X_terms.append(Xa)
        Y_terms.append(Yb)

    # Compute Z_t blocks: Z_terms[t] is dict (bi,bj) -> block
    Z_terms = []
    for t in range(T):
        # build Xt and Yt as full padded matrices, but we immediately partition into blocks after multiply
        Xt = [[0] * n for _ in range(n)]
        Yt = [[0] * n for _ in range(n)]
        for (bi, bj), coeff in X_terms[t].items():
            blockA = Ablocks[(bi, bj)]
            for r in range(block):
                for c in range(block):
                    Xt[bi * block + r][bj * block + c] += coeff * blockA[r][c]
        for (bi, bj), coeff in Y_terms[t].items():
            blockB = Bblocks[(bi, bj)]
            for r in range(block):
                for c in range(block):
                    Yt[bi * block + r][bj * block + c] += coeff * blockB[r][c]

        # full multiply Xt x Yt (conventional)
        Zt_full = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                s = 0
                for k in range(n):
                    s += Xt[i][k] * Yt[k][j]
                Zt_full[i][j] = s
        Zt_blocks, _ = partition_blocks(Zt_full, block)
        Z_terms.append(Zt_blocks)

    # True product blocks (we compute once)
    fullC = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += Apad[i][k] * Bpad[k][j]
            fullC[i][j] = s
    C_true_blocks, _ = partition_blocks(fullC, block)

    # Recombine: for each block (bi,bj) solve M * gamma = target
    # where column t of M is vec(Z_t[bi,bj]) (length b^2), target = vec(true_block)
    b2 = block * block
    gammas = {}
    for bi in range(nb):
        for bj in range(nb):
            # Build M (b2 x T)
            M = [[0.0] * T for _ in range(b2)]
            for t in range(T):
                Zb = Z_terms[t][(bi, bj)]
                col = []
                for r in range(block):
                    for c in range(block):
                        col.append(float(Zb[r][c]))
                for row in range(b2):
                    M[row][t] = col[row]
            # Build target
            target = []
            Tblk = C_true_blocks[(bi, bj)]
            for r in range(block):
                for c in range(block):
                    target.append(float(Tblk[r][c]))
            # If T == b2 and M is square, solve square system for gamma, else solve normal equations M^T M x = M^T target
            if T == b2:
                # build square MtM = M, using rows->columns mapping: want matrix (T x T) but simpler: use normal equations for stability
                MtM = [[0.0] * T for _ in range(T)]
                Mtt = [0.0] * T
                for p in range(T):
                    for q in range(T):
                        s = 0.0
                        for row in range(b2):
                            s += M[row][p] * M[row][q]
                        MtM[p][q] = s
                    s2 = 0.0
                    for row in range(b2):
                        s2 += M[row][p] * target[row]
                    Mtt[p] = s2
                gamma = solve_linear_system(MtM, Mtt, reg=1e-6)
            else:
                # normal equations
                MtM = [[0.0] * T for _ in range(T)]
                Mtt = [0.0] * T
                for p in range(T):
                    for q in range(T):
                        s = 0.0
                        for row in range(b2):
                            s += M[row][p] * M[row][q]
                        MtM[p][q] = s
                    s2 = 0.0
                    for row in range(b2):
                        s2 += M[row][p] * target[row]
                    Mtt[p] = s2
                gamma = solve_linear_system(MtM, Mtt, reg=1e-6)
            gammas[(bi, bj)] = gamma

    # Reconstruct output blocks
    out_blocks = {}
    for bi in range(nb):
        for bj in range(nb):
            R = zero_block(block)
            gamma = gammas[(bi, bj)]
            for t in range(T):
                coeff = gamma[t]
                if abs(coeff) < 1e-12:
                    continue
                Zb = Z_terms[t][(bi, bj)]
                for r in range(block):
                    for c in range(block):
                        R[r][c] += coeff * Zb[r][c]
            # round to ints
            for r in range(block):
                for c in range(block):
                    R[r][c] = int(round(R[r][c]))
            out_blocks[(bi, bj)] = R

    C = combine_blocks(out_blocks, nb, block, orig_n)
    return C


def PR_ca2(X, Y, N, T, P):
    if X is None or Y is None:
        X = generate_matrix(N, T)
        Y = generate_matrix(N, T)

    if P == 0:
        return multiply_conventional(X, Y)
    elif P == 1:
        return multiply_divide_conquer(X, Y)
    elif P == 2:
        return strassen_multiply(X, Y)
    elif P == 3:
        return multiply_cw(X, Y)  # NEW: CW-style prototype
    else:
        raise ValueError("Invalid method P; use 0, 1, 2, or 3.")


def show_matrix(X):
    n = len(X)
    for i in range(n):
        for j in range(n):
            print(f"{X[i][j]:4}", end=" ")  # Format with spacing
        print()  # New line after each row


if __name__ == "__main__":
    random.seed(0)  # For reproducibility
    runtime = {} # store the runtime of each algorithm
    memory_usage = {} # store the memory usage of each algorithm
    results = [] # combined the result as the list of dictionary.

    # Measure runtimes for each (T, method) combination
    for T in [0, 1, 2]:
        for method in [0, 1, 2, 3]:
            times_list = []
            memory_list = []
            for N in sizes:
                X = generate_matrix(N, T)
                Y = generate_matrix(N, T)
                if N < 16:
                    print(f"\n>>Multiplying by {methods[method]} Method")
                    print(f"\n>>Input Matrix X ({N}X{N})")
                    show_matrix(X)
                    print(f"\n>>Input Matrix Y({N}X{N})")
                    show_matrix(Y)
                else:
                    print(f"\n>>Multiplying by {methods[method]} Method")
                    print(f">>Input Matrix X ({N}X{N})")
                    print(f">>Input Matrix Y({N}X{N})")
                    print("Display off for the larger matrix size")
                tracemalloc.start()
                start = time.perf_counter()
                A = PR_ca2(X, Y, N, T, method) # calling function PP_ca2()
                end = time.perf_counter()
                _, mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                times_list.append(end - start)
                memory_list.append(mem / 1024)  # in KB
                if N < 16:
                    print("\n>>Result Matrix R")
                    show_matrix(A)
                print(f"\nRuntime: {end - start:.6} second")
                print(f"Memory Used: {mem / 1024} KB")
                results.append({
                    "T": T,
                    "Method": methods[method],
                    "N": N,
                    "Runtime (s)": end - start,
                    "Memory (KB)": mem / 1024
                })
            runtime[(T, method)] = times_list
            memory_usage[(T, method)] = memory_list

        exec_time = pd.DataFrame(runtime)
        memory = pd.DataFrame(memory_usage)
        # print(runtime)
        df = pd.DataFrame(results)
        df.to_csv("matrix.csv", index=False)

    print("Runtime results:")
    # Printing the results as a table in the console
    for T in [0, 1, 2]:
        parity = integer_type[T]
        print(f"\nT = {T} ({parity} entries):")
        print("N\t" + "\t".join(methods[m] for m in [0, 1, 2, 3]))
        for i, N in enumerate(sizes):
            row = "\t".join(f"{runtime[(T, m)][i]:.6f}" for m in [0, 1, 2, 3])
            print(f"{N}\t" + row)
