# Maximização de Lucro para Sorveteria

## Descrição
Este sistema visa maximizar o lucro de uma sorveteria utilizando **programação linear**. Os usuários podem:
- Cadastrar variáveis de decisão.**
- Cadastrar restrições.
- Calcular a produção ótima para maximizar o lucro.

## Tecnologias
- Backend: Python.
- Frontend: HTML, CSS.

## Estrutura do Projeto
- `app.py`: Configura o servidor Flask e toda parte de backend.
- `index.html`: Pagina inicial que pede quantidade de variáveis de decisão e restrições.
- `optimize.html`: Pede os nomes das variáveis de decisão e restrições.
- `restrictions.html`: Define os valores das variáveis de decisão e restrições.
- `result.html`: Mostra os resultados da operação.

## Como rodar (abra o terminal na pasta do projeto)
**1. Clone o repositório:**
- git clone <url>

**2. Crie um ambiente virtual e ative:**
- python3 -m venv venv 
- source venv/bin/activate

**3. Instale as dependências:**
- pip install -r requirements.txt

**4. Inicie o servidor no terminal do vsCode:** 
- python app.py 
