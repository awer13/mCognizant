# generator_app/analyzer.py
import random
from typing import Any, Dict, List, Optional

import sympy
from sympy import symbols, summation, oo, limit
from sympy.parsing.sympy_parser import parse_expr

from .task_template import BaseTask, AnalyzedTask
from .generators.series_generator_1 import SeriesTaskClass1
from .generators.series_generator_2 import SeriesTaskClass2
from .generators.series_generator_3 import SeriesTaskClass3
from .generators.series_generator_4 import SeriesTaskClass4

# Выпадающие варианты (по ТЗ)
JUSTIFY_OPTIONS = [
    "по определению",
    "по необходимому условию сходимости",
    "по признаку Коши",
    "по признаку Даламбера",
    "по признаку Лейбница",
    "по интегральному признаку",
]
CONVERGENCE_OPTIONS = ["сходится", "расходится", "неизвестно", "неопределено"]


def _norm_text(s: Any) -> str:
    return str(s or "").strip().lower().replace("ё", "е")


def _symp(s: Any) -> Optional[sympy.Expr]:
    if s is None:
        return None
    txt = str(s).strip()
    if txt == "":
        return None
    try:
        locals_ = {"oo": sympy.oo, "e": sympy.E, "pi": sympy.pi}
        return parse_expr(txt, local_dict=locals_, evaluate=True)
    except Exception:
        try:
            return sympy.nsimplify(txt)
        except Exception:
            return None


def _sympy_equal(a: Any, b: Any, *, tol: float = 1e-6) -> bool:
    ea, eb = _symp(a), _symp(b)
    if ea is None or eb is None:
        return False
    try:
        diff = sympy.simplify(ea - eb)
        if diff == 0:
            return True
        if diff.is_real:
            try:
                return abs(float(diff)) <= tol
            except Exception:
                return False
        return False
    except Exception:
        try:
            fa = float(ea.evalf())
            fb = float(eb.evalf())
            return abs(fa - fb) <= tol
        except Exception:
            return False


