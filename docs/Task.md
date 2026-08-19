# PR Campaign Assistant — Implementation Task Breakdown

## 1. Purpose

This document breaks the PR Campaign Assistant MVP into small implementation tasks.

Each task should be independently understandable and should result in a working, testable increment of the product.

The implementation should follow:

```text
Task
 ↓
Implement
 ↓
Test
 ↓
Review
 ↓
Commit
```

AI coding agents should implement one task at a time rather than receiving the entire project as a single request.

---

# 2. Task Dependency Overview

```text
TASK-001 Project Initialization
        │
        ├──────────────┐
        ▼              ▼
TASK-002 Backend    TASK-003 Frontend
        │              │
        └──────┬───────┘
               ▼
        TASK-004 Campaign
               │
               ▼
        TASK-005 Journalists
               │
               ▼
        TASK-006 CSV Import
               │
               ▼
        TASK-007 Journalist UI
               │
               ▼
        TASK-008 AI Analysis
               │
               ▼
        TASK-009 Analysis Results
               │
               ▼
        TASK-010 Journalist Details
               │
               ▼
        TASK-011 Pitch Generation
               │
               ▼
        TASK-012 AI Validation
               │
               ▼
        TASK-013 Error Handling & UX
               │
               ▼
        TASK-014 Testing & Quality
               │
               ▼
        TASK-015 Deployment & Documentation
```

---

# 3. TASK-001 — Initialize Project

## Objective

Create the initial repository structure and development environment.

## Requirements

Create:

```text
pr-campaign-assistant/
├── README.md
├── frontend/
├── backend/
└── sample-data/
```

Initialize:

* React + TypeScript frontend
* FastAPI backend
* Python virtual environment configuration
* Git configuration
* Environment configuration
* Basic project documentation

The frontend and backend should both be runnable locally.

## Acceptance Criteria

* [ ] Repository has the expected structure.
* [ ] React application starts successfully.
* [ ] FastAPI application starts successfully.
* [ ] Frontend can access the backend.
* [ ] Environment configuration is documented.
* [ ] No secrets are committed.
* [ ] Existing PRD and architecture documents are included.

## Tests

Verify:

* Frontend starts.
* Backend starts.
* Backend health endpoint responds successfully.

---

# 4. TASK-002 — Implement Backend Foundation

## Objective

Create the basic FastAPI backend structure described in the architecture.

## Requirements

Implement:

* FastAPI application
* Configuration
* Database connection
* Base database setup
* API routing structure
* Error handling foundation
* Health endpoint

Organize backend code into the appropriate modules.

## Acceptance Criteria

* [ ] FastAPI application starts.
* [ ] Database connection works.
* [ ] API routes can be registered.
* [ ] Health endpoint works.
* [ ] Configuration is loaded from environment variables.
* [ ] Basic error handling exists.
* [ ] Backend tests can run successfully.

---

# 5. TASK-003 — Implement Frontend Foundation

## Objective

Create the initial React application structure.

## Requirements

Implement:

* Application entry point
* Routing
* Basic page structure
* API client
* Shared types
* Basic layout/navigation
* Loading state support
* Error display support

Create placeholder pages for:

```text
Campaign
Journalists
Analysis
Journalist Details
Pitch
```

## Acceptance Criteria

* [ ] React application starts.
* [ ] Pages can be navigated.
* [ ] API client can communicate with the backend.
* [ ] Basic layout is consistent across pages.
* [ ] No business logic is implemented in the UI yet.

---

# 6. TASK-004 — Implement Campaign Management

## Objective

Allow users to create and view campaigns.

## Requirements

Implement the Campaign entity with:

* ID
* Campaign name
* Company name
* Product/service description
* Campaign/story description
* Target audience
* Key topics
* Desired outcome
* Creation date

Implement backend:

* Campaign model
* Campaign repository
* Campaign service
* Campaign API

Implement frontend:

* Campaign form
* Campaign view
* Form validation
* Success/error states

## Acceptance Criteria

* [ ] User can create a campaign.
* [ ] Required fields are validated.
* [ ] Campaign is persisted.
* [ ] Created campaign can be retrieved.
* [ ] Validation errors are displayed clearly.
* [ ] Backend tests exist for campaign creation.

---

# 7. TASK-005 — Implement Journalist Management

