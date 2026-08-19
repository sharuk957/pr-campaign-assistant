# PR Campaign Assistant

## 1. Overview

### 1.1 Product

PR Campaign Assistant is an AI-powered tool that helps PR consultants identify journalists who are relevant to a specific campaign and prepare personalized outreach pitches.

A consultant provides campaign information and a list of journalists. The system evaluates the relevance of each journalist, explains the reasoning, ranks the journalists, and allows the consultant to generate a personalized pitch for a selected journalist.

### 1.2 Problem

PR consultants spend significant time reviewing journalists and determining who is relevant to a particular campaign.

The process often involves:

* Reviewing journalist profiles
* Understanding topics covered by journalists
* Matching journalists to campaign topics
* Determining why a journalist might be interested
* Writing personalized outreach messages

The goal of this product is to reduce this manual effort while keeping the consultant in control of the final outreach decision.

### 1.3 Goal

Enable a PR consultant to go from:

**Campaign idea → relevant journalists → personalized pitches**

in a simple workflow.

### 1.4 Target User

The primary user is a PR consultant responsible for media outreach.

The user has:

* A campaign or story to promote
* A list of journalists
* Information about those journalists
* A need to prioritize outreach

---

# 2. Product Goals

The MVP should allow a consultant to:

1. Create a campaign.
2. Import a list of journalists.
3. Analyze journalist relevance against the campaign.
4. View journalists ranked by relevance.
5. Understand why a journalist was considered relevant.
6. Review the evidence used for the recommendation.
7. Generate a personalized pitch for a selected journalist.
8. Review and copy the generated pitch.

The product should prioritize **usefulness, explainability, and reliable AI output**.

---

# 3. Core User Flow

```text
Create Campaign
      ↓
Enter Campaign Information
      ↓
Import Journalist List
      ↓
Analyze Journalists
      ↓
View Ranked Results
      ↓
Review Journalist
      ↓
Generate Personalized Pitch
      ↓
Review Pitch
      ↓
Copy Pitch
```

---

# 4. Functional Requirements

## FR-01: Create Campaign

The user must be able to create a campaign.

A campaign should contain:

* Campaign name
* Company name
* Product/service description
* Campaign/story description
* Target audience
* Key topics
* Desired outcome

Example:

```text
Campaign:
AI Developer Security Platform Launch

Company:
Acme Security

Product:
An AI-powered platform that detects security vulnerabilities
in Python applications.

Campaign:
Acme has launched a new AI-powered developer security platform
that automatically identifies vulnerabilities in Python code.

Target audience:
Software developers and engineering teams

Key topics:
AI, cybersecurity, Python, developer tools

Desired outcome:
Generate media coverage among technology publications.
```

### Acceptance Criteria

* The user can enter all required campaign information.
* Required fields are clearly identified.
* The user cannot create a campaign when required information is missing.
* A successfully created campaign can be viewed.
* Campaign information is available for journalist analysis.

---

# 5. FR-02: Import Journalists

The user must be able to import journalists using a CSV file.

The CSV should support:

* Name
* Email
* Publication
* Role
* Topics
* Biography
* Recent articles

Example:

```text
name,email,publication,role,topics,bio,recent_articles
Emma Smith,emma@example.com,Tech Weekly,Technology Writer,"AI;Developer Tools;Python","Technology journalist covering developer tools and AI","AI coding tools;Python security"
```

### Acceptance Criteria

* The user can upload a CSV file.
* The system validates the uploaded file.
* Invalid files produce a clear error message.
* Valid journalist records are imported.
* Imported journalists are associated with the campaign.
* The user can review the imported journalists before starting analysis.

---

# 6. FR-03: Analyze Journalist Relevance

The system must analyze each journalist against the selected campaign.

The analysis should consider the information available about the journalist, including:

* Topics
* Biography
* Publication
* Role
* Recent articles

The system should produce a relevance score between **0 and 100**.

Each analysis should also provide:

* Relevance score
* Priority
* Reasons for the score
* Supporting evidence
* Potential concerns

Example:

```text
Emma Smith

Relevance Score: 92
Priority: High

Reasons:
- Covers AI and developer tools.
- Has written about Python-related topics.
- Her publication focuses on technology.

Supporting Evidence:
- Topic: AI
- Topic: Developer Tools
- Recent article: Python security

Potential Concerns:
- No recent evidence of cybersecurity-specific coverage.
```

