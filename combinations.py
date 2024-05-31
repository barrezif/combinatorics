from itertools import combinations, product
import math

S1 = set([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
S2 = set([8,9,10,11,12,13,14,15,16,17])
H1S = 5
H2S = 5

def calculate_number_of_combinations_with_no_overlap(s1, s2, h1_size, h2_size):
    overlap = s1 & s2
    s1_size = len(s1)
    s2_size = len(s2)
    return count_non_overlapping_combinations(s1_size, s2_size, h1_size, h2_size, len(overlap))

def count_non_overlapping_combinations_3hands(size_s1, size_s2, size_s3, size_h1, size_h2, size_h3,
                                             size_intersection_12, size_intersection_13, size_intersection_23,
                                             size_intersection_123):
    non_intersect_s1 = size_s1 - size_intersection_12 - size_intersection_13 + size_intersection_123
    non_intersect_s2 = size_s2 - size_intersection_12 - size_intersection_23 + size_intersection_123
    non_intersect_s3 = size_s3 - size_intersection_13 - size_intersection_23 + size_intersection_123

    total_count = 0

    for i in range(size_intersection_12 + 1):
        for j in range(size_intersection_13 + 1):
            for k in range(size_intersection_23 + 1):
                remaining_h1 = size_h1 - i - j
                remaining_h2 = size_h2 - i - k
                remaining_h3 = size_h3 - j - k

                if remaining_h1 > non_intersect_s1 or remaining_h2 > non_intersect_s2 or remaining_h3 > non_intersect_s3:
                    continue

                if remaining_h1 < 0 or remaining_h2 < 0 or remaining_h3 < 0:
                    continue

                combinations_h1 = math.comb(size_intersection_12, i) * math.comb(size_intersection_13, j) * math.comb(non_intersect_s1, remaining_h1)
                combinations_h2 = math.comb(size_intersection_12, i) * math.comb(size_intersection_23, k) * math.comb(non_intersect_s2, remaining_h2)
                combinations_h3 = math.comb(size_intersection_13, j) * math.comb(size_intersection_23, k) * math.comb(non_intersect_s3, remaining_h3)

                total_count += combinations_h1 * combinations_h2 * combinations_h3

    return total_count

def count_non_overlapping_combinations(size_s1, size_s2, size_h1, size_h2, size_intersection):
    non_intersect_s1 = size_s1 - size_intersection
    total_count = 0

    for i in range(min(size_h1, size_intersection) + 1):
        remaining_h1 = size_h1 - i
        available_h2 = size_s2 - i

        if remaining_h1 > non_intersect_s1 or available_h2 < size_h2:
            continue

        combinations_h1 = math.comb(size_intersection, i)
        combinations_non_intersect_s1 = math.comb(non_intersect_s1, remaining_h1)
        combinations_h2 = math.comb(available_h2, size_h2)

        total_count += combinations_h1 * combinations_non_intersect_s1 * combinations_h2

    return total_count


def hardcoded_all_combinations(S1, S2, h1_size, h2_size):
    
    H1 = combinations(S1, h1_size)
    H2 = combinations(S2, h2_size)
    hand_combinations = product(H1, H2)

    all_valid_combinations = set()
    total_combination_size = 0
    lhs = rhs = 0
    second = 0
    for h1, h2 in hand_combinations:
        total_combination_size += 1
        curr_combination = frozenset(h1) | frozenset(h2)
        if len(curr_combination) != h1_size + h2_size:
            continue
        frozen1 = frozenset([(i, 1) for i in h1])
        frozen2 = frozenset([(i, 2) for i in h2])
        curr_combination = frozen1 | frozen2
        second += 1
        if curr_combination not in all_valid_combinations:
            all_valid_combinations.add(curr_combination)
            lhs += (((8,1) in frozen1) + 0)
            rhs +=  (((8,2) in frozen2) + 0)

    print("Number of valid combinations: ",
        len(all_valid_combinations), "/",
        total_combination_size)
    print(f'{lhs}/{len(all_valid_combinations)}')
    print(f'{rhs}/{len(all_valid_combinations)}')
    print(f'{len(all_valid_combinations) - (lhs + rhs)}/{len(all_valid_combinations)} ')



print("RESULT - ", calculate_number_of_combinations_with_no_overlap(S1, S2, H1S, H2S))
hardcoded_all_combinations(S1, S2, H1S, H2S)