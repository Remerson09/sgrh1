
from flask import Flask, render_template, request, session, flash, redirect, url_for

from flask_sqlalchemy import SQLAlchemy


# Inicialize o app
app = Flask(__name__)
app.secret_key = 'ifto'

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sgrh-remersonConceicao.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialize o SQLAlchemy
db = SQLAlchemy(app)


from models import Pessoa, Profissao, FolhaPagamento, Capacitacao


with app.app_context():
    db.create_all()

@app.route('/')
def opa():
    if session.get('usuario'):
        return render_template('base.html')
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/index')
def ola():
    if session.get('usuario'):
        return render_template('base.html')
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/login')
def login():
    proxima = request.args.get('proxima', 'index')
    return render_template('login.html', proxima=proxima)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    if request.method == 'POST':
        user = request.form['user']
        senha = request.form['password']
        proxima_pagina = request.form.get('proxima', 'index')
        pessoa = db.session.query(Pessoa).filter_by(nome=user).first()
        if pessoa != None:
            if pessoa.nome == user and pessoa.senha == senha:
                session['usuario'] = user
                flash(session['usuario'] + " logado com sucesso!")
                return redirect(proxima_pagina)
        if user == "remerson" and senha == "123":
            session['usuario'] = "admin"
            flash(session['usuario'] + " logado com sucesso!")
            return redirect(url_for('form_pessoa'))

        flash("Login falhou.")
        return redirect(url_for('login', proxima=proxima_pagina))

@app.route('/logout')
def logout():
    if session.get('usuario'):
        session.pop('usuario', None)
        flash("Logout realizado com sucesso!")
    else:
        flash("Já está deslogado.")
    return redirect(url_for('login'))

@app.route('/listar_pessoas')
def listape():
    if session.get('usuario'):
        return render_template('lista.html', pessoas=db.session.query(Pessoa).all())
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/listar_profissoes')
def listapr():
    if session.get('usuario'):
        return render_template('saida_profissao.html', profissaos=db.session.query(Profissao).all())
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/form', methods=['GET', 'POST'])
def form_pessoa():
    if session.get('usuario') != None:
        if request.method == 'POST':
            nome = request.form['nome']
            cpf = request.form['cpf']
            endereco = request.form['endereco']
            profissao = request.form['profissao']
            return render_template('index.html', nome=nome, cpf=cpf, endereco=endereco, profissao=profissao)
        return render_template('form.html')
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/form_profissao', methods=['GET', 'POST'])
def form_profissao():
    if session.get('usuario') != None:
        if request.method == 'POST':
            nome = request.form['nome']
            status = request.form['status']
            return render_template('index.html', nome=nome, status=status)
        return render_template('form_profissao.html')
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if session.get('usuario') != None:
        if request.method == 'POST':
            nome = request.form['nome']
            senha = request.form['senha']
            endereco = request.form['endereco']
            profissao = request.form['profissao']

            pessoaR = Pessoa(nome=nome, senha=senha, endereco=endereco, profissao=profissao)

            db.session.add(pessoaR)
            db.session.commit()

            return render_template('lista.html', pessoas=db.session.query(Pessoa).all())
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/criar_profissao', methods=['GET', 'POST'])
def criar_profissao():
    if session.get('usuario') != None:
        if request.method == 'POST':
            nome = request.form['nome']
            status = request.form['status']

            profissaoR = Profissao(profissao=nome, status=status)

            db.session.add(profissaoR)
            db.session.commit()

            return render_template('saida_profissao.html', profissaos=db.session.query(Profissao).all())
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))


@app.route('/rm_profissao/<int:id>', methods=['POST'])
def rm_profissao(id):
    if session.get('usuario') != None:
        if request.method == 'POST':
            profissao = db.session.query(Profissao).get(id)
            if profissao is None:
                # Procurando pela profissão pelo nome caso não encontre pelo ID
                nome = request.form.get('nome')
                profissao = db.session.query(Profissao).filter_by(profissao=nome).first()

            if profissao:
                db.session.delete(profissao)
                db.session.commit()
                return render_template('saida_profissao.html', profissaos=db.session.query(Profissao).all())
            flash("Erro: Profissão não encontrada.")
            return render_template('saida_profissao.html', profissaos=db.session.query(Profissao).all())
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))


@app.route('/rm_pessoa/<int:id>', methods=['POST'])
def rm_pessoa(id):
    if session.get('usuario') is not None:
        if request.method == 'POST':
            pessoa = db.session.query(Pessoa).get(id)
            if pessoa is None:
                # Procurando pela pessoa pelo nome caso não encontre pelo ID
                nome = request.form.get('nome')
                pessoa = db.session.query(Pessoa).filter_by(nome=nome).first()

            if pessoa:
                # Verificar se há capacitações associadas
                capacitacoes = db.session.query(Capacitacao).filter_by(pessoa_id=pessoa.id).all()
                if capacitacoes:
                    flash(f"Não é possível deletar {pessoa.nome} porque há capacitações associadas.")
                    return redirect(url_for('listape')) # Redirecionar para a lista de pessoas

                # Se não houver capacitações associadas, deletar a pessoa
                db.session.delete(pessoa)
                db.session.commit()
                flash(f"Pessoa {pessoa.nome} deletada com sucesso!")
                return redirect(url_for('listape'))
            else:
                flash("Erro: Pessoa não encontrada.")
                return redirect(url_for('listape'))
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))


@app.route('/form_capacitacao', methods=['GET', 'POST'])
def form_capacitacao():
    if session.get('usuario') is not None:
        # Buscar todas as pessoas cadastradas no banco de dados
        pessoas = db.session.query(Pessoa).all()
        return render_template('form_capacitacao.html', pessoas=pessoas)
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

