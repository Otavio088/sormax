from flask import Blueprint, flash, render_template, request, session, redirect
from decimal import Decimal, ROUND_HALF_UP
from icecreampy.ext.database import db
from icecreampy.models.category import Category
from icecreampy.models.restrictions import Restriction
from icecreampy.models.products import Product
from icecreampy.models.products_restrictions import ProductRestriction
from icecreampy.models.fixed_costs import FixedCost
from icecreampy.models.result import Result
from icecreampy.models.result_products import ResultProduct
from sqlalchemy.orm import joinedload

bp = Blueprint('category_routes', __name__)

@bp.route('/register-products', methods=['GET', 'POST'])
def category_registration():
    if not session.get('loggedin'):
        return redirect('/')

    result = get_all_data_categories()

    costs = [fc.to_json() for fc in FixedCost.query.all()]

    return render_template('register-products.html', categories=result, fixed_costs=costs)

@bp.route('/register-category', methods=['POST'])
def register_category():
    category_id = request.form.get('category_id')
    category_name = request.form.get('category')
    category_days_production = request.form.get('days_production')
    restrictions = []

    # Pega todas os insumos trazidos pelo formulário
    for key in request.form:
        if key.startswith('restrictions['):
            index = key.split('[')[1].split(']')[0]
            field = key.split('[')[2].split(']')[0]

            # Garante que o insumo com esse índice existe
            while len(restrictions) <= int(index):
                restrictions.append({"name": "", "quantity": "", "unit": "", "unit_price": ""})
            restrictions[int(index)][field] = request.form[key]

    try:
        if category_id:
            # Consulta tudo que tem esse id de categoria
            cat = Category.query.get(category_id)
            cat.name = category_name
            cat.days_production = category_days_production
        else:
            # Nova categoria para adicionar no banco
            cat = Category(
                name=category_name,
                days_production=category_days_production
            )
            db.session.add(cat)
            db.session.flush() # Envia operações SQL para o banco mas nao finaliza a transação
            print(f'Categoria criada: id={cat.id}, nome={cat.name}, dias de produção={cat.days_production}')

        # ids dos que serão update
        received_ids = set()
        for r in restrictions:
            if r.get('id'):
                restriction = Restriction.query.get(int(r['id']))
                
                # Alteração dos atributos do obj existente
                if restriction and restriction.category_id == cat.id:
                    restriction.name = r['name']
                    restriction.quantity_available = r['quantity']
                    restriction.unit_type = r['unit']
                    restriction.unit_price = r['unit_price']

                    received_ids.add(restriction.id)                    
            else:
                # Insert no caso de não tiver o id vindo do form
                new_restriction = Restriction(
                    category_id = cat.id,
                    name = r['name'],
                    unit_type = r['unit'],
                    quantity_available = r['quantity'],
                    unit_price = r['unit_price']
                )
                db.session.add(new_restriction)
                db.session.flush()
                received_ids.add(new_restriction.id)

                # Buscar todos os produtos da categoria
                products_in_category = Product.query.join(ProductRestriction).join(Restriction).filter(
                    Restriction.category_id == cat.id
                ).all()

                for p in products_in_category:
                    # Verifica se o vínculo já existe
                    existing = ProductRestriction.query.filter_by(
                        product_id=p.id,
                        restriction_id=new_restriction.id
                    ).first()
                    if not existing:
                        new_link = ProductRestriction(
                            product_id=p.id,
                            restriction_id=new_restriction.id,
                            quantity_used=Decimal('0.00')
                        )
                        db.session.add(new_link)

        # Remove insumos excluídos pelo usuário
        if category_id:
            current_ids = { r.id for r in cat.restrictions }
            to_delete = current_ids - received_ids

            for restriction_id in to_delete:
                ProductRestriction.query.filter_by(restriction_id=restriction_id).delete()
                Restriction.query.filter_by(id=restriction_id).delete()

        # Efetiva todas as alterações feitas
        db.session.commit()
        print('Categoria atualizada com sucesso!')
    except Exception as err:
        db.session.rollback()
        print('Erro ao atualizar categoria: ', err)

    return redirect('/register-products')

