import pandas as pd

# 데이터 불러오기
file_path = 'solution5.xlsx'
data = pd.read_excel(file_path)

# 필요한 칼럼 선택 (모든 솔루션 데이터를 포함)
live_columns = ['Solution5']
live_data = data[live_columns]
# 생존율로 변환하는 함수 정의
def survival_rate_transform(time):
    # 3600초 이하면 첫 번째 공식 사용
    return time / 60

# 데이터 변환
live_data = live_data.apply(lambda x: survival_rate_transform(x))
# 60분을 초과하는 구조 시간의 개수 계산
over_60_minutes = (live_data > 60).sum()

# 결과 출력
print("Number of cases where rescue time exceeded 60 minutes:")
print(over_60_minutes)