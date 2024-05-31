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


