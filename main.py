import random
from deap import base, creator, tools
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from rtree import index
import csv
import matplotlib.pyplot as plt

def extract_coordinates_from_csv(file_path):
    coordinates = []
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        next(reader)  # 첫 번째 줄은 헤더이므로 건너뜁니다
        for row in reader:
            latitude_str = row[1]
            longitude_str = row[2]
            # 위도와 경도가 비어 있는 경우 해당 행을 건너뜁니다.
            if latitude_str == '' or longitude_str == '':
                continue
            latitude = float(latitude_str)
            longitude = float(longitude_str)
            coordinates.append((latitude, longitude))
    return coordinates

# CSV 파일 경로 설정
file_path = '공공장소_위도경도.csv'

# 후보지 좌표 리스트 (예시)
candidate_locations = extract_coordinates_from_csv(file_path)
print(candidate_locations)
print(len(candidate_locations))

# 유전자 인코딩: 인계점 설치 여부를 이진수로 표현
def encode_genes():
    return [random.randint(0, 1) for _ in candidate_locations]


# 목적함수: 커버 면적 최대화 및 인계점 수 최소화
def objective_function(genes):
    # 인계점 설치된 좌표 추출
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    # 커버 면적 계산 (중복 제외)
    covered_area = calculate_covered_area(installed_locations)

    # 인계점 수 계산
    num_installations = sum(genes)

    # 목적함수 값 계산 (최대화할 값과 최소화할 값)
    return 10*covered_area, -num_installations


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

    return total_covered_area * 111 *111  # 위도 좌표 0.0001 당 약 11m

# DEAP 설정
creator.create("FitnessMulti", base.Fitness, weights=(10.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, encode_genes)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", objective_function)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selNSGA2)


# 유전 알고리즘 실행
def run_genetic_algorithm():
    population = toolbox.population(n=100)

    for generation in range(2):
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
        circle = plt.Circle((loc[1], loc[0]), radius/111, color='blue', alpha=0.5)
        ax.add_patch(circle)

    # 인계점 설치된 좌표를 플롯
    for loc in installed_locations:
        ax.plot(loc[1], loc[0], 'bo', markersize=5)

    # 플롯 설정
    ax.set_xlabel('LatitudeLongitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Helicopter Handover Points with Coverage Area')
    plt.axis('equal')
    plt.show()

# 상위 5개 대안 선택 및 시각화
def select_and_visualize_top_solutions(population, candidate_locations, num_solutions=5):
    # 평가된 유전자들을 목적함수 값에 따라 정렬
    sorted_population = sorted(population, key=lambda ind: ind.fitness.values, reverse=True)

    # 상위 5개 대안 추출 및 시각화
    for i in range(num_solutions):
        print(f"Alternative {i+1}: Fitness = {sorted_population[i].fitness.values}")
        visualize_genes(sorted_population[i], candidate_locations)

def save_top_solutions_to_csv(population, candidate_locations, num_solutions=5, output_filename="top_solutions.csv"):
    # 평가된 유전자들을 목적함수 값에 따라 정렬
    sorted_population = sorted(population, key=lambda ind: ind.fitness.values, reverse=True)

    # 상위 5개 대안의 좌표 추출
    top_solutions = []
    for i in range(num_solutions):
        solution = sorted_population[i]
        coordinates = [candidate_locations[gene] for gene in solution]
        top_solutions.append(coordinates)

    # CSV 파일로 저장
    with open(output_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Alternative", "X", "Y"])
        for i, solution_coords in enumerate(top_solutions, start=1):
            writer.writerow([f"Alternative {i}"] + solution_coords)

# 유전 알고리즘 실행 후 상위 5개 대안 선택 및 시각화
def check_encode_genes():
    genes = [1 for _ in candidate_locations]
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]
    return installed_locations
print(calculate_covered_area(check_encode_genes())*10)

population = run_genetic_algorithm()
select_and_visualize_top_solutions(population, candidate_locations)
save_top_solutions_to_csv(population, candidate_locations, num_solutions=5, output_filename="top_solutions.csv")


