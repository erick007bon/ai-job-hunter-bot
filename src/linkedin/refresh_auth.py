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
        logger.info("[AuthRefresh] Ejecutando renovación de cookies...")
        # Asumimos que solve_linkedin_challenge.py está en la raíz
        result = subprocess.run(
            [sys.executable, "solve_linkedin_challenge.py"],
            capture_output=True,
            text=True,
            timeout=300 # 5 min max
        )
        if result.returncode == 0:
            logger.info("[AuthRefresh] Renovación exitosa")
            return True
        else:
            logger.error(f"[AuthRefresh] Error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"[AuthRefresh] Excepción: {e}")
        return False
