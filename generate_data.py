import json

def make_cross(n):
    mid = n // 2
    grid = [[0] * n for _ in range(n)]
    for i in range(n):
        grid[mid][i] = 1
        grid[i][n-1-i] = 1
    return grid

def make_x(n):
    grid = [[0] * n for _ in range(n)]
    for i in range(n):
        grid[i][i] = 1
        grid[i][n - 1 -i] = 1
    return grid

data = {
    "filters": {
        "size_3":  {"cross": make_cross(3), "x": make_x(3)},
        "size_5":  {"cross": make_cross(5),  "x": make_x(5)},
        "size_13": {"cross": make_cross(13), "x": make_x(13)},
        "size_25": {"cross": make_cross(25), "x": make_x(25)}
    },
    "patterns": {
        "size_3_1":  {"input": make_cross(3),  "expected": "+"},
        "size_3_2":  {"input": make_x(3),      "expected": "x"},
        "size_5_1":  {"input": make_cross(5),  "expected": "+"},
        "size_5_2":  {"input": make_x(5),      "expected": "x"},
        "size_13_1": {"input": make_cross(13), "expected": "+"},
        "size_13_2": {"input": make_x(13),     "expected": "x"},
        "size_13_3": {"input": make_cross(13), "expected": "Cross"},
        "size_25_1": {"input": make_cross(25), "expected": "+"},
        "size_25_2": {"input": make_x(25),     "expected": "x"},
        "size_25_3": {"input": make_x(25),     "expected": "X"}
    }
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=4)

print("data.json 생성 완료")