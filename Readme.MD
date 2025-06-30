# SORMAX 🍦

## Descrição
SORMAX se trata de um sistema que visa auxiliar sorveterias de pequeno porte na tomada de decisão de suas produções utilizando a Programação Linear (PL) para retornar o ponto ótimo de produção. Tudo isso de acordo com as variáveis de decisão (sorvetes) e as restrições (insumos utilizados para produzir esses sorvetes).

### Funcionalidades:
- Criar Categorias para englobar produções
- Cadastrar variáveis de decisão.
- Cadastrar restrições.
- Cadastrar custos fixoss da empresa.
- Calcular a produção ótima para maximizar o lucro.
- Salvar maximizações.
- Consultar resultados salvos.
- Deletar produtos, insumos, custos e maximizações.

---

## Tecnologias Utilizadas

- **Backend:** Python (`pulp`, `sqlalchemy`)  
- **Frontend:** HTML, CSS, JavaScript  
- **Framework Web:** Flask  
- **Banco de Dados:** MySQL  

---

## Como rodar (abra o terminal na pasta do projeto)
**1. Clone o repositório:**
- git clone <URL_DO_REPOSITÓRIO>

**2. Crie um ambiente virtual e ative:**
- python3 -m venv venv (linux/mac)
- source venv/bin/activate (linux/mac)

- python -m venv venv (windows)
- venv\Scripts\activate (windows)

**3. Instale as dependências:**
- pip install -r requirements.txt

**4. Configure o Banco de Dados:**
Você precisará de um servidor MySQL rodando.

**4.1. Crie um arquivo .env na raiz do projeto de acordo com o .envexample.**
Substitua usuario e senha pelos seus dados de acesso ao MySQL.

**4.2. Criação automática do banco de dados via código Python:**
Execute o seguinte comando no terminal: python create_db.py

**5. Inicie o servidor no terminal do vsCode:** 
- flask run
