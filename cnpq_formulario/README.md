# 📝 Sistema de Gestão de Formulários (Full-Stack)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

Aplicação robusta desenvolvida para o **CNPq** com o objetivo de centralizar e automatizar a coleta de dados de pesquisadores nacionais. O sistema substituiu fluxos manuais baseados em planilhas por uma interface web intuitiva com persistência de dados.

---

## 🎯 Impacto do Projeto
- **Eficiência:** Automatização do processo de preenchimento de moldes internos.
- **Confiabilidade:** Padronização da entrada de dados, eliminando erros comuns de preenchimento manual.
- **Escalabilidade:** Implementação de sistema de login e perfis de usuário para gestão de acessos.

---

## 🛠️ Tech Stack & Diferenciais Técnicos
- **Backend:** Python + Flask (Arquitetura limpa e rotas organizadas).
- **ORM:** SQLAlchemy para manipulação do banco SQLite (facilita futuras migrações).
- **Frontend:** Jinja2 para renderização dinâmica, HTML5 e CSS3 customizado.
- **Relatórios:** Implementação do **WeasyPrint** para conversão direta de HTML para PDF profissional.

---

## ⚙️ Funcionalidades Principais
- [x] **Gestão de Usuários:** Cadastro, autenticação segura e troca de senha.
- [x] **Formulários Dinâmicos:** Interface para coleta de dados técnicos de projetos de pesquisa.
- [x] **Automação de Documentos:** Geração automática de arquivos baseados em moldes pré-definidos.
- [x] **Admin Tools:** Scripts de limpeza e estruturação automática da base de dados.

---

## 🚀 Como Executar
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt