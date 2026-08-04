import yaml, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from validate_email import validate_email
from webdriver_manager.chrome import ChromeDriverManager
from linkedineasyapply import LinkedinEasyApply

def init_browser():
    browser_options = Options()
    options = [
        '--disable-blink-features',
        '--no-sandbox',
        '--start-maximized',
        '--disable-extensions',
        '--ignore-certificate-errors',
        '--headless=new',
        '--disable-blink-features=AutomationControlled'
    ]

    # No usamos user-data-dir local porque correrá en GitHub Actions Ubuntu

    for option in options:
        browser_options.add_argument(option)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=browser_options)
    driver.implicitly_wait(1)  # Wait time in seconds to allow loading of elements
    driver.set_window_position(0, 0)
    driver.maximize_window()
    return driver

def _overlay_env_vars(parameters):
    """
    El archivo auto_apply_config.yaml commiteado en git NO contiene datos
    personales (el repo es publico). Los valores reales se inyectan aqui
    desde variables de entorno en runtime (local .env o GitHub Secrets).
    Si una variable no esta definida, el placeholder "CHANGE_ME" se queda
    y la validacion de abajo se encarga de frenar la ejecucion en vez de
    postular con datos falsos/vacios.
    """
    env_map = {
        'CANDIDATE_EMAIL': ('email',),
        'CANDIDATE_OPENAI_KEY': ('openaiApiKey',),
        'CANDIDATE_FIRST_NAME': ('personalInfo', 'First Name'),
        'CANDIDATE_LAST_NAME': ('personalInfo', 'Last Name'),
        'CANDIDATE_PHONE_COUNTRY_CODE': ('personalInfo', 'Phone Country Code'),
        'CANDIDATE_PHONE': ('personalInfo', 'Mobile Phone Number'),
        'CANDIDATE_STREET': ('personalInfo', 'Street address'),
        'CANDIDATE_CITY': ('personalInfo', 'City'),
        'CANDIDATE_STATE': ('personalInfo', 'State'),
        'CANDIDATE_ZIP': ('personalInfo', 'Zip'),
        'CANDIDATE_LINKEDIN': ('personalInfo', 'Linkedin'),
        'CANDIDATE_WEBSITE': ('personalInfo', 'Website'),
        'CANDIDATE_PRONOUNS': ('personalInfo', 'Pronouns'),
        'CANDIDATE_GENDER': ('eeo', 'gender'),
        'CANDIDATE_RACE': ('eeo', 'race'),
        'CANDIDATE_VETERAN': ('eeo', 'veteran'),
        'CANDIDATE_DISABILITY': ('eeo', 'disability'),
        'CANDIDATE_CITIZENSHIP': ('eeo', 'citizenship'),
        'CANDIDATE_CLEARANCE': ('eeo', 'clearance'),
    }
    for env_key, path in env_map.items():
        value = os.environ.get(env_key)
        if not value:
            continue
        if len(path) == 1:
            parameters[path[0]] = value
        else:
            parameters[path[0]][path[1]] = value
    return parameters


