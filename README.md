# Organizador de HDs

Um aplicativo com interface gráfica moderna para organizar e gerenciar conteúdo de HDs externos, com funcionalidades para detectar e tratar arquivos e pastas duplicadas.

## Funcionalidades

### 1. Organização de HD
- Análise completa da estrutura de pastas
- Detecção de pastas com nomes duplicados
- Comparação de conteúdo entre pastas
- Identificação de arquivos duplicados em todo o HD
- Opções para mesclar ou remover pastas duplicadas
- Log detalhado de todas as operações

### 2. Mesclagem de HDs
- Capacidade de mesclar conteúdo entre dois HDs diferentes
- Tratamento automático de arquivos duplicados
- Preservação da estrutura de pastas
- Log detalhado do processo de mesclagem

### 3. Tratamento de Arquivos Duplicados
- Detecção inteligente usando hash SHA-256
- Comparação de conteúdo byte a byte
- Opções flexíveis para gerenciar duplicatas:
  - Manter todos os arquivos
  - Manter apenas o primeiro arquivo
  - Escolher manualmente qual manter
- Movimentação automática para pasta "Arquivos Duplicados"

## Interface Gráfica
- Design moderno com tema escuro
- Interface intuitiva e responsiva
- Botões animados e interativos
- Áreas organizadas em cards
- Feedback visual em tempo real
- Barras de progresso para operações longas
- Logs detalhados das operações

## Requisitos

- Python 3.8 ou superior
- PyQt6
- Sistema Operacional: Windows, Linux ou macOS

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Crie um ambiente virtual (recomendado):
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/macOS:
```bash
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar

### Interface Gráfica
1. Execute o programa:
```bash
python organizador_hd_gui.py
```

2. Na aba "Organizar HD":
   - Selecione o HD que deseja organizar
   - Clique em "Iniciar Organização"
   - Siga as instruções na interface para tratar pastas e arquivos duplicados

3. Na aba "Mesclar HDs":
   - Selecione o HD de destino
   - Selecione o HD de origem
   - Clique em "Iniciar Mesclagem"
   - O programa irá mover e organizar automaticamente os arquivos

### Logs e Relatórios
- Todas as operações são registradas em arquivos de log
- Os logs são salvos no HD processado:
  - `reorganizacao_log.txt` para organização
  - `mesclagem_log.txt` para mesclagem

### Arquivos Duplicados
- São movidos automaticamente para a pasta "Arquivos Duplicados"
- Nomes são ajustados automaticamente para evitar conflitos
- Mantém um registro de todas as movimentações no log

## Segurança
- Não deleta arquivos sem confirmação
- Mantém backups em pasta específica
- Logs detalhados de todas as operações
- Verificações de integridade dos arquivos

## Contribuição
Sinta-se à vontade para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Envie um pull request

## Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
