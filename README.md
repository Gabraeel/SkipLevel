# Skip Level

Sorteio animado de 5 colaboradores a partir de uma lista editável (32 participantes de início).

## Estrutura

| Arquivo | Função |
| --- | --- |
| `main.py` | Ponto de entrada |
| `ui.py` | Janela principal, fluxo do sorteio e ações |
| `widgets.py` | Roleta de nomes (canvas animado) e cards dos sorteados |
| `pages.py` | Abas Participantes e Histórico |
| `raffle.py` | Regras do sorteio e da lista (sem interface) |
| `storage.py` | Salva lista, sorteados, histórico e preferências |
| `data.py` | Lista original de participantes |
| `theme.py` | Paleta, fontes e utilitários |
| `assets/` | Logotipo e ícone |
| `build.bat` | Gera o `.exe` no Windows |

## Instalação (Python 3.10+)

```
pip install -r requirements.txt
```

## Executar

```
python main.py
```

## Gerar o executável (Windows)

Dê dois cliques em `build.bat`, ou rode na pasta do projeto:

```
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SkipLevel --icon assets\icon.ico --add-data "assets;assets" --collect-all customtkinter main.py
```

O arquivo final fica em `dist\SkipLevel.exe` e pode ser copiado para qualquer máquina Windows, sem instalar Python.

## Como funciona

- **Sorteio:** os 5 nomes são escolhidos com `random.SystemRandom` (entropia do sistema), sem repetição, antes da animação começar; a roleta apenas revela o resultado. A tecla Enter também inicia o sorteio.
- **Não repetir quem já foi sorteado** (ligado por padrão): cada nova rodada exclui quem já saiu, inclusive em dias diferentes. Desligue para que todos concorram sempre.
- **Reiniciar:** todos voltam a concorrer; o histórico é mantido.
- **Aba Participantes:** adicionar (vários de uma vez com `;`), remover com opção de desfazer, buscar e restaurar a lista original.
- **Aba Histórico:** todos os sorteios com data e hora; copiar ou limpar.
- **Copiar Lista de Vencedores:** envia a lista numerada, com data e hora, para a área de transferência.

## Onde os dados ficam

Lista, sorteados, histórico e tema são salvos automaticamente em `%APPDATA%\SkipLevel\skiplevel.json` (Windows) ou `~/.config/SkipLevel/skiplevel.json` (Linux). Apagar esse arquivo devolve o app ao estado original.
