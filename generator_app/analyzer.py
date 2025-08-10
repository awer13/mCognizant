# generator_app/analyzer.py

import sympy
import random

from .task_template import BaseTask, AnalyzedTask
from .generators.series_generator_1 import SeriesTaskClass1
from .generators.series_generator_2 import SeriesTaskClass2
# --- ДОБАВЬТЕ ИМПОРТЫ НОВЫХ КЛАССОВ ДАННЫХ ---
from .generators.series_generator_3 import SeriesTaskClass3
from .generators.series_generator_4 import SeriesTaskClass4

class TaskAnalyzer:
    def analyze(self, task: BaseTask) -> AnalyzedTask:
        solutions = {}
        
        if isinstance(task, SeriesTaskClass1) or isinstance(task, SeriesTaskClass2):
            # ... (ваша существующая логика для геометрических рядов) ...
            k = sympy.symbols('k')
            if isinstance(task, SeriesTaskClass1):
                r = sympy.S(task.b) / task.c
            else: # SeriesTaskClass2
                r = sympy.S(1) / (1 + task.c)
            series_term = r**k
            
            n_for_an = random.randint(3, 8)
            n_for_sn = random.randint(3, 8)
            an_value = series_term.subs(k, n_for_an)
            solutions[f"Значение a_n при n={n_for_an}"] = f"\\(a_{{{n_for_an}}} = {sympy.latex(an_value)}\\)"
            sn_formula = sympy.summation(series_term, (k, 0, sympy.symbols('n')))
            sn_value = sn_formula.subs(sympy.symbols('n'), n_for_sn)
            solutions[f"Значение S_n при n={n_for_sn}"] = f"\\(S_{{{n_for_sn}}} = {sympy.latex(sn_value.evalf(4))}\\)"
            total_sum = sympy.summation(series_term, (k, 0, sympy.oo))
            solutions["Сумма ряда"] = f"\\(S = {sympy.latex(total_sum)}\\)"
            sum_from_2 = sympy.summation(series_term, (k, 2, sympy.oo))
            solutions["Сумма ряда с k=2"] = f"\\(S_2 = {sympy.latex(sum_from_2)}\\)"
            solutions["Сходимость"] = "Сходится" if total_sum.is_finite else "Расходится"
            solutions["Обоснование"] = f"по необходимому условию сходимости"
        
        elif isinstance(task, SeriesTaskClass3):
            n = sympy.symbols('n')
            a_n_formula = (task.b + task.p * n**2) / (task.c * n**2 + task.d * n)
            limit_val = sympy.limit(a_n_formula, n, sympy.oo)
            convergence = "расходится" if limit_val != 0 else "неизвестно"
            n_for_an = random.randint(5, 15)
            
            solutions = {
                f"Значение a_n при n={n_for_an}": f"\\(a_{{{n_for_an}}} = {sympy.latex(a_n_formula.subs(n, n_for_an))}\\)",
                "Значение предела": f"\\(\\lim_{{n \\to \\infty}} a_n = {sympy.latex(limit_val)}\\)",
                "Сходимость": convergence,
                "Обоснование": "по необходимому условию сходимости"
            }

        elif isinstance(task, SeriesTaskClass4):
            n = sympy.symbols('n')
            a_n_formula = (task.b + task.p * n) / (task.c * n - task.d)
            limit_val = sympy.limit(a_n_formula, n, sympy.oo)
            convergence = "расходится" if limit_val != 0 else "неизвестно"
            n_for_an = random.randint(5, 15)
            
            solutions = {
                f"Значение a_n при n={n_for_an}": f"\\(a_{{{n_for_an}}} = {sympy.latex(a_n_formula.subs(n, n_for_an))}\\)",
                "Значение предела": f"\\(\\lim_{{n \\to \\infty}} a_n = {sympy.latex(limit_val)}\\)",
                "Сходимость": convergence,
                "Обоснование": "по необходимому условию сходимости"
            }
        
        else:
            return None 

        print(f"✅ Анализатор: Задача '{task.task_type}' успешно решена.")
        return AnalyzedTask(original_task=task, solutions=solutions)