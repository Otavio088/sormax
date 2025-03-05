from flask import Blueprint, render_template, request, session, redirect
import pulp

bp = Blueprint('result', __name__)

@bp.route('/result', methods=['POST', 'GET'])
def calculate():
    if request.method == 'POST':
        variable_prices = [
            float(request.form.get(f'price_x{i}', '0').replace(',', '.')) 
            for i in range(session['num_variables'])
        ]
        restriction_units = [
            request.form.get(f'type_y{i}', 'Unit') 
            for i in range(session['num_restrictions'])
        ]
        available_restrictions = [
            float(request.form.get(f'available_quantity_y{i}', '0').replace(',', '.')) 
            for i in range(session['num_restrictions'])
        ]
        necessary_restrictions = [
            [float(request.form.get(f'necessary_y{i}_for_x{j}', '0').replace(',', '.')) 
            for j in range(session['num_variables'])]
            for i in range(session['num_restrictions'])
        ]

        if session['optimization_type'] == 'maximization':
            
            # Definir o problema de maximização do lucro
            prob = pulp.LpProblem('Maximize_IcecreamParlor', pulp.LpMaximize)

            # Definir as variáveis de decisão
            x = [
                pulp.LpVariable(f"x{i+1}", lowBound=0, cat='Continuous') 
                for i in range(session['num_variables'])
            ]

            # Definir a função objetivo (maximizar o lucro)
            prob += pulp.lpSum([
                variable_prices[i] * x[i] for i in range(session['num_variables'])
            ]), "Profit"

            # Adicionar as restrições ao problema
            for i in range(session['num_restrictions']):
                prob += pulp.lpSum([
                    necessary_restrictions[i][j] * x[j] for j in range(session['num_variables'])
                ]) <= available_restrictions[i], f"Restriction_{i+1}"

            # Resolver o problema
            prob.solve()

            # Verificar se a solução é ótima
            if prob.status != pulp.LpStatusOptimal:
                return render_template(
                    'result.html',
                    message="O problema não pôde ser resolvido de forma ótima!"
                )

            # Obter os resultados ótimos
            max_profit = round(pulp.value(prob.objective) or 0, 2)
            quantities = [round(pulp.value(x[i]) or 0, 0) for i in range(session['num_variables'])]
            used_restrictions = [
                round(sum(quantities[j] * necessary_restrictions[i][j] for j in range(session['num_variables'])) or 0, 2)
                for i in range(session['num_restrictions'])
            ]

            # Total lucro de cada produto
            total_values = [
                round(variable_prices[i] * quantities[i], 2) for i in range(session['num_variables'])
            ]

            costs_variables = []

            # Salvar os resultados na sessão
            session['max_profit'] = max_profit
            session['variable_prices'] = variable_prices
            session['quantities_production'] = quantities
            session['total_values'] = total_values
            session['restriction_units'] = restriction_units
            session['available_restrictions'] = available_restrictions
            session['used_restrictions'] = used_restrictions
            session['costs_variables'] = []

            # Preparar os dados para o gráfico
            chart_data = [
                {"name": f"Produto {i+1}", "y": quantities[i]} 
                for i in range(session['num_variables'])
            ]
            print('SESSION AQUI:', session)
            return render_template(
                'result.html',
                chart_data=chart_data
            )

        if session['optimization_type'] == 'minimization':
            min_production = [
                float(request.form.get(f'min_x{i}', '0').replace(',', '.')) 
                for i in range(session['num_variables'])
            ]

            # Definir o problema de minimização de custos
            prob = pulp.LpProblem('Minimization_IcecreamParlor', pulp.LpMinimize)

            # Definir as variáveis de decisão
            x = [
                pulp.LpVariable(f"x{i+1}", lowBound=0, cat='Continuous') 
                for i in range(session['num_variables'])
            ]

            # Definir a função objetivo (minimizar os custos)
            prob += pulp.lpSum([
                variable_prices[i] * x[i] for i in range(session['num_variables'])
            ]), "Cost"

            # Adicionar as restrições ao problema
            for i in range(session['num_restrictions']):
                prob += pulp.lpSum([
                    necessary_restrictions[i][j] * x[j] for j in range(session['num_variables'])
                ]) <= available_restrictions[i], f"Restriction_{i+1}"

            # Adicionar restrições de produção mínima para cada variável
            for i in range(session['num_variables']):
                prob += x[i] >= min_production[i], f"MinProduction_{i+1}"

            # Resolver o problema
            prob.solve()

            # Verificar se a solução é ótima
            if prob.status != pulp.LpStatusOptimal:
                return render_template(
                    'result.html',
                    message="O problema não pôde ser resolvido de forma ótima!"
                )

            # Obter os resultados ótimos
            min_cost = round(pulp.value(prob.objective) or 0, 2)
            quantities = [round(pulp.value(x[i]) or 0, 0) for i in range(session['num_variables'])]
            used_restrictions = [
                round(sum(quantities[j] * necessary_restrictions[i][j] for j in range(session['num_variables'])) or 0, 2)
                for i in range(session['num_restrictions'])
            ]

            costs_variables = [
                round(quantities[i] * variable_prices[i], 2) 
                      for i in range(session['num_variables'])
            ]

            # Salvar os resultados na sessão
            session['min_cost'] = min_cost
            session['variable_prices'] = variable_prices
            session['quantities_production'] = quantities
            session['restriction_units'] = restriction_units
            session['available_restrictions'] = available_restrictions
            session['used_restrictions'] = used_restrictions
            session['costs_variables'] = costs_variables

            # Preparar os dados para o gráfico
            chart_data = min_production
        
    if not session.get('variable_prices'):
        return redirect('/values')

    print('session: ', session)

    return render_template(
        'result.html',
        chart_data=chart_data
    )