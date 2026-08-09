from backend.algorithms import (
    binary_search,
    binary_search_count,
    insertion_sort,
    insertion_sort_count,
    linear_search,
    linear_search_count,
)


def check(case_name, result, expected):
    if result == expected:
        print(f"PASS: {case_name}")
    else:
        print(f"FAIL: {case_name} — expected {expected}, got {result}")


records = []
insertion_sort(records, "value")
check("insertion_sort empty", records, [])

records = [{"value": 7}]
insertion_sort(records, "value")
check("insertion_sort single element", records, [{"value": 7}])

records = [{"value": 1}, {"value": 3}, {"value": 5}, {"value": 7}, {"value": 9}]
check("binary_search first", binary_search(records, 1, "value"), 0)
check("binary_search middle", binary_search(records, 5, "value"), 2)
check("binary_search last", binary_search(records, 9, "value"), 4)
check("binary_search absent", binary_search(records, 6, "value"), -1)

small = [{"value": 3}, {"value": 1}, {"value": 2}]
count = insertion_sort_count(small, "value")
check("insertion_sort_count sorted result", small, [{"value": 1}, {"value": 2}, {"value": 3}])
check("insertion_sort_count positive int", type(count) == int and count > 0, True)

bcount = binary_search_count(records, 7, "value")
check(
    "binary_search_count known index",
    bcount["index"] == 3 and type(bcount["comparison_count"]) == int and bcount["comparison_count"] > 0,
    True,
)

lcount = linear_search_count(records, 100, "value")
check(
    "linear_search_count absent",
    lcount["index"] == -1 and lcount["comparison_count"] == len(records),
    True,
)
