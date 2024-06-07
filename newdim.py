import numpy as np
import matplotlib.pyplot as plt

# 설정
grid_size = 100  # 100x100 그리드
num_bases = 20  # 인계점 후보의 수
cost_per_base = 10  # 인계점당 비용
total_budget = 100  # 총 예산
coverage_radius = 10  # 커버리지 반경
max_safety_value = 10  # 중심에서의 최대 안전 수치

# 랜덤하게 인계점 후보를 생성
np.random.seed(42)
base_candidates = np.random.rand(num_bases, 2) * grid_size  # 0-100 범위 내의 랜덤 인계점 후보

# 안전 수치를 계산하는 함수
def calculate_safety(installed_locations, coverage_radius, max_safety_value):
    safety_dict = {}
    for base in installed_locations:
        base_x, base_y = base
        for dx in range(-coverage_radius, coverage_radius + 1):
            for dy in range(-coverage_radius, coverage_radius + 1):
                x = base_x + dx
                y = base_y + dy
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    dist = np.sqrt(dx**2 + dy**2)
                    if dist <= coverage_radius:
                        safety_value = max(0, max_safety_value * (1 - dist / coverage_radius))
                        safety_dict[(x, y)] = max(safety_dict.get((x, y), 0), safety_value)
    return safety_dict

# 적합도 함수
def fitness_function(individual):
    selected_bases = base_candidates[individual == 1]
    safety_dict = calculate_safety(selected_bases, coverage_radius, max_safety_value)
    safety_sum = sum(safety_dict.values())

    cost = np.sum(individual) * cost_per_base
    if cost > total_budget:
        return -1  # 페널티 부여

    return safety_sum

# 유전 알고리즘 함수
def crossover(parent1, parent2, crossover_rate):
    if np.random.rand() < crossover_rate:
        point = np.random.randint(1, len(parent1))
        child1 = np.concatenate((parent1[:point], parent2[point:]))
        child2 = np.concatenate((parent2[:point], parent1[point:]))
        return child1, child2
    else:
        return parent1.copy(), parent2.copy()

def mutate(individual, mutation_rate):
    for i in range(len(individual)):
        if np.random.rand() < mutation_rate:
            individual[i] = 1 - individual[i]  # 0 -> 1, 1 -> 0
    return individual

# 유전 알고리즘 설정
population_size = 50
generations = 1
mutation_rate = 0.1
crossover_rate = 0.7

# 초기 인구 생성
population = np.random.randint(2, size=(population_size, num_bases))

# 유전 알고리즘 실행
for generation in range(generations):
    fitness_scores = np.array([fitness_function(individual) for individual in population])

    # Ensure that fitness scores are non-negative
    min_fitness = np.min(fitness_scores)
    if min_fitness < 0:
        fitness_scores -= min_fitness

    sum_fitness = np.sum(fitness_scores)
    if sum_fitness == 0:
        probabilities = np.ones_like(fitness_scores) / len(fitness_scores)
    else:
        probabilities = fitness_scores / sum_fitness

    selected_indices = np.random.choice(range(population_size), size=population_size, p=probabilities)
    selected_population = population[selected_indices]

    new_population = []
    for i in range(0, population_size, 2):
        parent1 = selected_population[i]
        parent2 = selected_population[i + 1]
        child1, child2 = crossover(parent1, parent2, crossover_rate)
        new_population.extend([child1, child2])

    new_population = [mutate(individual, mutation_rate) for individual in new_population]
    population = np.array(new_population)

    best_fitness = np.max(fitness_scores)
    print(f"Generation {generation + 1}: Best Fitness = {best_fitness}")

# 최적화된 결과 출력
best_individual = population[np.argmax(fitness_scores)]
selected_bases = base_candidates[best_individual == 1]

# 시각화
def plot_coverage(base_candidates, selected_bases, coverage_radius):
    safety_dict = calculate_safety(selected_bases, coverage_radius, max_safety_value)
    plt.figure(figsize=(10, 10))
    grid = np.zeros((grid_size, grid_size))

    for (x, y), safety_value in safety_dict.items():
        grid[int(x), int(y)] = safety_value

    plt.imshow(grid, cmap='viridis', origin='lower')
    plt.colorbar(label='Safety Value')
    plt.scatter(base_candidates[:, 0], base_candidates[:, 1], c='red', label='Base Candidates', alpha=0.5)
    plt.scatter(selected_bases[:, 0], selected_bases[:, 1], c='green', label='Selected Bases')

    plt.legend()
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Coverage Optimization')
    plt.show()

plot_coverage(base_candidates, selected_bases, coverage_radius)