# from itertools import product

# def count_combinations(set1, set2, intersection):
#     # Calculate the valid combinations
#     valid_combinations = []
#     for item1 in set1:
#         for item2 in set2:
#             if (item1, item2) not in intersection and (item2, item1) not in intersection:
#                 valid_combinations.append((item1, item2))
    
#     # Print the valid combinations
#     print("Valid Combinations:")
#     for combination in valid_combinations:
#         print(combination)
    
#     # Return the count of valid combinations
#     return len(valid_combinations)


# # Example usage
# set1 = set([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
# set2 = set([8,9,10,11,12,13,14,15,16,17])
# intersection = set1 & set2

# count = count_combinations(set1, set2, intersection)
# print("Number of Combinations:", count)

from itertools import product, combinations


def count_combinations(set1, set2, intersection, num_items):
    valid_combinations = []

    def generate_combinations(set1, set2, intersection, num_items, combo1, combo2):
        if len(combo1) == num_items and len(combo2) == num_items:
            valid_combinations.append((combo1, combo2))
            return

        if len(combo1) < num_items:
            for item in set1:
                if item not in combo1 and item not in intersection:
                    generate_combinations(set1, set2, intersection, num_items, combo1 + (item,), combo2)

        if len(combo2) < num_items:
            for item in set2:
                if item not in combo2 and item not in intersection:
                    generate_combinations(set1, set2, intersection, num_items, combo1, combo2 + (item,))

    generate_combinations(set1, set2, intersection, num_items, (), ())

    # Print the valid combinations
    print("Valid Combinations:")
    for combination in valid_combinations:
        print(combination)

    # Return the count of valid combinations
    return len(valid_combinations)


# Example usage
set1 = set([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
set2 = set([8,9,10,11,12,13,14,15,16,17])
intersection = set1 & set2
num_items = 5

count = count_combinations(set1, set2, intersection, num_items)
print("Number of Combinations:", count)