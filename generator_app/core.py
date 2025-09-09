# generator_app/core.py
import pkgutil, importlib, inspect

class TaskController:
    """
    Ядро-диспетчер. Управляет регистрацией и вызовом генераторов.
    Умеет автоподхватывать генераторы из пакета generator_app.generators.
    """
    def __init__(self):
        self._generators = {}
        print("✅ Ядро (TaskController) инициализировано.")

    def register_generator(self, task_type: str, generator_class):
        """Регистрирует генератор."""
        self._generators[task_type] = generator_class
        label = getattr(generator_class, "LABEL", task_type)
        # на всякий случай проставим TASK_TYPE в класс, если не задан
        if not getattr(generator_class, "TASK_TYPE", None):
            setattr(generator_class, "TASK_TYPE", task_type)
        print(f"  -> Генератор для '{task_type}' зарегистрирован (label='{label}').")

    def topics(self):
        """Список тем для UI: [{'id': 'series_class_1', 'label': '...'}, ...]"""
        items = [{"id": k, "label": getattr(v, "LABEL", k)} for k, v in self._generators.items()]
        # можно отсортировать по label
        return sorted(items, key=lambda x: x["label"])

    def create_task(self, task_type: str, complexity: int):
        generator_class = self._generators.get(task_type)
        if not generator_class:
            print(f"⚠️ Ошибка: Генератор для типа '{task_type}' не найден.")
            return None
        generator_instance = generator_class()
        print(f"⚙️ Ядро: Запрашиваю новую задачу у генератора '{task_type}'...")
        return generator_instance.generate()

    # === АВТОПОИСК ГЕНЕРАТОРОВ ===
    def autodiscover_generators(self):
        """
        Загружает все модули из generator_app.generators и регистрирует генераторы.
        Поддерживаются два паттерна:
        1) В модуле есть классы с методом generate() и атрибутом TASK_TYPE (и опц. LABEL)
        2) В модуле определён список __all_generators__ = [(task_type, Class), ...]
        """
        from . import generators as gens_pkg
        base_pkg_name = gens_pkg.__name__
        print("🔎 Автопоиск генераторов в", base_pkg_name)

        for m in pkgutil.iter_modules(gens_pkg.__path__):
            mod_name = f"{base_pkg_name}.{m.name}"
            try:
                module = importlib.import_module(mod_name)
            except Exception as e:
                print(f"⚠️ Не удалось импортировать {mod_name}: {e}")
                continue

            # Паттерн 2: список пар (task_type, class)
            pairs = getattr(module, "__all_generators__", None)
            if pairs:
                for task_type, cls in pairs:
                    try:
                        self.register_generator(task_type, cls)
                    except Exception as e:
                        print(f"⚠️ Ошибка регистрации {task_type} из {mod_name}: {e}")
                continue

            # Паттерн 1: ищем классы с TASK_TYPE + generate()
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ != module.__name__:
                    continue
                task_type = getattr(obj, "TASK_TYPE", None)
                if task_type and callable(getattr(obj, "generate", None)):
                    try:
                        self.register_generator(task_type, obj)
                    except Exception as e:
                        print(f"⚠️ Ошибка регистрации {task_type} из {mod_name}: {e}")
