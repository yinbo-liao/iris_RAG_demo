# Multi-Agent Iris Analytics System (Advanced Architecture with RAG Agent)

## Overview

This project demonstrates an enterprise-style Agentic AI architecture using the Iris dataset. The system is designed around a Main Orchestrator Agent and several specialized subagents, each with a clearly defined role, model selection strategy, and least-privilege permissions.

---

# System Architecture

```text
                        User
                          |
                          v
                Main Orchestrator Agent
                          |
      -------------------------------------------------
      |               |              |                |
      v               v              v                v

 Data Pattern     Random Forest    SVM Agent     XGBoost Agent
 Analysis Agent      Agent

      -------------------------------------------------
                          |
                          v
                   Evaluation Agent
                          |
                          v
                     RAG Agent
                          |
                          v
                Main Orchestrator Agent
                          |
                          v
                     Final Report
```

---

# Agent Definitions

## 1. Main Orchestrator Agent

### Role
- Receive user requests.
- Decompose tasks.
- Delegate work to subagents.
- Collect results.
- Generate final executive summary.

### Suggested Model
- GPT-5
- GPT-4o
- Claude Sonnet

### Permissions
- Read user request
- Invoke subagents
- Read subagent outputs

### Restrictions
- Does not train models.
- Does not perform detailed data analysis.
- Does not directly manipulate datasets.

### Expected Output
- End-to-end business summary.
- Recommendations.
- Consolidated findings.

---

## 2. Data Pattern Analysis Agent

### Role
Perform exploratory data analysis (EDA).

### Responsibilities
- Class distribution analysis
- Feature statistics
- Correlation analysis
- Category pattern identification
- Outlier investigation
- Class separability evaluation

### Suggested Model
- GPT-4o-mini
- Claude Haiku
- Llama 3.x

### Permissions
- Read Iris dataset
- Execute Pandas analysis
- Generate charts and statistics

### Restrictions
- Cannot train ML models.
- Cannot access evaluation results.

### Example Findings
- Setosa is clearly separable.
- Petal dimensions provide strongest signals.
- Virginica and Versicolor overlap.

---

## 3. Random Forest Agent

### Role
Train and evaluate a Random Forest classifier.

### Suggested Model
- GPT-4o-mini

### Permissions
- Read dataset
- Train Random Forest model

### Output
```json
{
  "model": "Random Forest",
  "accuracy": 0.97,
  "precision": 0.96,
  "recall": 0.97,
  "f1": 0.97
}
```

---

## 4. SVM Agent

### Role
Train and evaluate an SVM classifier.

### Suggested Model
- GPT-4o-mini

### Permissions
- Read dataset
- Train SVM model

### Output
```json
{
  "model": "SVM",
  "accuracy": 0.98,
  "precision": 0.98,
  "recall": 0.98,
  "f1": 0.98
}
```

---

## 5. XGBoost Agent

### Role
Train and evaluate an XGBoost classifier.

### Suggested Model
- GPT-4o-mini

### Permissions
- Read dataset
- Train XGBoost model

### Output
```json
{
  "model": "XGBoost",
  "accuracy": 0.98,
  "precision": 0.97,
  "recall": 0.98,
  "f1": 0.98
}
```

---

## 6. Evaluation Agent

### Role
Compare model performance objectively.

### Responsibilities
- Compare metrics
- Rank models
- Identify strongest candidate
- Explain tradeoffs

### Suggested Model
- GPT-4o-mini
- Claude Sonnet

### Permissions
- Read model metrics
- Produce ranking report

### Restrictions
- Cannot retrain models.
- Cannot modify results.

### Example Output
```json
{
  "ranking": [
    "SVM",
    "XGBoost",
    "Random Forest"
  ],
  "best_model": "SVM",
  "reason": "Highest overall classification performance"
}
```

---

# Extension With RAG Agent

## Why Add RAG?

Traditional machine learning results explain what happened.

RAG (Retrieval-Augmented Generation) explains why it happened using external knowledge.

The RAG Agent enriches analytical results with:

- Botanical knowledge
- Species descriptions
- Scientific references
- Dataset documentation
- Machine learning best practices

---

## 7. RAG Knowledge Agent

### Role
Retrieve domain knowledge and contextual information to support analysis.

### Responsibilities
- Query vector database
- Retrieve knowledge documents
- Return relevant context
- Support final explanation generation

### Suggested Model
- GPT-4o-mini
- Small LLM optimized for retrieval workflows

### Permissions
- Read-only vector database access
- Read-only knowledge base access

### Restrictions
- No model training
- No dataset modification
- No ranking decisions

---

## RAG Pipeline

```text
User Question
      |
      v
Embedding Model
      |
      v
Vector Database
      |
      v
Top-K Retrieval
      |
      v
RAG Agent
      |
      v
Retrieved Context
      |
      v
Orchestrator Agent
```

---

## Suggested RAG Knowledge Sources

### Iris Dataset Knowledge
- Species information
- Botanical descriptions
- Original Fisher Iris documentation

### Machine Learning Knowledge
- Classification algorithms
- Best practices
- Evaluation methodologies

### Experiment Documentation
- Project notes
- Analysis reports
- Historical experiment outputs

---

## Recommended Vector Database

### Beginner
- ChromaDB

### Intermediate
- FAISS

### Production
- PostgreSQL + pgvector
- Azure AI Search
- Pinecone

---

# End-to-End Workflow

## Step 1
User asks:

```text
Analyze Iris dataset and recommend the best classifier.
```

## Step 2
Orchestrator delegates tasks.

```text
A. Pattern Analysis Agent
B. Random Forest Agent
C. SVM Agent
D. XGBoost Agent
```

## Step 3
Agents execute in parallel.

## Step 4
Evaluation Agent ranks models.

## Step 5
RAG Agent retrieves supporting knowledge.

## Step 6
Main Agent generates final report.

---

# Benefits of This Architecture

## Scalability
Agents can be added without redesigning the system.

## Cost Optimization
Use smaller models for specialized tasks.

## Security
Least-privilege permissions reduce risk.

## Explainability
RAG provides evidence-backed explanations.

## Parallelism
Multiple models train simultaneously.

## Enterprise Readiness
Architecture mirrors modern production-grade multi-agent systems.

---

# Final Recommendation

For the Iris project, implement:

1. Main Orchestrator Agent
2. Data Pattern Analysis Agent
3. Random Forest Agent
4. SVM Agent
5. XGBoost Agent
6. Evaluation Agent
7. RAG Knowledge Agent

This architecture demonstrates advanced Agentic AI concepts including task decomposition, role specialization, parallel execution, model orchestration, retrieval-augmented generation, evaluation governance, and final synthesis.
