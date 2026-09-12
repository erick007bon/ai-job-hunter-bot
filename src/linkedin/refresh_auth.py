import os
import sys
import subprocess
import logging

# Configurar logging simple para que el bot pueda leerlo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_refresh():
    """
    Intenta ejecutar el script solve_linkedin_challenge.py para renovar cookies.
    """
    try:
        logger.info("[AuthRefresh] Ejecutando renovación de cookies (puede tardar un momento)...")
        # Dejamos que imprima directo en la consola para que el usuario pueda ver si pide PIN
        result = subprocess.run(
            [sys.executable, "solve_linkedin_challenge.py"],
            text=True,
            timeout=650 # 10 min max, para darle tiempo a esperar el PIN
        )
        if result.returncode == 0:
            logger.info("[AuthRefresh] Renovación exitosa")
            return True
        else:
            logger.error(f"[AuthRefresh] Error: el script de renovación devolvió código {result.returncode}")
            return False
    except subprocess.TimeoutExpired as e:
        logger.error(f"[AuthRefresh] Timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"[AuthRefresh] Excepción: {e}")
        return False
