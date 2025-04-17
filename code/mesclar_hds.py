import os
import shutil
import filecmp
from collections import defaultdict

def mover_para_duplicados(arquivo_origem, pasta_duplicados):
    """Move um arquivo para a pasta de duplicados com um nome único."""
    os.makedirs(pasta_duplicados, exist_ok=True)
    nome_arquivo = os.path.basename(arquivo_origem)
    destino = os.path.join(pasta_duplicados, nome_arquivo)
    
    # Se já existe um arquivo com mesmo nome na pasta de duplicados
    contador = 1
    while os.path.exists(destino):
        nome_base, extensao = os.path.splitext(nome_arquivo)
        destino = os.path.join(pasta_duplicados, f"{nome_base}_{contador}{extensao}")
        contador += 1
    
    shutil.move(arquivo_origem, destino)
    return destino

def mesclar_hds(hd_destino, hd_origem):
    """
    Mescla o conteúdo de dois HDs, movendo todos os arquivos do HD de origem para o HD de destino.
    Arquivos duplicados são movidos para uma pasta especial.
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
    
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"\n=== Nova operação de mesclagem ===\n")
        log.write(f"HD Origem: {hd_origem}\n")
        log.write(f"HD Destino: {hd_destino}\n\n")
        
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
                        # Se são idênticos, move o arquivo de origem para pasta de duplicados
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
    
    confirmacao = input(f"\nATENÇÃO: Todos os arquivos de '{hd_origem}' serão movidos para '{hd_destino}'.\nDeseja continuar? (s/n): ").lower()
    
    if confirmacao == 's':
        if mesclar_hds(hd_destino, hd_origem):
            print("\nProcesso de mesclagem concluído com sucesso!")
        else:
            print("\nErro durante o processo de mesclagem!")
    else:
        print("\nOperação cancelada pelo usuário.")

if __name__ == "__main__":
    main() 