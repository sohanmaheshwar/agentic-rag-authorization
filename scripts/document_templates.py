"""Document templates and variations for generating realistic demo documents."""

import random

TEMPLATES = {
    "engineering": {
        "architecture": """Title: {title}
Department: engineering
Classification: {classification}
Type: Technical Architecture

Summary:
This document describes the {component} architecture for our {system}.

Architecture Overview:
{overview}

Microservices Patterns Used:
{patterns}

Key Components:
{components}

Technical Specifications:
{specifications}

Implementation Guidelines:
{guidelines}

Related Documents: {related}
""",
        "guide": """Title: {title}
Department: engineering
Classification: {classification}
Type: Development Guide

Introduction:
This guide covers {topic} for engineering teams.

Best Practices:
{best_practices}

Common Patterns:
{patterns}

Examples:
{examples}

Troubleshooting:
{troubleshooting}

Related Documents: {related}
""",
        "memo": """Title: {title}
Department: engineering
Classification: {classification}
Type: Engineering Memo

Date: {date}
From: Engineering Leadership

Subject: {subject}

Context:
{context}

Key Points:
{key_points}

Action Items:
{action_items}

Timeline: {timeline}
""",
        "spec": """Title: {title}
Department: engineering
Classification: {classification}
Type: Technical Specification

Version: {version}
Status: {status}

Overview:
{overview}

Requirements:
{requirements}

Design:
{design}

Implementation Notes:
{implementation}

Testing Strategy: {testing}
""",
    },
    "sales": {
        "proposal": """Title: {title}
Department: sales
Classification: {classification}
Type: Sales Proposal

Client: {client}
Opportunity: {opportunity}

Executive Summary:
{executive_summary}

Proposed Solution:
{solution}

Pricing:
{pricing}

Timeline:
{timeline}

Next Steps: {next_steps}
""",
        "guide": """Title: {title}
Department: sales
Classification: {classification}
Type: Sales Guide

Product: {product}

Key Features:
{features}

Target Market:
{market}

Competitive Advantages:
{advantages}

Common Objections & Responses:
{objections}

Resources: {resources}
""",
        "playbook": """Title: {title}
Department: sales
Classification: {classification}
Type: Sales Playbook

Target Segment: {segment}

Discovery Questions:
{discovery}

Qualification Criteria:
{qualification}

Demo Flow:
{demo_flow}

Closing Strategies:
{closing}

Success Metrics: {metrics}
""",
        "report": """Title: {title}
Department: sales
Classification: {classification}
Type: Sales Report

Period: {period}
Region: {region}

Performance Summary:
{summary}

Key Wins:
{wins}

Pipeline Analysis:
{pipeline}

Recommendations: {recommendations}
""",
    },
    "hr": {
        "policy": """Title: {title}
Department: hr
Classification: {classification}
Type: HR Policy

Policy Number: {policy_number}
Effective Date: {effective_date}

Purpose:
{purpose}

Scope:
{scope}

Policy Statement:
{policy_statement}

Procedures:
{procedures}

Violations: {violations}
""",
        "guide": """Title: {title}
Department: hr
Classification: {classification}
Type: Employee Guide

Topic: {topic}

Overview:
{overview}

Employee Responsibilities:
{responsibilities}

Resources:
{resources}

Contact Information: {contact}
""",
        "handbook": """Title: {title}
Department: hr
Classification: {classification}
Type: HR Handbook

Section: {section}

Introduction:
{intro}

Policies:
{policies}

Procedures:
{procedures}

Resources: {resources}
""",
        "memo": """Title: {title}
Department: hr
Classification: {classification}
Type: HR Memo

Date: {date}
To: All Employees

Subject: {subject}

Announcement:
{announcement}

Details:
{details}

Action Required: {action}
""",
    },
    "finance": {
        "report": """Title: {title}
Department: finance
Classification: {classification}
Type: Financial Report

Period: {period}
Report Type: {report_type}

Summary:
{summary}

Key Metrics:
{metrics}

Analysis:
{analysis}

Recommendations:
{recommendations}

Approved By: {approver}
""",
        "policy": """Title: {title}
Department: finance
Classification: {classification}
Type: Finance Policy

Policy: {policy_name}

Objective:
{objective}

Guidelines:
{guidelines}

Approval Requirements:
{approval}

Compliance: {compliance}
""",
        "analysis": """Title: {title}
Department: finance
Classification: {classification}
Type: Financial Analysis

Subject: {subject}
Date: {date}

Executive Summary:
{executive_summary}

Detailed Analysis:
{analysis}

Risk Assessment:
{risk}

Recommendations: {recommendations}
""",
        "memo": """Title: {title}
Department: finance
Classification: {classification}
Type: Finance Memo

Date: {date}
From: Finance Department

Subject: {subject}

Background:
{background}

Financial Impact:
{impact}

Next Steps: {next_steps}
""",
    },
    "public": {
        "handbook": """Title: {title}
Department: public
Classification: public
Type: Company Handbook

Section: {section}

Introduction:
{intro}

Content:
{content}

Key Points:
{key_points}

Additional Resources: {resources}
""",
        "policy": """Title: {title}
Department: public
Classification: public
Type: Company Policy

Policy: {policy_name}

Overview:
{overview}

Guidelines:
{guidelines}

Contact: {contact}
""",
    },
}