## Objective

Create the journalist data model and basic management functionality.

## Requirements

Implement the Journalist entity:

* ID
* Name
* Email
* Publication
* Role
* Topics
* Biography
* Recent articles

Journalists must be associated with a campaign.

Implement:

* Journalist model
* Repository
* Service
* API
* Basic frontend listing

## Acceptance Criteria

* [ ] Journalists can be stored.
* [ ] Journalists are associated with campaigns.
* [ ] Journalists can be retrieved for a campaign.
* [ ] Journalist information is displayed.
* [ ] Tests cover the core journalist operations.

---

# 8. TASK-006 — Implement Journalist CSV Import

## Objective

Allow users to import journalists from a CSV file.

## Requirements

Support the following CSV fields:

```text
name
email
publication
role
topics
bio
recent_articles
```

The backend must:

* Receive the uploaded file.
* Validate required columns.
* Parse records.
* Validate individual records.
* Store valid journalists.
* Return meaningful validation errors.

The frontend must:

* Provide a CSV upload interface.
* Show upload progress/loading state.
* Display validation errors.
* Show successful import results.

## Acceptance Criteria

* [ ] Valid CSV files can be imported.
* [ ] Invalid files are rejected.
* [ ] Missing columns are detected.
* [ ] Invalid rows are reported.
* [ ] Valid journalists are persisted.
* [ ] Imported journalists appear in the journalist list.
* [ ] CSV parsing has automated tests.

---

# 9. TASK-007 — Implement Journalist List and Details UI

## Objective

Create the user interface for reviewing imported journalists.

## Requirements

The journalist list should display:

* Name
* Publication
* Role
* Topics

The journalist detail view should display:

* Name
* Email
* Publication
* Role
* Topics
* Biography
* Recent articles

The UI should clearly distinguish source information from future AI-generated analysis.

## Acceptance Criteria

* [ ] User can view all campaign journalists.
* [ ] User can open an individual journalist.
* [ ] All available journalist information is displayed.
* [ ] Empty states are handled.
* [ ] Loading states are handled.
* [ ] API errors are displayed clearly.

---

# 10. TASK-008 — Implement AI Service

## Objective

Create the AI integration layer without yet implementing the complete analysis workflow.

## Requirements

Create an AI service that:

* Communicates with the selected LLM provider.
* Loads prompts.
* Sends structured requests.
* Receives responses.
* Parses responses.
* Handles provider errors.

The AI integration must be isolated from the rest of the application.

Create an initial abstraction that can support:

```text
analyze_journalist()
generate_pitch()
```

## Acceptance Criteria

* [ ] LLM credentials are loaded from environment variables.
* [ ] AI provider calls are isolated inside the AI layer.
* [ ] Provider failures are handled.
* [ ] Responses can be parsed into application structures.
* [ ] AI calls can be mocked in tests.
* [ ] No API key is committed to the repository.

---

# 11. TASK-009 — Implement Journalist Relevance Analysis

## Objective

Analyze each journalist against a campaign.

## Requirements

The analysis should use:

```text
Campaign
+
Journalist
```

The AI should return:

* Relevance score
* Priority
* Reasons
* Supporting evidence
* Potential concerns

The backend must:

1. Retrieve the campaign.
2. Retrieve associated journalists.
3. Send campaign and journalist information to the AI service.
4. Validate the response.
5. Store the analysis.
6. Continue processing if one journalist fails.
7. Return analysis results.

## Acceptance Criteria

* [ ] Journalists can be analyzed against a campaign.
* [ ] Each successful analysis has a score from 0–100.
* [ ] Each analysis contains reasoning.
* [ ] Supporting evidence is included.
* [ ] Analysis is persisted.
* [ ] One failed analysis does not stop all processing.
* [ ] AI calls are mocked in automated tests.

---

# 12. TASK-010 — Implement Analysis Results UI

## Objective

Allow users to view and understand journalist analysis results.

## Requirements

Display:

* Journalist name
* Publication
* Relevance score
* Priority
* Short explanation

Order journalists by relevance score.

Allow the user to open the complete analysis.

The detailed analysis should display:

* Score
* Priority
* Reasons
* Supporting evidence
* Potential concerns

## Acceptance Criteria

