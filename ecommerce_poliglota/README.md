# Vitrine — E-commerce com Banco de Dados Poliglota

Aplicação acadêmica desenvolvida em Python + Streamlit, com Supabase (PostgreSQL/Auth), MongoDB e Redis.

## Funcionalidades

- Área pública: catálogo, busca, carrinho, totalização e finalização via WhatsApp.
- Área administrativa: login Supabase, cadastro, edição e exclusão de produtos no MongoDB.
- Redis: cache do catálogo por 60 segundos, invalidação após alterações e lista dos cinco produtos adicionados recentemente pelo visitante.

## Requisitos

- Python 3.10 ou superior
- Docker Desktop (para executar MongoDB e Redis localmente)
- Projeto Supabase

## 1. Preparar os serviços

Na pasta do projeto, execute:

```bash
docker compose up -d
```

Isso inicia MongoDB na porta `27017` e Redis na porta `6379`.

## 2. Preparar o Supabase

1. Crie um projeto no Supabase.
2. Em Authentication > Users, crie o usuário administrador (e-mail e senha).
3. Em Project Settings > API, copie a Project URL e a chave `anon`/publishable compatível com o SDK.
4. A aplicação usa Supabase Auth para autenticar o administrador. O e-mail também precisa estar na variável `ADMIN_EMAILS`.

Não coloque a `service_role` key no aplicativo nem publique credenciais no GitHub.

## 3. Configurar ambiente Python

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .envd .env
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` e informe `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `ADMIN_EMAILS` e, se desejar, `WHATSAPP_NUMBER`.

## 4. Executar

```bash
streamlit run app.py
```

O navegador abrirá a aplicação localmente.

## Como demonstrar o Redis

- Abra a loja pela primeira vez: o catálogo é consultado no MongoDB e armazenado no Redis por 60 segundos.
- Atualize a página/consulte novamente: o catálogo pode ser servido pelo cache.
- Cadastre, edite ou exclua um produto pela administração: a chave de cache é invalidada para que a próxima consulta busque os dados atualizados.
- Adicione produtos ao carrinho: os cinco produtos adicionados mais recentemente são registrados no Redis por visitante, com expiração de sete dias.

## Estrutura de dados

Coleção MongoDB `ecommerce.products`:

```json
{
  "name": "Nome do produto",
  "description": "Descrição do produto",
  "price": 49.9,
  "image_url": "https://exemplo.com/imagem.jpg",
  "active": true,
  "created_at": "2026-11-14T12:00:00+00:00",
  "updated_at": "2026-11-14T12:00:00+00:00"
}
```


