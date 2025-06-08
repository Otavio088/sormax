from decimal import Decimal
from flask import Blueprint, flash, render_template, request, session, redirect
from icecreampy.ext.database import db
from icecreampy.models.category import Category
from icecreampy.models.restrictions import Restriction
from icecreampy.models.products import Product
from icecreampy.models.products_restrictions import ProductRestriction
from sqlalchemy.orm import joinedload

bp = Blueprint('category_routes', __name__)

@bp.route('/register-products', methods=['GET', 'POST'])
def category_registration():
    if not session.get('loggedin'):
        return redirect('/')

    result = get_all_data_categories()

    return render_template('register-products.html', categories=result)

@bp.route('/register-category', methods=['POST'])
def register_category():
    category_id = request.form.get('category_id')
    category_name = request.form.get('category')
    restrictions = []

    # Pega todas os insumos trazidos pelo formulário
    for key in request.form:
        if key.startswith('restrictions['):
            index = key.split('[')[1].split(']')[0]
            field = key.split('[')[2].split(']')[0]

            # Garante que o insumo com esse índice existe
            while len(restrictions) <= int(index):
                restrictions.append({"name": "", "quantity": "", "unit": ""})
            restrictions[int(index)][field] = request.form[key]

    try:
        if (category_id):
            # Consulta tudo que tem esse id de categoria
            cat = Category.query.get(category_id)
            cat.name = category_name
        else:
            # Nova categoria para adicionar no banco
            cat = Category(name=category_name)
            db.session.add(cat)
            db.session.flush() # Envia operações SQL para o banco mas nao finaliza a transação

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

                    received_ids.add(restriction.id)                    
            else:
                # Insert no caso de não tiver o id vindo do form
                new_restriction = Restriction(
                    category_id = cat.id,
                    name = r['name'],
                    unit_type = r['unit'],
                    quantity_available = r['quantity']
                )
                db.session.add(new_restriction)
                db.session.flush() # PReenche o new_restriction.id com valor gerado no banco
                received_ids.add(new_restriction.id)

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
            db.session.delete(category)
            db.session.commit()
            print('Categoria deletada com sucesso!')
    except Exception as err:
        db.session.rollback()
        print('Erro ao deletar categoria: ', err)

    return redirect('/register-products')

@bp.route('/save-products', methods=['POST'])
def register_product():
    try:
        print("request.form dict:", request.form.to_dict(flat=False))
        
        products = []
        product_ids = set()

        for key in request.form:
            if key.startswith('products[') and 'restrictions' not in key:
                parts = key.split('[')
                product_index = int(parts[1].split(']')[0])
                field = parts[2].split(']')[0]

                while len(products) <= product_index:
                    products.append({'id': None, 'name': '', 'price': Decimal('0.00'), 'restrictions': []})

                value = request.form[key]

                if field == 'id':
                    products[product_index]['id'] = int(value)
                    product_ids.add(int(value))
                elif field == 'name':
                    products[product_index]['name'] = value
                elif field == 'price':
                    products[product_index]['price'] = Decimal(value.replace(',', '.'))

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

        for prod in products:
            if prod['id']:
                # Produto já existente, atualiza
                product = Product.query.get(prod['id'])
                if product:
                    product.name = prod['name']
                    product.price = prod['price']
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
                # Novo produto
                product = Product(name=prod['name'], price=prod['price'])
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

        # Remover produtos que não vieram no form (filtrando por categoria)
        category_id = request.form.get('category_id_prod')

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
    categories = Category.query.options(joinedload(Category.restrictions)).order_by(Category.name).all()
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

        category_dict['products'] = product_list
        result.append(category_dict)

    return result or []