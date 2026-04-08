# 🏦 API Bancária Assíncrona - FastAPI

Esta é uma API RESTful de alto desempenho desenvolvida com **FastAPI**, focada na gestão de operações bancárias de conta corrente. O sistema permite o registo de utilizadores, autenticação segura via **JWT** e operações financeiras com validação de regras de negócio.

## 🚀 Funcionalidades

- **Autenticação JWT:** Proteção de endpoints para garantir que apenas utilizadores autorizados acedam aos seus dados.
- **Gestão de Transações:** Registo de depósitos e saques com validação automática.
- **Validação de Saldo:** Impede a realização de saques superiores ao saldo disponível na conta.
- **Extrato em Tempo Real:** Visualização do saldo atual e histórico completo de transações.
- **Documentação Automática:** Integração com Swagger UI e ReDoc.

## 🛠️ Tecnologias Utilizadas

- **FastAPI:** Framework moderno e rápido para construção de APIs.
- **SQLAlchemy (Async):** ORM para mapeamento de banco de dados de forma assíncrona.
- **SQLite (aiosqlite):** Banco de dados leve e eficiente para o desenvolvimento.
- **Pydantic:** Validação de dados e gestão de esquemas.
- **Python-jose & Passlib:** Segurança, hashing de senhas e geração de tokens JWT.

## 📋 Requisitos de Negócio Implementados

1. **Operações Positivas:** Não são permitidos depósitos ou saques com valores negativos ou zero.
2. **Saldo Suficiente:** A API valida se o utilizador possui saldo antes de processar um saque.
3. **Persistência Assíncrona:** Todas as operações de entrada/saída (I/O) no banco de dados são não-bloqueantes.

## 🔧 Como Executar o Projeto

1. **Clonar o Repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
   cd NOME_DO_REPOSITORIO