### Acceptance Criteria

* Every valid journalist receives a relevance score.
* Scores are between 0 and 100.
* Every analysis includes an explanation.
* The explanation is based on available journalist and campaign information.
* The system does not intentionally present unsupported information as fact.
* Failure to analyze one journalist does not prevent other journalists from being analyzed.
* The user can identify highly relevant journalists from the results.

---

# 7. FR-04: Rank Journalists

The system must display journalists ordered by relevance.

The results should show:

* Journalist name
* Publication
* Relevance score
* Priority
* Short explanation

Example:

```text
1. Emma Smith       92   High
2. John Williams    88   High
3. Sarah Johnson    71   Medium
4. David Brown      24   Low
```

### Acceptance Criteria

* Journalists are ordered by relevance score.
* The highest-scoring journalists appear first.
* The user can open an individual journalist's analysis.
* The ranking updates when new analysis is generated.

---

# 8. FR-05: View Journalist Details

The user must be able to inspect an individual journalist.

The detail view should contain:

### Journalist Information

* Name
* Email
* Publication
* Role
* Topics
* Biography
* Recent articles

### Relevance Analysis

* Relevance score
* Priority
* Reasons
* Supporting evidence
* Potential concerns

The interface must clearly distinguish between:

**Journalist-provided/source information**

and

**AI-generated analysis.**

### Acceptance Criteria

* The user can open a journalist from the ranked results.
* All available journalist information is displayed.
* The corresponding relevance analysis is displayed.
* Source information and AI-generated analysis are visually distinguishable.

---

# 9. FR-06: Generate Personalized Pitch

The user must be able to generate an outreach pitch for a selected journalist.

The generated pitch should use:

* Campaign information
* Journalist information
* Relevance analysis
* Supporting evidence

The pitch should contain:

* Subject line
* Greeting
* Personalized opening
* Campaign/story introduction
* Reason the story may be relevant
* Call to action

Example:

```text
Subject: Python security research for your developer tools coverage

Hi Emma,

I noticed your recent coverage of Python and developer tools...

[Campaign-specific pitch]

Given your coverage of developer tooling and Python,
I thought this might be relevant to your audience.

Would you be interested in taking a look?
```

### Acceptance Criteria

* The user can generate a pitch for a selected journalist.
* The generated pitch is based on the campaign and journalist information.
* The pitch uses the available relevance information.
* The pitch does not intentionally introduce unsupported journalist claims.
* The user can regenerate the pitch.
* The user can copy the generated pitch.

---

# 10. FR-07: AI Grounding

AI-generated recommendations and pitches must be grounded in the information available to the system.

The system must not present unsupported claims about:

* Journalist expertise
* Journalist interests
* Previous articles
* Publications
* Contact information
* Opinions
* Previous interactions

If there is insufficient information, the system should acknowledge the limitation rather than inventing information.

Example:

```text
Insufficient evidence to determine whether this journalist
regularly covers cybersecurity.
```

is preferable to:

```text
This journalist regularly covers cybersecurity.
```

### Acceptance Criteria

* AI analysis is based on supplied information.
* Missing information is not treated as evidence.
* AI output is validated before being accepted by the application.
* The application can handle invalid or incomplete AI responses.

---

# 11. FR-08: Error Handling

The application must provide understandable feedback when an operation cannot be completed.

The system should handle at least:

* Missing campaign information
* Invalid CSV files
* Empty journalist files
* Invalid journalist records
* Analysis failures
* AI provider failures
* Pitch generation failures

### Acceptance Criteria

* Users receive a clear error message.
* The application does not expose technical stack traces to the user.
* A temporary AI failure does not corrupt existing campaign or journalist data.
* Users can retry failed operations where appropriate.

---

# 12. User Interface

The MVP should contain the following main screens.

## Campaign

Allows the user to:

* Create a campaign
* View campaign information
* Start the journalist workflow

## Journalists

Allows the user to:

* Upload a CSV
* View imported journalists
* Start analysis

## Analysis Results

Allows the user to:

* View ranked journalists
* View relevance scores
* Filter or identify high-priority journalists
* Open journalist details

