# 🛍️ Vitrine – E-commerce

Um projeto de loja virtual desenvolvido com Python e Streamlit, com integração a bancos de dados e serviços externos para oferecer uma experiência de navegação e gerenciamento de produtos.

LINK DA APLICAÇÂO WEB COLAR NO GOOGLE: e-commerce-mgjeg5vrbmkguff7mwc6m2
.streamlit.app

## 👨‍💻 Desenvolvedores

- **Bilsã**
- **Guilherme Edilson**

Projeto desenvolvido em conjunto por Bilsã e Guilherme Edilson.

## 📌 Sobre o projeto

A **Vitrine** é uma aplicação de e-commerce criada com o objetivo de simular o funcionamento de uma loja virtual. O sistema permite que os usuários visualizem produtos, consultem informações, adicionem itens ao carrinho e acompanhem os produtos visualizados recentemente.

Além da área destinada aos clientes, o projeto possui um painel administrativo protegido por autenticação, permitindo o gerenciamento dos produtos cadastrados na loja.

## 🚀 Tecnologias e recursos utilizados

### 🐍 Python
Linguagem de programação utilizada para desenvolver a lógica e o funcionamento da aplicação.

### 🎈 Streamlit
Framework utilizado para construir a interface visual do site e disponibilizar a aplicação na internet.

### 🍃 MongoDB
Banco de dados utilizado para armazenar as informações dos produtos, permitindo operações de cadastro, consulta, edição e exclusão.

### 🔐 Supabase
Serviço utilizado para realizar a autenticação dos administradores, controlando o acesso ao painel administrativo.

### ⚡ Redis
Banco de dados em memória utilizado para melhorar o desempenho da aplicação por meio de cache de produtos e armazenamento temporário dos produtos visualizados recentemente.

### 📦 Bibliotecas adicionais

- **PyMongo:** integração entre Python e MongoDB.
- **Redis-py:** comunicação entre Python e Redis.
- **Supabase-py:** integração com os serviços do Supabase.
- **Certifi:** disponibilização de certificados para conexões seguras.
- **Python-dotenv:** carregamento de variáveis de ambiente a partir do arquivo `.env`.

## ✨ Funcionalidades

### 🛒 Área do cliente
- Visualização dos produtos disponíveis.
- Exibição de nomes, preços, imagens e descrições.
- Adição de produtos ao carrinho.
- Visualização dos itens selecionados.
- Cálculo do valor total do carrinho.
- Histórico de produtos visualizados recentemente.

### ⚙️ Painel administrativo
- Login de administradores.
- Controle de acesso por e-mail autorizado.
- Cadastro de novos produtos.
- Edição de produtos existentes.
- Exclusão de produtos cadastrados.
- Gerenciamento do catálogo da loja.

### ⚡ Desempenho e armazenamento
- Cache temporário dos produtos utilizando Redis.
- Atualização do cache quando os produtos são modificados.
- Armazenamento permanente dos produtos no MongoDB.
- Registro temporário de produtos visualizados recentemente.

## 🏗️ Organização do sistema

Cada tecnologia possui uma responsabilidade específica:

| Tecnologia | Responsabilidade |
|---|---|
| Python | Lógica da aplicação |
| Streamlit | Interface e publicação do site |
| MongoDB | Armazenamento dos produtos |
| Redis | Cache e produtos recentes |
| Supabase | Autenticação administrativa |

## 🌐 Hospedagem

A aplicação foi publicada utilizando o **Streamlit Community Cloud**, permitindo o acesso ao sistema por meio de um endereço na internet.

As credenciais e configurações dos serviços externos são armazenadas em variáveis de ambiente e nos Secrets do Streamlit.

## 🎯 Objetivo do projeto

O objetivo da Vitrine é aplicar conhecimentos de programação, desenvolvimento web, integração de bancos de dados, autenticação e otimização de desempenho, criando uma aplicação que simula funcionalidades de um comércio eletrônico.

## 👥 Autoria

**Desenvolvido por Bilsã e Guilherme Edilson.**

Projeto acadêmico – Vitrine E-commerce.
