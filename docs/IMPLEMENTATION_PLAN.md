# 구현 계획 — Mini NPU Simulator

> MISSION.md 기반으로 `main.py` + `data.json` 을 단계별로 구현하는 설계 문서입니다.

---

## 1. 파일 구성

```
npu/
├── main.py          # 메인 실행 파일 (전체 로직 포함)
├── data.json        # 5×5 / 13×13 / 25×25 필터 및 패턴 데이터
├── docs/
│   ├── MISSION.md
│   ├── README.md
│   └── IMPLEMENTATION_PLAN.md  ← 이 문서
```

`main.py` 하나에 모든 로직을 담습니다. 외부 라이브러리는 사용하지 않으며 `json`, `time` 표준 라이브러리만 사용합니다.

---

## 2. 모듈 설계 (함수 단위)

```
main.py
│
├── [데이터 구조]
│   └── Matrix              # n×n 2차원 리스트를 감싸는 클래스
│
├── [라벨 정규화]
│   └── normalize_label()   # '+' / 'x' / 'cross' → 'Cross' / 'X'
│
├── [MAC 연산]
│   └── mac()               # 이중 반복문으로 직접 구현
│
├── [점수 비교 / 판정]
│   └── judge()             # epsilon 기반 비교 → Cross / X / UNDECIDED
│
├── [성능 측정]
│   └── measure_mac()       # 10회 반복 후 평균 ms 반환
│
├── [입력 처리]
│   └── input_matrix()      # 콘솔에서 n×n 입력 + 검증 + 재입력 유도
│
├── [모드 1]
│   └── mode_manual()       # 필터 A/B + 패턴 입력 → MAC → 결과 출력
│
├── [모드 2]
│   ├── load_data_json()    # data.json 파싱 + 스키마 검증
│   └── mode_json()         # 전체 판정 + 성능 분석 + 결과 요약 출력
│
└── main()                  # 모드 선택 진입점
```

---

## 3. 데이터 구조

### 3-1. Matrix 클래스

```python
class Matrix:
    def __init__(self, data: list[list[float]]):
        self.n = len(data)
        self.data = data          # data[row][col]

    def get(self, row: int, col: int) -> float:
        return self.data[row][col]
```

- 2차원 리스트를 직접 사용해도 되지만, 클래스로 감싸면 크기 검증 로직을 한 곳에서 관리할 수 있습니다.
- 보너스 과제(1차원 배열 최적화)를 구현할 때 내부 표현만 바꾸고 인터페이스는 유지할 수 있습니다.

### 3-2. data.json 스키마

```json
{
  "filters": {
    "size_5": {
      "cross": [[...], ...],
      "x":     [[...], ...]
    },
    "size_13": { ... },
    "size_25": { ... }
  },
  "patterns": {
    "size_5_1":  { "input": [[...], ...], "expected": "+" },
    "size_5_2":  { "input": [[...], ...], "expected": "x" },
    "size_13_1": { "input": [[...], ...], "expected": "x" },
    ...
  }
}
```

- 필터 키: `cross` 또는 `x` (소문자) → 로드 시 `normalize_label()` 적용
- `expected`: `'+'`, `'x'`, `'Cross'`, `'X'` 등 → 로드 시 `normalize_label()` 적용
- 패턴 키: `size_{N}_{idx}` 형식에서 `N`을 추출해 `size_{N}` 필터를 선택

---

## 4. 핵심 알고리즘

### 4-1. 라벨 정규화

```python
def normalize_label(raw: str) -> str:
    v = raw.strip().lower()
    if v in ('+', 'cross'):
        return 'Cross'
    if v in ('x',):
        return 'X'
    raise ValueError(f"알 수 없는 라벨: {raw!r}")
```

### 4-2. MAC 연산 (외부 라이브러리 금지)

```python
EPSILON = 1e-9

def mac(pattern: Matrix, filter_: Matrix) -> float:
    total = 0.0
    n = pattern.n
    for i in range(n):
        for j in range(n):
            total += pattern.get(i, j) * filter_.get(i, j)
    return total
```

시간 복잡도: **O(N²)** — 이중 반복문이 N×N 번 실행됩니다.

### 4-3. 판정 (epsilon 기반)

```python
def judge(score_cross: float, score_x: float) -> str:
    if abs(score_cross - score_x) < EPSILON:
        return 'UNDECIDED'
    return 'Cross' if score_cross > score_x else 'X'
```

### 4-4. 성능 측정 (10회 평균)

```python
import time

def measure_mac(pattern: Matrix, filter_: Matrix, repeat: int = 10) -> float:
    """MAC 연산을 repeat 회 반복 후 평균 시간(ms)을 반환."""
    start = time.perf_counter()
    for _ in range(repeat):
        mac(pattern, filter_)
    elapsed = time.perf_counter() - start
    return (elapsed / repeat) * 1000  # ms 단위
```

- I/O 시간 제외, 연산 함수 호출 구간만 측정합니다.

---

## 5. 입력 검증 (모드 1)

```python
def input_matrix(n: int, label: str) -> Matrix:
    print(f"{label} ({n}줄 입력, 공백 구분)")
    rows = []
    while len(rows) < n:
        line = input()
        tokens = line.split()
        if len(tokens) != n:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
            rows = []   # 처음부터 재입력
            continue
        try:
            rows.append([float(t) for t in tokens])
        except ValueError:
            print(f"입력 형식 오류: 숫자만 입력하세요.")
            rows = []
    return Matrix(rows)
```

