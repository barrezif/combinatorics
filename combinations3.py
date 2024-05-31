from itertools import combinations, product
from enum import Enum
import math

# S1 = set([1,2,3,4,5,11,12,13,14])
# S2 = set([2,3,4,5,6,7,8,9,10])
# S3 = set([9,10,11,12,13,14,15])

# S1 = set([1,2,3,4,5,6,7,8,9,10,12,13])
# S2 = set([3,5,6,7,9,10,11,13,14])
# S3 = set([4,5,6,7,8,9,10,12,13,14,15])

# S1 = set([1,2,3,5,6,7,8,9,10,11,13,14])
# S2 = set([3,4,5,6,7,9,10,11,12,13,14,15])
# S3 = set([5,6,7,8,9,10,11,12,13,14,15,16,17,18])

# S1 = set([1,3,4,5,7,8,11,12,15])
# S2 = set([1,2,3,4,5,6,7,8,9,11,12,13,15])
# S3 = set([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])

# S1 = set([1,2,3,4,5,6,7,8,9,10,11,12])
# S2 = set([1,3,4,5,7,8,10])
# S3 = set([7,8,9,10,11,12,13,14,15])

# S1 = set([2,3,4,5,6,7])
# S2 = set([3,4,1,5,6,7,8])
# S3 = set([5,6,7,8,9])

# S1 = set([i for i in range(1, 20)])
# S2 = set([i for i in range(1, 21)])
# S3 = set([i for i in range(1, 21)])

S1 = set([i for i in range(1, 8)])
S2 = set([i for i in range(1, 8)])
S3 = set([i for i in range(1, 5)])

H1S = 3
H2S = 2
H3S = 2


class Section(Enum):
    _1 = 1
    _2 = 2
    _3 = 3
    _12 = 4
    _13 = 5
    _23 = 6
    _123 = 7


class Hand:
    def __init__(self, valid_sections):
        self.valid_sections = valid_sections

Hand1 = Hand([Section._1, Section._12, Section._13, Section._123])
Hand2 = Hand([Section._2, Section._12, Section._23, Section._123])
Hand3 = Hand([Section._3, Section._13, Section._23, Section._123])

class Section2:
    def __init__(self, section, size):
        self.section = section
        self.size = size

class SubCombination:
    def __init__(self, choices, total_combinations):
        self.choices = choices # { Hand : defaultdict{ Sections : Int }} marking how many items from each section each hand has
        self.total_combinations = total_combinations

class Combination:
    def __init__(self, subcombinations, total):
        self.subcominations = subcombinations
        self.total = total


    def get_probability(hand, owns):
        pass
        # iterate through all subchoices collecting the choices for the chosen hand
        # (section needs to know size so that we divide correctly to get the right probability for what getting an individual item would be)
        # collect the section the items belong to 


all_combinations = {}

def calculate_number_of_combinations_with_no_overlap(s1, s2, s3, h1_size, h2_size, h3_size):
    overlap_12 = s1 & s2
    overlap_13 = s1 & s3
    overlap_23 = s2 & s3
    overlap_123 = s1 & s2 & s3

    s1_size = len(s1)
    s2_size = len(s2)
    s3_size = len(s3)

    return count_non_overlapping_combinations_3hands2(s1_size, s2_size, s3_size, h1_size, h2_size, h3_size,
                                              len(overlap_12), len(overlap_13), len(overlap_23), len(overlap_123))

def calculate_number_of_combinations_with_no_overlap2(s1, s2, s3, h1_size, h2_size, h3_size):
    overlap_12 = s1 & s2
    overlap_13 = s1 & s3
    overlap_23 = s2 & s3
    overlap_123 = s1 & s2 & s3

    print(f'{overlap_12=} {overlap_13=} {overlap_23=} {overlap_123=}')
    s1_size = len(s1)
    s2_size = len(s2)
    s3_size = len(s3)

    return count_non_overlapping_combinations_3hands2(s1_size-1, s2_size-1, s3_size-1, h1_size -1, h2_size, h3_size,
                                              len(overlap_12)-1, len(overlap_13)-1, len(overlap_23)-1, len(overlap_123)-1)

def calculate_number_of_combinations_with_no_overlap3(s1, s2, s3, h1_size, h2_size, h3_size):
    overlap_12 = s1 & s2
    overlap_13 = s1 & s3
    overlap_23 = s2 & s3
    overlap_123 = s1 & s2 & s3

    s1_size = len(s1)
    s2_size = len(s2)
    s3_size = len(s3)

    return count_non_overlapping_combinations_3hands2(s1_size-1, s2_size-1, s3_size-1, h1_size, h2_size-1, h3_size,
                                              len(overlap_12)-1, len(overlap_13)-1, len(overlap_23)-1, len(overlap_123)-1)

def calculate_number_of_combinations_with_no_overlap4(s1, s2, s3, h1_size, h2_size, h3_size):
    overlap_12 = s1 & s2
    overlap_13 = s1 & s3
    overlap_23 = s2 & s3
    overlap_123 = s1 & s2 & s3

    s1_size = len(s1)
    s2_size = len(s2)
    s3_size = len(s3)

    return count_non_overlapping_combinations_3hands2(s1_size-1, s2_size-1, s3_size-1, h1_size, h2_size, h3_size-1,
                                              len(overlap_12)-1, len(overlap_13)-1, len(overlap_23)-1, len(overlap_123)-1)


def count_non_overlapping_combinations_3hands2(size_s1, size_s2, size_s3, size_h1, size_h2, size_h3,
                                             intersection_12, intersection_13, intersection_23,
                                             intersection_123):

    print("After picking -------------")
    non_intersect_s1 = size_s1 - intersection_12 - intersection_13 + intersection_123
    non_intersect_s2 = size_s2 - intersection_12 - intersection_23 + intersection_123
    non_intersect_s3 = size_s3 - intersection_13 - intersection_23 + intersection_123
    strict_intersect_12 = intersection_12 - intersection_123
    strict_intersect_13 = intersection_13 - intersection_123
    strict_intersect_23 = intersection_23 - intersection_123
    print(f'{strict_intersect_12=} {strict_intersect_13=} {strict_intersect_23=} {intersection_123=} {non_intersect_s3=}')
    total_count = 0

    for h1_i_12 in range(strict_intersect_12 + 1):
        for h1_i_13 in range(strict_intersect_13 + 1):
            for h1_i_123 in range(intersection_123 + 1):
                remaining_h1 = size_h1 - h1_i_12 - h1_i_13 - h1_i_123
                if remaining_h1 < 0 or remaining_h1 > non_intersect_s1: # can cut the loops down by breaking when remaining < 0 and continuing on other condition
                    continue
                for h2_j_12 in range(strict_intersect_12 - h1_i_12 + 1):
                    for h2_j_23 in range(strict_intersect_23 + 1):
                        for h2_j_123 in range(intersection_123 - h1_i_123 + 1):
                            remaining_h2 = size_h2 - h2_j_12 - h2_j_23 - h2_j_123
                            if remaining_h2 < 0 or remaining_h2 > non_intersect_s2:
                                continue

                            if size_h3 > size_s3 - h2_j_23 - h1_i_13 - h1_i_123 - h2_j_123:
                                continue

                            combinations_h1 = max(math.comb(strict_intersect_12, h1_i_12), 1) * max(math.comb(strict_intersect_13, h1_i_13), 1) * max(math.comb(intersection_123, h1_i_123), 1) * max(math.comb(non_intersect_s1, remaining_h1), 1)
                            combinations_h2 = max(math.comb(strict_intersect_12 - h1_i_12, h2_j_12), 1) * max(math.comb(strict_intersect_23, h2_j_23), 1) * max(math.comb(intersection_123 - h1_i_123, h2_j_123), 1) * max(math.comb(non_intersect_s2, remaining_h2), 1)
                            combinations_h3 = max(math.comb(size_s3 - h2_j_23 - h1_i_13 - h1_i_123 - h2_j_123, size_h3), 1)
                            count = combinations_h1 * combinations_h2 * combinations_h3
                            h3_k_13 = strict_intersect_13 - h1_i_13
                            h3_k_23 = strict_intersect_23 - h2_j_23
                            h3_k_123 = intersection_123 - h2_j_123 - h1_i_123
                            remaining_h3 = size_h3 - h3_k_13 - h3_k_23 - h3_k_123
                            if debug:
                                print(f'1/2-{h1_i_12} 1/3-{h1_i_13} 1/2/3-{h1_i_123}, 1-{remaining_h1}')
                                print(f'1/2-{h2_j_12} 2/3-{h2_j_23} 1/2/3-{h2_j_123} 2-{remaining_h2}')
                                print(f'1/3-{h3_k_13} 2/3-{h3_k_23} 1/2/3-{h3_k_123} 3-{remaining_h3}')
                                print(count)
                                print("==============")
                            total_count += count
    return total_count

debug = True
all_possible_combinations = calculate_number_of_combinations_with_no_overlap(S1, S2, S3, H1S, H2S, H3S)
debug = False
h1_has_from_s123 = calculate_number_of_combinations_with_no_overlap2(S1, S2, S3, H1S, H2S, H3S)
h2_has_from_s123 = calculate_number_of_combinations_with_no_overlap3(S1, S2, S3, H1S, H2S, H3S)
h3_has_from_s123 = calculate_number_of_combinations_with_no_overlap4(S1, S2, S3, H1S, H2S, H3S)
print("All Possible combinations - ", all_possible_combinations)
print("Combinations where H1 has one - ", h1_has_from_s123)
print("Combinations where H2 it instead - ", h2_has_from_s123)
print("Combinations where H3 it instead - ", h3_has_from_s123)
print("unnaccounted for - ", all_possible_combinations - (h1_has_from_s123 + h2_has_from_s123 + h3_has_from_s123))


"""
Given a player:
    * Show compositions by likelyhood (* two from here, 1 from here, 0 from here 75%)
    * Show the probability of them having a particular number from most likely to least likely
"""




"""
Given a player and a domino, returns the new state of the board

Can optimize it even more by making it only calculate the dominoes that are in the portion of the venn diagram
where it overlaps with others

Don't even need to calculate anything!

Literally, everything starts in the middle, and when a player skips, those things move out to an outer group, until they fall to the isolated group


123 - (if 3 doesn't have it) -> 12 - (if 1 doesn't have it) -> 2

So if person skips on 4, we get all of the dominoes that have 4,
for all of them, we move them to an outer level

so to make it quick, we can map out all dominoes onto a map where the key is 0-6

We'll need to delete twice if we remove once, we can't forget.q

"""








