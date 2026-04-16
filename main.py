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

def main():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    choice = input("선택: ").strip()

    if choice == "1":
        print("(모드 1은 다음 단계에서 구현합니다)")
    elif choice == "2":
        print("(모드 2는 다음 단계에서 구현합니다)")
    else:
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()

