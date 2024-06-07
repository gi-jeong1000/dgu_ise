import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union
from rtree import index
import csv
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution

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
candidate_locations = extract_coordinates_from_csv(file_path)
print(candidate_locations)
print(len(candidate_locations))

budget = 1000  # 총 예산
installation_cost_per_point = 10  # 인계점 하나 당 설치 비용

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

def objective_function(genes):
    genes = (genes > 0.5).astype(int)
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]
    covered_area = calculate_covered_area(installed_locations)
    return -covered_area  # minimize negative of covered area

def is_within_budget(genes):
    num_installations = sum((genes > 0.5).astype(int))
    total_cost = num_installations * installation_cost_per_point
    return total_cost <= budget

def constraint(genes):
    return budget - sum((genes > 0.5).astype(int)) * installation_cost_per_point

bounds = [(0, 1) for _ in range(len(candidate_locations))]

result = differential_evolution(
    objective_function,
    bounds,
    strategy='best1bin',
    maxiter=100,
    popsize=15,
    tol=0.01,
    mutation=(0.5, 1),
    recombination=0.7,
    disp=True,
    polish=True,
    constraints={'type': 'ineq', 'fun': constraint}
)

best_solution = (result.x > 0.5).astype(int)
best_fitness = -result.fun

print(f"Best Solution = {best_solution}, Best Fitness = {best_fitness}")

def visualize_genes(genes, candidate_locations):
    installed_locations = [loc for gene, loc in zip(genes, candidate_locations) if gene == 1]
    for loc in candidate_locations:
        plt.plot(loc[1], loc[0], 'ro', markersize=2)
    for loc in installed_locations:
        plt.plot(loc[1], loc[0], 'bo', markersize=5)
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title('Helicopter Handover Points Visualization')
    plt.show()

def visualize_genes_with_coverage(genes, candidate_locations, radius=5):
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
    plt.show()

visualize_genes(best_solution, candidate_locations)
visualize_genes_with_coverage(best_solution, candidate_locations)

def save_solution_to_csv(solution, candidate_locations, filename="best_solution.csv"):
    coordinates = [candidate_locations[idx] for idx, gene in enumerate(solution) if gene == 1]
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Index", "Latitude", "Longitude"])
        for j, (latitude, longitude) in enumerate(coordinates):
            writer.writerow([j, latitude, longitude])
        writer.writerow(["Total Installations", sum(solution)])

save_solution_to_csv(best_solution, candidate_locations)