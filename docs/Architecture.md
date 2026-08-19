# PR Campaign Assistant — Architecture Document

## 1. Overview

PR Campaign Assistant is a web application that helps PR consultants identify relevant journalists for a campaign and generate personalized outreach pitches.

The system consists of:

* A React frontend
* A FastAPI backend
* A relational database
* An AI service for journalist analysis and pitch generation

The application follows a **modular monolith** architecture. All backend functionality runs within a single application while being organized into clear modules.

---

## 2. System Architecture

```text
                    ┌──────────────────┐
                    │      User        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ React Frontend   │
                    └────────┬─────────┘
                             │
                         HTTP / JSON
                             │
                             ▼
                    ┌──────────────────┐
                    │ FastAPI Backend  │
                    │                  │
                    │  API             │
                    │  Services        │
                    │  AI Integration  │
                    │  Data Access     │
                    └───────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐    ┌─────────────────┐
        │    Database     │    │   LLM Provider  │
        └─────────────────┘    └─────────────────┘
```

---

# 3. Components

## 3.1 Frontend

The frontend provides the user interface for the application.

### Responsibilities

* Campaign creation
* Journalist CSV upload
* Journalist listing
* Analysis results
* Journalist details
* Pitch generation
* Pitch review and copying
* Displaying errors and loading states

### Main areas

```text
frontend/
├── pages/
├── components/
├── services/
└── types/
```

The frontend communicates with the backend through REST APIs.

The frontend does not perform AI analysis or business-critical scoring.

---

# 4. Backend

The backend provides the application's API and business logic.

```text
backend/
└── app/
    ├── api/
    ├── services/
    ├── models/
    ├── repositories/
    └── ai/
```

## 4.1 API Layer

The API layer handles HTTP requests and responses.

Responsibilities:

* Request validation
* Authentication/authorization if introduced later
* Calling application services
* Returning responses
* Returning appropriate errors

Example endpoints:

```text
POST   /api/campaigns
GET    /api/campaigns/{campaign_id}

POST   /api/campaigns/{campaign_id}/journalists/import
GET    /api/campaigns/{campaign_id}/journalists

POST   /api/campaigns/{campaign_id}/analysis
GET    /api/campaigns/{campaign_id}/analysis

POST   /api/campaigns/{campaign_id}/journalists/{journalist_id}/pitch
```

API routes should contain minimal business logic.

---

# 5. Application Services

Services contain the application's business logic.

### Campaign Service

Responsible for:

* Creating campaigns
* Retrieving campaigns
* Updating campaign information

### Journalist Service

Responsible for:

* Importing journalists
* Validating journalist data
* Retrieving journalists
* Associating journalists with campaigns

### Analysis Service

Responsible for:

* Preparing campaign and journalist information
* Requesting AI analysis
* Validating the AI response
* Saving analysis results
* Ranking journalists

### Pitch Service

Responsible for:

* Preparing campaign and journalist information
* Requesting pitch generation
* Validating generated pitches
* Saving generated pitches

---

# 6. AI Integration

AI functionality is isolated behind an AI integration layer.

```text
Analysis Service
       │
       ▼
   AI Service
       │
       ▼
   LLM Provider
```

The AI service is responsible for:

* Building AI requests
* Selecting the appropriate prompt
* Calling the LLM provider
* Parsing responses
* Returning structured results
* Handling AI provider errors

The rest of the application should not directly depend on the LLM provider.

---

# 7. AI Analysis

Journalist analysis receives two primary inputs:

```text
Campaign
   +
Journalist
   ↓
AI Analysis
   ↓
Analysis Result
```

The analysis result contains:

```text
score
priority
reasons
supporting_evidence
concerns
```

Example:

```json
{
  "score": 92,
  "priority": "high",
  "reasons": [
    "Covers AI and developer tools"
  ],
  "supporting_evidence": [
    "Topic: AI",
    "Topic: Developer Tools"
  ],
  "concerns": []
}
```

The backend validates the AI response before storing it.

AI-generated information is treated as untrusted data.

---

# 8. Pitch Generation

Pitch generation uses information already stored in the application.

```text
Campaign
    +
Journalist
    +
Analysis
    │
    ▼
Pitch Service
    │
    ▼
AI Service
    │
    ▼
LLM Provider
    │
    ▼
Generated Pitch
```

The generated pitch contains:

```text
subject
body
```

The pitch is stored so that the user can review it after generation.

---

# 9. Data Layer

The data layer manages persistent application data.

The primary entities are:

```text
Campaign
Journalist
Analysis
Pitch
```

