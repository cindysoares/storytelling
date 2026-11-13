# Storytelling Bibivaiafeira

Aplicação web simples para exibir uma imagem de acordo com um status persistido no servidor.

## Tecnologias

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL (Neon em produção)
- Server-Sent Events (SSE) para atualização da tela em tempo real
- Render para hospedagem

## Como funciona

A página `GET /bibivaiafeira` apresenta a imagem associada ao status atual. O navegador mantém uma conexão SSE aberta em `/api/events`. Quando o status muda, o servidor envia um evento e a página troca a imagem **sem recarregar**.

Os status aceitos são:

- `start`
- `products`
- `purchase`

As imagens ilustrativas estão em `app/static/images/`. Substitua os SVGs por suas imagens, mantendo os nomes `start.svg`, `products.svg` e `purchase.svg` (ou ajuste o mapeamento em `app/main.py`).

## Executar localmente

Requer Python 3.11 ou superior.

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse:

- Página: http://localhost:8000/bibivaiafeira
- Documentação da API: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Sem `DATABASE_URL`, a aplicação usa SQLite local (`storytelling.db`). Para produção, configure PostgreSQL.

## API

### Consultar o status atual

```http
GET /api/status
```

Exemplo de resposta:

```json
{
  "status": "start",
  "image": "/static/images/start.svg"
}
```

### Alterar o status

O endpoint solicitado é `POST /bibivaiafeira`, recebendo o status por query parameter:

```bash
curl -X POST "http://localhost:8000/bibivaiafeira?status=products"
```

Exemplo de resposta:

```json
{
  "message": "Status atualizado com sucesso.",
  "status": "products",
  "image": "/static/images/products.svg"
}
```

Valores permitidos: `start`, `products`, `purchase`. Um valor inválido resulta em HTTP 422 (validação automática do FastAPI).

### Atualização em tempo real

O navegador conecta-se a:

```http
GET /api/events
```

Essa rota usa Server-Sent Events. O servidor verifica o status persistido a cada segundo e envia um evento quando detecta uma mudança. A página não precisa de refresh. O EventSource do navegador tenta reconectar automaticamente em caso de queda da conexão.

## Deploy no Render + Neon

### 1. Criar o banco no Neon

1. Crie uma conta em https://neon.com/.
2. Crie um projeto PostgreSQL.
3. Copie a connection string (formato PostgreSQL).
4. Guarde-a para configurar a variável `DATABASE_URL` no Render.

### 2. Publicar o código no GitHub

Crie um repositório GitHub e envie todo o conteúdo deste projeto para a raiz dele.

### 3. Criar o serviço no Render

1. Acesse https://render.com/ e conecte sua conta GitHub.
2. Escolha **New > Blueprint** (ou crie um **Web Service** apontando para o repositório).
3. O arquivo `render.yaml` configura build, comando de inicialização e health check.
4. Configure `DATABASE_URL` com a connection string do Neon.
   - Se o Neon fornecer uma URL `postgresql://...`, a aplicação converte automaticamente para o driver `psycopg`.
5. Faça o deploy.

Após o deploy, a página estará em:

```text
https://SEU-SERVICO.onrender.com/bibivaiafeira
```

O nome do serviço/subdomínio depende da disponibilidade no Render. Para ter um domínio contendo `storytelling`, escolha um nome de serviço como `storytelling-bibivaiafeira`, se estiver disponível. Um domínio próprio `.com.br` precisa ser registrado separadamente.

## Observações sobre o plano gratuito

- O serviço web gratuito do Render pode entrar em repouso após um período sem tráfego; a primeira visita depois disso pode demorar para responder.
- O banco Neon possui limites próprios no plano gratuito. Consulte os limites atuais no site do provedor.
- O banco PostgreSQL externo é importante porque o disco local de um serviço gratuito pode ser efêmero. Não use o SQLite local como persistência de produção.
- Este MVP não implementa autenticação, conforme solicitado. Qualquer pessoa que conheça a URL do POST poderá alterar o status. Não publique dados sensíveis nesse serviço.
- Para manter o SSE simples, o serviço consulta o banco a cada segundo por conexão aberta. Para este MVP e uma instância pequena, é uma solução direta; se o número de espectadores crescer bastante, vale migrar para notificações/pub-sub.

## Estrutura

```text
.
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/styles.css
│       ├── js/app.js
│       └── images/
│           ├── start.svg
│           ├── products.svg
│           └── purchase.svg
├── requirements.txt
├── Procfile
├── render.yaml
└── README.md
```
