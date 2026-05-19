import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Spaço Laila Souza", layout="wide", page_icon="💅")

# --- BANCO DE DADOS ---
conn = sqlite3.connect('salao_premium.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, whatsapp TEXT, aniversario TEXT, molde_f_dir TEXT, molde_f_esq TEXT, ultima_visita TEXT, total_visitas INTEGER DEFAULT 0)')
cursor.execute('CREATE TABLE IF NOT EXISTS servicos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL)')
cursor.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco_custo REAL, preco_venda REAL, estoque INTEGER)')
cursor.execute('CREATE TABLE IF NOT EXISTS agenda (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER, servicos TEXT, data TEXT, hora TEXT, status TEXT DEFAULT "Agendado", row_color TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, cliente_nome TEXT, descricao TEXT, valor REAL, forma_pagamento TEXT, data TEXT, status TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_nome TEXT, data TEXT, conteudo_html TEXT)')
# Nova tabela para controle de custos/saídas
cursor.execute('CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY AUTOINCREMENT, descricao TEXT, valor REAL, categoria TEXT, data TEXT)')
conn.commit()

# --- SISTEMA DE NAVEGAÇÃO ---
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "Agenda"

# --- DESIGN PREMIUM REESTRUTURADO (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        /* Fundo Cinza Moderno e Fontes */
        html, body, [data-testid="stWidgetLabel"] p, .stMarkdown {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: #333333 !important;
        }
        .main { background-color: #EAEAEA !important; } /* Fundo Cinza Elegante */
        [data-testid="stSidebar"] { display: none !important; }
        .block-container { padding: 30px 50px !important; max-width: 100% !important; }
        
        /* Nome do Salão Centralizado no Topo */
        .salon-title-container {
            text-align: center;
            padding: 20px 0;
            margin-bottom: 25px;
        }
        .salon-title {
            font-size: 42px;
            font-weight: 700;
            color: #262626;
            letter-spacing: 2px;
            margin: 0;
        }
        .salon-subtitle {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 4px;
            color: #8C6246;
            margin-top: 5px;
        }

        /* Container do Painel de Informações Financeiras */
        .info-dashboard {
            background-color: #FFFFFF;
            border-radius: 24px;
            padding: 25px 40px;
            border: 1px solid #D1D1D1;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.03);
            margin-bottom: 35px;
        }
        
        /* Botões de Ação Cinza (Estilo Flutuante Arredondado) */
        div.nav-bar-buttons button {
            background: #3A3A3A !important; /* Cinza Escuro */
            color: #FFFFFF !important;
            border: none !important;
            padding: 12px 20px !important;
            border-radius: 16px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
            transition: all 0.2s ease !important;
            width: 100%;
        }
        div.nav-bar-buttons button:hover {
            background: #8C6246 !important; /* Toque amadeirado clássico no clique/hover */
            transform: translateY(-2px);
        }
        
        /* Cards Brancos de Conteúdo Abaixo */
        .premium-card {
            background: #FFFFFF;
            border-radius: 24px;
            padding: 30px;
            border: 1px solid #D1D1D1;
            box-shadow: 0 8px 20px rgba(0,0,0,0.02);
            margin-top: 25px;
        }
        
        /* Slots de Atendimento */
        .timeline-slot {
            background: linear-gradient(135deg, #A67553 0%, #8C6246 100%);
            border-radius: 16px;
            padding: 20px;
            color: white !important;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .timeline-slot h5, .timeline-slot span, .timeline-slot div { color: white !important; }

        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            border: 1px solid #D1D1D1 !important;
            border-radius: 24px !important;
            padding: 30px !important;
        }

        div[data-testid="stForm"] .stButton>button {
            background: #8C6246 !important;
            color: white !important;
            border-radius: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. NOME DO SALÃO NO CENTRO DO TOPO
# ==========================================
st.markdown("""
    <div class="salon-title-container">
        <div class="salon-title">Spaço Laila Souza</div>
        <div class="salon-subtitle">Nail Design & Estética</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. PAINEL DE INFORMAÇÕES LOGO ABAIXO
# ==========================================
mes_atual = datetime.now().strftime("%Y-%m")

# Entrada Bruta (Tudo que foi pago e NÃO é 'Pagar Depois')
df_caixa = pd.read_sql_query("SELECT valor FROM financeiro WHERE status='Pago' AND forma_pagamento != 'Pagar Depois'", conn)
entradas = df_caixa['valor'].astype(float).sum() if not df_caixa.empty else 0.0

# Total de Saídas (Gastos cadastrados)
df_gastos_total = pd.read_sql_query("SELECT valor FROM gastos", conn)
saidas = df_gastos_total['valor'].astype(float).sum() if not df_gastos_total.empty else 0.0

# Dinheiro Real em Caixa (Entradas menos Gastos)
dinheiro_em_caixa = entradas - saidas

# Valor a receber (Tudo lançado como 'Pagar Depois')
df_receber = pd.read_sql_query("SELECT valor FROM financeiro WHERE forma_pagamento = 'Pagar Depois'", conn)
valor_a_receber = df_receber['valor'].astype(float).sum() if not df_receber.empty else 0.0

# Atendimentos realizados no mês
df_mes = pd.read_sql_query(f"SELECT COUNT(*) as total FROM tickets WHERE data LIKE '{mes_atual}%'", conn)
atendimentos_mes = df_mes['total'][0] if not df_mes.empty else 0

st.markdown('<div class="info-dashboard">', unsafe_allow_html=True)
c_inf1, c_inf2, c_inf3 = st.columns(3)
c_inf1.metric("💵 Dinheiro em Caixa (Líquido)", f"R$ {dinheiro_em_caixa:.2f}")
c_inf2.metric("⏳ Valor a Receber", f"R$ {valor_a_receber:.2f}")
c_inf3.metric("✨ Atendimentos no Mês", f"{atendimentos_mes} realizados")
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. BOTÕES DE AÇÃO EM CINZA EMBAIXO (INCLUINDO GASTOS)
# ==========================================
st.markdown('<div class="nav-bar-buttons" style="display: flex; gap: 12px; margin-bottom: 10px;">', unsafe_allow_html=True)
col_m1, col_m2, col_m3, col_m4, col_m5, col_m6, col_m7, col_m8 = st.columns([1,1,1,1,1,1,1,1])
with col_m1: 
    if st.button("📅 Agenda", key="m_age"): st.session_state["pagina_atual"] = "Agenda"
with col_m2: 
    if st.button("📊 Painel Geral", key="m_pai"): st.session_state["pagina_atual"] = "Painel"
with col_m3: 
    if st.button("👥 Clientes", key="m_cli"): st.session_state["pagina_atual"] = "Clientes"
with col_m4: 
    if st.button("💇 Serviços", key="m_ser"): st.session_state["pagina_atual"] = "Serviços"
with col_m5: 
    if st.button("📦 Estoque", key="m_est"): st.session_state["pagina_atual"] = "Estoque"
with col_m6: 
    if st.button("💸 Caixa", key="m_cai"): st.session_state["pagina_atual"] = "Caixa"
with col_m7: 
    if st.button("📉 Gastos", key="m_gas"): st.session_state["pagina_atual"] = "Gastos"
with col_m8: 
    if st.button("🧾 Cupons", key="m_cup"): st.session_state["pagina_atual"] = "Cupons"
st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 4. ESPAÇO DE CONTEÚDO DAS FUNÇÕES
# ==========================================

# 1. ABA AGENDA
if st.session_state["pagina_atual"] == "Agenda":
    col_lateral, col_timeline = st.columns([1, 2.6])
    
    with col_lateral:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0;'>Calendário</h4>", unsafe_allow_html=True)
        data_selecionada = st.date_input("Filtrar Data", value=datetime.now(), label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("✨ Agendar Novo Horário"):
            clientes = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
            servicos = pd.read_sql_query("SELECT nome FROM servicos", conn)
            with st.form("Form Nova Agenda"):
                c_sel = st.selectbox("Cliente", clientes['nome'].tolist() if not clientes.empty else ["Nenhum"])
                s_sel = st.multiselect("Serviços", servicos['nome'].tolist() if not servicos.empty else [])
                h_agm = st.text_input("Horário (ex: 14:00)")
                if st.form_submit_button("Confirmar Horário"):
                    c_id = clientes[clientes['nome'] == c_sel]['id'].values[0]
                    cursor.execute("INSERT INTO agenda (cliente_id, servicos, data, hora, status) VALUES (?,?,?,?,'Agendado')", (int(c_id), ", ".join(s_sel), str(data_selecionada), h_agm))
                    conn.commit()
                    st.rerun()

    with col_timeline:
        st.markdown('<div class="premium-card" style="min-height: 400px;">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='margin-top:0;'>⏱️ Linha do Tempo — {data_selecionada.strftime('%d/%m/%Y')}</h4>", unsafe_allow_html=True)
        
        df_agenda = pd.read_sql_query(f"SELECT agenda.id, clientes.nome as cliente_nome, agenda.servicos, agenda.hora, agenda.status FROM agenda JOIN clientes ON agenda.cliente_id = clientes.id WHERE agenda.data = '{str(data_selecionada)}' AND agenda.status != 'Finalizado' ORDER BY agenda.hora ASC", conn)
        
        if df_agenda.empty:
            st.info("Nenhum cliente agendado para este dia.")
        else:
            for idx, row in df_agenda.iterrows():
                st.markdown(f"""
                    <div class="timeline-slot">
                        <div>
                            <span style="font-size:12px; font-weight:700; background:rgba(255,255,255,0.2); padding:5px 12px; border-radius:30px;">{row['hora']}</span>
                            <h5 style="margin:10px 0 2px 0; font-size:19px; font-weight:600;">{row['cliente_nome']}</h5>
                            <span style="font-size:14px; opacity:0.9;">{row['servicos']}</span>
                        </div>
                        <div style="font-size:13px; font-weight:500; background:rgba(0,0,0,0.15); padding:4px 10px; border-radius:8px;">{row['status']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                b_col, _ = st.columns([1.5, 3])
                if row['status'] == 'Agendado':
                    if b_col.button("▶️ Iniciar Atendimento", key=f"st_{row['id']}"):
                        cursor.execute("UPDATE agenda SET status='Em Andamento' WHERE id=?", (int(row['id']),))
                        conn.commit()
                        st.rerun()
                elif row['status'] == 'Em Andamento':
                    if b_col.button("🏁 Ir para o Caixa", key=f"py_{row['id']}"):
                        st.session_state['caixa_auto_cliente'] = row['cliente_nome']
                        st.session_state['caixa_auto_servicos'] = [s.strip() for s in row['servicos'].split(',')] if row['servicos'] else []
                        st.session_state['caixa_auto_agenda_id'] = row['id']
                        st.session_state["pagina_atual"] = "Caixa"
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 2. ABA CAIXA
elif st.session_state["pagina_atual"] == "Caixa":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>💸 Fechamento e Recebimento</h3>", unsafe_allow_html=True)
    
    df_c = pd.read_sql_query("SELECT id, nome FROM clientes", conn)
    df_s = pd.read_sql_query("SELECT nome, preco FROM servicos", conn)
    df_p = pd.read_sql_query("SELECT id, nome, preco_venda FROM produtos WHERE estoque > 0", conn)
    
    cliente_padrao = st.session_state.get('caixa_auto_cliente', df_c['nome'].tolist()[0] if not df_c.empty else "")
    servicos_sugeridos = st.session_state.get('caixa_auto_servicos', [])
    agenda_id_vinculado = st.session_state.get('caixa_auto_agenda_id', None)
    
    with st.form("Form Caixa Real"):
        cli_cx = st.selectbox("Selecione a Cliente", df_c['nome'].tolist() if not df_c.empty else ["Nenhum"], index=df_c['nome'].tolist().index(cliente_padrao) if cliente_padrao in df_c['nome'].tolist() else 0)
        serv_cx = st.multiselect("Procedimentos Realizados", df_s['nome'].tolist() if not df_s.empty else [], default=[s for s in servicos_sugeridos if s in df_s['nome'].tolist()])
        prod_cx = st.multiselect("Produtos Vendidos (Lojinha)", df_p['nome'].tolist() if not df_p.empty else [])
        forma_p = st.selectbox("Forma de Pagamento", ["Pix", "Débito", "Crédito", "Dinheiro", "Pagar Depois"])
        
        if st.form_submit_button("Finalizar e Registrar"):
            total_salao = sum(df_s[df_s['nome'] == s]['preco'].values[0] for s in serv_cx)
            total_loja = sum(df_p[df_p['nome'] == p]['preco_venda'].values[0] for p in prod_cx)
            total_geral = total_salao + total_loja
            data_str = datetime.now().strftime("%Y-%m-%d")
            status_p = "Pago" if forma_p != "Pagar Depois" else "Pagar Depois"
            
            if serv_cx:
                cursor.execute("INSERT INTO financeiro (tipo, cliente_nome, descricao, valor, forma_pagamento, data, status) VALUES (?,?,?,?,?,?,?)", ("Salão", cli_cx, "Serviços", total_salao, forma_p, data_str, status_p))
            if prod_cx:
                for p in prod_cx:
                    cursor.execute("UPDATE produtos SET estoque = estoque - 1 WHERE nome = ?", (p,))
                cursor.execute("INSERT INTO financeiro (tipo, cliente_nome, descricao, valor, forma_pagamento, data, status) VALUES (?,?,?,?,?,?,?)", ("Lojinha", cli_cx, "Produtos", total_loja, forma_p, data_str, status_p))
                
            if agenda_id_vinculado:
                cursor.execute("UPDATE agenda SET status='Finalizado' WHERE id=?", (int(agenda_id_vinculado),))
                
            recibo_html = f"""<div style="background:#FFF; padding:20px; border-radius:12px; border:1px dashed #8C6246; font-family:monospace; color:#333;">
                <b>SPAÇO LAILA SOUZA</b><br>
                ------------------------------<br>
                CLIENTE: {cli_cx}<br>
                TOTAL: R$ {total_geral:.2f}<br>
                PAGAMENTO: {forma_p}<br>
                ------------------------------
            </div>"""
            cursor.execute("INSERT INTO tickets (cliente_nome, data, conteudo_html) VALUES (?,?,?)", (cli_cx, data_str, recibo_html))
            conn.commit()
            
            if 'caixa_auto_cliente' in st.session_state: del st.session_state['caixa_auto_cliente']
            if 'caixa_auto_servicos' in st.session_state: del st.session_state['caixa_auto_servicos']
            if 'caixa_auto_agenda_id' in st.session_state: del st.session_state['caixa_auto_agenda_id']
            
            st.success("Caixa processado com sucesso!")
            st.session_state["pagina_atual"] = "Agenda"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. ABA PAINEL HISTÓRICO
elif st.session_state["pagina_atual"] == "Painel":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📊 Histórico Financeiro Geral</h3>", unsafe_allow_html=True)
    df_historico = pd.read_sql_query("SELECT tipo as 'Origem', cliente_nome as 'Cliente', descricao as 'Item', valor as 'Valor (R$)', forma_pagamento as 'Pagamento', data as 'Data' FROM financeiro ORDER BY id DESC", conn)
    if not df_historico.empty:
        st.dataframe(df_historico, use_container_width=True)
    else:
        st.info("Nenhuma movimentação financeira encontrada.")
    st.markdown('</div>', unsafe_allow_html=True)

# 4. ABA CLIENTES
elif st.session_state["pagina_atual"] == "Clientes":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>👥 Fichas Técnicas das Clientes</h3>", unsafe_allow_html=True)
    with st.form("Ficha"):
        nome = st.text_input("Nome da Cliente")
        wha = st.text_input("WhatsApp de Contato")
        md = st.text_input("Especificação Molde F (Mão Direita)")
        me = st.text_input("Especificação Molde F (Mão Esquerda)")
        if st.form_submit_button("Salvar Ficha Técnica"):
            cursor.execute("INSERT INTO clientes (nome, whatsapp, molde_f_dir, molde_f_esq) VALUES (?,?,?,?)", (nome, wha, md, me))
            conn.commit()
            st.success("Ficha salva com sucesso!")
            st.rerun()
            
    df_clientes = pd.read_sql_query("SELECT nome as 'Cliente', whatsapp as 'WhatsApp', molde_f_dir as 'Molde Dir.', molde_f_esq as 'Molde Esq.' FROM clientes", conn)
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 5. ABA SERVIÇOS
elif st.session_state["pagina_atual"] == "Serviços":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>💇 Menu de Procedimentos</h3>", unsafe_allow_html=True)
    with st.form("Serv"):
        ns = st.text_input("Nome do Serviço")
        ps = st.number_input("Preço de Tabela (R$)", min_value=0.0)
        if st.form_submit_button("Cadastrar Serviço"):
            cursor.execute("INSERT INTO servicos (nome, preco) VALUES (?,?)", (ns, ps))
            conn.commit()
            st.success("Serviço adicionado!")
            st.rerun()
            
    df_servicos = pd.read_sql_query("SELECT nome as 'Procedimento', preco as 'Preço (R$)' FROM servicos", conn)
    if not df_servicos.empty:
        st.dataframe(df_servicos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. ABA ESTOQUE
elif st.session_state["pagina_atual"] == "Estoque":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📦 Vitrine de Produtos & Estoque</h3>", unsafe_allow_html=True)
    with st.form("Prod"):
        np = st.text_input("Nome do Produto")
        custo = st.number_input("Preço de Custo (R$)", min_value=0.0)
        venda = st.number_input("Preço de Venda (R$)", min_value=0.0)
        un = st.number_input("Quantidade Inicial", min_value=0, step=1)
        if st.form_submit_button("Cadastrar no Estoque"):
            cursor.execute("INSERT INTO produtos (nome, preco_custo, preco_venda, estoque) VALUES (?,?,?,?)", (np, custo, venda, un))
            conn.commit()
            st.success("Item adicionado ao inventário!")
            st.rerun()
            
    df_produtos = pd.read_sql_query("SELECT nome as 'Produto', preco_custo as 'Custo', preco_venda as 'Venda', estoque as 'Quantidade' FROM produtos", conn)
    if not df_produtos.empty:
        st.dataframe(df_produtos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 7. ABA GASTOS (⭐ ADICIONADA AQUI)
elif st.session_state["pagina_atual"] == "Gastos":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📉 Lançamento de Gastos / Despesas</h3>", unsafe_allow_html=True)
    with st.form("FormGastos"):
        desc_g = st.text_input("Descrição do Gasto (Ex: Conta de Luz, Aluguel, Compra de Gel)")
        val_g = st.number_input("Valor da Despesa (R$)", min_value=0.0)
        cat_g = st.selectbox("Categoria", ["Infraestrutura (Luz/Água)", "Aluguel", "Produtos/Insumos", "Marketing", "Outros"])
        if st.form_submit_button("Registrar Saída"):
            dt_g = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO gastos (descricao, valor, categoria, data) VALUES (?,?,?,?)", (desc_g, val_g, cat_g, dt_g))
            conn.commit()
            st.success("Gasto registrado e debitado do Caixa principal!")
            st.rerun()
            
    df_gastos = pd.read_sql_query("SELECT descricao as 'Descrição', valor as 'Valor (R$)', categoria as 'Categoria', data as 'Data Lançamento' FROM gastos ORDER BY id DESC", conn)
    if not df_gastos.empty:
        st.markdown("#### Histórico de Despesas")
        st.dataframe(df_gastos, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 8. ABA CUPONS
elif st.session_state["pagina_atual"] == "Cupons":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>🧾 Histórico de Recibos Gerados</h3>", unsafe_allow_html=True)
    df_t = pd.read_sql_query("SELECT id, cliente_nome, data, conteudo_html FROM tickets ORDER BY id DESC", conn)
    if df_t.empty:
        st.info("Nenhum cupom emitido até o momento.")
    else:
        for idx, row in df_t.iterrows():
            with st.expander(f"Recibo #{row['id']} — {row['cliente_nome']} ({row['data']})"):
                st.markdown(row['conteudo_html'], unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)