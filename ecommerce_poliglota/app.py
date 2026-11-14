import os
import json
import html
from datetime import datetime, timezone
from urllib.parse import quote

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError
from redis import Redis
from redis.exceptions import RedisError
from supabase import create_client, Client

load_dotenv()
st.set_page_config(page_title="Vitrine | E-commerce", page_icon="🛍️", layout="wide")

# ---------- Configurações e conexões ----------
@st.cache_resource
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("Configure SUPABASE_URL e SUPABASE_ANON_KEY no arquivo .env.")
    return create_client(url, key)

@st.cache_resource
def get_mongo_collection():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017").strip()
    db_name = os.getenv("MONGODB_DATABASE", "ecommerce").strip()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    collection = client[db_name]["products"]
    collection.create_index([("created_at", DESCENDING)])
    collection.create_index("name")
    return collection

@st.cache_resource
def get_redis():
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0").strip()
    client = Redis.from_url(url, decode_responses=True, socket_connect_timeout=3)
    client.ping()
    return client


def admin_emails():
    return {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}


def money(value):
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def load_products(collection, redis_client):
    cache_key = "ecommerce:products:catalog:v1"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached), True
    except RedisError:
        pass
    products = []
    for doc in collection.find({"active": {"$ne": False}}).sort("created_at", DESCENDING):
        doc["_id"] = str(doc["_id"])
        products.append(doc)
    try:
        redis_client.setex(cache_key, 60, json.dumps(products, default=str, ensure_ascii=False))
    except RedisError:
        pass
    return products, False


def invalidate_catalog(redis_client):
    try:
        redis_client.delete("ecommerce:products:catalog:v1")
    except RedisError:
        pass


def register_recent(redis_client, product):
    try:
        key = f"ecommerce:recent:{st.session_state.get('visitor_id', 'guest')}"
        redis_client.lrem(key, 0, product["_id"])
        redis_client.lpush(key, product["_id"])
        redis_client.ltrim(key, 0, 4)
        redis_client.expire(key, 60 * 60 * 24 * 7)
    except RedisError:
        pass


def get_recent_ids(redis_client):
    try:
        key = f"ecommerce:recent:{st.session_state.get('visitor_id', 'guest')}"
        return redis_client.lrange(key, 0, 4)
    except RedisError:
        return []


def whatsapp_link(cart, products_by_id):
    lines = []
    total = 0.0
    for product_id, qty in cart.items():
        product = products_by_id.get(product_id)
        if not product:
            continue
        subtotal = float(product.get("price", 0)) * qty
        total += subtotal
        lines.append(f"{qty}x {product.get('name', 'Produto')} - {money(subtotal)}")
    message = "Olá! Gostaria de fazer o seguinte pedido:\n" + "\n".join(lines) + f"\n\nTotal: {money(total)}"
    phone = "".join(ch for ch in os.getenv("WHATSAPP_NUMBER", "").strip() if ch.isdigit())
    base = f"https://wa.me/{phone}" if phone else "https://wa.me/"
    return base + "?text=" + quote(message), message, total


# ---------- Estado da sessão ----------
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "visitor_id" not in st.session_state:
    import uuid
    st.session_state.visitor_id = str(uuid.uuid4())
if "admin_session" not in st.session_state:
    st.session_state.admin_session = None