def validate_yaml():
    with open("auto_apply_config.yaml", 'r', encoding='utf-8') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    parameters = _overlay_env_vars(parameters)

    mandatory_params = ['email',
                        'password',
                        'disableAntiLock',
                        'remote',
                        'lessthanTenApplicants',
                        'newestPostingsFirst',
                        'experienceLevel',
                        'jobTypes',
                        'date',
                        'positions',
                        'locations',
                        'residentStatus',
                        'distance',
                        'outputFileDirectory',
                        'checkboxes',
                        'universityGpa',
                        'languages',
                        'experience',
                        'personalInfo',
                        'eeo',
                        'uploads']

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise Exception(mandatory_param + ' is not defined in the config.yaml file!')

    assert validate_email(parameters['email'])
    assert len(str(parameters['password'])) > 0
    assert isinstance(parameters['disableAntiLock'], bool)
    assert isinstance(parameters['remote'], bool)
    assert isinstance(parameters['lessthanTenApplicants'], bool)
    assert isinstance(parameters['newestPostingsFirst'], bool)
    assert isinstance(parameters['residentStatus'], bool)
    assert len(parameters['experienceLevel']) > 0
    experience_level = parameters.get('experienceLevel', [])
    at_least_one_experience = False

    for key in experience_level.keys():
        if experience_level[key]:
            at_least_one_experience = True
    assert at_least_one_experience

    assert len(parameters['jobTypes']) > 0
    job_types = parameters.get('jobTypes', [])
    at_least_one_job_type = False
    for key in job_types.keys():
        if job_types[key]:
            at_least_one_job_type = True

    assert at_least_one_job_type
    assert len(parameters['date']) > 0
    date = parameters.get('date', [])
    at_least_one_date = False

    for key in date.keys():
        if date[key]:
            at_least_one_date = True
    assert at_least_one_date

    approved_distances = {0, 5, 10, 25, 50, 100}
    assert parameters['distance'] in approved_distances
    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert len(parameters['uploads']) >= 1 and 'resume' in parameters['uploads']
    assert len(parameters['checkboxes']) > 0

    checkboxes = parameters.get('checkboxes', [])
    assert isinstance(checkboxes['driversLicence'], bool)
    assert isinstance(checkboxes['requireVisa'], bool)
    assert isinstance(checkboxes['legallyAuthorized'], bool)
    assert isinstance(checkboxes['certifiedProfessional'], bool)
    assert isinstance(checkboxes['urgentFill'], bool)
    assert isinstance(checkboxes['commute'], bool)
    assert isinstance(checkboxes['backgroundCheck'], bool)
    assert isinstance(checkboxes['securityClearance'], bool)
    assert 'degreeCompleted' in checkboxes
    assert isinstance(parameters['universityGpa'], (int, float))

    languages = parameters.get('languages', [])
    language_types = {'none', 'conversational', 'professional', 'native or bilingual'}
    for language in languages:
        assert languages[language].lower() in language_types

    experience = parameters.get('experience', [])
    for tech in experience:
        assert isinstance(experience[tech], int)
    assert 'default' in experience

    assert len(parameters['personalInfo'])
    personal_info = parameters.get('personalInfo', [])
    for info in personal_info:
        assert personal_info[info] != ''

    assert len(parameters['eeo'])
    eeo = parameters.get('eeo', [])
    for survey_question in eeo:
        assert eeo[survey_question] != ''

    # Salvaguarda: si algun placeholder "CHANGE_ME" quedo sin resolver por
    # variable de entorno, NO se debe postular con eso (enviaria datos falsos
    # o vacios a empresas reales). Frenamos con un error explicito en vez de
    # continuar en silencio.
    unresolved = []
    if str(parameters.get('email', '')).strip().upper().startswith('CHANGE_ME'):
        unresolved.append('email (CANDIDATE_EMAIL)')
    for field, env_hint in [
        ('First Name', 'CANDIDATE_FIRST_NAME'), ('Last Name', 'CANDIDATE_LAST_NAME'),
        ('Mobile Phone Number', 'CANDIDATE_PHONE'), ('City', 'CANDIDATE_CITY'),
    ]:
        if str(personal_info.get(field, '')).strip().upper().startswith('CHANGE_ME'):
            unresolved.append(f'personalInfo.{field} ({env_hint})')
    for field, env_hint in [
        ('gender', 'CANDIDATE_GENDER'), ('race', 'CANDIDATE_RACE'),
        ('veteran', 'CANDIDATE_VETERAN'), ('disability', 'CANDIDATE_DISABILITY'),
    ]:
        if str(eeo.get(field, '')).strip().upper().startswith('CHANGE_ME'):
            unresolved.append(f'eeo.{field} ({env_hint})')
    if unresolved:
        raise Exception(
            "auto_apply_config.yaml tiene placeholders sin resolver y no hay "
            "variables de entorno que los reemplacen. Por seguridad, NO se va a "
            "postular con datos de relleno. Define estas variables antes de correr:\n  - "
            + "\n  - ".join(unresolved)
        )

    if not parameters.get('openaiApiKey') or str(parameters.get('openaiApiKey')).strip().upper() in ('CHANGE_ME', 'SK-PROJ-YOUR-OPENAI-API-KEY'):
        # Antes: se enviaban las postulaciones igual, con respuestas de texto EN BLANCO
        # a las preguntas del formulario. Eso produce postulaciones incompletas/pobres
        # a empresas reales a tu nombre. Ahora se frena explicitamente en vez de
        # continuar en silencio con respuestas vacias.
        raise Exception(
            "OPENAI_API_KEY (via CANDIDATE_OPENAI_KEY) no esta configurada. "
            "Postular sin ella genera respuestas en blanco en las preguntas del "
            "formulario. Configura la variable de entorno o corre con debug=True "
            "y revisa manualmente antes de habilitar esto de nuevo."
        )

    return parameters

if __name__ == '__main__':
    parameters = validate_yaml()
    browser = init_browser()

    # Inyección de Sesión de LinkedIn para Evadir Captchas en la Nube
    print("Abriendo LinkedIn.com...")
    browser.get("https://www.linkedin.com")
    li_at = os.environ.get("LINKEDIN_LI_AT")
    logged_in_by_cookie = False
    
    if li_at:
        print("Inyectando Cookie de Sesion de LinkedIn (li_at) desde Secrets...")
        browser.add_cookie({"name": "li_at", "value": li_at, "domain": ".linkedin.com"})
        print("Cargando feed para validar sesión...")
        browser.get("https://www.linkedin.com/feed/")
        import time
        time.sleep(5)
        print(f"URL actual despues de inyectar cookie: {browser.current_url}")
        if "feed" in browser.current_url:
            print("¡Inicio de sesión EXITOSO mediante cookie li_at! Saltando login manual.")
            logged_in_by_cookie = True
        else:
            print("La cookie li_at no fue suficiente para iniciar sesión. Se intentará login por credenciales.")
    else:
        print("ADVERTENCIA: No se encontró la cookie LINKEDIN_LI_AT en el entorno.")

    bot = LinkedinEasyApply(parameters, browser)
    if not logged_in_by_cookie:
        print("Ejecutando login manual por credenciales...")
        bot.login()
        bot.security_check()
    else:
        print("Procediendo directamente a postular...")
    
    bot.start_applying()