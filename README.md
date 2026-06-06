# Document Manager API

> Backend para gerenciamento de documentos com assinatura digital, análise por IA e processamento de PDFs.

---

## Sumário

- [Visão geral](#visão-geral)
- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Módulos](#módulos)
- [Integrações](#integrações)
- [Fluxos](#fluxos)
- [Webhooks](#webhooks)
- [Configuração](#configuração)
- [Execução](#execução)
- [Decisões de design](#decisões-de-design)
- [Roadmap](#roadmap)

---

## Visão geral

A Document Manager API é uma aplicação backend construída com Django REST Framework. Ela centraliza o ciclo de vida de documentos: criação, extração de conteúdo, análise semântica via IA e envio para assinatura digital.

**Capacidades principais:**

- Gerenciamento de usuários e empresas com isolamento por ownership
- Upload, versionamento e armazenamento de documentos
- Extração automática de texto de PDFs via `pypdf`
- Análise de conteúdo com Google Gemini (resumos, insights, semântica)
- Integração com ZapSign para assinatura digital e rastreamento de status
- Orquestração de fluxos automatizados via webhooks e n8n

---

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| Framework | Django 5.x + Django REST Framework |
| Banco de dados | PostgreSQL |
| Extração de PDF | pypdf |
| IA | Google Gemini API |
| Assinatura digital | ZapSign API |
| Infraestrutura | Docker / Docker Compose |
| Observabilidade | `logging` (stdlib) |

---

## Arquitetura

O sistema segue uma arquitetura em camadas com separação clara de responsabilidades. Nenhuma camada acessa diretamente o que não é de sua responsabilidade — em especial, o ORM nunca é acessado fora da camada de repositório.

```
Request
  ↓
View (HTTP)          → recebe a requisição, delega, retorna resposta
  ↓
Serializer           → validação de input apenas
  ↓
Service              → regras de negócio, orquestração de integrações
  ↓
Repository           → queries, persistência, isolamento do ORM
  ↓
PostgreSQL
```

### Diagrama geral

```mermaid
flowchart TD
    Client[Client / Frontend] --> API[Django REST API]

    API --> Auth[Authentication]
    API --> Comp[Companies]
    API --> Doc[Documents]
    API --> Sig[Signers]

    Doc --> SvcDoc[Document Service]
    Auth --> SvcAuth[Auth Service]
    Comp --> SvcComp[Company Service]
    Sig --> SvcSig[Signer Service]

    SvcDoc --> RepoDoc[Document Repository]
    SvcAuth --> RepoAuth[User Repository]
    SvcComp --> RepoComp[Company Repository]
    SvcSig --> RepoSig[Signer Repository]

    RepoDoc --> DB[(PostgreSQL)]
    RepoAuth --> DB
    RepoComp --> DB
    RepoSig --> DB

    SvcDoc --> PDF[PDF Extractor]
    SvcDoc --> AI[Gemini AI]
    SvcDoc --> ZS[ZapSign API]
```

### Responsabilidades por camada

**View Layer**
Recebe a requisição HTTP, delega para o service correspondente e retorna a resposta. Não contém lógica de negócio.

**Serializer Layer**
Responsável exclusivamente por validação e desserialização de input. Não acessa banco nem chama services diretamente.

**Service Layer**
Orquestra o fluxo de negócio: cria entidades, chama integrações externas (PDF, IA, ZapSign) e coordena persistência via repository.

**Repository Layer**
Centraliza todo acesso ao banco de dados via Django ORM. Isola queries e facilita mocking em testes.

---

## Módulos

### `authentication`
- Cadastro e login de usuários com autenticação por token
- Criação automática de empresa no registro

### `companies`
- CRUD completo de empresas
- Validação de ownership por usuário
- Soft delete

### `documents`
- Upload e criação de documentos
- Extração de texto de PDFs
- Análise com Gemini AI
- Integração com ZapSign

### `signers`
- Gerenciamento de signatários por documento
- Validação de e-mail

---

## Integrações

### Google Gemini AI
Utilizado para análise semântica de documentos após extração do texto.

- Geração de resumos
- Extração de insights
- Análise semântica de conteúdo

### ZapSign
Plataforma de assinatura digital integrada ao fluxo de publicação de documentos.

- Criação de envelopes de assinatura
- Rastreamento de status por `external_id`
- Callbacks via webhook

### PDF Extractor
Processamento de arquivos PDF para extração de texto.

- Biblioteca: `pypdf`
- Fallback em caso de falha na extração
- Resultado armazenado em `extracted_text`

---

## Fluxos

### Criação de documento

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Repository
    participant PDF
    participant AI
    participant ZapSign

    Client->>API: POST /documents/
    API->>Service: valida + executa lógica de negócio
    Service->>Repository: cria Document
    Repository-->>Service: Document persistido

    Service->>PDF: extrai texto
    PDF-->>Service: extracted_text

    Service->>AI: analisa documento
    AI-->>Service: insights

    Service->>ZapSign: cria envelope
    ZapSign-->>Service: external_id

    Service-->>API: resultado
    API-->>Client: 201 Created
```

**Passo a passo:**

1. Request recebida pela API
2. Serializer valida o input
3. Service cria a entidade `Document`
4. PDF é baixado e processado
5. Texto é extraído (`extracted_text`)
6. Gemini analisa o conteúdo
7. Resultado é persistido
8. Documento pode ser enviado ao ZapSign para assinatura

---

## Webhooks

O sistema emite eventos para integrações externas (ex: n8n) nas seguintes situações:

| Evento | Descrição |
|---|---|
| `document.created` | Documento criado com sucesso |
| `document.processed` | PDF processado e texto extraído |
| `document.signed` | Assinatura concluída no ZapSign |

**Exemplo de payload:**

```json
{
  "event": "document.created",
  "document_id": 123,
  "company_id": 10
}
```

### Automações com n8n

O n8n é utilizado para orquestrar fluxos automatizados:

- Sincronização de status com ZapSign
- Notificações por evento
- Reprocessamento de documentos com falha
- Workflows de aprovação

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
DEBUG=True
SECRET_KEY=your-secret-key

DATABASE_URL=postgres://user:password@localhost:5432/docmanager

ZAPSIGN_API_TOKEN=your-zapsign-token
GEMINI_API_KEY=your-gemini-key

LOG_LEVEL=INFO
```

---

## Execução

**Subir o ambiente:**

```bash
docker compose up --build
```

**Aplicar migrations:**

```bash
docker compose exec backend python manage.py migrate
```

**Rodar testes:**

```bash
docker compose exec backend pytest
```

---

## Logging

O sistema usa o módulo `logging` padrão do Python com os seguintes níveis:

| Nível | Uso |
|---|---|
| `INFO` | Fluxo normal de operação |
| `WARNING` | Falhas recuperáveis (ex: extração de PDF com fallback) |
| `ERROR` | Falhas críticas que impedem a operação |

---

## Decisões de design

**Services não acessam o ORM diretamente.**
Todo acesso ao banco passa pelo repository, mantendo a camada de serviço testável e agnóstica ao mecanismo de persistência.

**Repositories centralizam o acesso a dados.**
Evita duplicação de queries e facilita a substituição ou mock em testes unitários.

**Integrações externas são isoladas.**
Gemini, ZapSign e o extrator de PDF são módulos independentes, chamados exclusivamente pelo service layer.

**Serializers apenas validam.**
Nenhuma lógica de negócio ou acesso a banco nos serializers — apenas validação e desserialização de input.

**Views apenas orquestram.**
A view recebe, delega e responde. Nada mais.

---

## Roadmap

- [ ] Processamento assíncrono com Celery
- [ ] Arquitetura orientada a eventos
- [ ] Retry automático em falhas de integração
- [ ] Dashboard de observabilidade
- [ ] Versionamento de documentos