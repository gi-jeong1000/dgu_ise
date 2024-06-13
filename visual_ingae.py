import folium
from folium.plugins import MarkerCluster
from folium import Circle

# 주어진 데이터프레임 예시로 사용
# df는 주어진 데이터프레임이라 가정합니다
# df에 위도(`Latitude`)와 경도(`Longitude`) 열이 있다고 가정합니다

# NaN값이 포함된 행을 제외한 데이터프레임 생성
# df_without_nan = map.dropna(subset=['Latitude', 'Longitude'])

# 지도의 중심 설정
map_center = [37,127]

# 지도 생성
m = folium.Map(location=map_center, zoom_start=12)

# 데이터프레임 순회하며 CircleMarker로 좌표 추가
# for index, row in df_without_nan.iterrows():
#     folium.CircleMarker(
#         location=[row['Latitude'], row['Longitude']],
#         radius=3,  # 작은 원의 반지름 설정
#         color='blue',  # 원의 테두리 색상
#         fill=True,
#         fill_color='blue',  # 원의 내부 색상
#         fill_opacity=0.7,  # 원의 내부 색상의 투명도
#     ).add_to(m)

hospital_coordinates = [
    (35.15152359361237,128.1057325713286),
    (35.521733941582276,129.42878028192865),
    (35.10084989386397,129.01850209166477 )
]

# 병원 좌표를 빨간색으로 표시
for coord in hospital_coordinates:
    folium.Marker(
        location=coord,
        icon=folium.Icon(color='red', icon='hospital')
    ).add_to(m)

# # 각 병원을 중심으로 70km 반경의 원 그리기
for coord in hospital_coordinates:
    Circle(
        location=coord,
        radius=80000,  # 70km를 미터로 변환하여 입력
        color='red',
        fill=False
    ).add_to(m)
# 지도를 HTML 파일로 저장하거나 화면에 출력
m.save('map_with_circle.html')
# m
# 화면에 출력