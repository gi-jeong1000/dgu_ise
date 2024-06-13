import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기
file_path = 'solution2.xlsx'
data = pd.read_excel(file_path)

# 필요한 칼럼 선택
live_columns = ['Solution2']
live_data = data[live_columns]

# 생존율로 변환하는 함수 정의
def survival_rate_transform(time):
    # 3600초 이하면 첫 번째 공식 사용
    return time / 60  # 분 단위로 변환

# 데이터 변환
transformed_data = live_data.applymap(survival_rate_transform)

# 통계치 계산
stats = pd.DataFrame({
    'Mean': transformed_data.mean(),
    'Median': transformed_data.median(),
    'Variance': transformed_data.var(),
    'Coefficient of Variation': transformed_data.std() / transformed_data.mean(),
    'Skewness': transformed_data.skew(),
    'Kurtosis': transformed_data.kurt()
})

# 히스토그램 그리기
plt.figure(figsize=(10, 6))
colors = ['blue', 'green']  # 솔루션 1과 솔루션 3에 대한 색상 지정
for i, column in enumerate(live_columns):
    transformed_data[column].hist(bins=30, alpha=0.5, label=f'{column}', color=colors[i])
plt.title('Combined Histogram of Solution 1 and Solution 3')
plt.xlabel('Rescue Time (min)')
plt.ylabel('Frequency')
plt.legend()  # 범례 추가
plt.tight_layout()
plt.show()

# 통계 출력
print(stats)