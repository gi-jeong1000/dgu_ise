import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 데이터 불러오기
file_path = 'solution5.xlsx'
data = pd.read_excel(file_path)

# 필요한 칼럼 선택
live_columns = ['Solution5']
live_data = data[live_columns]

# 생존율로 변환하는 함수 정의
def survival_rate_transform(time):
    # 3600초 이하면 첫 번째 공식 사용
    return time / 60

# 데이터 변환
live_data = live_data.apply(lambda x: survival_rate_transform(x))

# 평균, 분산, 변동계수, 왜도, 첨도 계산
stats = pd.DataFrame({
    'Mean': live_data.mean(),
    'Variance': live_data.var(),
    'Coefficient of Variation': live_data.std() / live_data.mean(),
    'Skewness': live_data.skew(),  # 왜도
    'Kurtosis': live_data.kurt()  # 첨도
})

# 그래픽 패널 생성
plt.figure(figsize=(18, 6))  # 가로 길이를 줄여서 조정

# 박스 플롯 그리기
plt.subplot(131)
sns.boxplot(data=live_data)
plt.title('Box Plot of Solution5 Time Data')

# 바이올린 플롯 그리기
plt.subplot(132)
sns.violinplot(data=live_data)
plt.title('Violin Plot of Solution5 Time Data')

# KDE 플롯 그리기
plt.subplot(133)
sns.kdeplot(live_data['Solution5'], label='Solution5', fill=True)
plt.title('KDE Plot of Solution5 Time Data')
plt.legend()

plt.tight_layout()
plt.show()

# 계산된 통계 출력
print(stats)