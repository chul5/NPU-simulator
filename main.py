import time
import json

class Matrix:
    def __init__(self, data):
        self.n = len(data)
        self.data = data

    def get(self, row, col):
        return self.data[row][col]

def mac(pattern, filter_):
    total = 0.0
    n = pattern.n
    for i in range(n):
        for j in range(n):
            total += pattern.get(i, j) * filter_.get(i,j)
    return total

EPSILON = 1e-9

def normalize_label(raw):
    v = raw.strip().lower()
    if v in ('+', 'cross'):
        return 'Cross'
    if v == 'x':
        return 'X'
    raise ValueError(f"알 수 없는 라벨: {raw!r}")

def judge(score_cross, score_x):
    if abs(score_cross - score_x) < EPSILON:
        return 'UNDECIDED'
    if score_cross > score_x:
        return 'Cross'
    return 'X'

def input_matrix(n, label):
    print(f"{label} ({n}줄 입력, 공백 구분)")

    rows = []
    while len(rows) < n:
        line = input()
        tokens = line.split()
        if len(tokens) != n:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하시오")
            rows = []
            continue
        try:
            rows.append([float(t) for t in tokens])
        except ValueError:
            print(f"입력 형식 오류: 숫자만 입력하시오")
            rows =[]
    return Matrix(rows)

def measure_mac(pattern, filter_, repeat=10):
    start = time.perf_counter()
    for _ in range(repeat):
        mac(pattern, filter_)
    elapsed = time.perf_counter() - start
    return (elapsed / repeat) * 1000

def mode_manual():
    n = 3
    print()
    filter_a = input_matrix(n, "필터 A")
    print()
    filter_b = input_matrix(n, "필터 B")
    print()
    pattern = input_matrix(n, "패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms  = measure_mac(pattern, filter_a)

    print()
    print("#----------------------------------------")
    print("# MAC 결과")
    print("#----------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_ms:.3f} ms")

    if abs(score_a - score_b) < EPSILON:
        print("판정: UNDECIDED")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")

def load_data_json(path="data.json"):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    filters = {}
    for size_key, filter_pair in raw["filters"].items():
        n = int(size_key.split("_")[1])
        filters[size_key] = {
            normalize_label(k): Matrix(v)
            for k, v in filter_pair.items()
        }

    patterns = {}
    for pat_key, case in raw["patterns"].items():
        n = int(pat_key.split("_")[1])
        patterns[pat_key] = {
            "input":    Matrix(case["input"]),
            "expected": normalize_label(case["expected"]),
            "size_key": f"size_{n}"
        }

    return filters, patterns

def mode_json():
    filters, patterns = load_data_json()

    print()
    print("#----------------------------------------")
    print("# 패턴 분석 (라벨 정규화 적용)")
    print("#----------------------------------------")

    results = []
    for pat_key, case in patterns.items():
        size_key = case["size_key"]
        f_cross  = filters[size_key]["Cross"]
        f_x      = filters[size_key]["X"]

        score_cross = mac(case["input"], f_cross)
        score_x     = mac(case["input"], f_x)
        verdict     = judge(score_cross, score_x)
        expected    = case["expected"]
        outcome     = "PASS" if verdict == expected else "FAIL"

        print(f"--- {pat_key} ---")
        print(f"Cross 점수: {score_cross}  |  X 점수: {score_x}")
        print(f"판정: {verdict}  |  expected: {expected}  |  {outcome}")
        print()

        results.append(outcome)

    total  = len(results)
    passed = results.count("PASS")
    failed = results.count("FAIL")

    print("#----------------------------------------")
    print("# 결과 요약")
    print("#----------------------------------------")
    print("# 성능 분석 (평균/10회)")
    print("#----------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':>14} {'연산 횟수':>10}")
    print("-" * 40)
    for n in [3, 5, 13, 25]:
        sample = filters[f"size_{n}"]["Cross"]
        avg_ms = measure_mac(sample, sample)
        ops    = n * n
        print(f"{str(n)+'×'+str(n):<10} {avg_ms:>14.3f} {ops:>10}")
    print()
    print("#----------------------------------------")
    print(f"총 테스트: {total}개  /  통과: {passed}개  /  실패: {failed}개")

def main():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    choice = input("선택: ").strip()

    if choice == "1":
        mode_manual()
    elif choice == "2":
        mode_json()
    else:
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()

