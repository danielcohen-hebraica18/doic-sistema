[README.md](https://github.com/user-attachments/files/27659475/README.md)
# 🛡️ Sistema de Inteligência — Clube A Hebraica de São Paulo

**Protocolo DOIC-8000 | Departamento de Segurança Institucional**

---

## 📁 Estrutura do Projeto

### Vercel (`doic-sistema`)
| Arquivo | Descrição |
|---|---|
| `index.html` | Tela de login do sistema |
| `sistema.html` | Interface principal — chat, módulos e navegação |
| `checagem.html` | Sistema de Checagem de Prestadores (login por depto) |
| `policia.html` | Página de resposta da verificação policial |

### Railway (`doic-pdf-service`)
| Arquivo | Descrição |
|---|---|
| `app.py` | Backend principal — todas as rotas |
| `especialista.py` | Gerador dos 3 PDFs do Especialista de Segurança |
| `especialista_prompt.py` | Base de conhecimento e cálculo de orçamento |
| `requirements.txt` | Dependências Python |
| `Procfile` | Configuração do servidor |

---

## 🚀 Módulos do Sistema

### 🔍 Agente de Inteligência (DOIC-8000)
- Busca notícias em tempo real via OSINT
- Gera relatório PDF profissional com 9 seções
- Escala de Almirantado, Matriz de Risco e Recomendações
- Integrado com o Especialista de Segurança

### 🛡️ Especialista de Segurança
- Formulário de planejamento por evento e espaço
- Gera 3 documentos PDF em ZIP:
  - Planejamento Geral de Segurança
  - Planejamento Operacional (equipe de campo)
  - Dashboard Executivo (diretoria)
- Cálculo automático de orçamento por espaço (planilha)
- Integrado com o relatório DOIC-8000

### ✅ Sistema de Checagem de Prestadores
- Login individual por departamento (35 deptos)
- Senha administrador para acesso total
- Cadastro de prestadores (Nome, CPF, RG)
- E-mail automático para verificação policial via Resend
- Consulta e histórico filtrado por depto
- Relatórios por período com exportação XLS
- Integrado com a IA (responde consultas no chat)

### 📈 Power BI
- 5 dashboards integrados via SharePoint:
  - Assessment 2026
  - Infos Eventos 2026
  - Manutenções 2026
  - Numeral 2026
  - Ocorrências 2026

### 🔒 Seleção Segura
- Acesso direto ao sistema externo de seleção

---

## ⚙️ Variáveis de Ambiente

### Railway
| Variável | Descrição |
|---|---|
| `ANTHROPIC_API_KEY` | Chave da API Anthropic (Claude) |
| `AIRTABLE_TOKEN` | Token de acesso ao Airtable |
| `AIRTABLE_BASE_ID` | ID da base do Airtable |
| `EMAIL_CHECAGEM` | E-mail remetente (Gmail) |
| `EMAIL_PASS_CHECAGEM` | App Password do Gmail |
| `RESEND_API_KEY` | Chave da API Resend (envio de e-mails) |
| `BASE_URL` | URL da Vercel |

---

## 🔐 Acessos

| Sistema | URL | Credenciais |
|---|---|---|
| Sistema de Inteligência | `hebraicaseguranca.vercel.app` | `admin@hebraica.com.br` / `Hebraica@2026` |
| Checagem (Admin) | `hebraicaseguranca.vercel.app/checagem.html` | Qualquer depto + `HEBRAICA@2026` |
| Checagem (Depto) | `hebraicaseguranca.vercel.app/checagem.html` | Depto + senha individual |

---

## 🗃️ Banco de Dados — Airtable

### Tabelas utilizadas
- **Checagens** — registros do sistema de checagem de prestadores
- Demais tabelas — dados operacionais (ocorrências, chaves, briefing, etc.)

---

## 📦 Deploy

1. Push para GitHub → Vercel e Railway fazem deploy automático
2. Vercel: branch `main` do repositório `doic-sistema`
3. Railway: branch `main` do repositório `doic-pdf-service`

---

*Clube A Hebraica de São Paulo — Departamento de Segurança Institucional*
*Sistema DOIC-8000 — Uso Interno Restrito*
