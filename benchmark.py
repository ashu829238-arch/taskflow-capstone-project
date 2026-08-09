import random

from backend.algorithms import (
    binary_search_count,
    insertion_sort_count,
    linear_search_count,
)


def make_records(size):
    priorities = ["low", "medium", "high"]
    records = [
        {
            "title": f"Task {i:05d}",
            "priority": priorities[i % 3],
            "due_date": None,
        }
        for i in range(size)
    ]
    random.Random(size).shuffle(records)
    return records


def run():
    sizes = [10, 500, 3000]

    print("Algorithm benchmark: comparison counts")
    for size in sizes:
        records = make_records(size)

        sort_records = list(records)
        sort_comparisons = insertion_sort_count(sort_records, "title")

        target = f"Task {size - 1:05d}"
        binary_result = binary_search_count(sort_records, target, "title")
        linear_result = linear_search_count(records, target, "title")

        print(
            f"size={size}: "
            f"insertion_sort_count={sort_comparisons}, "
            f"binary_search_count={binary_result['comparison_count']}, "
            f"linear_search_count={linear_result['comparison_count']}"
        )


if __name__ == "__main__":
    run()
