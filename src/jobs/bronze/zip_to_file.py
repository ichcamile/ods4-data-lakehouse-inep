import zipfile
import os
import shutil

# Base paths
base_dir = '/Users/mile/Documents/Projetos/ods4-data-lakehouse-inep'
zip_dir = os.path.join(base_dir, 'data', 'raw')
file_path = os.path.join(base_dir, 'data', 'bronze')

for ano in range(2004, 2026):
    # Check both versions of the filename (with and without trailing underscore)
    zip_name_with_underscore = f'microdados_censo_escolar_{ano}_.zip'
    zip_name_without_underscore = f'microdados_censo_escolar_{ano}.zip'
    
    path_with_underscore = os.path.join(zip_dir, zip_name_with_underscore)
    path_without_underscore = os.path.join(zip_dir, zip_name_without_underscore)
    
    if os.path.exists(path_with_underscore):
        target_zip_path = path_with_underscore
        zip_name = zip_name_with_underscore
    elif os.path.exists(path_without_underscore):
        target_zip_path = path_without_underscore
        zip_name = zip_name_without_underscore
    else:
        print(f'Aviso: Arquivo não encontrado, pulando -> {zip_name_without_underscore} (ou {zip_name_with_underscore})')
        continue

    destino_ano = os.path.join(file_path, f'ano={ano}')
    os.makedirs(destino_ano, exist_ok=True)

    print(f'\n--- Iniciando extração do ano {ano} ---')

    with zipfile.ZipFile(target_zip_path, 'r') as zip_ref:
        filesInZip = zip_ref.namelist()

        for files in filesInZip:
            if 'dados/' in files.lower() and files.lower().endswith('.csv'):
                name_file = os.path.basename(files)
                if not name_file:
                    continue
                final_path = os.path.join(destino_ano, name_file)

                with zip_ref.open(files) as source, open(final_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                    
                print(f'  -> Salvo: {final_path}')

print('\n✅ Processo de extração de todos os anos concluído!')
