import base64
import json

def verificar_token_jwt(token: str) -> bool:
    """
    Verifica se uma string é um token JWT válido.

    Essa função checa se o token possui três partes separadas por pontos ('.') e,
    em seguida, tenta decodificar a parte do header e do payload que estão em base64 urlsafe.
    Se ambos puderem ser decodificados e transformados em JSON, o token é considerado válido.

    Parameters:
        token (str): O token JWT a ser verificado.
    
    Returns:
        bool: True se o token parecer ser um JWT válido, False caso contrário.
    """
    # Verifica se o token possui três partes separadas por ponto.
    segments = token.split('.')
    if len(segments) != 3:
        return False

    # Função auxiliar para decodificar cada segmento, ajustando o padding se necessário.
    def decode_segment(segment: str) -> bytes:
        padding = '=' * (-len(segment) % 4)
        return base64.urlsafe_b64decode(segment + padding)

    try:
        # Tenta decodificar o header (primeira parte)
        header_bytes = decode_segment(segments[0])
        header = json.loads(header_bytes.decode('utf-8'))
        
        # Tenta decodificar o payload (segunda parte)
        payload_bytes = decode_segment(segments[1])
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # O token não necessariamente precisa ter um payload JSON válido para a verificação estrutural,
        # mas se chegamos até aqui sem exceções, consideramos que o token tem o formato adequado.
    except Exception:
        return False

    return True