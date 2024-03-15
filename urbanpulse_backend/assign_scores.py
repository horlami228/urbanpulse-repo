# Function to assign scores based on distance ranges
def assign_score(distance, ranges):
    for range_ in ranges:
        if distance <= range_[0]:
            return range_[1]
    return 0
