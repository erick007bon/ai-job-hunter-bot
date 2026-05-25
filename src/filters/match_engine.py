"""
Motor de filtrado inteligente: filtra trabajos por keywords relevantes al perfil de Erick
"""

KEYWORDS_POSITIVOS = [
    'python', 'data', 'analyst', 'engineer', 'scientist', 'machine learning',
    'ml', 'ai', 'sql', 'power bi', 'economist', 'econom', 'analytics',
    'backend', 'fastapi', 'django', 'flask', 'remote', 'remoto',
    'junior', 'mid', 'entry', 'associate', 'intern', 'trainee',
    'llm', 'nlp', 'deep learning', 'pytorch', 'tensorflow',
]

KEYWORDS_NEGATIVOS = [
    'senior only', '10+ years', '8+ years', 'director', 'vp of',
    'chief', 'c-level', 'native english required', 'fluent english required',
    'clearance', 'us citizen only', 'must be us',
]

class MatchEngine:
    def filter_jobs(self, jobs: list) -> list:
        resultados = []
        vistos = set()

        for job in jobs:
            url = job.get('url', '')
            if url in vistos:
                continue
            vistos.add(url)

            texto = (
                job.get('title', '') + ' ' +
                job.get('description', '') + ' ' +
                ' '.join(str(t) for t in job.get('tags', []))
            ).lower()

            # Verificar al menos 1 keyword positivo
            tiene_match = any(kw in texto for kw in KEYWORDS_POSITIVOS)
            # Verificar que no tiene keywords negativos bloqueantes
            bloqueado = any(kw in texto for kw in KEYWORDS_NEGATIVOS)

            if tiene_match and not bloqueado:
                resultados.append(job)

        # Ordenar: primero los que tengan mas matches
        def score(j):
            t = (j.get('title','') + ' ' + j.get('description','')).lower()
            return sum(1 for kw in KEYWORDS_POSITIVOS if kw in t)

        resultados.sort(key=score, reverse=True)
        return resultados[:30]
