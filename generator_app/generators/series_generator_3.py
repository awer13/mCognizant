# generator_app/generators/series_generator_3.py

import random
from dataclasses import dataclass, field
from ..task_template import BaseTask

@dataclass
class SeriesTaskClass3(BaseTask):
    """Данные для задачи по необходимому условию (квадратичной)."""
    b: int = 0
    c: int = 0
    d: int = 0
    p: int = 0
    task_type: str = field(default="series_class_3", init=False)

    def get_latex_formula(self) -> str:
        # Для корректного отображения знака 'd'
        d_sign = "+" if self.d >= 0 else ""
        return f"$$\\sum_{{k=1}}^{{\\infty}}\\frac{{{self.b}+{self.p}k^2}}{{{self.c}k^2{d_sign}{self.d}k}}$$"

class SeriesGeneratorClass3:
    """
    Генерирует задачи по необходимому условию, гибко следуя ТЗ.
    Формула: (b+pk^2)/(ck^2+dk)
    """
    def generate(self, complexity: int = 10) -> SeriesTaskClass3:
        # Генерируем параметры, соблюдая все условия из ТЗ
        while True:
            c = random.randint(1, 9)
            d = random.randint(0, 9)
            b = random.randint(-9, -1)
            p = random.randint(-9, 9)

            # Проверяем условия, чтобы избежать неопределенностей
            if c == -d: continue
            if p == c and b == d: continue
            break
        
        return SeriesTaskClass3(b=b, c=c, d=d, p=p)