VARIATIONS = {
    "engineering": {
        "components": [
            "Authentication Service",
            "Payment Gateway",
            "Notification System",
            "Data Pipeline",
            "API Gateway",
            "Message Queue",
            "Cache Layer",
            "Search Engine",
        ],
        "systems": [
            "platform",
            "product ecosystem",
            "infrastructure",
            "microservices architecture",
            "data processing system",
        ],
        "topics": [
            "Code Review Process",
            "API Design Guidelines",
            "Security Best Practices",
            "Testing Strategies",
            "Deployment Procedures",
            "Monitoring and Alerting",
            "Database Optimization",
        ],
        "overviews": [
            "Our system follows a microservices architecture with clear service boundaries and well-defined interfaces.",
            "This architecture emphasizes scalability, reliability, and maintainability through modular design.",
            "The system is designed for high availability and fault tolerance with redundancy at multiple levels.",
        ],
        "microservices_patterns": [
            "- API Gateway Pattern: Centralized entry point for all client requests\n- Service Discovery: Dynamic service registration and lookup using Consul\n- Circuit Breaker: Prevents cascade failures using Hystrix pattern\n- Database per Service: Each microservice owns its data store",
            "- Saga Pattern: Distributed transactions across multiple services\n- Event Sourcing: All changes captured as immutable events\n- CQRS: Separate read and write models for optimal performance\n- Sidecar Pattern: Service mesh using Istio for cross-cutting concerns",
            "- Backend for Frontend (BFF): Specialized backends for web and mobile clients\n- Strangler Fig: Gradual migration from monolith to microservices\n- Anti-Corruption Layer: Protects new services from legacy system complexity\n- Bulkhead Pattern: Isolates resources to prevent total system failure",
            "- API Composition: Aggregates data from multiple services\n- Retry Pattern: Automatic retry with exponential backoff\n- Timeout Pattern: Prevents indefinite waiting for responses\n- Health Check API: Each service exposes health endpoints for monitoring",
        ],
    },
    "sales": {
        "clients": [
            "Acme Corp",
            "TechStart Inc",
            "Global Solutions",
            "Enterprise Systems LLC",
            "Innovation Partners",
            "Digital Ventures",
        ],
        "products": [
            "Enterprise Platform",
            "Analytics Suite",
            "Integration Hub",
            "Security Framework",
            "Developer Tools",
        ],
        "opportunities": [
            "$500K Annual Contract",
            "$1.2M Enterprise Deal",
            "$250K Pilot Program",
            "$800K Multi-Year Agreement",
        ],
    },
    "hr": {
        "topics": [
            "Performance Reviews",
            "Professional Development",
            "Benefits Enrollment",
            "Workplace Safety",
            "Diversity and Inclusion",
            "Remote Work Guidelines",
        ],
        "sections": [
            "Employee Conduct",
            "Leave Policies",
            "Compensation and Benefits",
            "Career Development",
            "Workplace Culture",
        ],
    },
    "finance": {
        "periods": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "FY 2024"],
        "report_types": [
            "Quarterly Financial Review",
            "Budget Analysis",
            "Revenue Forecast",
            "Expense Report",
            "Investment Analysis",
        ],
    },
    "public": {
        "sections": [
            "Company Mission and Values",
            "Code of Conduct",
            "Communication Guidelines",
            "Office Policies",
            "Getting Started",
        ],
    },
    "common": {
        "classifications": ["internal", "confidential"],
        "dates": ["2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05"],
        "generic_content": [
            "This section provides detailed information and guidelines.",
            "Please review carefully and contact the relevant department with questions.",
            "Regular updates will be communicated through standard channels.",
        ],
    },
}


def get_variation(dept, key, default_list=None):
    """Get a random variation for a department and key."""
    if dept in VARIATIONS and key in VARIATIONS[dept]:
        return random.choice(VARIATIONS[dept][key])
    elif "common" in VARIATIONS and key in VARIATIONS["common"]:
        return random.choice(VARIATIONS["common"][key])
    elif default_list:
        return random.choice(default_list)
    return f"[{key}]"
