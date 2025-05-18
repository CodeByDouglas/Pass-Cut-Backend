import sys
import os
from unittest.mock import MagicMock

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cria mocks para os módulos que não são encontrados
mock_db = MagicMock()
mock_extensions = MagicMock()
mock_extensions.db = mock_db

# Registra os mocks no sys.modules
sys.modules['app'] = MagicMock()
sys.modules['app.extensions'] = mock_extensions
sys.modules['app.models'] = MagicMock()
sys.modules['app.models.models'] = MagicMock()