import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from shapely.geometry import Point
import csv

# 설정
coverage_radius = 10  # 커버리지 반경 (km)
max_safety_value = 10  # 중심에서의 최대 안전 수치


# CSV 파일에서 좌표 읽기
def read_coordinates_from_csv(file_path):
    coordinates = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 첫 번째 줄은 헤더이므로 건너뜁니다
        for row in reader:
            latitude = float(row[1])
            longitude = float(row[2])
            coordinates.append((latitude, longitude))
    return np.array(coordinates)


# 안전 수치를 계산하는 함수
def calculate_safety(installed_locations, coverage_radius, max_safety_value):
    safety_dict = {}
    radius = coverage_radius / 111  # 1도는 약 111km

    for base in installed_locations:
        base_x, base_y = base
        for dx in range(-coverage_radius, coverage_radius + 1):
            for dy in range(-coverage_radius, coverage_radius + 1):
                x = base_x + dx / 111
                y = base_y + dy / 111
                dist = np.sqrt(dx ** 2 + dy ** 2)
                if dist <= coverage_radius:
                    safety_value = max(0, max_safety_value * (1 - dist / coverage_radius))
                    if (x, y) in safety_dict:
                        safety_dict[(x, y)] = max(safety_dict[(x, y)], safety_value)
                    else:
                        safety_dict[(x, y)] = safety_value
    return safety_dict


# 시각화 함수
def visualize_genes_with_coverage(candidate_locations, coverage_radius, max_safety_value):
    safety_dict = calculate_safety(candidate_locations, coverage_radius, max_safety_value)

    # GeoDataFrame 생성
    gdf = gpd.GeoDataFrame(geometry=[Point(xy[1], xy[0]) for xy in candidate_locations])
    gdf_safety = gpd.GeoDataFrame(
        geometry=[Point(x, y) for (x, y) in safety_dict.keys()],
        data={'safety_value': list(safety_dict.values())}
    )

    # 좌표계 설정 (WGS 84)
    gdf.set_crs(epsg=4326, inplace=True)
    gdf_safety.set_crs(epsg=4326, inplace=True)

    # 지도 설정
    fig, ax = plt.subplots(figsize=(10, 10))

    # GeoDataFrame 플롯
    gdf.plot(ax=ax, color='red', label='Base Candidates', markersize=5)

    # 지도 배경 추가
    ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik)

    # 인계점 커버리지 원 추가 및 안전 수치 시각화
    for (x, y), safety_value in safety_dict.items():
        circle = plt.Circle((x, y), coverage_radius / 111, color='blue', alpha=0.2 * (safety_value / max_safety_value))
        ax.add_patch(circle)

    # 플롯 설정
    ax.set_xlim([127, 130])  # 경남 지역의 경도 범위
    ax.set_ylim([34, 36])  # 경남 지역의 위도 범위
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Helicopter Handover Points with Coverage Area')
    plt.axis('equal')
    plt.show()


# CSV 파일 경로 설정
file_path = 'top_solution_1.csv'

# CSV 파일에서 좌표 읽기
candidate_locations = read_coordinates_from_csv(file_path)

# 시각화
visualize_genes_with_coverage(candidate_locations, coverage_radius, max_safety_value)