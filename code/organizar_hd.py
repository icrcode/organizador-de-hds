import os
import shutil
import filecmp
import hashlib
from collections import defaultdict

def calcular_hash_arquivo(caminho_arquivo, block_size=65536):
    """Calcula o hash SHA-256 de um arquivo"""
    sha256 = hashlib.sha256()
    with open(caminho_arquivo, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def encontrar_arquivos_duplicados(pasta):
    """Encontra todos os arquivos duplicados em todas as pastas"""
    # Dicionário para armazenar arquivos por tamanho
    arquivos_por_tamanho = defaultdict(list)
    # Dicionário para armazenar arquivos por hash
    arquivos_por_hash = defaultdict(list)
    
    # Primeiro, agrupa arquivos por tamanho
    for raiz, _, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            caminho_completo = os.path.join(raiz, arquivo)
            try:
                tamanho = os.path.getsize(caminho_completo)
                arquivos_por_tamanho[tamanho].append(caminho_completo)
            except (OSError, IOError):
                continue
    
    # Para arquivos com mesmo tamanho, calcula o hash
    for tamanho, arquivos in arquivos_por_tamanho.items():
        if len(arquivos) > 1:  # Só verifica grupos com mais de um arquivo
            for arquivo in arquivos:
                try:
                    hash_arquivo = calcular_hash_arquivo(arquivo)
                    arquivos_por_hash[hash_arquivo].append(arquivo)
                except (OSError, IOError):
                    continue
    
    # Retorna apenas grupos de arquivos duplicados
    return {hash_: arquivos for hash_, arquivos in arquivos_por_hash.items() 
            if len(arquivos) > 1}

def move_duplicate_file(src_path, duplicates_folder):
    """Move um arquivo duplicado para a pasta de arquivos duplicados."""
    os.makedirs(duplicates_folder, exist_ok=True)
    filename = os.path.basename(src_path)
    dst_path = os.path.join(duplicates_folder, filename)
    
    # Se já existir um arquivo com o mesmo nome na pasta de duplicados,
    # adiciona um número ao final
    counter = 1
    while os.path.exists(dst_path):
        base_name, ext = os.path.splitext(filename)
        dst_path = os.path.join(duplicates_folder, f"{base_name}_{counter}{ext}")
        counter += 1
    
    shutil.move(src_path, dst_path)
    return dst_path

def main():
    # Configurações iniciais
    hd_path = input("Digite o caminho completo do HD externo: ").strip()
    log_file = os.path.join(hd_path, "reorganizacao_log.txt")
    pasta_duplicados = os.path.join(hd_path, "Arquivos Duplicados")
    
    if not os.path.exists(hd_path):
        print("Caminho não encontrado!")
        return
    
    # Etapa 1: Coletar informações sobre a estrutura atual
    print("\n=== ETAPA 1: Analisando estrutura de pastas ===")
    folders_by_name = defaultdict(list)
    
    for root, dirs, files in os.walk(hd_path):
        for dir_name in dirs:
            full_path = os.path.join(root, dir_name)
            folders_by_name[dir_name.lower()].append(full_path)
    
    # Etapa 2: Identificar pastas com nomes duplicados
    print("\n=== ETAPA 2: Identificando pastas duplicadas por nome ===")
    duplicate_folders = {name: paths for name, paths in folders_by_name.items() if len(paths) > 1}
    
    if not duplicate_folders:
        print("Nenhuma pasta duplicada encontrada por nome.")
    else:
        print(f"Encontradas {len(duplicate_folders)} pastas com nomes duplicados:")
        for name, paths in duplicate_folders.items():
            print(f"\nPasta '{name}':")
            for path in paths:
                print(f"  - {path}")
    
    # Etapa 3: Comparar conteúdo de pastas duplicadas
    print("\n=== ETAPA 3: Comparando conteúdo de pastas duplicadas ===")
    identical_groups = []
    
    for name, paths in duplicate_folders.items():
        compared = set()
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                path1, path2 = paths[i], paths[j]
                if (path1, path2) not in compared:
                    comparison = filecmp.dircmp(path1, path2)
                    if not comparison.left_only and not comparison.right_only and not comparison.diff_files:
                        identical_groups.append((path1, path2))
                    compared.add((path1, path2))
    
    # Nova Etapa: Encontrar todos os arquivos duplicados
    print("\n=== ETAPA 4: Procurando arquivos duplicados em todas as pastas ===")
    arquivos_duplicados = encontrar_arquivos_duplicados(hd_path)
    
    if arquivos_duplicados:
        print(f"\nEncontrados {len(arquivos_duplicados)} grupos de arquivos duplicados.")
        
        # Criar pasta para arquivos duplicados
        os.makedirs(pasta_duplicados, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write("\n=== Arquivos Duplicados Encontrados ===\n")
            
            for hash_arquivo, arquivos in arquivos_duplicados.items():
                print(f"\nArquivos idênticos encontrados:")
                for i, arquivo in enumerate(arquivos):
                    print(f"{i+1}: {arquivo}")
                
                action = input("\nDeseja (1) Manter todos, (2) Manter apenas o primeiro, "
                             "(3) Escolher manualmente qual manter? ").strip()
                
                if action == '2':
                    # Manter o primeiro arquivo e mover os outros para a pasta de duplicados
                    primeiro = arquivos[0]
                    for arquivo in arquivos[1:]:
                        novo_nome = os.path.join(pasta_duplicados, os.path.basename(arquivo))
                        contador = 1
                        while os.path.exists(novo_nome):
                            base, ext = os.path.splitext(os.path.basename(arquivo))
                            novo_nome = os.path.join(pasta_duplicados, f"{base}_{contador}{ext}")
                            contador += 1
                        shutil.move(arquivo, novo_nome)
                        log.write(f"Arquivo duplicado movido: {arquivo} -> {novo_nome}\n")
                        print(f"Movido: {arquivo} -> {novo_nome}")
                
                elif action == '3':
                    manter = int(input("Digite o número do arquivo que deseja manter: ").strip()) - 1
                    if 0 <= manter < len(arquivos):
                        arquivo_manter = arquivos[manter]
                        for i, arquivo in enumerate(arquivos):
                            if i != manter:
                                novo_nome = os.path.join(pasta_duplicados, os.path.basename(arquivo))
                                contador = 1
                                while os.path.exists(novo_nome):
                                    base, ext = os.path.splitext(os.path.basename(arquivo))
                                    novo_nome = os.path.join(pasta_duplicados, f"{base}_{contador}{ext}")
                                    contador += 1
                                shutil.move(arquivo, novo_nome)
                                log.write(f"Arquivo duplicado movido: {arquivo} -> {novo_nome}\n")
                                print(f"Movido: {arquivo} -> {novo_nome}")
    else:
        print("Nenhum arquivo duplicado encontrado.")
    
    # Continuar com o processamento de pastas idênticas
    print("\n=== ETAPA 5: Processando pastas idênticas ===")
    with open(log_file, 'a') as log:
        for group in identical_groups:
            print(f"\nPastas idênticas encontradas:")
            print(f"1: {group[0]}")
            print(f"2: {group[1]}")
            
            action = input("Deseja (1) Manter ambas, (2) Manter apenas a primeira, "
                         "(3) Manter apenas a segunda, ou (4) Mesclar conteúdo? ").strip()
            
            if action == '2':
                log.write(f"Removendo pasta duplicada: {group[1]}\n")
                shutil.rmtree(group[1])
                print(f"Pasta {group[1]} removida.")
            elif action == '3':
                log.write(f"Removendo pasta duplicada: {group[0]}\n")
                shutil.rmtree(group[0])
                print(f"Pasta {group[0]} removida.")
            elif action == '4':
                for item in os.listdir(group[1]):
                    src = os.path.join(group[1], item)
                    dst = os.path.join(group[0], item)
                    if not os.path.exists(dst):
                        shutil.move(src, dst)
                log.write(f"Conteúdo mesclado: {group[1]} -> {group[0]}\n")
                shutil.rmtree(group[1])
                print(f"Pastas mescladas em {group[0]}")
            else:
                print("Ambas pastas mantidas.")
    
    print("\nProcesso concluído! Um log foi salvo em", log_file)

if __name__ == "__main__":
    main()