---
name: aws-genai-lens
description: Enforces AWS Well-Architected Generative AI Lens best practices for foundation model workloads on Amazon Bedrock and SageMaker AI. Use when designing GenAI architectures, implementing RAG pipelines, selecting foundation models, configuring Bedrock Guardrails, fine-tuning models, optimizing GenAI costs, securing AI workloads, or applying responsible AI principles including fairness, explainability, and safety.
---

# AWS Well-Architected Generative AI Lens

Reference: [AWS GenAI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/) (updated Nov 2025)

## When to Apply

- Designing GenAI architectures on AWS (Bedrock, SageMaker AI)
- Implementing RAG pipelines with vector stores and knowledge bases
- Selecting foundation models and deciding between prompting, RAG, and fine-tuning
- Configuring guardrails for content safety, PII protection, and hallucination detection
- Optimizing GenAI workload costs (model selection, caching, batching)
- Securing AI workloads (prompt injection defense, data protection, access control)
- Applying responsible AI principles to production FM workloads

---

## GenAI Design Principles

1. **Design for controlled autonomy** — bound agent actions with explicit guardrails and stopping conditions
2. **Implement comprehensive observability** — monitor prompts, responses, latency, cost, and quality metrics
3. **Optimize resource efficiency** — right-size models; use caching and batching to reduce cost
4. **Establish distributed resilience** — design for FM endpoint failures, throttling, and degraded responses
5. **Standardize resource management** — centralize model access, prompt catalogs, and configuration
6. **Secure interaction boundaries** — validate inputs, filter outputs, enforce least privilege on FM endpoints

---

## Lifecycle Phases

| Phase | Key Activities |
|-------|---------------|
| **1. Scoping** | Define the business problem; determine if GenAI is the right solution; identify success metrics |
| **2. Model Selection** | Evaluate models by modality, accuracy, latency, cost, and context window; benchmark candidates |
| **3. Customization** | Prompt engineering → RAG → fine-tuning (progressive investment); evaluate after each stage |
| **4. Development & Integration** | Build application logic, implement guardrails, integrate with existing systems |
| **5. Deployment** | Deploy to production with monitoring, scaling, and rollback capability |
| **6. Continuous Improvement** | Monitor quality metrics; refine prompts, retrieval, and models; manage model lifecycle |

---

## Model Selection and Customization Strategy

### Decision Tree

```
Start with prompt engineering (lowest cost, fastest iteration)
  ↓ Not meeting quality bar?
Add RAG for knowledge-grounded tasks
  ↓ Still not meeting quality bar?
Fine-tune when behavior/style is the bottleneck
  ↓ Need maximum control?
Custom training via SageMaker HyperPod
```

- MUST start with prompt engineering and evaluate before investing in RAG or fine-tuning
- MUST benchmark multiple models on representative tasks before selecting
- SHOULD use the smallest model that meets quality requirements — model right-sizing is the single biggest cost lever

### Model Selection Criteria

| Criterion | Considerations |
|-----------|---------------|
| **Modality** | Text, image, audio, video, multi-modal, embedding |
| **Quality** | Accuracy on your task benchmarks; reasoning capability |
| **Context Window** | How much input context the task requires |
| **Latency** | Real-time vs batch tolerance |
| **Cost** | Per-token pricing; throughput pricing; reserved capacity |
| **Provider** | Anthropic, Meta, Mistral, Amazon, Cohere, AI21, Stability AI (via Bedrock) |

---

## Prompt Engineering

### Rules

- MUST implement a centralized prompt catalog with version control — treat prompts as code
- MUST separate system prompts from user input to prevent instruction override
- MUST use few-shot examples for tasks requiring consistent format or style
- SHOULD implement prompt templates with variable substitution for maintainability
- SHOULD measure and track prompt performance metrics (quality, latency, cost)

### Prompt Injection Defense

- MUST use Bedrock Guardrails Prompt Attack filter on all user-facing endpoints
- MUST sanitize and validate all user inputs before sending to the model
- MUST assume injection CAN succeed — design defense-in-depth (input filtering + output validation + action authorization)
- SHOULD separate system instructions from user content using clear delimiters
- MUST NOT trust model output for security-critical decisions without validation

