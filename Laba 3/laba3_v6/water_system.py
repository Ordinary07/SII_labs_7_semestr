import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random


class WaterTreatmentSystem:
    def __init__(self, db_path='water_treatment.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создание таблицы онтологии
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ontology (
                id INTEGER PRIMARY KEY,
                concept TEXT NOT NULL,
                property TEXT NOT NULL,
                value REAL NOT NULL,
                description TEXT
            )
        ''')

        # Создание таблицы правил
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                condition TEXT NOT NULL,
                action TEXT NOT NULL,
                priority INTEGER DEFAULT 1
            )
        ''')

        # Создание таблицы измерений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pollution_level REAL,
                water_flow REAL,
                ph_level REAL,
                temperature REAL,
                oxygen_level REAL
            )
        ''')

        # Создание таблицы действий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT,
                intensity REAL,
                duration INTEGER
            )
        ''')

        # Добавляем данные в онтологию
        ontology_data = [
            ('pollution_level', 'low', 0.0, 'Низкий уровень загрязнения'),
            ('pollution_level', 'medium', 0.3, 'Средний уровень загрязнения'),
            ('pollution_level', 'high', 0.7, 'Высокий уровень загрязнения'),
            ('pollution_level', 'critical', 0.9, 'Критический уровень загрязнения'),
            ('ph_level', 'acidic', 6.0, 'Кислая среда'),
            ('ph_level', 'neutral', 7.0, 'Нейтральная среда'),
            ('ph_level', 'alkaline', 8.0, 'Щелочная среда'),
            ('temperature', 'cold', 10.0, 'Холодная вода'),
            ('temperature', 'optimal', 20.0, 'Оптимальная температура'),
            ('temperature', 'warm', 30.0, 'Теплая вода'),
            ('oxygen_level', 'low', 2.0, 'Низкий уровень кислорода'),
            ('oxygen_level', 'normal', 5.0, 'Нормальный уровень кислорода'),
            ('oxygen_level', 'high', 8.0, 'Высокий уровень кислорода')
        ]

        cursor.executemany('''
            INSERT OR IGNORE INTO ontology (concept, property, value, description)
            VALUES (?, ?, ?, ?)
        ''', ontology_data)

        # Добавляем правила
        rules_data = [
            ('Высокое загрязнение - усиленная очистка', 'pollution_level > 0.7', 'activate_chemical_treatment', 1),
            ('Среднее загрязнение - стандартная очистка', 'pollution_level > 0.3 and pollution_level <= 0.7',
             'activate_standard_treatment', 2),
            ('Низкое загрязнение - минимальная очистка', 'pollution_level <= 0.3', 'activate_minimal_treatment', 3),
            ('Кислая среда - добавление щелочи', 'ph_level < 6.5', 'add_alkaline', 2),
            ('Щелочная среда - добавление кислоты', 'ph_level > 7.5', 'add_acid', 2),
            ('Низкая температура - подогрев', 'temperature < 15', 'activate_heating', 3),
            ('Высокая температура - охлаждение', 'temperature > 25', 'activate_cooling', 3),
            ('Низкий кислород - аэрация', 'oxygen_level < 3', 'activate_aeration', 2)
        ]

        cursor.executemany('''
            INSERT OR IGNORE INTO rules (name, condition, action, priority)
            VALUES (?, ?, ?, ?)
        ''', rules_data)

        conn.commit()
        conn.close()
        print("База данных создана и заполнена!")


class FuzzyLogic:
    """Класс для нечеткой логики"""

    @staticmethod
    def triangular_mf(x, a, b, c):
        if x <= a:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x <= c:
            return (c - x) / (c - b)
        else:
            return 0.0

    def fuzzify_pollution(self, level):
        return {
            'low': self.triangular_mf(level, 0, 0, 0.3),
            'medium': self.triangular_mf(level, 0.1, 0.4, 0.7),
            'high': self.triangular_mf(level, 0.5, 0.8, 1.0)
        }


