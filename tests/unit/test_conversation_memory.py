import unittest

from app.services.conversation_memory import ConversationMemory


class TestConversationMemory(unittest.TestCase):
    def setUp(self):
        """
        Configura una nueva instancia de ConversationMemory antes de cada prueba.
        """
        self.memory = ConversationMemory(max_history=5)

    def test_initialization(self):
        """
        Prueba que la memoria se inicializa correctamente.
        """
        self.assertEqual(self.memory.get_history(), [])
        self.assertEqual(self.memory.max_history, 5)

    def test_add_message(self):
        """
        Prueba que se pueden añadir mensajes a la memoria.
        """
        self.memory.add_message("user", "Hola")
        self.memory.add_message("model", "Hola, ¿cómo estás?")

        history = self.memory.get_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hola")
        self.assertEqual(history[1]["role"], "model")
        self.assertEqual(history[1]["content"], "Hola, ¿cómo estás?")

    def test_get_history(self):
        """
        Prueba que el historial se devuelve correctamente.
        """
        self.memory.add_message("user", "Test 1")
        self.memory.add_message("model", "Test 2")

        self.assertEqual(len(self.memory.get_history()), 2)

        history_copy = self.memory.get_history()
        history_copy.append("mutated")

        # Asegurarse de que get_history devuelve una copia, no la referencia original
        self.assertIsNot(self.memory.get_history(), history_copy)
        self.assertEqual(len(self.memory.get_history()), 2)

    def test_clear_memory(self):
        """
        Prueba que la memoria se puede limpiar.
        """
        self.memory.add_message("user", "No me borraré")
        self.memory.clear()
        self.assertEqual(self.memory.get_history(), [])

    def test_max_history_limit(self):
        """
        Prueba que la memoria respeta el límite máximo de historial.
        """
        for i in range(10):
            self.memory.add_message("user", f"Mensaje {i}")

        history = self.memory.get_history()
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0]["content"], "Mensaje 5")
        self.assertEqual(history[4]["content"], "Mensaje 9")

    def test_add_message_with_invalid_role(self):
        """
        Prueba que se lanza un error si el rol no es válido.
        """
        with self.assertRaises(ValueError):
            self.memory.add_message("invalid_role", "Este mensaje fallará")


if __name__ == "__main__":
    unittest.main()
