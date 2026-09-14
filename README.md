# 🏢 Portal do Cliente & Gestão de Obras e Processos Administrativos
### METROCON ENGENHARIA E CONSTRUÇÕES LTDA (CNPJ: 07.427.908/0001-25)

Plataforma web profissional desenvolvida em **Python**, **Streamlit** e **SQLite** para centralização de relacionamento com clientes, acompanhamento de obras, reformas e tramitações de processos administrativos (legalização, alvarás, AVCB de bombeiros e habite-se).

---

## 🎯 Objetivos do Sistema
- **Transparência Total:** Acesso 24/7 a diários de obra/processo, fotos, cronogramas e atas de reunião.
- **Redução de Ruídos:** Elimina a dependência de mensagens fragmentadas em WhatsApp e e-mails operacionais.
- **Canal Único e Auditável:** Central de mensagens e acervo documental com versionamento formal.
- **Conformidade com a LGPD:** Trilha auditável de todos os logins, downloads e visualizações, com hash seguro de senhas (PBKDF2/SHA-256).

---

## 🌟 Funcionalidades Principais

1. **Dashboard do Projeto:**
   - Indicadores-chave (Progresso físico-financeiro %, Status atualizado, Previsão de conclusão).
   - Dados do responsável técnico (Engenheiro civil, CREA e contatos).
   - Resumo das últimas movimentações (último diário, ata e documento inserido).

2. **Central de Documentos & Acervo Técnico:**
   - Categorias padronizadas: *Projetos*, *Contratos*, *Documentos Legais (ART/RRT)*, *Aprovações em Órgãos*, *Anexos Gerais*.
   - Controle de versões (v1.0, v2.0...) e histórico técnico.
   - Download seguro com registro em log de auditoria.

3. **Diário de Obra (RDO) e Diário de Processo (RDP):**
   - Para **Obras/Reformas**: Clima, efetivo em canteiro, atividades executadas, ocorrências e galeria de fotos com legendas.
   - Para **Processos Administrativos**: Protocolos emitidos, comparecimento a secretarias municipais, certidões e pareceres fiscais.

4. **Cronograma Visual Interativo (Gantt com Plotly):**
   - Gráfico de Gantt com datas previstas vs. realizadas.
   - Cards de etapas com badges de status (*Concluído*, *Em Andamento*, *Em Análise no Órgão*, *A Iniciar*, *Atrasado*).
   - Edição ágil de percentuais e prazos para a equipe técnica.

5. **Atas de Reunião & Alinhamentos Estratégicos:**
   - Registro de pauta, participantes, decisões consolidadas e pendências com prazos e responsáveis.

6. **Central de Mensagens Formais:**
   - Mensagens com suporte a anexos e notificações de leitura entre o cliente e a equipe técnica.

7. **Painel de Gestão Administrativa:**
   - Cadastro de novos projetos, novos clientes e engenheiros, e adição de etapas ao cronograma.

8. **Segurança & LGPD:**
   - Trilha completa de auditoria de acessos (`audit_logs`).
   - Exportação de dados pessoais do titular (Art. 18 da LGPD).
   - Termos de privacidade integrados.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o Python 3.10+ instalado.

### 2. Instalação das dependências
```bash
pip install -r requirements.txt
```

### 3. Execução da aplicação
```bash
streamlit run app.py
```
O sistema abrirá automaticamente no seu navegador no endereço `http://localhost:8501`.

---

## 👥 Contas de Demonstração

| Perfil | E-mail de Acesso | Senha | Descrição |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@metrocon.com.br` | `Admin@123456` | Acesso global, gestão de usuários e auditoria |
| **Engenheiro** | `engenharia@metrocon.com.br` | `Eng@123456` | Eng. Carlos Eduardo - Postagem de RDO/RDP, documentos e cronograma |
| **Cliente (Obra)** | `cliente.reserva@gmail.com` | `Cliente@123456` | Dr. Roberto - Acompanha a Construção Residencial Casa 42 |
| **Cliente (Processo)** | `diretoria@inovaempreendimentos.com.br` | `Cliente@123456` | Dra. Juliana - Acompanha a Regularização do Alpha Tower |

*(A tela de login possui botões de acesso rápido com 1 clique para agilizar seus testes).*

---

## 📁 Estrutura de Arquivos
```
portal_cliente_obras/
├── app.py                      # Ponto de entrada, autenticação e roteamento
├── database/
│   ├── connection.py           # Conexão SQLite e migrations
│   ├── schema.sql              # DDL de tabelas e índices
│   └── seed.py                 # Carga de dados realistas e mock files
├── modules/
│   ├── auth.py                 # Login, sessão e consentimento LGPD
│   ├── dashboard.py            # Visão geral e KPIs do projeto
│   ├── documents.py            # Central de documentos categorizados e versionados
│   ├── daily_log.py            # Diário de Obra (RDO) e Processo (RDP)
│   ├── schedule.py             # Cronograma visual com Plotly Gantt
│   ├── meetings.py             # Atas de reunião e pendências
│   ├── messages.py             # Mensagens formais com anexos
│   ├── admin_management.py     # Gestão de projetos, usuários e etapas
│   └── lgpd_compliance.py      # Trilha de auditoria e privacidade
├── utils/
│   ├── security.py             # Hashing PBKDF2, salt e sanitização
│   └── ui_components.py        # CSS corporativo, badges e helpers visuais
├── uploads/                    # Armazenamento local seguro de arquivos
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação completa
```

---
**METROCON ENGENHARIA E CONSTRUÇÕES LTDA**  
*Excelência técnica, transparência e segurança digital.*