* [ ] Results are displayed after analysis.
* [ ] Journalists are ranked by score.
* [ ] Score and priority are visible.
* [ ] User can open detailed analysis.
* [ ] Loading state is displayed while analysis is running.
* [ ] Failed analysis is represented clearly.
* [ ] Empty results are handled.

---

# 13. TASK-011 — Implement Pitch Generation

## Objective

Generate a personalized outreach pitch for a selected journalist.

## Requirements

Pitch generation should use:

```text
Campaign
+
Journalist
+
Relevance Analysis
```

The generated pitch should contain:

* Subject
* Body

The user should be able to:

* Generate a pitch.
* Regenerate a pitch.
* Copy the pitch.

## Acceptance Criteria

* [ ] User can generate a pitch from journalist details.
* [ ] Campaign information is included in the generation context.
* [ ] Journalist information is included.
* [ ] Relevance analysis is included.
* [ ] Generated pitch is stored.
* [ ] User can regenerate the pitch.
* [ ] User can copy the pitch.
* [ ] Pitch generation failures are handled.

---

# 14. TASK-012 — Implement AI Grounding and Validation

## Objective

Ensure AI output does not introduce unsupported journalist information.

## Requirements

The system must validate AI responses.

For relevance analysis:

* Score must be 0–100.
* Priority must be valid.
* Required fields must exist.
* Supporting evidence must reference available information.

For pitch generation:

* Required output fields must exist.
* The pitch must be based on supplied campaign and journalist information.
* Unsupported journalist claims should be prevented or flagged.

Add tests for cases such as:

```text
Journalist has no cybersecurity information
             ↓
AI should not claim
"Journalist regularly covers cybersecurity"
```

## Acceptance Criteria

* [ ] Invalid AI responses are rejected.
* [ ] Invalid scores are rejected.
* [ ] Missing fields are handled.
* [ ] Unsupported information is not blindly accepted.
* [ ] Grounding-related tests exist.
* [ ] Existing valid AI workflows continue to work.

---

# 15. TASK-013 — Improve Error Handling and User Experience

## Objective

Make the complete workflow reliable and understandable for normal users.

## Requirements

Review the entire application for:

* Loading states
* Empty states
* Validation errors
* API errors
* AI failures
* CSV failures
* Disabled states
* Retry behavior

The application should not expose technical errors or stack traces to users.

## Acceptance Criteria

* [ ] All major actions have loading states.
* [ ] Empty states are understandable.
* [ ] User-facing errors are clear.
* [ ] AI failures can be retried.
* [ ] CSV errors identify the problem.
* [ ] Buttons prevent accidental duplicate submissions.
* [ ] No raw backend errors are displayed.

---

# 16. TASK-014 — End-to-End Testing and Quality Review

## Objective

Verify the complete MVP workflow.

## Requirements

Test the primary workflow:

```text
Create Campaign
      ↓
Import Journalists
      ↓
Analyze Journalists
      ↓
View Rankings
      ↓
Open Journalist
      ↓
Generate Pitch
      ↓
Copy Pitch
```

Add automated tests where appropriate.

Perform a manual review of:

* Frontend behavior
* Backend behavior
* AI behavior
* Error handling
* Data persistence

Review the generated code for:

* Unnecessary complexity
* Duplicated logic
* Poor naming
* Missing validation
* Security issues
* Unhandled errors

## Acceptance Criteria

* [ ] Complete workflow works from beginning to end.
* [ ] Automated tests pass.
* [ ] No critical console errors.
* [ ] No critical backend errors.
* [ ] AI failures are handled.
* [ ] Invalid input is handled.
* [ ] Application works using clean sample data.
* [ ] Code has been manually reviewed.

---

# 17. TASK-016 — Documentation and Deployment

## Objective

Prepare the application for public evaluation.

## Requirements

Update `README.md` with:

* Product overview
* Problem being solved
* Features
* Architecture overview
* Technology stack
* Local setup
* Environment variables
* How to run frontend
* How to run backend
* How to run tests
* Sample data instructions
* Application workflow

Deploy a working version of the application.

## Acceptance Criteria

* [ ] New developer can understand the project from README.
* [ ] Application can be started from a clean environment.
* [ ] Required environment variables are documented.
* [ ] Tests can be executed using documented commands.
* [ ] Application is publicly accessible.
* [ ] Demo workflow works in the deployed environment.


