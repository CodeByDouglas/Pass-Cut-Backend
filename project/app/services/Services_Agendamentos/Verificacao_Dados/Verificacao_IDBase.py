def verificar_id_base(id_base: str) -> bool:
  
    return len(id_base) == 10 and id_base.isdigit()