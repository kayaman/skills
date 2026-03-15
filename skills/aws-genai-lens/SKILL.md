---
name: aws-genai-lens
description: Enforces AWS Well-Architected Generative AI Lens best practices for foundation model workloads on Amazon Bedrock and SageMaker AI. Use when designing GenAI architectures, implementing RAG pipelines, selecting foundation models, configuring Bedrock Guardrails, fine-tuning models, optimizing GenAI costs, securing AI workloads, or applying responsible AI principles including fairness, explainability, and safety.
---

# AWS Well-Architected Generative AI Lens

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book / Resource | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *AWS Well-Architected Generative AI Lens* (official) | AWS | AWS Docs | 2025 |
| *AI Engineering* | Chip Huyen | O'Reilly | 2025 |
| *Generative AI on AWS* | Fregly, Barth, Eigenbrode | O'Reilly | 2023 |
| *Hands-On Large Language Models* | Jay Alammar, Maarten Grootendorst | O'Reilly | 2024 |
| *Build a Large Language Model (From Scratch)* | Sebastian Raschka | Manning | 2024 |
| *Designing Machine Learning Systems* | Chip Huyen | O'Reilly | 2022 |

### Online References

- AWS GenAI Lens (updated Nov 2025): docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/
- AWS Responsible AI Lens (Nov 2025)
- AWS re:Invent 2025 announcements: AgentCore, Reinforcement Fine-Tuning, S3 Vectors

## Topics to Cover

- Six GenAI design principles: controlled autonomy, observability, resource efficiency, distributed resilience, standardized management, secure boundaries
- Six lifecycle phases: Scoping, Model Selection, Customization, Development & Integration, Deployment, Continuous Improvement
- Responsible AI: fairness, explainability, privacy/security, safety, controllability, veracity/robustness, governance, transparency
- Model selection: prompt engineering → RAG → fine-tuning decision tree
- Prompt engineering: centralized catalogs, versioning, injection prevention, Guardrails Prompt Attack filter
- RAG patterns: Bedrock Knowledge Bases, chunking strategies, vector stores (OpenSearch, Aurora pgvector, Neptune GraphRAG, S3 Vectors), contextual grounding
- Fine-tuning: LoRA, QLoRA, SFT, continued pre-training, model distillation, Reinforcement Fine-Tuning
- Cost optimization: model right-sizing, prompt caching, batch processing, intelligent routing, pricing tiers
- Security: PrivateLink, KMS, IAM least privilege, OWASP Top 10 for LLMs, AgentCore Cedar policies
- Amazon Bedrock Guardrails: content filters, denied topics, word filters, PII detection, contextual grounding, automated reasoning
