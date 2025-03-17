# FORECASTIT - Sistema de Gerenciamento de Férias

Sistema profissional para gerenciamento de férias desenvolvido para a FORECASTIT.

## Funcionalidades

- Autenticação de usuários
- Calendário de férias
- Dashboard administrativo
- Solicitação e aprovação de férias
- Gestão de colaboradores

## Requisitos

- Python 3.8+
- Pip (Gerenciador de pacotes Python)

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
```
3. Ative o ambiente virtual:
```bash
venv\Scripts\activate
```
4. Instale as dependências:
```bash
pip install -r requirements.txt
```
5. Execute a aplicação:
```bash
python run.py
```

## Estrutura do Projeto

```
forecastit-vacation-system/
├── app/
│   ├── static/
│   ├── templates/
│   ├── models/
│   ├── routes/
│   └── __init__.py
├── config.py
├── requirements.txt
├── README.md
└── run.py
```