검증 항목:
- 열 수 불일치 → 안내 메시지 출력 후 전체 재입력
- 숫자 파싱 실패 → 안내 메시지 출력 후 전체 재입력

---

## 6. JSON 로드 및 스키마 검증 (모드 2)

```python
import json

def load_data_json(path: str = 'data.json') -> dict:
    with open(path, encoding='utf-8') as f:
        return json.load(f)
```

패턴 처리 시 검증 흐름:

```
패턴 키 파싱 → N 추출 → size_N 필터 존재 여부 확인
    → 필터 크기 == 패턴 크기 확인
    → 불일치 시: 케이스 FAIL 처리 + 원인 메시지 저장 (프로그램 중단 X)
```

```python
# 의사 코드
for key, case in patterns.items():
    try:
        N = int(key.split('_')[1])           # "size_5_1" → 5
        f_cross = filters[f'size_{N}']['cross']
        f_x     = filters[f'size_{N}']['x']
        # 크기 검증
        if len(case['input']) != N:
            raise ValueError("패턴 크기 불일치")
        # MAC + 판정
        ...
    except Exception as e:
        results.append({'key': key, 'verdict': 'FAIL', 'reason': str(e)})
```

---

## 7. 출력 형식

### 모드 1 출력

```
#----------------------------------------
# [3] MAC 결과
#----------------------------------------
A 점수: 1.0
B 점수: 5.0
연산 시간(평균/10회): 0.012 ms
판정: B
```

### 모드 2 출력

```
#----------------------------------------
# [2] 패턴 분석 (라벨 정규화 적용)
#----------------------------------------
--- size_5_1 ---
Cross 점수: 1.0
X 점수: 5.0
판정: X | expected: X | PASS

#----------------------------------------
# [3] 성능 분석 (평균/10회)
#----------------------------------------
크기      평균 시간(ms)   연산 횟수
------------------------------------
3×3           0.010          9
5×5           0.031          25
13×13         0.187          169
25×25         0.682          625

#----------------------------------------
# [4] 결과 요약
#----------------------------------------
총 테스트: 8개 / 통과: 7개 / 실패: 1개
실패 케이스:
- size_13_1: 동점(UNDECIDED) 처리 규칙에 따라 FAIL
```

---

## 8. 구현 순서 (단계별 작업)

| 단계 | 작업 | 완료 기준 |
|:----:|------|----------|
| 1 | `Matrix` 클래스 + `mac()` 구현 | 3×3 십자가/X 예시 점수(5, 1) 일치 |
| 2 | `normalize_label()` 구현 | `+` → `Cross`, `x` → `X` 변환 확인 |
| 3 | `judge()` + epsilon 비교 구현 | 동점 케이스 UNDECIDED 출력 확인 |
| 4 | `input_matrix()` 구현 (입력 검증) | 열 수 오류 / 파싱 오류 시 재입력 유도 확인 |
| 5 | `mode_manual()` 완성 (모드 1 전체) | 예시 입력으로 재현성 확인 |
| 6 | `data.json` 작성 | 5×5/13×13/25×25 필터 + 패턴 8개 이상 포함 |
| 7 | `load_data_json()` + `mode_json()` 구현 | PASS/FAIL 합산, 스키마 오류 케이스 FAIL 처리 확인 |
| 8 | `measure_mac()` + 성능 분석 출력 | 크기별 평균 시간 표 출력 확인 |
| 9 | `main()` + 모드 선택 흐름 완성 | 전체 실행 흐름 순서(모드1 → 모드2) 확인 |
| 10 | README 결과 리포트 작성 | FAIL 원인 분석 + O(N²) 설명 10줄 이상 |

---

## 9. 보너스 과제 계획 (선택)

### 9-1. 1차원 배열 최적화

`Matrix` 내부를 `list[list[float]]` 대신 `list[float]` (길이 N²)로 변경합니다.

```python
# 접근: data[i * n + j]  (row-major)
def get(self, row, col):
    return self.data[row * self.n + col]
```

`mac()` 함수는 동일하게 사용하고, `Matrix.data` 내부 표현만 교체합니다.  
최적화 전/후를 동일 입력으로 `measure_mac()` 비교하여 결과를 출력합니다.

### 9-2. 패턴 생성기

```python
def generate_cross(n: int) -> Matrix:
    """n×n 십자가 패턴 생성 (중앙 행/열 = 1, 나머지 = 0)"""

def generate_x(n: int) -> Matrix:
    """n×n X 패턴 생성 (대각선 = 1, 나머지 = 0)"""
```

생성된 패턴을 모드 1 기본값과 성능 분석용 입력으로 재활용합니다.

---

## 10. 주요 엣지 케이스 체크리스트

- [ ] 3×3 십자가 vs 십자가 필터 → 점수 5.0, 판정 Cross
- [ ] 3×3 X vs X 필터 → 점수 5.0, 판정 X
- [ ] 수학적 동점 케이스 → `UNDECIDED` 출력, FAIL 처리
- [ ] `data.json`에서 필터 키 `'cross'` → `normalize_label()` 적용 후 `'Cross'`
- [ ] `data.json`에서 `expected: '+'` → `normalize_label()` 적용 후 `'Cross'`
- [ ] 필터와 패턴 크기 불일치 → 프로그램 중단 없이 케이스 FAIL 처리
- [ ] 모드 1 입력에서 열 수 부족 → 안내 문구 + 재입력 유도
- [ ] 모드 1 입력에서 문자 혼입 → 안내 문구 + 재입력 유도
