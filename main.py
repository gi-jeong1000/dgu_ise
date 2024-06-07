import random
from deap import base, creator, tools
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from rtree import index
import csv
import matplotlib.pyplot as plt
import numpy as np

def extract_coordinates_from_csv(file_path):
    coordinates = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # 첫 번째 줄은 헤더이므로 건너뜁니다
        for row in reader:
            latitude_str = row[1]
            longitude_str = row[2]
            if latitude_str == '' or longitude_str == '':
                continue
            latitude = float(latitude_str)
            longitude = float(longitude_str)
            coordinates.append((latitude, longitude))
    return coordinates

# CSV 파일 경로 설정
file_path = '10km_제외_위도경도.csv'

# 후보지 좌표 리스트 (예시)
candidate_locations = extract_coordinates_from_csv(file_path)
print(candidate_locations)
print(len(candidate_locations))

# 예산 설정 및 인계점 개당 설치 비용
budget = 4400000000  # 총 예산
installation_cost_per_point = 10  # 인계점 하나 당 설치 비용

# 유전자 인코딩: 인계점 설치 여부를 이진수로 표현
def encode_genes():
    while True:
        genes = [0] * len(candidate_locations)
        num_points = budget // installation_cost_per_point
        selected_points = random.sample(range(len(candidate_locations)), num_points)
        for point in selected_points:
            genes[point] = 1
        if is_within_distance_constraint(genes):
            return genes

# 목적함수: 커버 면적 최대화
def objective_function(genes):
    # 인계점 설치된 좌표 추출
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    # 커버 면적 계산 (중복 제외)
    covered_area = calculate_covered_area(installed_locations)

    # 목적함수 값 계산 (최대화할 값)
    return covered_area,

# 커버 면적 계산 함수 (중복 제외)
def calculate_covered_area(installed_locations, radius=10):
    # 실제 위도 경도를 고려하여 면적 변환
    radius = radius / 111  # 1도는 약 111km
    # R-트리 인덱스 생성
    idx = index.Index()

    # 각 인계점에 대한 원을 생성하고 R-트리에 추가
    circles = []
    for i, (x, y) in enumerate(installed_locations):
        circle = Point(x, y).buffer(radius)
        circles.append(circle)
        idx.insert(i, circle.bounds)

    # 겹치는 원들을 찾아내고 하나의 면적으로 합침
    merged_circles = unary_union(circles)

    # 커버된 총 면적 계산
    total_covered_area = merged_circles.area

    return total_covered_area * 111 * 111  # 위도 좌표 0.0001 당 약 11m

# 예산 제약 조건을 확인하는 함수
def is_within_budget(genes):
    num_installations = sum(genes)
    total_cost = num_installations * installation_cost_per_point
    return total_cost <= budget

# 거리 제약 조건을 확인하는 함수
def is_within_distance_constraint(genes, min_distance=10):
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]
    for i, loc1 in enumerate(installed_locations):
        for j, loc2 in enumerate(installed_locations):
            if i != j:
                distance = np.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2) * 111
                if distance < min_distance:
                    return False
    return True

# DEAP 설정
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, encode_genes)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", objective_function)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# 유전 알고리즘 실행
def run_genetic_algorithm():
    population = toolbox.population(n=100)

    for generation in range(10):
        # 평가, 선택, 교차, 변이 등의 과정 수행
        fitnesses = map(toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        offspring = toolbox.select(population, len(population))
        offspring = list(offspring)

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.8:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < 0.2:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # 예산 제약 조건 및 거리 제약 조건을 만족하지 않는 개체를 수정
        for ind in offspring:
            while not (is_within_budget(ind) and is_within_distance_constraint(ind)):
                ind[random.choice([i for i, gene in enumerate(ind) if gene == 1])] = 0

        population[:] = offspring

        best_solution = max(population, key=lambda ind: ind.fitness.values)
        print(f"Generation {generation}: Best Solution = {best_solution.fitness.values}")
    return population

# 유전자 시각화 함수
def visualize_genes(genes, candidate_locations):
    # 인계점 설치된 좌표 추출
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    # 모든 좌표를 플롯
    for loc in candidate_locations:
        plt.plot(loc[1], loc[0], 'ro', markersize=2)

    # 인계점 설치된 좌표를 다른 색으로 플롯
    for loc in installed_locations:
        plt.plot(loc[1], loc[0], 'bo', markersize=5)

    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title('Helicopter Handover Points Visualization')
    plt.show()

def visualize_genes_with_coverage(genes, candidate_locations, radius=5):
    # 인계점 설치된 좌표 추출
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    # 모든 인계점에 대한 원을 그리고 색칠
    fig, ax = plt.subplots()
    for loc in installed_locations:
        circle = plt.Circle((loc[1], loc[0]), radius / 111, color='blue', alpha=0.5)
        ax.add_patch(circle)

    # 인계점 설치된 좌표를 플롯
    for loc in installed_locations:
        ax.plot(loc[1], loc[0], 'bo', markersize=5)

    # 플롯 설정
    ax.set_xlabel('Latitude')
    ax.set_ylabel('Longitude')
    ax.set_title('Helicopter Handover Points with Coverage Area')
    plt.axis('equal')
    plt.show()

# 상위 5개 대안 선택 및 시각화
def select_and_visualize_top_solutions(population, candidate_locations, num_solutions=5):
    # 평가된 유전자들을 목적함수 값에 따라 정렬
    sorted_population = sorted(population, key=lambda ind: ind.fitness.values, reverse=True)

    # 상위 5개 대안 추출 및 시각화
    for i in range(num_solutions):
        num_installations = sum(sorted_population[i])
        print(f"Alternative {i + 1}: Fitness = {sorted_population[i].fitness.values}, Installations = {num_installations}")
        visualize_genes(sorted_population[i], candidate_locations)

def save_top_solutions_to_csv(population, candidate_locations, num_solutions=5):
    # 평가된 유전자들을 목적함수 값에 따라 정렬
    sorted_population = sorted(population, key=lambda ind: ind.fitness.values, reverse=True)

    # 상위 5개 대안의 좌표 추출 및 개별 파일로 저장
    for i in range(num_solutions):
        solution = sorted_population[i]
        num_installations = sum(solution)
        coordinates = [candidate_locations[idx] for idx, gene in enumerate(solution) if gene == 1]
        output_filename = f"top_solution_{i + 1}.csv"
        with open(output_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Latitude', 'Longitude'])
            for coord in coordinates:
                writer.writerow(coord)
            writer.writerow(['Total Installations', num_installations])

# 유전 알고리즘 실행 후 상위 5개 대안 선택 및 시각화
population = run_genetic_algorithm()
select_and_visualize_top_solutions(population, candidate_locations)
save_top_solutions_to_csv(population, candidate_locations, num_solutions=5)