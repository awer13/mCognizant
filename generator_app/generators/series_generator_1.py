# series_generator.py (финальная гибкая версия)

import random
from fractions import Fraction
from dataclasses import dataclass, field
from ..task_template import BaseTask 

@dataclass
class SeriesTaskClass1(BaseTask):
    b: int = 0
    c: int = 0
    # Поля n_for_an и n_for_sn убраны, так как вопросы будут генерироваться анализатором
    task_type: str = field(default="series_class_1", init=False)

    def get_latex_formula(self) -> str:
        # Используем Fraction для автоматического сокращения дроби
        r = Fraction(self.b, self.c)
        return f"$$\\sum_{{k=0}}^{{\\infty}}\\left(\\frac{{{r.numerator}}}{{{r.denominator}}}\\right)^k$$"

class SeriesGeneratorClass1:
    """
    Генерирует задачи, напрямую следуя фундаментальному правилу сходимости.
    """
    def generate(self, complexity: int = 10) -> SeriesTaskClass1:
        # 1. Генерируем знаменатель. 'complexity' - это максимальный размер знаменателя.
        # Это единственный "рычаг" управления.
        c = random.randint(2, complexity)

        # 2. Создаём список ВСЕХ возможных числителей, удовлетворяющих |b| < c и b != 0
        possible_b = [i for i in range(-c + 1, c) if i != 0]
        
        # 3. Выбираем случайный 'b' из этого списка
        b = random.choice(possible_b)
        
        return SeriesTaskClass1(b=b, c=c)