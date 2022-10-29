from pydantic import BaseModel

from txml_connector_adapter.data_objects.commands import Command

def test_command_decorator():
    class TestClass(BaseModel):
        field: str

    command_name = "test_name"
    decorated_test_class = Command(name=command_name)(TestClass)
    assert type(decorated_test_class) == type(BaseModel)
    decorated_test_class_instance = decorated_test_class(field="kek")
    assert type(decorated_test_class_instance) == TestClass
    assert decorated_test_class._command_name == command_name
    assert decorated_test_class_instance._command_name == command_name

def test_command_decorator_auto_name():
    class TestClass(BaseModel):
        field: str

    decorated_test_class = Command()(TestClass)
    decorated_test_class_instance = decorated_test_class(field="kek")
    assert decorated_test_class._command_name == "TestClass"
    assert decorated_test_class_instance._command_name == "TestClass"
