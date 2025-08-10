# task_contracts.py
from dataclasses import dataclass, field

@dataclass
class BaseTask:
    task_type: str
    def get_latex_formula(self) -> str:
        raise NotImplementedError

@dataclass
class SeriesTaskClass1(BaseTask):
    b: int; c: int; n_for_an: int; n_for_sn: int
    task_type: str = field(default="series_class_1", init=False)
    def get_latex_formula(self) -> str:
        return f"$$\\sum_{{k=0}}^{{\\infty}}\\left(\\frac{{{self.b}}}{{{self.c}}}\\right)^k$$"

@dataclass
class SeriesTaskClass2(BaseTask):
    c: int; n_for_an: int; n_for_sn: int
    task_type: str = field(default="series_class_2", init=False)
    def get_latex_formula(self) -> str:
        return f"$$\\sum_{{k=0}}^{{\\infty}}\\frac{{1}}{{(1+{self.c})^k}}$$"

@dataclass
class AnalyzedTask:
    """Хранит задачу и результаты её анализа (вопросы и ответы)."""
    original_task: BaseTask
    solutions: dict = field(default_factory=dict)