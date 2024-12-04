from flask import Flask, render_template, request, session
import pulp
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Chave Teste
app.secret_key = "chave_teste"

# Variável global para armazenar os resultados
cumulative_results = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize_post():
    num_variables = int(request.form['num_variables'])
    num_constraints = int(request.form['num_constraints'])
    return render_template('optimize.html', num_variables=num_variables, num_constraints=num_constraints)

@app.route('/restrictions', methods=['POST'])
def restrictions_post():
    data = request.form
    num_variables = int(data.get('num_variables'))
    num_constraints = int(data.get('num_constraints'))

    # Captura os nomes das variáveis e restrições
    variable_names = [data.get(f'var{i}', f'x{i+1}') for i in range(num_variables)]
    constraint_names = [data.get(f'constraint{i}', f'Restriction {i+1}') for i in range(num_constraints)]

    # Passa as variáveis e restrições para o template
    return render_template(
        'restrictions.html',
        num_variables=num_variables,
        num_constraints=num_constraints,
        variable_names=variable_names,
        constraint_names=constraint_names,  # Define constraint_names
        constraints=constraint_names       # constraints pode ser o mesmo que constraint_names
    )

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'GET':
        # Verifique se há resultados salvos na sessão
        if 'last_results' in session:
            return render_template('result.html', **session['last_results'])
        else:
            return render_template('result.html', mensagem="Nenhum resultado disponível.")

    data = request.form.to_dict()
    print(f"Dados recebidos: {data}")

    # Determinando dinamicamente o número de variáveis de decisão e restrições
    num_variables = len([key for key in data.keys() if key.startswith('value_x')])
    num_constraints = len([key for key in data.keys() if key.startswith('available')])

    print(f"num_constraints: {num_constraints}, num_variables: {num_variables}")

    # Recuperar os nomes das variáveis e restrições
    variable_names = [data.get(f'var{i}', f'x{i+1}') for i in range(num_variables)]
    constraint_names = [data.get(f'constraint{i}', f'Restriction {i+1}') for i in range(num_constraints)]
    print(f"Variáveis: {variable_names}, Restrições: {constraint_names}")  # Debugging

    # Coletando dados para recursos disponíveis
    available = [float(data[f'available{i}'].replace(',', '.')) for i in range(num_constraints)]
    print(f"available: {available}")

    # Coletando dados para as quantidades necessárias para cada variável em cada restrição
    required = {
        f'x{j+1}': [float(data[f'required_x{j+1}_{i}'].replace(',', '.')) for i in range(num_constraints)]
        for j in range(num_variables)
    }
    print(f"required: {required}")

    valores_unitarios = [float(data.get(f'value_x{j+1}', 0).replace(',', '.')) for j in range(num_variables)]
    print(f"valores_unitarios: {valores_unitarios}")

    # Definindo o problema de otimização em Pulp
    prob = pulp.LpProblem("Maximize_Lucro", pulp.LpMaximize)
    x = [pulp.LpVariable(f"x{i+1}", lowBound=0, cat='Continuous') for i in range(num_variables)]
    
    # Função objetivo (maximizar o lucro)
    prob += pulp.lpSum([valores_unitarios[i] * x[i] for i in range(num_variables)]), "Profit"
    print("Objective Function: ", pulp.lpSum([valores_unitarios[i] * x[i] for i in range(num_variables)]))  # Debugging a função objetivo

    # Adicionando restrições
    for i in range(num_constraints):
        prob += pulp.lpSum([required[f'x{j+1}'][i] * x[j] for j in range(num_variables)]) <= available[i], f"Restriction_{i+1}"

    # Resolver o problema
    prob.solve()
    print(f"Status: {prob.status}, Maximum Profit: {pulp.value(prob.objective)}")  # Verifique o status e o objetivo

    # Verificar se a solução é ótima
    if prob.status != pulp.LpStatusOptimal:
        return render_template(
            'result.html',
            mensagem="O problema não pôde ser resolvido de forma ótima."
        )

    # Obter os resultados ótimos
    max_profit = pulp.value(prob.objective) or 0
    quantities = [pulp.value(x[i]) or 0 for i in range(num_variables)]
    used_constraints = [
        sum(quantities[j] * required[f'x{j+1}'][i] for j in range(num_variables)) or 0
        for i in range(num_constraints)
    ]

    # Armazena os resultados para o gráfico
    cumulative_results.append({
        "execucao": len(cumulative_results) + 1,
        "lucro": max_profit,
        "quantidades": quantities,
        "variaveis": variable_names
    })

    session['last_results'] = {
        'lucro': max_profit,
        'quantidades': quantities,
        'valores_unitarios': valores_unitarios,
        'usado_restricoes': used_constraints,
        'available': available,
        'num_constraints': num_constraints,
        'num_variables': num_variables,
        'variables': variable_names,
        'constraints': constraint_names
    }

    return render_template(
        'result.html',
        lucro=max_profit,
        quantidades=quantities,
        valores_unitarios=valores_unitarios,
        usado_restricoes=used_constraints,
        available=available,
        num_constraints=num_constraints,
        num_variables=num_variables,
        variables=variable_names,  # Passar os nomes das variáveis
        constraints=constraint_names  # Passar os nomes das restrições
    )

@app.route('/graph')
def graph():
    if not cumulative_results:
        return render_template('graph.html', mensagem="Nenhum dado disponível para gerar o gráfico.")
    
    # Obtém o último resultado armazenado
    last_result = cumulative_results[-1]
    variables = last_result["variaveis"]
    quantities = last_result["quantidades"]
    lucro = last_result["lucro"]

    # Cria os dados para o gráfico de pizza
    data = quantities
    labels = variables

    # Gera o gráfico de pizza
    plt.figure(figsize=(8, 8))
    plt.pie(
        data,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        colors=plt.cm.tab20.colors[:len(labels)]
    )
    plt.title("Distribuição de Produção - Lucro Total: R$ {:.2f}".format(lucro), pad=20)
    plt.axis('equal')  # Garante que o gráfico seja um círculo perfeito

    # Salva o gráfico em base64 para exibir no HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('graph.html', graph_url=graph_url)


    
if __name__ == '__main__':
    app.run(debug=True)
