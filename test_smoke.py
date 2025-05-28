import sys
import types

# Создаем класс-заглушку, который имитирует поведение Listener
class MockListener:
    def __init__(self, on_press=None):
        self.on_press = on_press
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def join(self):
        pass

# Создаем мок-модуль keyboard
mock_keyboard = types.ModuleType("pynput.keyboard")
mock_keyboard.Listener = MockListener

# Подменяем модули в sys.modules
sys.modules["pynput"] = types.ModuleType("pynput")
sys.modules["pynput.keyboard"] = mock_keyboard

# Теперь можно безопасно импортировать main, даже если там используется pynput.keyboard.Listener
import main

def test_import_main():
    assert True