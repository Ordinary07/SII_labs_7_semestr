import numpy as np
import matplotlib.pyplot as plt

# Трапециевидная функция принадлежности

def trapezoidal_mf(x, a, b, c, d):
    if x <= a or x >= d:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return 1.0
    elif c < x < d:
        return (d - x) / (d - c)
    return 0.0

# Ввод параметров множества
def input_trapezoid(name):
    print(f"Введите параметры функции для множества {name} (a b c d):")
    a, b, c, d = map(float, input().split())
    return (a, b, c, d)

# Основная программа
if __name__ == "__main__":
    print("Предметная область: Энергопотребление\n")

    # Параметры множеств
    A_params = input_trapezoid("A (Уровень потребления энергии)")
    B_params = input_trapezoid("B (Энергоэффективность)")

    # Четкие объекты
    print("Введите значения энергии/эффективности через пробел:")
    x_values = list(map(float, input().split()))

    print("\nРезультаты объединения:")
    print("x\tμA(x)\tμB(x)\tμA∪B(x)")
    for x in x_values:
        muA = trapezoidal_mf(x, *A_params)
        muB = trapezoidal_mf(x, *B_params)
        muUnion = max(muA, muB)
        print(f"{x:.1f}\t{muA:.2f}\t{muB:.2f}\t{muUnion:.2f}")

    # Построение графиков
    X = np.linspace(min(x_values) - 5, max(x_values) + 5, 500)
    muA = [trapezoidal_mf(x, *A_params) for x in X]
    muB = [trapezoidal_mf(x, *B_params) for x in X]
    muUnion = [max(a, b) for a, b in zip(muA, muB)]

    plt.plot(X, muA, label="A (Уровень потребления энергии)", linewidth=2)
    plt.plot(X, muB, label="B (Энергоэффективность)", linewidth=2)
    plt.plot(X, muUnion, label="A ∪ B (объединение)", linestyle="--", color="black", linewidth=2)

    plt.title("Объединение нечетких множеств (Энергопотребление)")
    plt.xlabel("Значение")
    plt.ylabel("Степень принадлежности μ(x)")
    plt.legend()
    plt.grid(True)
    plt.show()
