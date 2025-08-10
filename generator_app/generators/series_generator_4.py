# generator_app/generators/series_generator_4.py

import random
from dataclasses import dataclass, field
from ..task_template import BaseTask

@dataclass
class SeriesTaskClass4(BaseTask):
    """Данные для задачи по необходимому условию (линейной)."""
    b: int = 0
    c: int = 0
    d: int = 0
    p: int = 0
    task_type: str = field(default="series_class_4", init=False)

    def get_latex_formula(self) -> str:
        # Для корректного отображения знака 'd'
        d_sign = "-" if self.d >= 0 else "+"
        d_val = abs(self.d)
        return f"$$\\sum_{{k=0}}^{{\\infty}}\\frac{{{self.b}+{self.p}k}}{{{self.c}k {d_sign} {d_val}}}$$"

class SeriesGeneratorClass4:
    """
    Генерирует задачи по необходимому условию, гибко следуя ТЗ.
    Формула: (b+pk)/(ck-d)
    """
    def generate(self, complexity: int = 10) -> SeriesTaskClass4:
        # Генерируем параметры, соблюдая все условия из ТЗ
        while True:
            c = random.randint(1, 9)
            d = random.randint(0, 9)
            b = random.randint(1, 9)
            p = random.randint(-9, 9)

            # Проверяем условия
            if c == d: continue
            if p == c and d == -b: continue
            break
            
        return SeriesTaskClass4(b=b, c=c, d=d, p=p)