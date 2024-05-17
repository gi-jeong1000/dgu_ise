import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일로부터 데이터 읽기
data = pd.read_csv('zzz.csv')  # 'your_coordinates.csv'는 당신이 가진 CSV 파일의 경로입니다.

# 시각화
plt.scatter(data['Longitude'], data['Latitude'], color='blue', s=10)  # 경도와 위도에 따른 산점도 생성
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('위도 경도 좌표 시각화')
plt.grid(True)  # 그리드 추가 (선택 사항)
plt.show()
