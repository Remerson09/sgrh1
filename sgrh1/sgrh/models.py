from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pessoa(db.Model):
    __tablename__ = 'pessoa'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(150), nullable=False)
    profissao = db.Column(db.String(100), nullable=False)
    # Relacionamento com FolhaPagamento e Capacitacao
    folhas_pagamento = db.relationship('FolhaPagamento', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    capacitacoes = db.relationship('Capacitacao', backref='pessoa', lazy=True, cascade="all, delete-orphan")

class Profissao(db.Model):
    __tablename__ = 'profissao'
    id = db.Column(db.Integer, primary_key=True)
    profissao = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

class FolhaPagamento(db.Model):
    __tablename__ = 'folha_pagamento'
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id', ondelete='CASCADE'), nullable=False)
    salario = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=False)

class Capacitacao(db.Model):
    __tablename__ = 'capacitacao'
    id = db.Column(db.Integer, primary_key=True)
    pessoa_id = db.Column(db.Integer, db.ForeignKey('pessoa.id', ondelete='CASCADE'), nullable=False)
    curso = db.Column(db.String(100), nullable=False)
    instituicao = db.Column(db.String(100), nullable=False)
    data_conclusao = db.Column(db.Date, nullable=False)
