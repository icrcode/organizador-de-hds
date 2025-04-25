import os
import shutil
import filecmp
import hashlib
from collections import defaultdict

def obter_pasta_tipo_arquivo(extensao):
    """
    Retorna o nome da pasta para um determinado tipo de arquivo baseado na extensão.
    """
    extensao = extensao.lower().lstrip('.')
    
    # Mapeamento de extensões para tipos de arquivo
    tipos = {
        # Documentos
        'pdf': 'PDFs',
        'doc': 'Documentos',
        'docx': 'Documentos',
        'txt': 'Documentos',
        'rtf': 'Documentos',
        'odt': 'Documentos',
        'xls': 'Planilhas',
        'xlsx': 'Planilhas',
        'csv': 'Planilhas',
        'ods': 'Planilhas',
        'ppt': 'Apresentacoes',
        'pptx': 'Apresentacoes',
        'odp': 'Apresentacoes',
        
        # Imagens
        'jpg': 'Imagens',
        'jpeg': 'Imagens',
        'png': 'Imagens',
        'gif': 'Imagens',
        'bmp': 'Imagens',
        'tif': 'Imagens',
        'tiff': 'Imagens',
        'svg': 'Imagens',
        'webp': 'Imagens',
        
        # Áudio
        'mp3': 'Audio',
        'wav': 'Audio',
        'ogg': 'Audio',
        'flac': 'Audio',
        'aac': 'Audio',
        'wma': 'Audio',
        
        # Vídeo
        'mp4': 'Videos',
        'avi': 'Videos',
        'mkv': 'Videos',
        'mov': 'Videos',
        'wmv': 'Videos',
        'flv': 'Videos',
        'webm': 'Videos',
        
        # Compactados
        'zip': 'Compactados',
        'rar': 'Compactados',
        '7z': 'Compactados',
        'tar': 'Compactados',
        'gz': 'Compactados',
        
        # Executáveis
        'exe': 'Executaveis',
        'msi': 'Executaveis',
        'bat': 'Executaveis',
        'sh': 'Executaveis',
        
        # Código
        'py': 'Codigo',
        'java': 'Codigo',
        'js': 'Codigo',
        'html': 'Codigo',
        'css': 'Codigo',
        'c': 'Codigo',
        'cpp': 'Codigo',
        'h': 'Codigo',
        'php': 'Codigo',
    }
    
    # Retorna o tipo correspondente ou "Outros" se não encontrado
    return tipos.get(extensao, 'Outros')

