# series_generator_2.py (финальная гибкая версия)

import random
from dataclasses import dataclass, field
from ..task_template import BaseTask

@dataclass
class SeriesTaskClass2(BaseTask):
    c: int = 0
    # Поля n_for_an и n_for_sn убраны
    task_type: str = field(default="series_class_2", init=False)

    def get_latex_formula(self) -> str:
        return f"$$\\sum_{{k=0}}^{{\\infty}}\\frac{{1}}{{(1+{self.c})^k}}$$"

class SeriesGeneratorClass2:
    """
    Генерирует задачи, напрямую следуя фундаментальному правилу сходимости.
    """
    def generate(self, complexity: int = 12) -> SeriesTaskClass2:
        # 1. 'complexity' - это максимальное абсолютное значение 'c'.
        # Убедимся, что оно не меньше 3, чтобы обеспечить наличие отрицательных вариантов.
        if complexity < 3:
            complexity = 3

        # 2. Создаём список ВСЕХ возможных 'c', удовлетворяющих c > 0 или c < -2
        positive_cs = list(range(1, complexity + 1))
        negative_cs = list(range(-complexity, -2))
        
        all_possible_cs = positive_cs + negative_cs
        
        # 3. Выбираем случайный 'c' из этого полного списка
        c = random.choice(all_possible_cs)
        
        return SeriesTaskClass2(c=c)