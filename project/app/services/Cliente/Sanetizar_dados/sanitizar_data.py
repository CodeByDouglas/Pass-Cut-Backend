from datetime import datetime, timedelta

def verificar_data(data_input: str) -> bool:
    """
    Recebe uma data como string e verifica se:
      1. A data é válida no formato 'YYYY-MM-DD'.
      2. A data está entre a data atual e os próximos 30 dias.
    
    Parâmetros:
        data_input (str): Data em formato 'YYYY-MM-DD'.
        
    Retorna:
        bool: True se a data for válida e estiver dentro do intervalo permitido, False caso contrário.
    """
    try:
        data = datetime.strptime(data_input, "%Y-%m-%d")
    except ValueError:
        return False
    
    hoje = datetime.now()
    limite = hoje + timedelta(days=30)
    
    if hoje.date() <= data.date() <= limite.date():
        return True
    return False