@bp.route('/delete-category', methods=['POST'])
def category_remove():
    category_id = request.form.get('category_id_remove')

    try:
        category = Category.query.get(category_id)

        if category:
            # 1. Buscar todos os produtos associados à categoria
            products = Product.query.join(ProductRestriction).join(Restriction).filter(
                Restriction.category_id == category.id
            ).all()
            product_ids = [p.id for p in products]

            # 2. Buscar todos os ResultProduct com esses produtos
            result_products = ResultProduct.query.filter(
                ResultProduct.product_id.in_(product_ids)
            ).all()

            # 3. Coletar todos os Result que serão afetados
            result_ids = {rp.result_id for rp in result_products}

            # 4. Deletar todos os ResultProduct
            for rp in result_products:
                db.session.delete(rp)

            # 5. Deletar todos os Result
            for result_id in result_ids:
                result = Result.query.get(result_id)
                if result:
                    db.session.delete(result)

            # 6. Deletar os produtos associados à categoria
            for product in products:
                db.session.delete(product)

            # 7. Deletar a categoria (e automaticamente as restrictions via cascade)
            db.session.delete(category)

            db.session.commit()
            print('Categoria, produtos, insumos e resultados deletados com sucesso!')
    except Exception as err:
        db.session.rollback()
        print('Erro ao deletar categoria: ', err)

    return redirect('/register-products')

