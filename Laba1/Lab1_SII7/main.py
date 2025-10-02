'''6. На языке Python разработайте скрипт, который с помощью генетического
алгоритма и полного перебора решает следующую задачу. Дано N наименований
продуктов, для каждого из которых известно m характеристик. Необходимо получить
самый дешевый рацион из k наименований, удовлетворяющий заданным медицинским
нормам для каждой из m характеристик.'''


import numpy as np
import random
import itertools
import matplotlib.pyplot as plt

# Список продуктов: (название, калории, белки, жиры, углеводы, цена)
products = [
    ("Хлеб", 250, 8, 2, 50, 20),
    ("Молоко", 60, 3, 3, 5, 25),
    ("Яйца", 150, 12, 10, 1, 30),
    ("Курица", 200, 20, 8, 0, 70),
    ("Рыба", 180, 22, 6, 0, 90),
    ("Сыр", 300, 20, 25, 2, 100),
    ("Яблоки", 50, 0, 0, 14, 15),
    ("Картофель", 80, 2, 0, 18, 10),
    ("Гречка", 330, 12, 3, 68, 40),
    ("Морковь", 40, 1, 0, 10, 8)
]

N = len(products)  # количество продуктов
M = 4              # число характеристик (калории, белки, жиры, углеводы)
K = 4              # число продуктов в рационе

# Медицинские нормы (диапазоны для калорий, белков, жиров и углеводов)
norms = {
    "calories": (2000, 2500),
    "protein": (60, 200),
    "fat": (40, 80),
    "carbs": (300, 400)
}

# ФУНКЦИЯ ПРИСПОСОБЛЕННОСТИ

def evaluate(chromosome):
    """
    Функция оценивает, насколько хороший рацион (хромосома).
    Возвращает стоимость и штраф, если нормы не соблюдены.
    """
    chosen = [products[i] for i in chromosome]

    # Суммируем характеристики по выбранным продуктам
    total_cal = sum(p[1] for p in chosen)
    total_prot = sum(p[2] for p in chosen)
    total_fat = sum(p[3] for p in chosen)
    total_carb = sum(p[4] for p in chosen)
    total_cost = sum(p[5] for p in chosen)

    # Штраф за выход за пределы нормы
    penalty = 0
    if not (norms["calories"][0] <= total_cal <= norms["calories"][1]):
        penalty += abs(total_cal - np.clip(total_cal, *norms["calories"]))
    if not (norms["protein"][0] <= total_prot <= norms["protein"][1]):
        penalty += abs(total_prot - np.clip(total_prot, *norms["protein"]))
    if not (norms["fat"][0] <= total_fat <= norms["fat"][1]):
        penalty += abs(total_fat - np.clip(total_fat, *norms["fat"]))
    if not (norms["carbs"][0] <= total_carb <= norms["carbs"][1]):
        penalty += abs(total_carb - np.clip(total_carb, *norms["carbs"]))

    return total_cost + penalty

# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ

def repair_chromosome(chrom):
    """
    Исправляем хромосому:
    - убираем дублирующиеся продукты
    - добавляем случайные продукты до K штук
    """
    chrom = list(dict.fromkeys(chrom))  # удаляем дубликаты, сохраняя порядок
    while len(chrom) < K:
        chrom.append(random.randrange(N))  # добавляем случайный продукт
        chrom = list(dict.fromkeys(chrom))  # убираем возможные дубли
    return chrom[:K]

# ГЕНЕТИЧЕСКИЙ АЛГОРИТМ

def initialize_population(pop_size):
    """Создаем начальную популяцию из случайных рационов."""
    return [random.sample(range(N), K) for _ in range(pop_size)]

# --- Кроссоверы (способы скрещивания) ---
def crossover_one_point(p1, p2):
    """Одноточечный кроссовер"""
    point = random.randint(1, K - 1)
    child = p1[:point] + [g for g in p2 if g not in p1[:point]]
    return repair_chromosome(child)

def crossover_two_point(p1, p2):
    """Двухточечный кроссовер"""
    a, b = sorted(random.sample(range(K), 2))
    child = p1[:a] + p2[a:b] + [g for g in p1 if g not in p2[a:b]]
    return repair_chromosome(child)

def crossover_uniform(p1, p2):
    """Равномерный кроссовер"""
    child = [p1[i] if random.random() < 0.5 else p2[i] for i in range(K)]
    return repair_chromosome(child)

# --- Мутации ---
def mutation_swap(chrom):
    """Меняем местами два продукта"""
    if len(chrom) < 2:
        return chrom
    i, j = random.sample(range(len(chrom)), 2)
    chrom[i], chrom[j] = chrom[j], chrom[i]
    return repair_chromosome(chrom)

def mutation_replace(chrom):
    """Заменяем один продукт на случайный другой"""
    i = random.randrange(len(chrom))
    chrom[i] = random.randrange(N)
    return repair_chromosome(chrom)

def mutation_shuffle(chrom):
    """Перемешиваем продукты внутри рациона"""
    random.shuffle(chrom)
    return repair_chromosome(chrom)

# --- Селекция ---
def selection(pop, fitnesses):
    """
    Турнирная селекция:
    выбираем лучший из двух случайных особей
    """
    i, j = random.sample(range(len(pop)), 2)
    return pop[i] if fitnesses[i] < fitnesses[j] else pop[j]

# --- Основной цикл генетического алгоритма ---
def genetic_algorithm(generations=100, pop_size=50):
    pop = initialize_population(pop_size)  # начальная популяция
    best_scores = []                       # история лучших значений
    best_solution = None                   # лучшее решение

    for gen in range(generations):
        fitnesses = [evaluate(ind) for ind in pop]  # оценка популяции
        best_idx = np.argmin(fitnesses)
        if best_solution is None or fitnesses[best_idx] < evaluate(best_solution):
            best_solution = pop[best_idx]           # сохраняем лучшее решение
        best_scores.append(min(fitnesses))

        new_pop = []
        for _ in range(pop_size):
            # выбираем родителей
            p1, p2 = selection(pop, fitnesses), selection(pop, fitnesses)
            # случайный кроссовер
            cross = random.choice([crossover_one_point, crossover_two_point, crossover_uniform])
            child = cross(p1.copy(), p2.copy())
            # случайная мутация
            mut = random.choice([mutation_swap, mutation_replace, mutation_shuffle])
            child = mut(child)
            new_pop.append(child)
        pop = new_pop
    return best_solution, best_scores

# ПОЛНЫЙ ПЕРЕБОР (для сравнения)
def brute_force():
    """
    Полный перебор всех комбинаций продуктов
    (точное, но медленное решение).
    """
    best_cost = float("inf")
    best_sol = None
    for comb in itertools.combinations(range(N), K):
        cost = evaluate(list(comb))
        if cost < best_cost:
            best_cost = cost
            best_sol = comb
    return best_sol, best_cost

# Запускаем генетический алгоритм и полный перебор
best_ga, scores = genetic_algorithm(generations=200, pop_size=100)
best_brute, brute_cost = brute_force()

# Выводим результаты
print("Лучшее решение (ГА):", [products[i][0] for i in best_ga], "стоимость:", evaluate(best_ga))
print("Лучшее решение (перебор):", [products[i][0] for i in best_brute], "стоимость:", brute_cost)

# График сходимости ГА
plt.plot(scores)
plt.title("Сходимость генетического алгоритма")
plt.xlabel("Поколение")
plt.ylabel("Значение функции приспособленности")
plt.grid(True)
plt.show()
