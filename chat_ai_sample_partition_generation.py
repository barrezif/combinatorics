def generate_partitions(set_elements, constraints):
    partitions = []

    def backtrack(current_partition, part_index):
        if part_index == len(constraints):
            partitions.append(list(current_partition))
            return

        for element in constraints[part_index]:
            if element not in current_partition:
                current_partition.append(element)
                # Explore further
                backtrack(current_partition, part_index + 1)
                # Backtrack
                current_partition.pop()

    # Start the backtracking process
    backtrack([], 0)

    return partitions



set_elements = {1, 2, 3, 4, 5, 6}
constraints = [
    {1, 2, 3},    # First part can pick from {1, 2, 3}
    {2, 3, 4, 5},  # Second part can pick from {2, 3, 4, 5}
    {4, 5, 6}     # Third part can pick from {4, 5, 6}
]

partitions = generate_partitions(set_elements, constraints)
print(partitions)