---

## RAG (Retrieval-Augmented Generation)

RAG augments FM responses with retrieved knowledge, reducing hallucination and keeping responses grounded.

### Amazon Bedrock Knowledge Bases

Automates the full RAG pipeline: ingestion → chunking → embedding → vector storage → retrieval → prompt augmentation.

### Vector Store Options

| Store | Best For | Key Feature |
|-------|----------|-------------|
| **OpenSearch Serverless** | General-purpose vector search | Fully managed; hybrid search (vector + keyword) |
| **Aurora PostgreSQL (pgvector)** | Teams already using Aurora | Familiar SQL; transactional consistency |
| **Neptune Analytics** | Knowledge graph + vector (GraphRAG) | Links related content; improves complex reasoning |
| **Amazon S3 Vectors** (2025) | High-scale, cost-sensitive workloads | Up to 2B vectors/index; ~90% cost reduction vs specialized DBs |
| **MongoDB Atlas** | MongoDB-native teams | Atlas Vector Search integration |
| **Pinecone** | Dedicated vector DB teams | Purpose-built vector search |

### Chunking Strategies

| Strategy | Use When |
|----------|----------|
| **Fixed-size** | Uniform content; simple implementation |
| **Semantic** | Content with natural topic boundaries |
| **Hierarchical** | Content with parent-child structure (sections, subsections) |
| **Custom (Lambda)** | Domain-specific chunking logic required |

### RAG Quality Rules

- MUST implement contextual grounding checks to detect hallucination in RAG responses
- SHOULD use hybrid search (vector + keyword) for better retrieval precision
- SHOULD evaluate retrieval quality separately from generation quality
- SHOULD implement metadata filtering to narrow retrieval scope

---

## Fine-Tuning

SHOULD fine-tune only when prompt engineering + RAG cannot achieve the required quality for behavior or style.

### Approaches

| Approach | Use When | Cost |
|----------|----------|------|
| **Supervised Fine-Tuning (SFT)** | Specific task format or domain style | Moderate |
| **Continued Pre-Training** | Domain-specific vocabulary and knowledge | High |
| **LoRA** (Low-Rank Adaptation) | Resource-efficient task adaptation | Low — dramatically less compute |
| **QLoRA** | Fine-tuning on limited GPU memory | Very low |
| **Model Distillation** | Compress a large model's capability into a smaller one | Moderate |
| **Reinforcement Fine-Tuning** (2025) | Align model behavior with human preferences | High — but avg 66% accuracy gain |

- MUST establish baseline metrics with prompting + RAG before fine-tuning
- MUST maintain a high-quality evaluation dataset throughout the fine-tuning process
- SHOULD use LoRA as the default fine-tuning approach for cost efficiency

---

## Responsible AI

### Eight Dimensions

| Dimension | Key Practices |
|-----------|--------------|
| **Fairness** | Bias detection and auditing across demographics; diverse evaluation datasets |
| **Explainability** | Interpretable decisions; document model limitations and known failure modes |
| **Privacy & Security** | Encryption at rest/transit; access controls; regulatory compliance (GDPR, HIPAA) |
| **Safety** | Content filtering; guardrails; output validation; harmful content prevention |
| **Controllability** | Human oversight; monitoring; ability to adjust or override model behavior |
| **Veracity & Robustness** | Accuracy validation; automated reasoning for hallucination detection; adversarial testing |
| **Governance** | AI review committees; model cards; documentation; escalation procedures |
| **Transparency** | Clear disclosure that content is AI-generated; model provenance documentation |

- MUST implement safety guardrails on all production FM endpoints
- MUST document model limitations and known failure modes
- SHOULD establish AI governance processes before production deployment

---

## Amazon Bedrock Guardrails

Six safeguard policies applied on both inbound prompts and outbound responses:

