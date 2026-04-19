import time

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
        print("(모드 2는 다음 단계에서 구현합니다)")
    else:
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()