# ---------- Estilo ----------
st.markdown("""
<style>
  .main {background: #f7f8fc;}
  .hero {padding: 1.6rem 1.8rem; border-radius: 18px; background: linear-gradient(120deg,#172554,#2563eb); color: white; margin-bottom: 1.2rem;}
  .hero h1 {color:white; margin:0; font-size:2.1rem;}
  .hero p {color:#dbeafe; margin:.45rem 0 0 0;}
  div[data-testid="stMetric"] {background:white; padding:14px; border-radius:12px; border:1px solid #e7eaf2;}
  .small-muted {color:#64748b; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🛍️ Vitrine")
page = st.sidebar.radio("Navegação", ["Loja", "Carrinho", "Administração"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption("E-commerce acadêmico • Python + Supabase + MongoDB + Redis")

# Inicializa conexões necessárias para loja/admin
try:
    collection = get_mongo_collection()
except Exception as exc:
    st.error("Não foi possível conectar ao MongoDB. Confira o serviço e MONGODB_URI no .env.")
    st.exception(exc)
    st.stop()
try:
    redis_client = get_redis()
    redis_ok = True
except Exception:
    redis_client = None
    redis_ok = False
    st.sidebar.warning("Redis indisponível: a loja continuará funcionando sem cache.")

# ---------- Loja ----------
if page == "Loja":
    st.markdown('<div class="hero"><h1>Encontre o que você procura.</h1><p>Produtos selecionados para facilitar suas escolhas.</p></div>', unsafe_allow_html=True)
    search = st.text_input("Buscar produto", placeholder="Digite o nome de um produto...")
    try:
        products, from_cache = load_products(collection, redis_client) if redis_client else (list(collection.find({"active": {"$ne": False}}).sort("created_at", DESCENDING)), False)
        if not redis_client:
            for p in products: p["_id"] = str(p["_id"])
    except PyMongoError as exc:
        st.error(f"Erro ao consultar os produtos: {exc}")
        products = []
    if search:
        products = [p for p in products if search.lower() in p.get("name", "").lower() or search.lower() in p.get("description", "").lower()]
    st.caption(f"{len(products)} produto(s) encontrado(s)" + (" • carregados do cache Redis" if from_cache else ""))
    if not products:
        st.info("Ainda não há produtos cadastrados. A área administrativa pode adicionar os primeiros itens.")
    else:
        cols = st.columns(3)
        for index, product in enumerate(products):
            with cols[index % 3]:
                with st.container(border=True):
                    image_url = product.get("image_url", "")
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.markdown("<div style='height:150px;background:#e2e8f0;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#64748b'>Sem imagem</div>", unsafe_allow_html=True)
                    st.subheader(product.get("name", "Produto"))
                    st.write(product.get("description", ""))
                    st.markdown(f"### {money(product.get('price', 0))}")
                    qty_key = f"qty_{product['_id']}"
                    qty = st.number_input("Quantidade", min_value=1, max_value=99, value=1, step=1, key=qty_key)
                    if st.button("Adicionar ao carrinho", key=f"add_{product['_id']}", use_container_width=True):
                        st.session_state.cart[product["_id"]] = st.session_state.cart.get(product["_id"], 0) + int(qty)
                        if redis_client: register_recent(redis_client, product)
                        st.toast(f"{product.get('name')} adicionado ao carrinho!")
    if redis_client:
        recent_ids = get_recent_ids(redis_client)
        if recent_ids:
            by_id = {p["_id"]: p for p in (products if not search else load_products(collection, redis_client)[0])}
            recent = [by_id[i] for i in recent_ids if i in by_id]
            if recent:
                st.markdown("---")
                st.subheader("Vistos recentemente")
                st.write(" • ".join(p.get("name", "Produto") for p in recent))

# ---------- Carrinho ----------
elif page == "Carrinho":
    st.title("🛒 Meu carrinho")
    all_docs = list(collection.find({}))
    products_by_id = {str(p["_id"]): p for p in all_docs}
    if not st.session_state.cart:
        st.info("Seu carrinho está vazio. Volte à loja para adicionar produtos.")
    else:
        total = 0.0
        for product_id in list(st.session_state.cart.keys()):
            product = products_by_id.get(product_id)
            if not product:
                del st.session_state.cart[product_id]
                continue
            qty = st.session_state.cart[product_id]
            price = float(product.get("price", 0))
            subtotal = price * qty
            total += subtotal
            c1, c2, c3, c4 = st.columns([4, 1, 2, 1])
            c1.write(f"**{product.get('name')}**")
            c2.write(f"{qty}x")
            c3.write(money(subtotal))
            if c4.button("Remover", key=f"remove_{product_id}"):
                del st.session_state.cart[product_id]
                st.rerun()
        st.divider()
        st.metric("Total do pedido", money(total))
        link, message, total = whatsapp_link(st.session_state.cart, products_by_id)
        st.caption("Confira os itens e finalize pelo WhatsApp. O pedido será enviado como mensagem; o pagamento é combinado diretamente com a loja.")
        st.link_button("Finalizar pedido pelo WhatsApp", link, type="primary", use_container_width=True)
        with st.expander("Visualizar mensagem do pedido"):
            st.code(message)
        if st.button("Esvaziar carrinho"):
            st.session_state.cart = {}
            st.rerun()

# ---------- Administração ----------
else:
    st.title("🔐 Administração")
    if not st.session_state.admin_session:
        st.write("Entre com uma conta criada no Supabase Auth e autorizada como administradora.")
        with st.form("admin_login"):
            email = st.text_input("E-mail", placeholder="admin@exemplo.com")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        if submitted:
            try:
                sb = get_supabase()
                response = sb.auth.sign_in_with_password({"email": email, "password": password})
                user_email = (response.user.email or "").lower()
                allowed = admin_emails()
                if not allowed or user_email not in allowed:
                    sb.auth.sign_out()
                    st.error("Conta autenticada, mas não autorizada. Inclua o e-mail em ADMIN_EMAILS no .env.")
                else:
                    st.session_state.admin_session = {"email": user_email}
                    st.success("Login realizado com sucesso!")
                    st.rerun()
            except Exception as exc:
                st.error("Não foi possível entrar. Confira e-mail, senha e configuração do Supabase.")
                st.caption(str(exc))
    else:
        top1, top2 = st.columns([4, 1])
        top1.success(f"Administrador conectado: {st.session_state.admin_session['email']}")
        if top2.button("Sair"):
            try: get_supabase().auth.sign_out()
            except Exception: pass
            st.session_state.admin_session = None
            st.rerun()
        st.subheader("Cadastrar novo produto")
        with st.form("new_product", clear_on_submit=True):
            name = st.text_input("Nome do produto*")
            description = st.text_area("Descrição")
            price = st.number_input("Preço (R$)*", min_value=0.01, value=10.00, step=1.00, format="%.2f")
            image_url = st.text_input("URL da imagem", placeholder="https://...")
            active = st.checkbox("Produto disponível na loja", value=True)
            save = st.form_submit_button("Cadastrar produto", type="primary")
        if save:
            if not name.strip():
                st.error("Informe o nome do produto.")
            else:
                try:
                    collection.insert_one({"name": name.strip(), "description": description.strip(), "price": float(price), "image_url": image_url.strip(), "active": active, "created_at": datetime.now(timezone.utc).isoformat(), "updated_at": datetime.now(timezone.utc).isoformat()})
                    if redis_client: invalidate_catalog(redis_client)
                    st.success("Produto cadastrado! O catálogo será atualizado na próxima consulta.")
                    st.rerun()
                except PyMongoError as exc:
                    st.error(f"Não foi possível cadastrar o produto: {exc}")
        st.divider()
        st.subheader("Produtos cadastrados")
        docs = list(collection.find({}).sort("created_at", DESCENDING))
        if not docs:
            st.info("Nenhum produto cadastrado ainda.")
        for doc in docs:
            pid = str(doc["_id"])
            with st.expander(f"{doc.get('name', 'Produto')} — {money(doc.get('price', 0))}"):
                with st.form(f"edit_{pid}"):
                    ename = st.text_input("Nome", value=doc.get("name", ""), key=f"ename_{pid}")
                    edesc = st.text_area("Descrição", value=doc.get("description", ""), key=f"edesc_{pid}")
                    eprice = st.number_input("Preço (R$)", min_value=0.01, value=max(0.01, float(doc.get("price", 0.01))), step=1.0, key=f"eprice_{pid}")
                    eimage = st.text_input("URL da imagem", value=doc.get("image_url", ""), key=f"eimage_{pid}")
                    eactive = st.checkbox("Disponível", value=bool(doc.get("active", True)), key=f"eactive_{pid}")
                    update = st.form_submit_button("Salvar alterações")
                d1, d2 = st.columns(2)
                if update:
                    collection.update_one({"_id": doc["_id"]}, {"$set": {"name": ename.strip(), "description": edesc.strip(), "price": float(eprice), "image_url": eimage.strip(), "active": eactive, "updated_at": datetime.now(timezone.utc).isoformat()}})
                    if redis_client: invalidate_catalog(redis_client)
                    st.success("Produto atualizado.")
                    st.rerun()
                if d2.button("Excluir produto", key=f"delete_{pid}"):
                    collection.delete_one({"_id": doc["_id"]})
                    if redis_client: invalidate_catalog(redis_client)
                    st.warning("Produto excluído.")
                    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Status dos serviços")
st.sidebar.write("🟢 MongoDB conectado")
st.sidebar.write("🟢 Supabase configurado" if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY") else "🟠 Supabase pendente de configuração")
st.sidebar.write("🟢 Redis conectado" if redis_ok else "🟠 Redis indisponível")