| Policy | Purpose | Configuration |
|--------|---------|---------------|
| **Content Filters** | Block hate, insults, sexual, violence, misconduct, prompt attack | Configurable strength per category |
| **Denied Topics** | Block up to 30 specific topics | Natural language topic descriptions |
| **Word Filters** | Exact-match blocking of specific words | Word list management |
| **Sensitive Information Filters** | Detect and block/mask PII | ML-based detection; block or mask options |
| **Contextual Grounding Checks** | Detect hallucination in RAG responses | Grounding score threshold |
| **Automated Reasoning Checks** | Formal mathematical logic verification | *"First GenAI safeguard to use formal logic"* |

- MUST configure content filters on all user-facing FM endpoints
- MUST enable PII detection for workloads handling personal data
- SHOULD enable contextual grounding checks for all RAG workloads
- The **ApplyGuardrail API** works with ANY model, including self-hosted or third-party

---

## Cost Optimization

### Pricing Models

| Model | Use When |
|-------|----------|
| **On-Demand** (per token) | Variable, unpredictable workloads; development and testing |
| **Provisioned Throughput** | Sustained, predictable production workloads; guaranteed capacity |
| **Batch** (up to 50% discount) | Non-real-time processing; bulk document analysis |
| **Cross-Region Inference** | Need lower latency or higher availability across regions |

### Cost Reduction Strategies

- MUST right-size the model — use the smallest model meeting quality requirements
- SHOULD implement prompt caching for repeated prefixes (system prompts, few-shot examples)
- SHOULD use batch processing for non-real-time workloads (up to 50% cost savings)
- SHOULD implement intelligent routing by query complexity (simple queries → smaller model)
- SHOULD set agent stopping conditions to prevent runaway loops
- SHOULD optimize prompt length — shorter prompts with same quality reduce per-request cost

---

## Security

### Rules

- MUST enforce least privilege IAM policies for all FM endpoint access
- MUST use AWS PrivateLink for private VPC-to-Bedrock connections in production
- MUST use customer-managed KMS keys for encryption of model inputs/outputs and fine-tuning data
- MUST enable CloudTrail logging for all Bedrock API calls
- SHOULD implement defense-in-depth: IAM → VPC → WAF → Guardrails → input validation → output encoding
- SHOULD use Bedrock AgentCore with Cedar policy language to enforce boundaries on agent tool calls

**Key guarantee:** Amazon Bedrock does not allow model providers to learn from customer data or prompts.

---

## Checklist

When designing or reviewing a GenAI workload on AWS:

- [ ] Business problem is clearly defined; GenAI is confirmed as the right approach
- [ ] Model selection is based on benchmarks, not assumptions; smallest effective model chosen
- [ ] Prompt engineering is exhausted before adding RAG; RAG before fine-tuning
- [ ] Centralized prompt catalog exists with version control
- [ ] Prompt injection defenses are implemented (Guardrails + input validation + defense-in-depth)
- [ ] RAG pipeline uses appropriate chunking and includes contextual grounding checks
- [ ] Bedrock Guardrails are configured: content filters, PII detection, and denied topics at minimum
- [ ] Cost optimization applied: model right-sizing, caching, batching where applicable
- [ ] IAM least privilege, PrivateLink, KMS encryption, and CloudTrail are configured
- [ ] Responsible AI dimensions are addressed: safety, fairness, transparency, governance
- [ ] Monitoring covers: latency, cost per request, quality metrics, guardrail triggers, error rates

## Key References

| Book / Resource | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *AWS Well-Architected Generative AI Lens* (official) | AWS | AWS Docs | 2025 |
| *AI Engineering* | Chip Huyen | O'Reilly | 2025 |
| *Generative AI on AWS* | Fregly, Barth, Eigenbrode | O'Reilly | 2023 |
| *Hands-On Large Language Models* | Jay Alammar, Maarten Grootendorst | O'Reilly | 2024 |
| *Build a Large Language Model (From Scratch)* | Sebastian Raschka | Manning | 2024 |
| *Designing Machine Learning Systems* | Chip Huyen | O'Reilly | 2022 |
