# Skip Level

Sorteio animado de 5 colaboradores a partir de uma lista fixa de 32 participantes.

## Estrutura

| Arquivo | Função |
| --- | --- |
| `main.py` | Ponto de entrada |
| `ui.py` | Janela principal, fluxo do sorteio e ações |
| `widgets.py` | Roleta de nomes (canvas animado) e cards dos sorteados |
| `raffle.py` | Regras do sorteio (sem interface) |
| `data.py` | Lista de participantes |
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

## Como funciona o sorteio

- Os 5 nomes são escolhidos com `random.SystemRandom` (entropia do sistema), sem repetição, antes da animação começar; a roleta apenas revela o resultado.
- **Não repetir quem já foi sorteado** (ligado por padrão): cada nova rodada exclui quem já saiu. Desligue para que todos concorram sempre.
- **Reiniciar** limpa o histórico e devolve os 32 nomes ao sorteio.
- **Copiar Lista de Vencedores** envia a lista numerada, com data e hora, para a área de transferência.
