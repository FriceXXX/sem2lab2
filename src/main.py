from datetime import datetime

from src.task import Task
from src.exceptions import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusError,
    TaskAlreadyCompletedError,
    InvalidStateTransitionError
)


def demonstrate_descriptors():

    print("\n\nDemonstrating descriptors"+"-" *60)

    try:
        task = Task("TASK-001", "Реализовать валидацию дескрипторов", priority=4)
        print(f"\nЗадача создана: {task.id}")

        print(f"  ID: {task.id}")
        print(f"  Описание: {task.description}")
        print(f"  Приоритет: {task.priority}")
        print(f"  Статус: {task.status}")

        print("\nПопытка установить некорректные значения:")

        try:
            task.id = "invalid id with spaces"
        except InvalidTaskIdError as e:
            print(f"Ошибка при установке ID: {e}")

        try:
            task.priority = 10
        except InvalidPriorityError as e:
            print(f"Ошибка при установке приоритета: {e}")

        try:
            task.description = ""
        except InvalidDescriptionError as e:
            print(f"Ошибка при установке описания: {e}")

    except Exception as e:
        print(f"Ошибка: {e}")


def demonstrate_properties():
    print("\n\nDemonstrating properties" + "-" *60)

    task = Task("TASK-002", "Изучить property в Python", priority=3)

    print(f"\nЗадача: {task.id}")
    print(f"  Время создания: {task.created_at.strftime('%H:%M:%S')}")
    print(f"  Активна: {task.is_active}")
    print(f"  Завершена: {task.is_completed}")
    print(f"  Возраст: {task.age:.2f} часов")

    try:
        task.created_at = datetime.now()
    except AttributeError as e:
        print(f"Нельзя изменить created_at: {e}")

    try:
        task.is_active = False
    except AttributeError as e:
        print(f"Нельзя установить is_active: {e}")


def demonstrate_state_transitions():
    print("\n\nDemonstrating state transitions" + "-" *60)
    task = Task("TASK-003", "Реализовать конечный автомат задачи", priority=4)

    print(f"\nНачальное состояние: {task.status}")
    print(f"Активна: {task.is_active}")

    task.start()
    print(f"  После start(): статус = {task.status}, активна = {task.is_active}")

    task.complete()
    print(f"  После complete(): статус = {task.status}, активна = {task.is_active}")
    print(f"  Время завершения: {task.completed_at.strftime('%H:%M:%S')}")

    print("Завершаем завершенную")
    try:
        task.start()
    except TaskAlreadyCompletedError as e:
        print(f"{e}")

    try:
        task.update_priority(5)
    except TaskAlreadyCompletedError as e:
        print(f"{e}")


def demonstrate_invariants():
    print("\n\nDemonstrating invariants" + "-" *60)

    try:
        Task("", "Пустой ID", priority=3)
    except InvalidTaskIdError as e:
        print(f"{e}")

    try:
        Task("TASK-005", "A" * 1001, priority=3)
    except InvalidDescriptionError as e:
        print(f"{e}")

    try:
        Task("TASK-006", "Некорректный приоритет", priority=0)
    except InvalidPriorityError as e:
        print(f"{e}")

    try:
        Task("TASK-007", "Некорректный статус", status="invalid")
    except InvalidStatusError as e:
        print(f"{e}")

    task = Task("TASK-008", "Тест переходов", priority=3)

    task.start()
    task.cancel()

    try:
        task.complete()
    except InvalidStateTransitionError as e:
        print(f"{e}")


def demonstrate_non_data_descriptor():
    task1 = Task("TASK-009", "Задача 1", priority=3)
    task2 = Task("TASK-010", "Задача 2", priority=4)

    print(f"\n{task1.id}: is_active = {task1.is_active}")
    print(f"{task2.id}: is_active = {task2.is_active}")

    task1.start()
    task2.start()
    task2.complete()

    print(f"\nПосле изменений:")
    print(f"{task1.id}: is_active = {task1.is_active}")
    print(f"{task2.id}: is_active = {task2.is_active}")

    print(f"  task1.__dict__: {task1.__dict__.get('is_active', 'не найдено')}")
    print(f"  task2.__dict__: {task2.__dict__.get('is_active', 'не найдено')}")



if __name__ == "__main__":
    print("Demonstrating" + "-" *60)

    demonstrate_descriptors()
    demonstrate_properties()
    demonstrate_state_transitions()
    demonstrate_invariants()
    demonstrate_non_data_descriptor()