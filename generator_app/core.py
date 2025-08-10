# core.py

class TaskController:
    """
    Ядро-диспетчер. Управляет регистрацией и вызовом
    специализированных генераторов задач.
    """
    def __init__(self):
        self._generators = {}
        print("✅ Ядро (TaskController) инициализировано.")

    def register_generator(self, task_type: str, generator_class):
        """
        Регистрирует новый генератор в системе.

        Args:
            task_type: Уникальный идентификатор типа задачи (e.g., 'series_class_1').
            generator_class: Класс генератора, который нужно связать с этим типом.
        """
        self._generators[task_type] = generator_class
        print(f"  -> Генератор для '{task_type}' зарегистрирован.")

    def create_task(self, task_type: str, complexity: int):
        """
        Создаёт экземпляр задачи, вызывая соответствующий генератор.

        Args:
            task_type: Идентификатор задачи, которую нужно сгенерировать.

        Returns:
            Объект задачи (наследник BaseTask) или None, если генератор не найден.
        """
        generator_class = self._generators.get(task_type)
        if not generator_class:
            print(f"⚠️ Ошибка: Генератор для типа '{task_type}' не найден.")
            return None
        
        # Создаем экземпляр нужного генератора и вызываем его метод generate()
        generator_instance = generator_class()
        print(f"⚙️ Ядро: Запрашиваю новую задачу у генератора '{task_type}'...")
        return generator_instance.generate()