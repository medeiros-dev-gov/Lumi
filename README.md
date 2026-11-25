# LUMI — Sistema de Biblioteca

Sistema web de gerenciamento de biblioteca desenvolvido com Python e Django. A aplicação permite consultar livros, gerenciar contas de usuários e acompanhar empréstimos.

## Tecnologias utilizadas

- Python 3.14.7
- Django 6.1.3
- SQLite
- HTML5 e CSS3
- Pillow

## Funcionalidades

- Cadastro e autenticação de usuários
- Login e logout
- Catálogo de livros
- Consulta de informações dos livros
- Visualização dos empréstimos do usuário
- Realização de empréstimos
- Devolução de livros
- Controle de disponibilidade de exemplares
- Renovação de empréstimos
- Painel administrativo do Django

## Requisitos

- Python 3.14 ou compatível
- pip
- Git

## Instalação

Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
cd lumi
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
```

Windows — PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows — Git Bash:

```bash
source .venv/Scripts/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute as migrações:

```bash
python manage.py migrate
```

Inicie o servidor:

```bash
python manage.py runserver
```

Acesse:

http://127.0.0.1:8000/

## Principais rotas

| Caminho | Descrição |
|---|---|
| `/catalog/` | Página inicial |
| `/catalog/books/` | Catálogo de livros |
| `/catalog/my-borrowed/` | Meus empréstimos |
| `/catalog/register/` | Cadastro |
| `/accounts/login/` | Login |
| `/admin/` | Administração |

## Estrutura do projeto

```text
lumi/
├── catalog/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── locallibrary/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── static/
│   └── css/
├── templates/
│   ├── catalog/
│   └── registration/
├── media/
├── requirements.txt
├── manage.py
└── README.md
```

## Comandos úteis

Verificar a configuração do Django:

```bash
python manage.py check
```

Verificar migrações:

```bash
python manage.py showmigrations
```

Aplicar migrações:

```bash
python manage.py migrate
```

Criar usuário administrador:

```bash
python manage.py createsuperuser
```

Executar testes:

```bash
python manage.py test
```

## Banco de dados

O projeto utiliza SQLite durante o desenvolvimento.

O banco local `db.sqlite3` e os arquivos de backup são mantidos fora do controle de versão.

## Observação

Este projeto está em desenvolvimento. A configuração atual é voltada ao ambiente local. Antes de publicar em produção, é necessário configurar segurança, variáveis de ambiente, hospedagem, arquivos estáticos e banco de dados de produção.

---

**LUMI — Sistema de Biblioteca**
Desenvolvido com Python e Django.