class TaskAnalyzer:
    """
    Новый интерфейс:
      - build_steps(topic_id, task) -> список шагов (подвопросов)
      - check_step(topic_id, step_key, user_value, payload) -> {ok, score, correct?}
      - grade_attempt(topic_id, payload, answers_for_question) -> итог по вопросу
    Старый метод analyze(task) оставлен для совместимости.
    """

    # ---------- построение шагов ----------
    def build_steps(self, topic_id: str, task: BaseTask) -> List[Dict[str, Any]]:
        if isinstance(task, (SeriesTaskClass1, SeriesTaskClass2)):
            return self._steps_geometric(task)
        if isinstance(task, SeriesTaskClass3):
            return self._steps_general_series_3(task)
        if isinstance(task, SeriesTaskClass4):
            return self._steps_general_series_4(task)

        return [{
            "key": "answer",
            "type": "input",
            "label": "Ваш ответ",
            "hint": None,
            "points": 10,
            "answer_expr": None,
        }]

    # Геометрический ряд: классы 1 и 2
    def _steps_geometric(self, task: BaseTask) -> List[Dict[str, Any]]:
        k = symbols('k')
        if isinstance(task, SeriesTaskClass1):
            r = sympy.S(task.b) / task.c
        else:
            r = sympy.S(1) / (1 + task.c)

        term_k = r**k
        rng = random.Random(getattr(task, "seed", 123456))
        n_for_an = rng.randint(3, 8)
        n_for_sn = rng.randint(3, 8)

        n_sym = symbols('n')
        an_value = term_k.subs(k, n_for_an)
        sn_formula = summation(term_k, (k, 0, n_sym))
        sn_value = sn_formula.subs(n_sym, n_for_sn)

        converges = abs(r) < 1
        conv_text = "сходится" if converges else "расходится"

        steps: List[Dict[str, Any]] = [
            {
                "key": "an",
                "type": "input",
                "label": f"Значение a_n при n={n_for_an}",
                "hint": "Подставьте n в общий член геометрического ряда.",
                "points": 20,
                "answer_expr": sympy.sstr(an_value),
            },
            {
                "key": "sn",
                "type": "input",
                "label": f"Значение S_n при n={n_for_sn}",
                "hint": "Формула суммы первых n+1 членов геометрической прогрессии.",
                "points": 20,
                "answer_expr": sympy.sstr(sn_value),
            },
            {
                "key": "conv",
                "type": "select",
                "label": "Сходимость ряда",
                "hint": "Для ∑ r^k ряд сходится при |r|<1.",
                "points": 20,
                "options": CONVERGENCE_OPTIONS,
                "answer_text": conv_text,
            },
        ]

        if converges:
            s_inf = summation(term_k, (k, 0, oo))
            steps.append({
                "key": "s_inf",
                "type": "input",
                "label": "Сумма ряда (бесконечная)",
                "hint": "Для геометрического ряда S=1/(1-r), если |r|<1.",
                "points": 30,
                "answer_expr": sympy.sstr(s_inf),
            })

        steps.append({
            "key": "justify",
            "type": "select",
            "label": "Обоснуйте ваш ответ",
            "hint": "Выберите подходящий признак/основание.",
            "points": 10,
            "options": JUSTIFY_OPTIONS,
            "answer_text": "по необходимому условию сходимости",
        })
        return steps

    # Класс 3
    def _steps_general_series_3(self, task: SeriesTaskClass3) -> List[Dict[str, Any]]:
        n = symbols('n')
        a_n = (task.b + task.p * n**2) / (task.c * n**2 + task.d * n)
        lim = limit(a_n, n, sympy.oo)
        rng = random.Random(getattr(task, "seed", 123456))
        n_for_an = rng.randint(5, 15)
        conv_text = "расходится" if lim != 0 else "неизвестно"

        return [
            {
                "key": "an",
                "type": "input",
                "label": f"Значение a_n при n={n_for_an}",
                "hint": "Подставьте n в формулу a_n.",
                "points": 25,
                "answer_expr": sympy.sstr(a_n.subs(n, n_for_an)),
            },
            {
                "key": "limit",
                "type": "input",
                "label": "Значение предела a_n",
                "hint": "Найдите lim_{n→∞} a_n.",
                "points": 35,
                "answer_expr": sympy.sstr(lim),
            },
            {
                "key": "conv",
                "type": "select",
                "label": "Сходимость ряда ∑ a_n",
                "hint": "Если lim a_n ≠ 0 — ряд расходится; если = 0 — вывод сделать нельзя.",
                "points": 30,
                "options": CONVERGENCE_OPTIONS,
                "answer_text": conv_text,
            },
            {
                "key": "justify",
                "type": "select",
                "label": "Обоснуйте ваш ответ",
                "hint": "Выберите подходящее основание.",
                "points": 10,
                "options": JUSTIFY_OPTIONS,
                "answer_text": "по необходимому условию сходимости",
            },
        ]

    # Класс 4
    def _steps_general_series_4(self, task: SeriesTaskClass4) -> List[Dict[str, Any]]:
        n = symbols('n')
        a_n = (task.b + task.p * n) / (task.c * n - task.d)
        lim = limit(a_n, n, sympy.oo)
        rng = random.Random(getattr(task, "seed", 123456))
        n_for_an = rng.randint(5, 15)
        conv_text = "расходится" if lim != 0 else "неизвестно"

        return [
            {
                "key": "an",
                "type": "input",
                "label": f"Значение a_n при n={n_for_an}",
                "hint": "Подставьте n в формулу a_n.",
                "points": 25,
                "answer_expr": sympy.sstr(a_n.subs(n, n_for_an)),
            },
            {
                "key": "limit",
                "type": "input",
                "label": "Значение предела a_n",
                "hint": "Найдите lim_{n→∞} a_n.",
                "points": 35,
                "answer_expr": sympy.sstr(lim),
            },
            {
                "key": "conv",
                "type": "select",
                "label": "Сходимость ряда ∑ a_n",
                "hint": "Если lim a_n ≠ 0 — ряд расходится; если = 0 — вывод сделать нельзя.",
                "points": 30,
                "options": CONVERGENCE_OPTIONS,
                "answer_text": conv_text,
            },
            {
                "key": "justify",
                "type": "select",
                "label": "Обоснуйте ваш ответ",
                "hint": "Выберите подходящее основание.",
                "points": 10,
                "options": JUSTIFY_OPTIONS,
                "answer_text": "по необходимому условию сходимости",
            },
        ]

    # ---------- проверка одного шага ----------
    def check_step(
        self,
        topic_id: str,
        step_key: str,
        user_value: Any,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        steps = (payload or {}).get("steps") or []
        step = next((s for s in steps if s.get("key") == step_key), None)
        if not step:
            return {"ok": False, "score": 0.0, "explain": "Неизвестный шаг."}

        points = float(step.get("points", 0))

        if step.get("type") == "select":
            expect = _norm_text(step.get("answer_text"))
            got = _norm_text(user_value)
            ok = (expect == got) if expect else (got in [_norm_text(x) for x in (step.get("options") or [])])
            return {"ok": ok, "score": points if ok else 0.0, "correct": step.get("answer_text")}

        expect_expr = step.get("answer_expr")
        if expect_expr is None:
            return {"ok": True, "score": points}

        ok = _sympy_equal(user_value, expect_expr)
        return {"ok": ok, "score": points if ok else 0.0, "correct": expect_expr}

    # ---------- суммарная оценка по вопросу ----------
    def grade_attempt(
        self,
        topic_id: str,
        payload: Dict[str, Any],
        answers_for_question: Dict[str, Any],
    ) -> Dict[str, Any]:
        steps = (payload or {}).get("steps") or []
        total = sum(float(s.get("points", 0)) for s in steps) or 1.0
        acc = 0.0
        details = []

        def _get_user_value_for_key(key: str) -> Any:
            if isinstance(answers_for_question, dict):
                if key in answers_for_question and isinstance(answers_for_question[key], dict):
                    return answers_for_question[key].get("answer")
                if "answer" in answers_for_question:
                    return answers_for_question.get("answer")
            return None

        for st in steps:
            key = st.get("key")
            val = _get_user_value_for_key(key)
            chk = self.check_step(topic_id, key, val, {"steps": steps})
            acc += float(chk.get("score", 0.0))
            details.append({"step": key, "ok": bool(chk.get("ok")), "score": chk.get("score", 0.0)})

        return {"score": acc, "total": total, "details": details}

    # ---------- старая совместимость ----------
    def analyze(self, task: BaseTask) -> Optional[AnalyzedTask]:
        solutions: Dict[str, str] = {}

        if isinstance(task, (SeriesTaskClass1, SeriesTaskClass2)):
            k = sympy.symbols('k')
            if isinstance(task, SeriesTaskClass1):
                r = sympy.S(task.b) / task.c
            else:
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
            solutions["Сходимость"] = "Сходится" if (abs(r) < 1) else "Расходится"
            solutions["Обоснование"] = "по необходимому условию сходимости"

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
                "Обоснование": "по необходимому условию сходимости",
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
                "Обоснование": "по необходимому условию сходимости",
            }
        else:
            return None

        print(f"✅ Анализатор: Задача '{getattr(task,'task_type','?')}' успешно решена.")
        return AnalyzedTask(original_task=task, solutions=solutions)
