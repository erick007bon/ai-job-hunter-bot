import json
import os
import re
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

cookies_path = os.path.expanduser(r'~/.linkedin-mcp/cookies.json')
if not os.path.isfile(cookies_path):
    print("No se encontró cookies.json en ~/.linkedin-mcp")
    exit(1)

with open(cookies_path, 'r', encoding='utf-8') as f:
    cookies = json.load(f)

li_at = ''
jsessionid = ''
for c in cookies:
    if c.get('name') == 'li_at':
        li_at = c.get('value', '')
    elif c.get('name') == 'JSESSIONID':
        jsessionid = c.get('value', '')

if not li_at or not jsessionid:
    print("No se encontraron li_at o JSESSIONID en cookies.json")
    exit(1)

print(f"✓ li_at fresco: {li_at[:25]}...")
print(f"✓ JSESSIONID fresco: {jsessionid[:25]}...")

env_path = '.env'
with open(env_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith('LINKEDIN_LI_AT='):
        new_lines.append(f'LINKEDIN_LI_AT="{li_at}"\n')
    elif line.startswith('LINKEDIN_JSESSIONID='):
        new_lines.append(f'LINKEDIN_JSESSIONID="{jsessionid}"\n')
    else:
        new_lines.append(line)

with open(env_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ .env actualizado con las cookies activas de tu sesión de LinkedIn!")
