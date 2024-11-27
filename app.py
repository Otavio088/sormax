from flask import Flask, render_template, request
import pulp

app = Flask(__name__)

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

@app.route('/calculate', methods=['POST'])
def calculate():
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

if __name__ == '__main__':
    app.run(debug=True)