@bp.route('/save-products', methods=['POST'])
def register_product():
    try:
        products = []
        product_ids = set()

        # Pega id da categoria para remover produtos que não vieram no form (filtrando por categoria) e utilizalo nos preços
        category_id = request.form.get('category_id_prod')

        # Dados formulário
        for key in request.form:
            if key.startswith('products[') and 'restrictions' not in key:
                parts = key.split('[')
                product_index = int(parts[1].split(']')[0])
                field = parts[2].split(']')[0]

                while len(products) <= product_index:
                    products.append({
                        'id': None,
                        'name': '',
                        'profit_percentage': Decimal('0.00'),
                        'restrictions': [],
                    })

                value = request.form[key]

                if field == 'id':
                    products[product_index]['id'] = int(value)
                    product_ids.add(int(value))
                elif field == 'name':
                    products[product_index]['name'] = value

                elif field == 'profit_percentage':
                    products[product_index]['profit_percentage'] = Decimal(value.replace(',', '.'))

        # Capturar restrições
        for key in request.form:
            if 'restrictions' in key and 'quantity' in key:
                parts = key.split('[')
                product_index = int(parts[1].split(']')[0])
                restriction_index = int(parts[3].split(']')[0])

                quantity_key = f'products[{product_index}][restrictions][{restriction_index}][quantity]'
                id_key = f'products[{product_index}][restrictions][{restriction_index}][id]'

                if id_key in request.form and quantity_key in request.form:
                    restriction = {
                        'id': int(request.form.get(id_key)),
                        'quantity': Decimal(request.form.get(quantity_key).replace(',', '.'))
                    }
                    products[product_index]['restrictions'].append(restriction)

        # Trata os produtos
        for prod in products:
            if prod['id']:
                product = Product.query.get(prod['id'])
                # Produto já existente, atualiza
                if product:
                    product.name = prod['name']
                    product.profit_percentage = prod['profit_percentage'] # salva a porcentagem de lucro

                    category = Category.query.get(int(category_id))
                    days_production = category.days_production

                    product.price = calculate_unit_price(prod, days_production) # envia o produto com seus atributos e os dias de produção da categoria
                    product.price_total = (product.price * (Decimal('1.00') + prod['profit_percentage'] / Decimal('100.00'))).quantize(Decimal('0.01')) # preço final de custo do produto com base na porcentagem de lucro
                else:
                    continue  # se o id não for encontrado, pula

                # Atualiza ou insere restrições
                existing_restr = {
                    pr.restriction_id: pr for pr in product.restrictions
                }

                for r in prod['restrictions']:

                    if r['id'] in existing_restr:
                        existing_restr[r['id']].quantity_used = r['quantity']
                    else:
                        new_pr = ProductRestriction(
                            product_id=product.id,
                            restriction_id=r['id'],
                            quantity_used=r['quantity']
                        )
                        db.session.add(new_pr)

                # Remove restrições que não vieram
                current_restr_ids = [r['id'] for r in prod['restrictions']]
                for restr_id in list(existing_restr):
                    if restr_id not in current_restr_ids:
                        db.session.delete(existing_restr[restr_id])


            else:
                category = Category.query.get(int(category_id))
                days_production = category.days_production

                base_cost = calculate_unit_price(prod, days_production)

                # Novo produto
                product = Product(
                    name=prod['name'],
                    profit_percentage=prod['profit_percentage'],
                    price=base_cost,
                    price_total=(base_cost * (Decimal('1.00') + prod['profit_percentage'] / Decimal('100.00'))).quantize(Decimal('0.01'))
                )
                db.session.add(product)
                db.session.flush()
                product_ids.add(product.id)

                for r in prod['restrictions']:
                    new_pr = ProductRestriction(
                        product_id=product.id,
                        restriction_id=r['id'],
                        quantity_used=r['quantity']
                    )
                    db.session.add(new_pr)

        # Para excluir os que não vieram
        existing_products = Product.query.join(ProductRestriction).join(Restriction).filter(
            Restriction.category_id == category_id
        ).all()

        for p in existing_products:
            if p.id not in product_ids:
                db.session.delete(p)

        db.session.commit()
        flash("Produtos atualizados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print("Erro:", e)
        flash("Erro ao salvar produtos.")

    return redirect('/register-products')

@bp.route('/maximize-products', methods=['GET'])
def data_maximization():
    if not session.get('loggedin'):
        return redirect('/')

    result = get_all_data_categories()

    return render_template('maximize.html', categories=result)

def get_all_data_categories():
    categories = Category.query.all()
    result = []

    for cat in categories:
        category_dict = cat.to_json()

        # Pega os produtos que usam os insumos dessa categoria
        product_ids = (
            db.session.query(ProductRestriction.product_id)
            .join(Restriction)
            .filter(Restriction.category_id == cat.id)
            .distinct()
        )

        products = Product.query.filter(Product.id.in_(product_ids)).all()

        product_list = []
        for prod in products:
            # Restrições utilizadas nesse produto específicas para essa categoria
            used_restrictions = (
                db.session.query(ProductRestriction)
                .filter_by(product_id=prod.id)
                .join(Restriction)
                .filter(Restriction.category_id == cat.id)
                .all()
            )

            product_list.append({
                'id': prod.id,
                'name': prod.name,
                'price': float(prod.price),
                'price_total': float(prod.price_total),
                'profit_percentage': float(prod.profit_percentage),
                'restrictions': [
                    {
                        'id': pr.restriction_id,
                        'name': pr.restriction.name,
                        'quantity': float(pr.quantity_used),
                        'unit': pr.restriction.unit_type
                    }
                    for pr in used_restrictions
                ]
            })

        # Atribui no dicionário
        category_dict['products'] = product_list

        result.append(category_dict)

    return result or []

def calculate_unit_price(prod, days_production):
    restrictions_cost = Decimal('0.00')
    max_possible_product = None

    # 1. Custo dos insumos e cálculo da quantidade máxima de produtos possíveis
    for r in prod.get('restrictions', []):
        restr = Restriction.query.get(r['id'])
        if restr and restr.unit_price is not None:
            unit_price = Decimal(str(restr.unit_price))
            quantity_used = r['quantity']
            restrictions_cost += unit_price * quantity_used

            # Calcular a quantidade máxima de produtos possíveis com esse insumo
            if quantity_used > 0:
                possible = restr.quantity_available / quantity_used
                if max_possible_product is None:
                    max_possible_product = possible
                else:
                    max_possible_product = min(max_possible_product, possible)

    # Garante que não tenha divisão por zero
    if not max_possible_product or max_possible_product == 0:
        max_possible_product = Decimal('1.00')

    # 2. Custo fixo proporcional ao tempo de produção e quantidade de produtos
    total_fixed_cost = Decimal('0.00')
    fixed_costs = FixedCost.query.all()
    for fc in fixed_costs:
        mensal = Decimal(str(fc.price_month))
        diario = mensal / Decimal('30')
        proporcional = diario * Decimal(str(days_production))
        total_fixed_cost += proporcional

    unit_fixed_cost = total_fixed_cost / max_possible_product

    # 3. Soma tudo
    total_cost = (restrictions_cost + unit_fixed_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return total_cost