from datetime import datetime

@app.route('/rm_capacitacao/<int:id>', methods=['POST'])
def rm_capacitacao(id):
    if session.get('usuario') is not None:
        if request.method == 'POST':
            capacitacao = db.session.query(Capacitacao).get(id)
            if capacitacao:
                db.session.delete(capacitacao)
                db.session.commit()
                flash(f"Capacitação '{capacitacao.curso}' deletada com sucesso!")
            else:
                flash("Erro: Capacitação não encontrada.")
        return redirect(url_for('listar_capacitacoes'))  # Redirecionar para a lista de capacitações
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))


@app.route('/criar_capacitacao', methods=['POST'])
def criar_capacitacao():
    if session.get('usuario') != None:
        if request.method == 'POST':
            pessoa_id = request.form['pessoa_id']
            pessoa = db.session.query(Pessoa).get(pessoa_id)  # Buscar o nome da pessoa pelo ID
            if pessoa:
                curso = request.form['curso']
                instituicao = request.form['instituicao']
                data_conclusao_str = request.form['data_conclusao']

                # Converte a string para um objeto datetime
                data_conclusao = datetime.strptime(data_conclusao_str, '%Y-%m-%d').date()

                capacitacao = Capacitacao(
                    pessoa_id=pessoa_id,
                    curso=curso,
                    instituicao=instituicao,
                    data_conclusao=data_conclusao
                )
                db.session.add(capacitacao)
                db.session.commit()
                flash(f"Capacitação cadastrada com sucesso para {pessoa.nome}!")
                return redirect(url_for('listar_capacitacoes'))
            else:
                flash("Pessoa não encontrada.")
                return redirect(url_for('form_capacitacao'))
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))


@app.route('/listar_capacitacoes')
def listar_capacitacoes():
    capacitacoes = db.session.query(Capacitacao).all()
    capacitacoes_formatadas = []
    for capacitacao in capacitacoes:
        capacitacao_formatada = {
            'pessoa': capacitacao.pessoa,
            'curso': capacitacao.curso,
            'instituicao': capacitacao.instituicao,
            'data_conclusao': capacitacao.data_conclusao.strftime('%d-%m-%Y'),
            'id': capacitacao.id
        }
        capacitacoes_formatadas.append(capacitacao_formatada)
    return render_template('lista_capacitacoes.html', capacitacoes=capacitacoes_formatadas)


@app.route('/form_folha_pagamento', methods=['GET', 'POST'])
def form_folha_pagamento():
    if session.get('usuario') is not None:
        # Buscar todas as pessoas cadastradas no banco de dados
        pessoas = db.session.query(Pessoa).all()
        return render_template('form_folha_pagamento.html', pessoas=pessoas)
    else:
        flash("Faça login primeiro.")

@app.route('/criar_folha_pagamento', methods=['POST'])
def criar_folha_pagamento():
    if session.get('usuario') != None:
        if request.method == 'POST':
            pessoa_id = request.form['pessoa_id']
            pessoa = db.session.query(Pessoa).get(pessoa_id)  # Buscar o nome da pessoa pelo ID
            if pessoa:
                salario = request.form['salario']
                data_pagamento_str = request.form['data_pagamento']
                data_pagamento = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()  # Converte para date
                folha = FolhaPagamento(pessoa_id=pessoa_id, salario=salario, data_pagamento=data_pagamento)
                db.session.add(folha)
                db.session.commit()
                flash(f"Folha de Pagamento cadastrada com sucesso para {pessoa.nome}!")
                return redirect(url_for('listar_folhas_pagamento'))
            else:
                flash("Pessoa não encontrada.")
                return redirect(url_for('form_folha_pagamento'))
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))


@app.route('/listar_folhas_pagamento')
def listar_folhas_pagamento():
    if session.get('usuario') != None:
        folhas = db.session.query(FolhaPagamento).all()
        return render_template('lista_folhas_pagamento.html', folhas=folhas)
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))

@app.route('/rm_folha_pagamento/<int:id>', methods=['POST'])
def rm_folha_pagamento(id):
    if session.get('usuario') is not None:
        if request.method == 'POST':
            folha = db.session.query(FolhaPagamento).get(id)
            if folha:
                pessoa_nome = None
                if folha.pessoa:
                    pessoa_nome = folha.pessoa.nome  # Isso força o carregamento de `pessoa`
                db.session.delete(folha)
                db.session.commit()
                if pessoa_nome:
                    flash(f"Folha de pagamento de {pessoa_nome} excluída com sucesso!")
                else:
                    flash("Folha de pagamento excluída com sucesso!")
            else:
                flash("Erro: Folha de pagamento não encontrada.")
        return redirect(url_for('listar_folhas_pagamento'))  # Redirecionar para a lista de folhas de pagamento
    else:
        flash("Faça login primeiro.")
        return redirect(url_for('login', proxima=request.url))
@app.route('/somar_folhas', methods=['POST'])
def somar_folhas():
        folha_ids = request.form.getlist('folha_ids')
        total_salario = 0

        if folha_ids:
            folhas_selecionadas = db.session.query(FolhaPagamento).filter(FolhaPagamento.id.in_(folha_ids)).all()
            total_salario = sum(folha.salario for folha in folhas_selecionadas)

        folhas = db.session.query(FolhaPagamento).all()
        return render_template('lista_folhas_pagamento.html', folhas=folhas, total_salario=total_salario)


if __name__ == '__main__':
    app.run(debug=True)
