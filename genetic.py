import random
from deap import base, creator, tools
from shapely.geometry import Point
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
budget = 1600  # 총 예산
installation_cost_per_point = 21  # 인계점 하나 당 설치 비용


# 유전자 인코딩: 인계점 설치 여부를 이진수로 표현
def encode_genes():
    genes = [0] * len(candidate_locations)
    num_points = min(budget // installation_cost_per_point, len(candidate_locations))
    selected_points = random.sample(range(len(candidate_locations)), num_points)
    for point in selected_points:
        genes[point] = 1
    return genes


# 목적함수: 커버 면적 최대화
def objective_function(genes):
    # 인계점 설치된 좌표 추출
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    # 커버 면적 계산 (중복 제외)
    covered_area = calculate_covered_area(installed_locations)

    return covered_area,


# 커버 면적 계산 함수 (중복 제외)
def calculate_covered_area(installed_locations, radius=10):
    radius = radius / 111  # 1도는 약 111km
    idx = index.Index()

    circles = []
    for i, (x, y) in enumerate(installed_locations):
        circle = Point(x, y).buffer(radius)
        circles.append(circle)
        idx.insert(i, circle.bounds)

    merged_circles = unary_union(circles)
    total_covered_area = merged_circles.area

    return total_covered_area * 111 * 111  # 위도 좌표 0.0001 당 약 11m


# 예산 제약 조건을 확인하는 함수
def is_within_budget(genes):
    num_installations = sum(genes)
    total_cost = num_installations * installation_cost_per_point
    return total_cost <= budget


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
    population = toolbox.population(n=500)
    elite_size = 5  # 정예 개체 수

    for generation in range(20):
        fitnesses = map(toolbox.evaluate, population)
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # 상위 개체를 유지 (정예 선택)
        elite_individuals = tools.selBest(population, elite_size)

        offspring = toolbox.select(population, len(population) - elite_size)
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

        # 예산 제약 조건을 만족하지 않는 개체 수정
        for ind in offspring:
            while not is_within_budget(ind):
                ind[random.choice([i for i, gene in enumerate(ind) if gene == 1])] = 0

        # fitness가 0인 개체 제거 및 유효한 fitness를 가진 개체만 남기기
        valid_offspring = []
        for ind in offspring:
            if ind.fitness.valid and ind.fitness.values[0] > 0:
                valid_offspring.append(ind)
            else:
                new_ind = toolbox.individual()
                while not is_within_budget(new_ind):
                    new_ind[random.choice([i for i, gene in enumerate(new_ind) if gene == 1])] = 0
                new_ind.fitness.values = toolbox.evaluate(new_ind)
                valid_offspring.append(new_ind)

        population[:] = elite_individuals + valid_offspring

        if population:
            best_solution = max(population, key=lambda ind: ind.fitness.values)
            print(f"Generation {generation}: Best Solution = {best_solution.fitness.values}")
        else:
            print(f"Generation {generation}: No valid solutions")

    return population


# 유전자 시각화 함수
def visualize_genes(genes, candidate_locations, filename=None):
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    for loc in candidate_locations:
        plt.plot(loc[1], loc[0], 'ro', markersize=2)

    for loc in installed_locations:
        plt.plot(loc[1], loc[0], 'bo', markersize=5)

    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title('Helicopter Handover Points Visualization')

    if filename:
        plt.savefig(filename)
    plt.show()


def visualize_genes_with_coverage(genes, candidate_locations, radius=5, filename=None):
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]

    fig, ax = plt.subplots()
    for loc in installed_locations:
        circle = plt.Circle((loc[1], loc[0]), radius / 111, color='blue', alpha=0.5)
        ax.add_patch(circle)

    for loc in installed_locations:
        ax.plot(loc[1], loc[0], 'bo', markersize=5)

    ax.set_xlabel('Latitude')
    ax.set_ylabel('Longitude')
    ax.set_title('Helicopter Handover Points with Coverage Area')
    plt.axis('equal')

    if filename:
        plt.savefig(filename)
    plt.show()


# 상위 5개 대안 선택 및 시각화
def select_and_visualize_top_solutions(population, candidate_locations, num_solutions=5):
    valid_population = [ind for ind in population if ind.fitness.valid and ind.fitness.values[0] > 0]

    sorted_population = sorted(valid_population, key=lambda ind: ind.fitness.values, reverse=True)

    for i in range(min(num_solutions, len(sorted_population))):
        num_installations = sum(sorted_population[i])
        print(
            f"Alternative {i + 1}: Fitness = {sorted_population[i].fitness.values}, Installations = {num_installations}")
        visualize_genes(sorted_population[i], candidate_locations, f"solution_{i + 1}.png")


def save_top_solutions_to_csv(population, candidate_locations, num_solutions=5):
    valid_population = [ind for ind in population if ind.fitness.valid and ind.fitness.values[0] > 0]

    sorted_population = sorted(valid_population, key=lambda ind: ind.fitness.values, reverse=True)

    for i in range(min(num_solutions, len(sorted_population))):
        solution = sorted_population[i]
        num_installations = sum(solution)
        coordinates = [candidate_locations[idx] for idx, gene in enumerate(solution) if gene == 1]
        output_filename = f"top_solution_{i + 1}.csv"

        with open(output_filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Latitude", "Longitude", "Installations"])
            for j, (latitude, longitude) in enumerate(coordinates):
                writer.writerow([j, latitude, longitude])
            writer.writerow(["Total Installations", num_installations])
population = run_genetic_algorithm()
select_and_visualize_top_solutions(population, candidate_locations)
save_top_solutions_to_csv(population, candidate_locations, num_solutions=5)