def calcular_hash_arquivo(caminho_arquivo, block_size=65536):
    """Calcula o hash SHA-256 de um arquivo"""
    sha256 = hashlib.sha256()
    with open(caminho_arquivo, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def encontrar_arquivos_duplicados(pasta, callback=None):
    """Encontra todos os arquivos duplicados em todas as pastas"""
    # Dicionário para armazenar arquivos por tamanho
    arquivos_por_tamanho = defaultdict(list)
    # Dicionário para armazenar arquivos por hash
    arquivos_por_hash = defaultdict(list)
    
    # Primeiro, agrupa arquivos por tamanho
    total_files = sum([len(files) for _, _, files in os.walk(pasta)])
    processed_files = 0
    
    for raiz, _, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            caminho_completo = os.path.join(raiz, arquivo)
            try:
                tamanho = os.path.getsize(caminho_completo)
                arquivos_por_tamanho[tamanho].append(caminho_completo)
            except (OSError, IOError):
                continue
            processed_files += 1
            if callback:
                callback(processed_files, total_files)
    
    # Para arquivos com mesmo tamanho, calcula o hash
    total_grupos = len([g for g in arquivos_por_tamanho.values() if len(g) > 1])
    grupos_processados = 0
    
    for tamanho, arquivos in arquivos_por_tamanho.items():
        if len(arquivos) > 1:  # Só verifica grupos com mais de um arquivo
            grupos_processados += 1
            for arquivo in arquivos:
                try:
                    hash_arquivo = calcular_hash_arquivo(arquivo)
                    arquivos_por_hash[hash_arquivo].append(arquivo)
                except (OSError, IOError):
                    continue
            if callback:
                callback(grupos_processados, total_grupos)
    
    # Retorna apenas grupos de arquivos duplicados
    return {hash_: arquivos for hash_, arquivos in arquivos_por_hash.items() 
            if len(arquivos) > 1}

def mover_para_duplicados(arquivo, pasta_duplicados):
    """
    Move um arquivo para a pasta de duplicados, organizando por tipo de arquivo.
    """
    # Obter nome e extensão do arquivo
    nome_arquivo = os.path.basename(arquivo)
    _, extensao = os.path.splitext(nome_arquivo)
    
    # Determinar a pasta de destino baseada no tipo de arquivo
    tipo_pasta = obter_pasta_tipo_arquivo(extensao)
    pasta_tipo = os.path.join(pasta_duplicados, tipo_pasta)
    
    # Criar a pasta do tipo se não existir
    os.makedirs(pasta_tipo, exist_ok=True)
    
    # Definir o caminho de destino
    destino = os.path.join(pasta_tipo, nome_arquivo)
    
    # Se já existe um arquivo com mesmo nome na pasta de destino
    contador = 1
    while os.path.exists(destino):
        nome_base, ext = os.path.splitext(nome_arquivo)
        destino = os.path.join(pasta_tipo, f"{nome_base}_{contador}{ext}")
        contador += 1
    
    # Mover o arquivo
    shutil.move(arquivo, destino)
    return destino

def processar_arquivos_duplicados(duplicados, pasta_duplicados, modo_acao=0, arquivo_manter=0, log_callback=None):
    """
    Processa arquivos duplicados de acordo com o modo de ação escolhido.
    
    Parâmetros:
    - duplicados: dicionário com hash como chave e lista de arquivos duplicados como valor
    - pasta_duplicados: pasta onde os arquivos duplicados serão movidos
    - modo_acao: 0=manter todos, 1=manter primeiro, 2=escolha manual, 3=mover todos para pasta específica
    - arquivo_manter: índice do arquivo a manter (para modo_acao=2)
    - log_callback: função para registrar mensagens de log
    """
    os.makedirs(pasta_duplicados, exist_ok=True)
    
    for hash_arquivo, arquivos in duplicados.items():
        if modo_acao == 0:  # Manter todos
            continue
            
        elif modo_acao == 1:  # Manter apenas o primeiro
            primeiro = arquivos[0]
            for arquivo in arquivos[1:]:
                novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                if log_callback:
                    log_callback(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}")
                    
        elif modo_acao == 2:  # Escolha manual
            if 0 <= arquivo_manter < len(arquivos):
                arquivo_manter_path = arquivos[arquivo_manter]
                for i, arquivo in enumerate(arquivos):
                    if i != arquivo_manter:
                        novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                        if log_callback:
                            log_callback(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}")
                            
        elif modo_acao == 3:  # Mover todos para pasta específica (mantém originais)
            for arquivo in arquivos:
                # Obter nome e extensão do arquivo
                nome_arquivo = os.path.basename(arquivo)
                _, extensao = os.path.splitext(nome_arquivo)
                
                # Determinar a pasta de destino baseada no tipo de arquivo
                tipo_pasta = obter_pasta_tipo_arquivo(extensao)
                pasta_tipo = os.path.join(pasta_duplicados, tipo_pasta)
                
                # Criar a pasta do tipo se não existir
                os.makedirs(pasta_tipo, exist_ok=True)
                
                # Definir o caminho de destino
                destino = os.path.join(pasta_tipo, nome_arquivo)
                
                # Se já existe um arquivo com mesmo nome na pasta de destino
                contador = 1
                while os.path.exists(destino):
                    nome_base, ext = os.path.splitext(nome_arquivo)
                    destino = os.path.join(pasta_tipo, f"{nome_base}_{contador}{ext}")
                    contador += 1
                
                # Copiar o arquivo (mantém o original)
                shutil.copy2(arquivo, destino)
                if log_callback:
                    log_callback(f"Arquivo duplicado copiado: {arquivo} -> {destino}")

def processar_pastas_identicas(grupo_pastas, modo_acao=0, log_callback=None):
    """
    Processa pastas idênticas de acordo com o modo de ação escolhido.
    
    Parâmetros:
    - grupo_pastas: tupla com dois caminhos de pastas idênticas
    - modo_acao: 0=manter ambas, 1=manter primeira, 2=manter segunda, 3=mesclar conteúdo
    - log_callback: função para registrar mensagens de log
    """
    folder1, folder2 = grupo_pastas
    
    try:
        if modo_acao == 1:  # Manter apenas a primeira
            shutil.rmtree(folder2)
            if log_callback:
                log_callback(f"Pasta removida: {folder2}")
                
        elif modo_acao == 2:  # Manter apenas a segunda
            shutil.rmtree(folder1)
            if log_callback:
                log_callback(f"Pasta removida: {folder1}")
                
        elif modo_acao == 3:  # Mesclar conteúdo
            # Mover arquivos únicos da segunda pasta para a primeira
            for item in os.listdir(folder2):
                src = os.path.join(folder2, item)
                dst = os.path.join(folder1, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                    if log_callback:
                        log_callback(f"Arquivo movido: {src} -> {dst}")
            
            # Remover a segunda pasta após a mesclagem
            shutil.rmtree(folder2)
            if log_callback:
                log_callback(f"Pastas mescladas em: {folder1}")
                
        else:  # Manter ambas (modo_acao == 0)
            if log_callback:
                log_callback("Ambas as pastas mantidas")
                
    except Exception as e:
        if log_callback:
            log_callback(f"Erro ao processar pastas: {str(e)}")

def main():
    # Configurações iniciais
    hd_path = input("Digite o caminho completo do HD externo: ").strip()
    log_file = os.path.join(hd_path, "reorganizacao_log.txt")
    pasta_duplicados = os.path.join(hd_path, "Arquivos Duplicados")
    
    if not os.path.exists(hd_path):
        print("Caminho não encontrado!")
        return
    
    # Perguntar sobre o modo de processamento
    print("\nDeseja processar todos os arquivos de uma vez (modo lote)?")
    batch_mode = input("Digite S para sim ou N para não: ").strip().upper() == 'S'
    
    duplicate_action = 0
    folder_action = 0
    
    if batch_mode:
        print("\nComo deseja tratar arquivos duplicados?")
        print("1. Perguntar para cada arquivo")
        print("2. Manter todos os arquivos")
        print("3. Manter apenas o primeiro arquivo (mover outros para pasta de duplicados)")
        print("4. Mover todos os duplicados para pasta específica (mantém originais)")
        duplicate_action = int(input("Escolha uma opção (1-4): ").strip()) - 1
        
        print("\nComo deseja tratar pastas duplicadas?")
        print("1. Perguntar para cada pasta")
        print("2. Manter todas as pastas")
        print("3. Manter apenas a primeira pasta")
        print("4. Mesclar conteúdo das pastas")
        folder_action = int(input("Escolha uma opção (1-4): ").strip()) - 1
    
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
            
            # Se estiver em modo de lote com ação automática
            if batch_mode and duplicate_action > 0:
                processar_arquivos_duplicados(
                    arquivos_duplicados, 
                    pasta_duplicados, 
                    modo_acao=duplicate_action,
                    log_callback=lambda msg: (print(msg), log.write(f"{msg}\n"))
                )
            else:
                # Processamento individual
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
                            novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                            log.write(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}\n")
                            print(f"Movido: {arquivo} -> {novo_caminho}")
                    
                    elif action == '3':
                        manter = int(input("Digite o número do arquivo que deseja manter: ").strip()) - 1
                        if 0 <= manter < len(arquivos):
                            arquivo_manter = arquivos[manter]
                            for i, arquivo in enumerate(arquivos):
                                if i != manter:
                                    novo_caminho = mover_para_duplicados(arquivo, pasta_duplicados)
                                    log.write(f"Arquivo duplicado movido: {arquivo} -> {novo_caminho}\n")
                                    print(f"Movido: {arquivo} -> {novo_caminho}")
    else:
        print("Nenhum arquivo duplicado encontrado.")
    
    # Continuar com o processamento de pastas idênticas
    print("\n=== ETAPA 5: Processando pastas idênticas ===")
    with open(log_file, 'a') as log:
        # Se estiver em modo de lote com ação automática para pastas
        if batch_mode and folder_action > 0:
            for group in identical_groups:
                processar_pastas_identicas(
                    group,
                    modo_acao=folder_action,
                    log_callback=lambda msg: (print(msg), log.write(f"{msg}\n"))
                )
        else:
            # Processamento individual de pastas
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
