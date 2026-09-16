# Dr. Forex Engine

**Quantitative Research & Controlled Execution Engine**

Dr. Forex Engine is a Python-based system for systematic strategy research, validation, and controlled live trading.

It is designed around a strict progression:

**Research → Demo Validation → Human Approval → Live Permission**

Live trading is never automatic. A strategy only receives live trading authority after it has been researched, tested, evaluated on demo accounts, and explicitly approved.

---

## Core Purpose

The engine is built to:

- Perform deep market research and feature analysis
- Discover and formulate trading strategies
- Conduct rigorous historical testing with realistic assumptions
- Evaluate robustness and resistance to overfitting
- Run controlled forward tests on demo accounts
- Track strategy performance and behaviour over time
- Allow human review and vetting of results
- Store approved strategies
- Grant or revoke live trading permission under explicit control

---

## Operating Principles

- Evidence must precede belief
- Validation must precede live authority
- Research and live execution remain separate layers
- No strategy trades live without explicit approval
- Approval is conditional and can be revoked
- Continuous monitoring and re-evaluation are required

A profitable backtest or demo result is not sufficient on its own for live trading permission.

---

## Intended Workflow

1. Research & Strategy Discovery  
2. Historical simulation and robustness testing  
3. Demo account forward evaluation  
4. Human review of performance, risk behaviour, and stability  
5. Explicit approval and permission granted  
6. Controlled live trading (with monitoring and kill switches)  
7. Ongoing performance tracking and possible revocation

---

## Project Status

Early development.

Current focus is on building a solid research and validation foundation before any live execution capabilities are added.
