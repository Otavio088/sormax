from flask import Blueprint, flash, render_template, request, session, redirect
from icecreampy.ext.database import db
from icecreampy.models.category import Category
from icecreampy.models.restrictions import Restriction
from sqlalchemy.orm import joinedload

bp = Blueprint('category_registration', __name__)

@bp.route('/register-products', methods=['GET', 'POST'])
def category_registration():
    if not session.get('loggedin'):
        return redirect('/')

    cats = Category.query.options(joinedload(Category.restrictions)).order_by(Category.name).all()
    cats_dict = [cat.to_json() for cat in cats]

    return render_template('register-products.html', categories=cats_dict)

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

            for id in to_delete:
                r = Restriction.query.get(id)
                db.session.delete(r)

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