### Relationships

```text
Campaign
   │
   ├────── Journalists
   │
   ├────── Analyses
   │
   └────── Pitches
```

An analysis belongs to a campaign and a journalist.

A pitch belongs to a campaign and a journalist.

---

# 10. Repository Layer

Repositories provide access to persistent data.

```text
CampaignRepository
JournalistRepository
AnalysisRepository
PitchRepository
```

Repositories are responsible for:

* Creating records
* Retrieving records
* Updating records
* Deleting records where required

Services use repositories rather than directly accessing the database.

```text
Service
   │
   ▼
Repository
   │
   ▼
Database
```

---

# 11. Main User Flows

## 11.1 Campaign Creation

```text
User
 │
 ▼
React
 │
 ▼
POST /campaigns
 │
 ▼
Campaign API
 │
 ▼
Campaign Service
 │
 ▼
Campaign Repository
 │
 ▼
Database
```

---

## 11.2 Journalist Import

```text
User
 │
 ▼
React
 │
 │ CSV
 ▼
Journalist API
 │
 ▼
Journalist Service
 │
 ├── Validate CSV
 ├── Parse records
 └── Save journalists
        │
        ▼
     Database
```

---

## 11.3 Journalist Analysis

```text
User
 │
 ▼
React
 │
 ▼
Analysis API
 │
 ▼
Analysis Service
 │
 ├── Get Campaign
 ├── Get Journalists
 │
 └── For each Journalist
          │
          ▼
       AI Service
          │
          ▼
      LLM Provider
          │
          ▼
      Validate Result
          │
          ▼
      Save Analysis
          │
          ▼
       Database
```

---

## 11.4 Pitch Generation

```text
User
 │
 ▼
React
 │
 ▼
Pitch API
 │
 ▼
Pitch Service
 │
 ├── Campaign
 ├── Journalist
 └── Analysis
          │
          ▼
       AI Service
          │
          ▼
      LLM Provider
          │
          ▼
      Validate Pitch
          │
          ▼
      Save Pitch
          │
          ▼
       Database
```

---

# 12. Error Handling

Errors are handled at the backend boundary and returned to the frontend in a consistent format.

Example:

```json
{
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Unable to analyze the journalists."
  }
}
```

Common error categories include:

* Invalid input
* Invalid CSV
* Resource not found
* AI provider failure
* Database failure
* Unexpected server error

Internal errors and stack traces should not be exposed to the user.

---

# 13. Project Structure

The project should remain simple and reflect the architecture.

```text
pr-campaign-assistant/
│
├── README.md
├── PRD.md
├── ARCHITECTURE.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   └── tests/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── ai/
│   │   └── main.py
│   │
│   └── tests/
│
└── sample-data/
    └── journalists.csv
```

---

# 14. Security

The application should:

* Store API credentials in environment variables.
* Never commit secrets to the repository.
* Validate uploaded files.
* Validate user input.
* Validate AI-generated output.
* Avoid exposing internal errors.
* Restrict uploaded file size.

---

# 15. Testing

The backend should contain tests for:

### Services

* Campaign creation
* Journalist import
* Journalist analysis
* Journalist ranking
* Pitch generation

### API

* Valid requests
* Invalid requests
* Missing resources
* Error responses

### AI Integration

* Valid AI responses
* Invalid AI responses
* Missing fields
* Invalid scores
* Unsupported output

External AI calls should be mocked in normal automated tests.

---

# 16. Deployment

The application can be deployed as:

```text
                    Internet
                       │
                       ▼
                ┌─────────────┐
                │   React     │
                │  Frontend   │
                └──────┬──────┘
                       │
                       │ HTTPS
                       ▼
                ┌─────────────┐
                │   FastAPI   │
                │   Backend   │
                └──────┬──────┘
                       │
                 ┌─────┴─────┐
                 │           │
                 ▼           ▼
              Database     LLM API
```

The frontend and backend are independently deployable.

The backend requires access to the database and the configured LLM provider.

---

# 17. Architecture Principles

The application follows a few simple principles:

### Keep responsibilities separate

UI, business logic, AI integration, and data access should remain separate.

### Keep the backend as a modular monolith

The MVP does not require multiple backend services.

### Keep AI behind a boundary

Only the AI integration layer communicates with the LLM provider.

### Validate AI output

AI responses must be validated before they become application data.

### Keep APIs simple

The frontend communicates with the backend through straightforward REST APIs.

### Avoid unnecessary complexity

New infrastructure, abstractions, or services should only be introduced when the product requires them.
