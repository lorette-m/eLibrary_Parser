class AuthorizationException(Exception):
    """Исключение, возникающее при проблемах с авторизацией."""
    def __init__(self, message="Не удалось авторизоваться. Проверьте введенные данные."):
        self.message = message
        super().__init__(self.message)

class AuthorTableMoreOneRow(Exception):
    """Исключение, возникающее, если найдено слишком много авторов."""
    def __init__(self, message="Найдено более одного автора по данному запросу. Уточните полное ФИО или код автора"):
        self.message = message
        super().__init__(self.message)