class InferenceEngine:
    """Машина логического вывода"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.fuzzy_logic = FuzzyLogic()

    def evaluate_conditions(self, measurements):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, name, condition, action, priority FROM rules ORDER BY priority')
        rules = cursor.fetchall()

        activated_rules = []

        for rule_id, name, condition, action, priority in rules:
            try:
                eval_condition = condition
                for key, value in measurements.items():
                    eval_condition = eval_condition.replace(key, str(value))

                if eval(eval_condition):
                    activated_rules.append({
                        'id': rule_id,
                        'name': name,
                        'action': action,
                        'priority': priority
                    })
            except Exception as e:
                print(f"Ошибка в правиле {name}: {e}")

        conn.close()
        return activated_rules

    def make_decision(self, measurements):
        fuzzy_pollution = self.fuzzy_logic.fuzzify_pollution(measurements['pollution_level'])

        print("Фаззифицированные значения загрязнения:")
        for level, value in fuzzy_pollution.items():
            if value > 0:
                print(f"  {level}: {value:.2f}")

        activated_rules = self.evaluate_conditions(measurements)
        return sorted(activated_rules, key=lambda x: x['priority'])


class WaterTreatmentSimulator:
    """Симулятор очистных сооружений"""

    def __init__(self):
        self.system = WaterTreatmentSystem()
        self.inference_engine = InferenceEngine(self.system.db_path)
        self.current_state = {
            'pollution_level': 0.5,
            'water_flow': 100.0,
            'ph_level': 7.0,
            'temperature': 20.0,
            'oxygen_level': 5.0
        }

    def save_measurement(self, measurements):
        conn = sqlite3.connect(self.system.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO measurements 
            (pollution_level, water_flow, ph_level, temperature, oxygen_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (measurements['pollution_level'], measurements['water_flow'],
              measurements['ph_level'], measurements['temperature'],
              measurements['oxygen_level']))

        conn.commit()
        conn.close()

    def save_action(self, action_type, intensity, duration):
        conn = sqlite3.connect(self.system.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO actions (action_type, intensity, duration)
            VALUES (?, ?, ?)
        ''', (action_type, intensity, duration))

        conn.commit()
        conn.close()

    def simulate_environment_change(self):
        self.current_state['pollution_level'] += random.uniform(-0.1, 0.15)
        self.current_state['pollution_level'] = max(0.0, min(1.0, self.current_state['pollution_level']))

        self.current_state['ph_level'] += random.uniform(-0.2, 0.2)
        self.current_state['ph_level'] = max(4.0, min(9.0, self.current_state['ph_level']))

        self.current_state['temperature'] += random.uniform(-1, 1)
        self.current_state['temperature'] = max(5.0, min(35.0, self.current_state['temperature']))

        self.current_state['oxygen_level'] += random.uniform(-0.5, 0.5)
        self.current_state['oxygen_level'] = max(1.0, min(10.0, self.current_state['oxygen_level']))

    def apply_action(self, action):
        action_type = action['action']

        if action_type == 'activate_chemical_treatment':
            self.current_state['pollution_level'] -= 0.3
            self.save_action('chemical_treatment', 0.8, 10)
            print("→ Применено: Усиленная химическая очистка")
        elif action_type == 'activate_standard_treatment':
            self.current_state['pollution_level'] -= 0.15
            self.save_action('standard_treatment', 0.5, 8)
            print("→ Применено: Стандартная очистка")
        elif action_type == 'activate_minimal_treatment':
            self.current_state['pollution_level'] -= 0.05
            self.save_action('minimal_treatment', 0.2, 5)
            print("→ Применено: Минимальная очистка")
        elif action_type == 'add_alkaline':
            self.current_state['ph_level'] += 0.3
            self.save_action('add_alkaline', 0.4, 3)
            print("→ Применено: Добавление щелочи")
        elif action_type == 'add_acid':
            self.current_state['ph_level'] -= 0.3
            self.save_action('add_acid', 0.4, 3)
            print("→ Применено: Добавление кислоты")

        self.current_state['pollution_level'] = max(0.0, min(1.0, self.current_state['pollution_level']))
        self.current_state['ph_level'] = max(4.0, min(9.0, self.current_state['ph_level']))

    def run_simulation(self, steps=10):
        print("=== СИМУЛЯЦИЯ СИСТЕМЫ УПРАВЛЕНИЯ ОЧИСТНЫМИ СООРУЖЕНИЯМИ ===")
        print("Создана база данных 'water_treatment.db' с онтологией и правилами\n")

        for step in range(steps):
            print(f"\n--- Шаг {step + 1} ---")
            print(f"Состояние: Загрязнение={self.current_state['pollution_level']:.2f}, "
                  f"pH={self.current_state['ph_level']:.2f}, "
                  f"Температура={self.current_state['temperature']:.1f}°C")

            self.save_measurement(self.current_state)

            decisions = self.inference_engine.make_decision(self.current_state)

            if decisions:
                best_decision = decisions[0]
                print(f"Активировано правило: {best_decision['name']}")
                self.apply_action(best_decision)
            else:
                print("Нет подходящих правил - система в оптимальном состоянии")
                self.save_action('no_action', 0.0, 0)

            self.simulate_environment_change()

        print(f"\n=== СИМУЛЯЦИЯ ЗАВЕРШЕНА ===")
        print("База данных 'water_treatment.db' сохранена")
        print("Содержит: онтологию, правила, измерения и действия")

    def visualize_results(self):
        """Визуализация результатов симуляции"""
        conn = sqlite3.connect(self.system.db_path)

        # Получаем данные измерений
        query = """
        SELECT timestamp, pollution_level, ph_level, temperature, oxygen_level 
        FROM measurements 
        ORDER BY timestamp
        """

        measurements_data = conn.execute(query).fetchall()

        if not measurements_data:
            print("Нет данных для визуализации")
            conn.close()
            return

        # Подготавливаем данные для графиков
        timestamps = [i for i in range(len(measurements_data))]
        pollution = [row[1] for row in measurements_data]
        ph_levels = [row[2] for row in measurements_data]
        temperature = [row[3] for row in measurements_data]
        oxygen = [row[4] for row in measurements_data]

        conn.close()

        # Создаем графики
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # График 1: Уровень загрязнения
        ax1.plot(timestamps, pollution, 'r-', linewidth=2, marker='o', markersize=4)
        ax1.set_title('Уровень загрязнения воды', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Уровень загрязнения', fontsize=12)
        ax1.set_xlabel('Шаг симуляции', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)

        # Добавляем зоны загрязнения
        ax1.axhspan(0, 0.3, alpha=0.2, color='green', label='Низкое')
        ax1.axhspan(0.3, 0.7, alpha=0.2, color='orange', label='Среднее')
        ax1.axhspan(0.7, 1.0, alpha=0.2, color='red', label='Высокое')
        ax1.legend()

        # График 2: Уровень pH
        ax2.plot(timestamps, ph_levels, 'g-', linewidth=2, marker='s', markersize=4)
        ax2.set_title('Уровень pH воды', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Уровень pH', fontsize=12)
        ax2.set_xlabel('Шаг симуляции', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(4, 9)

        # Добавляем оптимальную зону pH
        ax2.axhspan(6.5, 7.5, alpha=0.2, color='lime', label='Оптимальный pH')
        ax2.axhline(y=7.0, color='black', linestyle='--', alpha=0.5, label='Нейтральный pH')
        ax2.legend()

        # График 3: Температура
        ax3.plot(timestamps, temperature, 'b-', linewidth=2, marker='^', markersize=4)
        ax3.set_title('Температура воды', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Температура (°C)', fontsize=12)
        ax3.set_xlabel('Шаг симуляции', fontsize=12)
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 40)

        # График 4: Уровень кислорода
        ax4.plot(timestamps, oxygen, 'm-', linewidth=2, marker='d', markersize=4)
        ax4.set_title('Уровень кислорода', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Кислород (мг/л)', fontsize=12)
        ax4.set_xlabel('Шаг симуляции', fontsize=12)
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 12)

        # Добавляем оптимальную зону кислорода
        ax4.axhspan(3, 8, alpha=0.2, color='cyan', label='Оптимальный O₂')
        ax4.legend()

        plt.tight_layout()

        # Сохраняем график
        plt.savefig('water_treatment_results.png', dpi=300, bbox_inches='tight')
        print("График сохранен как 'water_treatment_results.png'")

        # Показываем график
        plt.show()


# ЗАПУСК ПРОГРАММЫ
if __name__ == "__main__":
    print("Запуск системы управления очистными сооружениями...")
    simulator = WaterTreatmentSimulator()
    simulator.run_simulation(steps=8)

    # Создаем график после симуляции
    simulator.visualize_results()

    input("\nНажмите Enter для выхода...")