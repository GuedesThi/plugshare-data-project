# Web Scraper PlugShare para Eletropostos no Estado do Rio de Janeiro


Este projeto é um conjunto de scripts em Python com foco em coletar dados de eletropostos (públicos e restritos) exclusivamente presentes no estado do Rio de Janeiro do site PlugShare, e gerar no final arquivos Excel padronizados com esses dados.

---
## 📁 Estrutura do Projeto

* **`main.py`**: contém a lógica da automação e coleta dos dados através da biblioteca Playwright. Aqui ocorre a interceptação de chamadas de API com os dados dos eletropostos, conversão de coordenadas para DMS, tratamento antifalhas e fechamento forçado de modais de login.
* **`scan_baixada.py`**: grades geográficas da Baixada Fluminense divida em setores específicos da região (Eixos: Nova Iguaçu/Queimados, Caxias, Meriti/Nilópolis e Seropédica).
* **`scan_capital.py`**: grades geográficas da Cidade do Rio de Janeiro divida em setores específicos da região (Eixos: Centro/Zona Sul, Barra da Tijuca, Grande Tijuca/Zona Norte e Recreio).
* **`scan_niteroi.py`**: grades geográficas de Niterói divida em setores específicos da região (Eixos: Centro/Icaraí, Região Oceânica e Pendotiba).
* **`consolidar_baixada.py` / `consolidar_capital.py` / `consolidar_niteroi.py`**: scripts executados no final de cada varredura (após passar por todos os setores de uma região) responsáveis por juntar os diferentes arquivos Excel num único só, removendo duplicatas através de suas chaves IDs.
* **`rodar_tudo.py`**: responsável por executar as varreduras. Atualmente definimos manualmente a região que deve ser escaneada, informando os arquivos `scan...py` e `consolidar...py` respectivos.

---
## 🛠️ Configuração do Ambiente

Para executar o projeto com sucesso, é necessário seguir o seguinte passo a passo:

1. Copiar o projeto para sua máquina através do seu terminal
```powershell
# faz uma cópia do projeto na sua máquina
git clone https://github.com/GuedesThi/plugshare-data-project.git

# entra na pasta
cd plugshare-data-project
```

2. Criar um ambiente virtual (.venv) através do seu terminal
```powershell
# windows: cria um ambiente virtual na pasta .venv
python -m venv .venv

# linux/mac: cria um ambiente virtual na pasta .venv
python3 -m venv .venv

# windows: ativa o ambiente virtual
.\.venv\Scripts\activate

# linux/mac: ativa o ambiente virtual
source .venv/bin/activate

# caso a ativação dê erro no windows, é necessário executar isso antes
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Instale as dependências do arquivo ``requirements.txt`
```powershell
pip install -r requirements.txt
```

4. Instale o motor Firefox (por enquanto é necessário ser com ele) que o Playwright usará para acessar o PlugShare
```powershell
playwright install firefox
```

---
## 🤖 Escanear região

Para informar qual região deve ser escaneada, basta informarmos em `rodar_tudo.py` seu arquivo `scan...py` na variável `scripts`, e sua função `consolidar...`:
```python
# rodar_tudo.py

...

try:
  from consolidar_niteroi import consolidar_niteroi
except ImportError:
  print("[ERRO] Arquivo consolidar_niteroi.py não encontrado!")

scripts = ["scan_niteroi.py"]

def iniciar_maratona():
  ...
  consolidar_niteroi()

if __name__ == "__main__":
  iniciar_maratona()
```
Após isso, basta executar no terminal o arquivo `rodar_tudo.py`:
```powershell
python .\rodar_tudo.py
```

---
## ✅ Resultados

Pelo terminal poderá ver uma série de prints dizendo que setor da região ele está escaneando, quantos faltam e quais eletropostos foram coletados. Ao passar por todo setor de uma região, é gerado um arquivo Excel com as informações dos eletropostos coletados. 
Ao escanerar todos os setores da região, a função do arquivo `consolidar...py` pega todos os arquivos Excel gerados e os junta num só, sem eletropostos repetidos.

---
## 👨‍💻 Em desenvolvimento

No momento as melhores grades geográficas que temos são das regiões da Baixada Fluminense, Capital do Rio de Janeiro, e Niterói. Estamos melhorando o escaneamento das regiões como Lagos, Serra e Sul do estado para coletarem o máximo de eletropostos possíveis.