## Journalist Details

Allows the user to:

* Review journalist information
* Review relevance analysis
* Review supporting evidence
* Generate a pitch

## Pitch

Allows the user to:

* Review the generated pitch
* Regenerate the pitch
* Copy the pitch

---

# 13. Data Requirements

The system needs to store the following information.

## Campaign

* Campaign ID
* Campaign name
* Company name
* Product/service description
* Campaign/story description
* Target audience
* Key topics
* Desired outcome
* Creation date

## Journalist

* Journalist ID
* Name
* Email
* Publication
* Role
* Topics
* Biography
* Recent articles

## Analysis

* Analysis ID
* Campaign
* Journalist
* Relevance score
* Priority
* Reasons
* Supporting evidence
* Potential concerns
* Creation date

## Pitch

* Pitch ID
* Campaign
* Journalist
* Subject
* Body
* Creation date

---

# 14. AI Requirements

AI is used for two primary capabilities:

### Journalist Analysis

The AI evaluates the relevance of a journalist to a campaign.

### Pitch Generation

The AI generates a personalized outreach pitch using the campaign, journalist, and relevance information.

AI-generated responses must be structured and validated before being used by the application.

The application must treat AI output as **untrusted data**.

---

# 15. Testing Requirements

The application should include automated tests covering the core product behavior.

## Campaign

* Valid campaign creation
* Missing required information
* Invalid campaign input

## Journalist Import

* Valid CSV
* Missing columns
* Empty CSV
* Invalid rows
* Duplicate or malformed records

## Journalist Analysis

* Valid analysis
* Invalid AI response
* Missing AI fields
* Invalid score
* Unsupported claims
* Analysis failure

## Pitch Generation

* Successful generation
* Missing campaign information
* Missing journalist information
* Invalid AI response
* Unsupported journalist claims

## API

* Successful requests
* Invalid requests
* Missing resources
* Expected error responses

External AI calls should be mocked for normal automated tests.

---

# 16. Success Criteria

The MVP is successful when a PR consultant can:

1. Create a campaign.
2. Import a journalist list.
3. Analyze the journalists.
4. Identify the most relevant journalists.
5. Understand why they were ranked highly.
6. Review the supporting evidence.
7. Generate a personalized pitch.
8. Review and copy the pitch.

The complete workflow should be usable without requiring technical knowledge.

---

# 17. MVP Constraints

The MVP should remain small enough to build and finish within approximately one or two evenings.

The priority is:

```text
Correctness
    ↓
Reliability
    ↓
Useful AI output
    ↓
Explainability
    ↓
Usability
```

The product should favor a small, complete workflow over a large number of partially implemented features.

---

# 18. Future Possibilities

Potential future capabilities include:

* Journalist discovery
* Web-based journalist research
* Automatic journalist profile enrichment
* Email outreach
* WhatsApp outreach
* Follow-up recommendations
* Campaign analytics
* Response tracking
* CRM integration
* HubSpot integration
* Contact history
* Pitch A/B testing
* Human approval workflows

These capabilities are outside the initial MVP.

---

# 19. Definition of Done

The MVP is complete when:

* [ ] A user can create a campaign.
* [ ] A user can import journalists using CSV.
* [ ] Imported journalists can be reviewed.
* [ ] Journalists can be analyzed against a campaign.
* [ ] Journalists are ranked by relevance.
* [ ] Each analysis includes an explanation.
* [ ] Supporting evidence is displayed.
* [ ] AI output is validated.
* [ ] Unsupported claims are handled appropriately.
* [ ] A personalized pitch can be generated.
* [ ] A pitch can be regenerated.
* [ ] A pitch can be copied.
* [ ] Core functionality has automated tests.
* [ ] AI failures are handled gracefully.
* [ ] Invalid input is handled gracefully.
* [ ] The application can be run from a clean environment.
* [ ] README documentation explains setup and usage.
* [ ] The repository contains meaningful incremental commits.
* [ ] The complete workflow can be demonstrated in a live demo.

---

# 20. Product Principle

> **AI should help the PR consultant make a better decision, not replace the consultant's judgment.**

The system should make recommendations and supporting reasoning visible so that the consultant can review the information and decide who to contact.
