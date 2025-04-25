import os
import shutil
import filecmp
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

def mover_para_duplicados(arquivo_origem, pasta_duplicados):
    """
    Move um arquivo para a pasta de duplicados, organizando por tipo de arquivo.
    """
    os.makedirs(pasta_duplicados, exist_ok=True)
    
    # Obter nome e extensão do arquivo
    nome_arquivo = os.path.basename(arquivo_origem)
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
    shutil.move(arquivo_origem, destino)
    return destino

def mesclar_hds(hd_destino, hd_origem, manter_primeiro=True, progress_callback=None):
    """
    Mescla o conteúdo de dois HDs, movendo todos os arquivos do HD de origem para o HD de destino.
    Arquivos duplicados são movidos para uma pasta especial, organizados por tipo.
    
    Args:
        hd_destino: Caminho do HD de destino
        hd_origem: Caminho do HD de origem
        manter_primeiro: Se True, mantém o primeiro arquivo e move duplicatas para pasta de duplicados
        progress_callback: Função de callback para atualizar o progresso (valor, máximo)
    """
    # Validar caminhos
    if not os.path.exists(hd_destino) or not os.path.exists(hd_origem):
        print("Um dos caminhos especificados não existe!")
        return False
    
    # Criar pasta para arquivos duplicados
    pasta_duplicados = os.path.join(hd_destino, "Arquivos Duplicados")
    os.makedirs(pasta_duplicados, exist_ok=True)
    
    # Criar arquivo de log
    log_file = os.path.join(hd_destino, "mesclagem_log.txt")
    
    # Contador para estatísticas
    stats = {
        "arquivos_movidos": 0,
        "arquivos_duplicados": 0,
        "pastas_criadas": 0
    }
    
    print("\n=== Iniciando processo de mesclagem de HDs ===")
    print(f"HD Destino: {hd_destino}")
    print(f"HD Origem: {hd_origem}")
    print(f"Modo: {'Manter primeiro arquivo' if manter_primeiro else 'Modo padrão'}")
    
    # Contar total de arquivos para barra de progresso
    total_files = sum([len(files) for _, _, files in os.walk(hd_origem)])
    processed_files = 0
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n=== Nova operação de mesclagem ===\n")
        log.write(f"HD Origem: {hd_origem}\n")
        log.write(f"HD Destino: {hd_destino}\n")
        log.write(f"Modo: {'Manter primeiro arquivo' if manter_primeiro else 'Modo padrão'}\n\n")
        
        # Percorrer toda a estrutura do HD de origem
        for pasta_atual, subpastas, arquivos in os.walk(hd_origem):
            # Calcular o caminho relativo para recriar a mesma estrutura no destino
            caminho_relativo = os.path.relpath(pasta_atual, hd_origem)
            pasta_destino = os.path.join(hd_destino, caminho_relativo)
            
            # Criar a estrutura de pastas no destino
            if caminho_relativo != '.':
                os.makedirs(pasta_destino, exist_ok=True)
                stats["pastas_criadas"] += 1
            
            # Processar cada arquivo na pasta atual
            for arquivo in arquivos:
                arquivo_origem = os.path.join(pasta_atual, arquivo)
                arquivo_destino = os.path.join(pasta_destino, arquivo)
                
                # Verificar se já existe um arquivo com mesmo nome no destino
                if os.path.exists(arquivo_destino):
                    # Comparar conteúdo dos arquivos
                    if filecmp.cmp(arquivo_origem, arquivo_destino, shallow=False):
                        # Se são idênticos e estamos no modo "manter primeiro"
                        # Move o arquivo de origem para pasta de duplicados
                        novo_caminho = mover_para_duplicados(arquivo_origem, pasta_duplicados)
                        log.write(f"Arquivo duplicado movido: {arquivo_origem} -> {novo_caminho}\n")
                        stats["arquivos_duplicados"] += 1
                    else:
                        # Se têm conteúdo diferente, move o arquivo de origem com um novo nome
                        novo_caminho = mover_para_duplicados(arquivo_origem, pasta_destino)
                        log.write(f"Arquivo com mesmo nome (conteúdo diferente) renomeado: {arquivo_origem} -> {novo_caminho}\n")
                        stats["arquivos_movidos"] += 1
                else:
                    # Se não existe arquivo com mesmo nome, move normalmente
                    shutil.move(arquivo_origem, arquivo_destino)
                    log.write(f"Arquivo movido: {arquivo_origem} -> {arquivo_destino}\n")
                    stats["arquivos_movidos"] += 1
                
                processed_files += 1
                if progress_callback:
                    progress_callback(processed_files, total_files)
    
    # Remover pastas vazias do HD de origem
    for pasta_atual, subpastas, arquivos in os.walk(hd_origem, topdown=False):
        try:
            os.rmdir(pasta_atual)
        except OSError:
            pass  # Ignora se a pasta não estiver vazia
    
    # Exibir estatísticas
    print("\n=== Estatísticas da Mesclagem ===")
    print(f"Arquivos movidos com sucesso: {stats['arquivos_movidos']}")
    print(f"Arquivos duplicados encontrados: {stats['arquivos_duplicados']}")
    print(f"Pastas criadas: {stats['pastas_criadas']}")
    print(f"\nLog completo salvo em: {log_file}")
    
    return True

def main():
    print("=== Mesclagem de HDs ===")
    print("Este programa irá mesclar o conteúdo de dois HDs, movendo todos os arquivos")
    print("do HD de origem para o HD de destino, tratando duplicações automaticamente.\n")
    
    hd_destino = input("Digite o caminho completo do HD DESTINO (onde os arquivos serão movidos): ").strip()
    hd_origem = input("Digite o caminho completo do HD ORIGEM (de onde os arquivos serão movidos): ").strip()
    
    if hd_destino == hd_origem:
        print("Erro: Os caminhos de origem e destino não podem ser iguais!")
        return
    
    print("\nComo deseja tratar arquivos duplicados?")
    print("1. Manter o primeiro arquivo (mover duplicatas para pasta 'Arquivos Duplicados')")
    print("2. Modo padrão (comportamento original)")
    
    opcao = input("Escolha uma opção (1 ou 2): ").strip()
    manter_primeiro = opcao == "1"
    
    confirmacao = input(f"\nATENÇÃO: Todos os arquivos de '{hd_origem}' serão movidos para '{hd_destino}'.\nDeseja continuar? (s/n): ").lower()
    
    if confirmacao == 's':
        if mesclar_hds(hd_destino, hd_origem, manter_primeiro):
            print("\nProcesso de mesclagem concluído com sucesso!")
        else:
            print("\nErro durante o processo de mesclagem!")
    else:
        print("\nOperação cancelada pelo usuário.")

if __name__ == "__main__":
    main()
