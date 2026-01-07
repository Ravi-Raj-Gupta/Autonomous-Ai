
PROJECT CONTEXT DOCUMENT
Project: An Agentic Operations Manager for MSMEs (AUTONOMOS)

This document captures the complete working context of the project idea discussed so far, rewritten in clear, natural, human language so it does not appear machine-generated. The structure and idea flow are preserved to ensure continuity.

1. Project Overview

AUTONOMOS is an intelligent operations manager designed specifically for small and medium-sized businesses. These businesses usually rely on manual coordination across inventory, procurement, vendors, invoicing, and workforce planning. As a result, owners spend most of their time reacting to daily operational issues instead of focusing on growth.

The goal of AUTONOMOS is to reduce this burden by acting as a decision-making layer that quietly manages routine operations and involves humans only when judgment or approval is genuinely required.

2. Core Problem Statement

Most MSMEs operate with disconnected tools and manual processes. Inventory data sits in spreadsheets, vendor communication happens over calls or emails, and staffing decisions are made on the fly. This fragmentation causes frequent errors, delays, stock shortages, and unnecessary stress for owners and managers.

Existing automation tools mostly execute predefined workflows. They do not understand context, do not adapt, and do not take responsibility for decisions.

3. What Makes AUTONOMOS Different

AUTONOMOS is not a dashboard or a reporting tool. It behaves more like a junior operations manager.

It continuously watches signals such as sales trends, inventory movement, vendor delays, and staff availability. Based on these signals, it independently takes actions like reordering stock, adjusting delivery timelines, communicating with vendors, and rebalancing internal tasks or shifts.

Human involvement is required only when a decision has financial, legal, or strategic risk.

4. Expected Impact

Business owners spend less time on daily firefighting and experience fewer operational mistakes. Businesses benefit from reduced stockouts, faster responses, and improved productivity without increasing headcount.

5. Feasibility and Prototype Scope

The project is feasible in a hackathon setting. The prototype can focus on inventory management and vendor communication using simulated data such as sales records and invoices.

6. Human-Effort Reduction Features

Daily summaries, plain-language commands, silent issue handling, one-click approvals, self-learning procedures, automated vendor communication, error detection, transparency features, gradual autonomy, and monthly effort reports together minimize human workload.

7. Scalability Vision

AUTONOMOS can expand into industry-specific versions and integrate with accounting and ERP systems using a modular SaaS model.

8. Positioning Statement

AUTONOMOS takes over routine operational thinking while keeping business owners in control of intent.


System architecture

                ┌───────────────────────────────┐
                │         User interface         │
                │  FastAPI + Jinja2 Dashboard    │
                │  (Approvals & Decisions UI)    │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │           API layer            │
                │  /ingest, /cycle, /decisions   │
                │  FastAPI routes + services     │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │       CrewAI orchestration     │
                │  Agents: Observer, Reasoner,   │
                │  PO Agent, Vendor Agent,       │
                │  Supervisor                    │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │       Intelligence layer       │
                │  Policies (inventory rules)    │
                │  LLM stub (rationale only)     │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │           Data layer           │
                │  SQLite/Postgres + SQLAlchemy  │
                │  Tables: Inventory, Sales,     │
                │  Vendors, POs, Decisions       │
                └───────────────┬───────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │         Communication          │
                │  Gmail SMTP (App Password)     │
                │  Vendor emails & PO notices    │
                └───────────────────────────────┘

