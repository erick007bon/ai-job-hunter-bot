"""
Scholarship Hunter — Script autónomo para buscar y postular becas internacionales.
Corre separado del bot de empleos para no mezclar flujos.

Uso:
    python scholarship_hunter.py             # Modo draft (no envía nada)
    python scholarship_hunter.py --report    # Genera reporte de becas disponibles
"""
import os
import sys
import datetime
import argparse

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scholarships.scholarship_scraper import ScholarshipScraper
from src.scholarships.scholarship_agent import ScholarshipAgent
from src.notifications.telegram_notifier import notify_scholarship_found, send_telegram
from src.config import Config


def main():
    parser = argparse.ArgumentParser(description='Scholarship Hunter Bot')
    parser.add_argument('--report', action='store_true', help='Solo generar reporte (no cartas)')
    args = parser.parse_args()

    print("=" * 60)
    print(" 🎓 SCHOLARSHIP HUNTER — Becas Internacionales IA/Datos")
    print("=" * 60)

    scraper = ScholarshipScraper()
    scholarships = scraper.fetch_all()
    print(f"\n[BECAS] Encontradas: {len(scholarships)} oportunidades\n")

    if args.report:
        # Solo imprimir resumen
        for s in scholarships:
            print(f"  📌 {s['name']}")
            print(f"     Org: {s['organization']}")
            print(f"     Monto: {s['amount']}")
            print(f"     Deadline: {s['deadline']}")
            print(f"     URL: {s['url']}\n")
        return

    # Generar cartas de motivación
    agent = ScholarshipAgent()
    report_lines = []

    for scholarship in scholarships:
        print(f"\n[PROCESANDO] {scholarship['name']}")
        print(f"  -> Generando carta de motivación con IA...")
        letter = agent.generate_motivation_letter(scholarship)
        path = agent.save_letter(scholarship, letter)
        print(f"  -> Guardada en: {path}")

        # Notificar por Telegram
        notify_scholarship_found(scholarship)

        report_lines.append(
            f"### 🎓 {scholarship['name']}\n"
            f"- **Organización:** {scholarship['organization']}\n"
            f"- **Monto:** {scholarship['amount']}\n"
            f"- **Deadline:** {scholarship['deadline']}\n"
            f"- **Carta guardada:** {path}\n"
            f"- **Aplica aquí:** {scholarship['url']}\n"
        )

    # Generar reporte
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today_file = datetime.datetime.now().strftime("%Y-%m-%d")
    report = f"# 🎓 SCHOLARSHIP HUNTER — Reporte {today}\n\n"
    report += f"> **Becas encontradas:** {len(scholarships)}\n\n---\n\n"
    report += "\n".join(report_lines)
    report += "\n\n---\n*Scholarship Hunter — FCH-ARX V4 Research Profile*"

    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(Config.REPORTS_DIR, f"becas_{today_file}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[DONE] Reporte de becas guardado: {filepath}")
    send_telegram(f"✅ Scholarship Hunter completado: {len(scholarships)} becas procesadas.")


if __name__ == "__main__":
    main()
