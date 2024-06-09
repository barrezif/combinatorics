class Foo:
    def __init__(self, name):
        self.name = name


"""
Testing whether an object gets stored as a reference or value in a python dictionary
"""
test_dic = {}
test_obj = Foo("Bar")
test_dic[1] = test_obj
test_dic[2] = test_obj

print(test_dic[1].name)
print(test_dic[2].name)

test_dic[2].name = "Bar2"
print(test_dic[2].name)
print(test_dic[1].name)

thing_sizes = [1, 2, 3, 4]


def get_iters(sizes, hand_size):
    for size_x in range(sizes[1]):
        for size_y in range(sizes[2]):
            for size_z in range(sizes[3]):
                if size_x+size_y+size_z != hand_size:
                    continue
                yield size_x, size_y, size_z


for x, y, z in get_iters(thing_sizes, 4):
    print(x, y, z)

# This ^ Outputs this:
# 0 1 3
# 0 2 2
# 1 0 3
# 1 1 2
# 1 2 1


""" We can use this as a start to dynamically determine the valid ways
one user can take from the subsets available to them.
"""


def recursive_iter(sizes, hand_size, idx, res):
    if idx >= len(sizes) and hand_size != 0:
        return []
    if idx >= len(sizes) or hand_size == 0:
        yield res
        return res
    for i in range(sizes[idx] + 1):
        results = recursive_iter(sizes, hand_size - i, idx+1, res + [i])
        if results:
            yield from results


for res in recursive_iter(thing_sizes, 4, 0, []):
    print(res)

"""This returns this:
[0, 0, 0, 4]
[0, 0, 1, 3]
[0, 0, 2, 2]
[0, 0, 3, 1]
[0, 1, 0, 3]
[0, 1, 1, 2]
[0, 1, 2, 1]
[0, 1, 3]
[0, 2, 0, 2]
[0, 2, 1, 1]
[0, 2, 2]
[1, 0, 0, 3]
[1, 0, 1, 2]
[1, 0, 2, 1]
[1, 0, 3]
[1, 1, 0, 2]
[1, 1, 1, 1]
[1, 1, 2]
[1, 2, 0, 1]
[1, 2, 1]



So for the list [1,2,3,4]
if the person has to pick 4, they can pick
0 from the first 3 and 4 from the last, 
0 from the first two, 1 from the third and 3 from the last... etc.


This will help us generate all of the combinations for however many subsets.


In our dominos case, we are only interested in the second half, where
the person takes 1 from the first, because that's the only way everyone
else's subpartitons will be able to work.

[1, 0, 0, 3]
[1, 0, 1, 2]
[1, 0, 2, 1]
[1, 0, 3]
[1, 1, 0, 2]
[1, 1, 1, 1]
[1, 1, 2]
[1, 2, 0, 1]
[1, 2, 1]

So we want to update the code above to make it nicer/cleaner, but also only return
these. Also, want to make sure they're all the same size, so adding 0 to the three of size 3.


Having this will let us work with any number of players instead of a fixed 3.
"""


print("======== 8 person game")
eight_person_game = [5, 4, 3, 2, 3, 2, 4, 3, 2, 4, 3, 2, 4, 5]
for res in recursive_iter(eight_person_game, 7, 0, []):
    print(res)

# An 8 person game would have we more subsets in an 8 person venn diagram than the array above.
# This approach either won't work with so many people, or I need to figure out a way to
# 1 . use heuristics to cut out any uneeded computations
# 2. find a new algorithm

# Running this took like 1 minute and a half...
# Since I need to know all of these combinations, I'm not sure there is a more fast way.

# Next best thing would just be to optimize whatever I'm doing.  