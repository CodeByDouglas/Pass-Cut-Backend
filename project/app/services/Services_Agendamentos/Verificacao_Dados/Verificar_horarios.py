import re

def verificar_horario_valido(horario: str) -> bool:
    """
    Verifica se o horário está no formato válido XX:XX:XX (24h) e se não contém SQL injection, XSS ou scripts maliciosos.
    Retorna True se for válido, False caso contrário.
    """
    # Regex para formato HH:MM:SS (24h)
    padrao = r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"
    if not isinstance(horario, str):
        return False
    if not re.match(padrao, horario):
        return False
    # Verifica se contém caracteres suspeitos de SQL injection ou XSS
    if any(x in horario for x in [";", "--", "'", '"', "<", ">", "/", "\\", "script", "select", "insert", "update", "delete", "drop", "or", "and", "union"]):
        return False
    return True