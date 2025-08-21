import random


def compute_random_array(length, max_number):
    r = range(max_number)
    return [random.choice(r) for _ in range(length)]


if __name__ == '__main__':
    print(compute_random_array(96, 1000))
