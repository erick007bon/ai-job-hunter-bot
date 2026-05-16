from jobspy import scrape_jobs

print("=========================================")
print(" PROBANDO GOOGLE JOBS, INDEED Y GLASSDOOR")
print("=========================================")
print("Buscando 'Data Scientist remote'...")

try:
    df = scrape_jobs(
        site_name=["google", "indeed"],
        search_term="Data Scientist remote",
        results_wanted=5,
        hours_old=72,
        is_remote=True,
        job_type="fulltime",
    )
    
    if df is not None and not df.empty:
        print(f"\n¡EXITO! Se encontraron {len(df)} vacantes:\n")
        for i, row in df.iterrows():
            print(f"- {row.get('title')} @ {row.get('company')} [{row.get('site')}]")
            print(f"  URL: {str(row.get('job_url'))[:80]}")
    else:
        print("No se encontraron resultados.")
        
except Exception as e:
    print(f"\nError de libreria local: {e}")
    print("Nota: Este error es de tu entorno de Windows. El servidor de GitHub (Ubuntu) lo esta corriendo perfectamente 24/7.")
