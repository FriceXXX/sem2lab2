import pytest
from src.validator import (
    ValidatedDescriptor,
    NonDataDescriptor,
    validate_task_id,
    validate_description,
    validate_priority,
    validate_status
)
from src.exceptions import (
    InvalidTaskIdError,
    InvalidDescriptionError,
    InvalidPriorityError,
    InvalidStatusError,
    TaskAlreadyCompletedError,
    InvalidStateTransitionError
)
from src.task import Task
from datetime import datetime, timedelta


class TestValidatedDescriptor:
    def test_validated_descriptor(self):
        class TestClass:
            field = ValidatedDescriptor('field', lambda x: x)

        obj = TestClass()
        obj.field = "test"
        assert obj.field == "test"


class TestNonDataDescriptor:
    def test_non_data_descriptor(self):
        class TestClass:
            prop = NonDataDescriptor('prop')

        obj = TestClass()
        obj.__dict__['prop'] = "test"
        assert obj.prop == "test"


class TestValidators:
    def test_validate_task_id_valid(self):
        """корректные ID."""
        valid_ids = [
            "TASK-001",
            "task123",
            "PROJECT-2-TASK",
            "simple"
        ]
        for task_id in valid_ids:
            result = validate_task_id(task_id)
            assert result == task_id

    def test_validate_task_id_invalid_types(self):
        """некорректные типы ID."""
        invalid_inputs = [123, None, [], {}]
        for invalid in invalid_inputs:
            with pytest.raises(InvalidTaskIdError):
                validate_task_id(invalid)

    def test_validate_task_id_empty(self):
        """пустой ID."""
        with pytest.raises(InvalidTaskIdError):
            validate_task_id("")

        with pytest.raises(InvalidTaskIdError):
            validate_task_id("   ")

    def test_validate_task_id_invalid_chars(self):
        """ID с недопустимыми символами"""
        with pytest.raises(InvalidTaskIdError):
            validate_task_id("task with spaces")

        with pytest.raises(InvalidTaskIdError):
            validate_task_id("task@#$")

    def test_validate_description_valid(self):
        """корректные описания"""
        valid_desc = [
            "Краткое описание",
            "Длинное описание" * 10,
            "   trimmed   "
        ]
        for desc in valid_desc:
            result = validate_description(desc)
            assert result == desc.strip()

    def test_validate_description_invalid_types(self):
        """некорректные типы описания"""
        with pytest.raises(InvalidDescriptionError):
            validate_description(123)

        with pytest.raises(InvalidDescriptionError):
            validate_description(None)

    def test_validate_description_empty(self):
        """пустое описание"""
        with pytest.raises(InvalidDescriptionError):
            validate_description("")

        with pytest.raises(InvalidDescriptionError):
            validate_description("   ")

    def test_validate_description_too_long(self):
        """слишком длинное описание"""
        long_desc = "A" * 1001
        with pytest.raises(InvalidDescriptionError):
            validate_description(long_desc)

    def test_validate_priority_valid(self):
        """корректнык приоритеты"""
        for priority in range(1, 6):
            result = validate_priority(priority)
            assert result == priority

    def test_validate_priority_invalid_types(self):
        """некорректные типы приоритета"""
        with pytest.raises(InvalidPriorityError):
            validate_priority("5")

        with pytest.raises(InvalidPriorityError):
            validate_priority(5.5)

    def test_validate_priority_out_of_range(self):
        """приоритет вне диапазона"""
        with pytest.raises(InvalidPriorityError):
            validate_priority(0)

        with pytest.raises(InvalidPriorityError):
            validate_priority(6)

    def test_validate_status_valid(self):
        """корректные статусы"""
        valid_statuses = ['created', 'in_progress', 'completed', 'cancelled']
        for status in valid_statuses:
            result = validate_status(status)
            assert result == status

    def test_validate_status_case_insensitive(self):
        """регистронезависимость статуса"""
        assert validate_status("CREATED") == "created"
        assert validate_status("In_Progress") == "in_progress"

    def test_validate_status_invalid(self):
        """некорректнsq статус"""
        with pytest.raises(InvalidStatusError):
            validate_status("invalid")



class TestTaskCreation:
    def test_create_valid_task(self):
        """корректная задача"""
        task = Task("TASK-001", "Test description", priority=3)

        assert task.id == "TASK-001"
        assert task.description == "Test description"
        assert task.priority == 3
        assert task.status == "created"
        assert isinstance(task.created_at, datetime)
        assert task.completed_at is None

    def test_create_task_with_defaults(self):
        """параметры по умолчанию"""
        task = Task("TASK-002", "Test")

        assert task.priority == 3
        assert task.status == "created"

    def test_create_task_invalid_id(self):
        """некорректный ID"""
        with pytest.raises(InvalidTaskIdError):
            Task("", "Test")

        with pytest.raises(InvalidTaskIdError):
            Task("invalid id", "Test")

    def test_create_task_invalid_description(self):
        """некорректное описание"""
        with pytest.raises(InvalidDescriptionError):
            Task("TASK-003", "")

        with pytest.raises(InvalidDescriptionError):
            Task("TASK-003", "A" * 1001)

    def test_create_task_invalid_priority(self):
        """некорректный приоритет"""
        with pytest.raises(InvalidPriorityError):
            Task("TASK-004", "Test", priority=0)

        with pytest.raises(InvalidPriorityError):
            Task("TASK-004", "Test", priority=6)

class TestTaskProperties:
    def test_created_at_readonly(self):
        task = Task("TASK-005", "Test")

        with pytest.raises(AttributeError):
            task.created_at = datetime.now()

    def test_is_active_property(self):
        """Проверка is_active на вычислимость"""
        task = Task("TASK-006", "Test")
        assert task.is_active is True

        task.start()
        assert task.is_active is True

        task.complete()
        assert task.is_active is False

    def test_is_completed_property(self):
        """Проверка is_completed"""
        task = Task("TASK-007", "Test")
        assert task.is_completed is False

        task.complete()
        assert task.is_completed is True

    def test_age_property(self):
        """Проверка возраста"""
        task = Task("TASK-008", "Test")
        assert task.age >= 0

        import time
        time.sleep(0.1)
        assert task.age > 0


class TestTaskStateTransitions:
    def test_start_task(self):
        """ перевод в работу"""
        task = Task("TASK-009", "Test")
        task.start()

        assert task.status == "in_progress"

    def test_start_already_started(self):
        """Повторный старт"""
        task = Task("TASK-010", "Test")
        task.start()
        task.start()

        assert task.status == "in_progress"

    def test_complete_task(self):
        """Завершение"""
        task = Task("TASK-011", "Test")
        task.start()
        task.complete()

        assert task.status == "completed"
        assert task.completed_at is not None
        assert task.is_completed is True

    def test_cancel_task(self):
        """Отмена"""
        task = Task("TASK-012", "Test")
        task.cancel()

        assert task.status == "cancelled"

    def test_complete_cancelled_task(self):
        """завершаем отменённую задачу"""
        task = Task("TASK-013", "Test")
        task.cancel()

        with pytest.raises(InvalidStateTransitionError):
            task.complete()

    def test_cancel_completed_task(self):
        """отменяем завершённую задачу"""
        task = Task("TASK-014", "Test")
        task.complete()

        with pytest.raises(InvalidStateTransitionError):
            task.cancel()

    def test_update_priority(self):
        """обновление приоритета"""
        task = Task("TASK-015", "Test", priority=3)
        task.update_priority(5)

        assert task
