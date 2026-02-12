"""Generate 50 realistic documents for the agentic RAG demo."""

import os
import random
from document_templates import TEMPLATES, VARIATIONS, get_variation

DOCUMENT_COUNTS = {
    "engineering": {"total": 15, "categories": {"architecture": 5, "guide": 5, "memo": 3, "spec": 2}},
    "sales": {"total": 10, "categories": {"proposal": 4, "guide": 3, "playbook": 2, "report": 1}},
    "hr": {"total": 10, "categories": {"policy": 4, "guide": 3, "handbook": 2, "memo": 1}},
    "finance": {"total": 10, "categories": {"report": 4, "policy": 3, "analysis": 2, "memo": 1}},
    "public": {"total": 5, "categories": {"handbook": 3, "policy": 2}},
}


def generate_engineering_doc(category, number):
    """Generate an engineering document."""
    variations = {}

    if category == "architecture":
        variations = {
            "title": f"{get_variation('engineering', 'components')} Architecture",
            "classification": get_variation("common", "classifications"),
            "component": get_variation("engineering", 'components'),
            "system": get_variation("engineering", "systems"),
            "overview": get_variation("engineering", "overviews"),
            "patterns": get_variation("engineering", "microservices_patterns"),
            "components": "- Service Layer: RESTful APIs with OpenAPI specification\n- Data Layer: Event-driven data synchronization\n- API Layer: GraphQL and REST endpoints\n- Integration Layer: Message broker using RabbitMQ",
            "specifications": "Language: Python 3.11, Java 17\nFramework: FastAPI, Spring Boot\nDatabase: PostgreSQL, MongoDB\nCache: Redis with clustering\nMessage Queue: RabbitMQ\nService Mesh: Istio",
            "guidelines": "- Follow 12-factor app methodology\n- Implement comprehensive observability (metrics, logs, traces)\n- Use semantic versioning for APIs\n- Enforce contract testing between services\n- Apply defense in depth for security",
            "related": "eng-guide-001, eng-spec-001",
        }
    elif category == "guide":
        topic = get_variation("engineering", "topics")
        variations = {
            "title": f"{topic} Guide",
            "classification": "internal",
            "topic": topic,
            "best_practices": "- Write clear, documented code\n- Use version control effectively\n- Implement comprehensive tests",
            "patterns": "- Repository pattern\n- Factory pattern\n- Observer pattern",
            "examples": "See code samples in the engineering repository",
            "troubleshooting": "Check logs in /var/log/application\nVerify configuration settings\nReview recent deployments",
            "related": "eng-architecture-001",
        }
    elif category == "memo":
        variations = {
            "title": f"Engineering Update - {number:03d}",
            "classification": "internal",
            "date": get_variation("common", "dates"),
            "subject": "Important technical updates and decisions",
            "context": "Recent architecture review and technical planning sessions",
            "key_points": "- New API standards adopted\n- Migration to microservices\n- Performance improvements prioritized",
            "action_items": "- Review new standards\n- Plan service decomposition\n- Benchmark current performance",
            "timeline": "Q2 2024",
        }
    else:  # spec
        variations = {
            "title": f"{get_variation('engineering', 'components')} Specification",
            "classification": "internal",
            "version": "1.0",
            "status": "Draft",
            "overview": "Technical specification for new service component",
            "requirements": "- High availability\n- Low latency\n- Scalability\n- Security",
            "design": "RESTful API design with JSON payloads\nStateless service architecture",
            "implementation": "Use existing frameworks and libraries\nFollow team coding standards",
            "testing": "Unit tests, integration tests, and load tests required",
        }

    return TEMPLATES["engineering"][category].format(**variations)


def generate_sales_doc(category, number):
    """Generate a sales document."""
    variations = {}

    if category == "proposal":
        variations = {
            "title": f"Sales Proposal - {get_variation('sales', 'clients')}",
            "classification": "confidential",
            "client": get_variation("sales", "clients"),
            "opportunity": get_variation("sales", "opportunities"),
            "executive_summary": "We propose a comprehensive solution to address your business needs and drive growth.",
            "solution": f"{get_variation('sales', 'products')} tailored to your requirements",
            "pricing": "Custom pricing based on usage and scale\nVolume discounts available",
            "timeline": "30-day implementation with ongoing support",
            "next_steps": "Schedule technical review\nCustomize proposal\nFinalize contract",
        }
    elif category == "guide":
        product = get_variation("sales", "products")
        variations = {
            "title": f"{product} Sales Guide",
            "classification": "internal",
            "product": product,
            "features": "- Enterprise-grade security\n- Scalable architecture\n- 24/7 support\n- Custom integrations",
            "market": "Enterprise customers with complex integration needs",
            "advantages": "- Market-leading features\n- Proven track record\n- Superior support",
            "objections": "Price: Emphasize ROI and TCO\nComplexity: Highlight managed services\nSecurity: Share compliance certifications",
            "resources": "Product demos, case studies, ROI calculator",
        }
    elif category == "playbook":
        variations = {
            "title": f"Sales Playbook - {number:03d}",
            "classification": "internal",
            "segment": "Enterprise",
            "discovery": "- What are your current pain points?\n- What solutions have you tried?\n- What are your goals?",
            "qualification": "- Budget confirmed\n- Timeline defined\n- Decision makers identified",
            "demo_flow": "1. Understand needs\n2. Show relevant features\n3. Address concerns\n4. Propose next steps",
            "closing": "Trial close throughout\nSummarize value\nAddress final objections",
            "metrics": "Close rate, deal size, sales cycle length",
        }
    else:  # report
        variations = {
            "title": f"Sales Report - {get_variation('finance', 'periods')}",
            "classification": "internal",
            "period": get_variation("finance", "periods"),
            "region": "North America",
            "summary": "Strong quarter with several major deals closed and healthy pipeline",
            "wins": f"- {get_variation('sales', 'clients')}: $500K\n- Major enterprise deal: $1.2M",
            "pipeline": "Qualified opportunities totaling $5M\nForecast confidence: High",
            "recommendations": "Invest in enterprise sales team\nExpand partner channel",
        }

    return TEMPLATES["sales"][category].format(**variations)


def generate_hr_doc(category, number):
    """Generate an HR document."""
    variations = {}

    if category == "policy":
        variations = {
            "title": f"HR Policy - {number:03d}",
            "classification": "internal",
            "policy_number": f"HR-{number:03d}",
            "effective_date": get_variation("common", "dates"),
            "purpose": "To establish clear guidelines and ensure consistent practices",
            "scope": "This policy applies to all employees",
            "policy_statement": "The company is committed to maintaining a professional and inclusive workplace",
            "procedures": "1. Review policy\n2. Acknowledge understanding\n3. Follow guidelines\n4. Report violations",
            "violations": "Violations may result in disciplinary action up to and including termination",
        }
    elif category == "guide":
        topic = get_variation("hr", "topics")
        variations = {
            "title": f"{topic} Employee Guide",
            "classification": "internal",
            "topic": topic,
            "overview": "This guide provides information to help you navigate company processes",
            "responsibilities": "- Follow company policies\n- Complete required training\n- Communicate with manager",
            "resources": "HR portal, manager, employee handbook",
            "contact": "hr@company.com",
        }
    elif category == "handbook":
        section = get_variation("hr", "sections")
        variations = {
            "title": f"Employee Handbook - {section}",
            "classification": "internal",
            "section": section,
            "intro": "This section outlines important policies and expectations",
            "policies": "Detailed policies and procedures for this area",
            "procedures": "Step-by-step guidance for common scenarios",
            "resources": "Additional resources and contacts",
        }
    else:  # memo
        variations = {
            "title": f"HR Announcement - {number:03d}",
            "classification": "internal",
            "date": get_variation("common", "dates"),
            "subject": "Important HR update",
            "announcement": "We are pleased to announce updates to company policies and benefits",
            "details": "Changes take effect next quarter\nNew benefits include expanded coverage",
            "action": "Review changes and contact HR with questions",
        }

    return TEMPLATES["hr"][category].format(**variations)


def generate_finance_doc(category, number):
    """Generate a finance document."""
    variations = {}

    if category == "report":
        variations = {
            "title": f"{get_variation('finance', 'report_types')}",
            "classification": "confidential",
            "period": get_variation("finance", "periods"),
            "report_type": get_variation("finance", "report_types"),
            "summary": "Financial performance remains strong with revenue growth and controlled expenses",
            "metrics": "Revenue: $10M (+15% YoY)\nExpenses: $7M\nProfit Margin: 30%",
            "analysis": "Strong revenue growth driven by enterprise sales\nOperating expenses well-managed",
            "recommendations": "Continue investing in growth\nMonitor expense ratios\nExpand into new markets",
            "approver": "CFO",
        }
    elif category == "policy":
        variations = {
            "title": f"Finance Policy - {number:03d}",
            "classification": "internal",
            "policy_name": f"Financial Control Policy {number:03d}",
            "objective": "Ensure proper financial controls and compliance",
            "guidelines": "- Follow approval hierarchies\n- Maintain documentation\n- Regular audits\n- Expense limits",
            "approval": "Manager approval: Up to $5K\nDirector approval: Up to $50K\nCFO approval: Above $50K",
            "compliance": "SOX compliance required\nRegular internal audits",
        }
    elif category == "analysis":
        variations = {
            "title": f"Financial Analysis - {number:03d}",
            "classification": "confidential",
            "subject": "Market and financial trends",
            "date": get_variation("common", "dates"),
            "executive_summary": "Analysis shows positive trends with manageable risks",
            "analysis": "Detailed breakdown of financial metrics and trends\nComparison to industry benchmarks",
            "risk": "Market volatility: Medium\nCurrency risk: Low\nCredit risk: Low",
            "recommendations": "Maintain current strategy\nHedge currency exposure\nDiversify revenue streams",
        }
    else:  # memo
        variations = {
            "title": f"Finance Update - {number:03d}",
            "classification": "internal",
            "date": get_variation("common", "dates"),
            "subject": "Financial planning update",
            "background": "Budget review and planning cycle",
            "impact": "Adjustments to departmental budgets\nRevised forecasts",
            "next_steps": "Department reviews\nFinal approval by month end",
        }

    return TEMPLATES["finance"][category].format(**variations)


def generate_public_doc(category, number):
    """Generate a public document."""
    variations = {}

    if category == "handbook":
        section = get_variation("public", "sections")
        variations = {
            "title": f"Company Handbook - {section}",
            "section": section,
            "intro": "Welcome! This handbook helps you understand our company culture and practices",
            "content": "Detailed information about company values, expectations, and resources",
            "key_points": "- We value integrity and transparency\n- We support growth and development\n- We foster collaboration",
            "resources": "Company intranet, manager, HR team",
        }
    else:  # policy
        variations = {
            "title": f"Company Policy - {number:03d}",
            "policy_name": f"General Policy {number:03d}",
            "overview": "This policy applies to all employees and outlines expectations",
            "guidelines": "- Treat others with respect\n- Communicate professionally\n- Follow company standards",
            "contact": "For questions, contact your manager or HR",
        }

    return TEMPLATES["public"][category].format(**variations)


def generate_document(dept, category, number):
    """Generate a single document."""
    generators = {
        "engineering": generate_engineering_doc,
        "sales": generate_sales_doc,
        "hr": generate_hr_doc,
        "finance": generate_finance_doc,
        "public": generate_public_doc,
    }

    return generators[dept](category, number)


def main():
    """Generate all 50 documents."""
    output_dir = "data/documents"
    os.makedirs(output_dir, exist_ok=True)

    generated = []

    for dept, config in DOCUMENT_COUNTS.items():
        doc_counter = 1
        for category, count in config["categories"].items():
            for _ in range(count):
                doc_id = f"{dept}-{category}-{doc_counter:03d}"
                filename = f"{doc_id}.txt"
                filepath = os.path.join(output_dir, filename)

                content = generate_document(dept, category, doc_counter)

                with open(filepath, 'w') as f:
                    f.write(content)

                generated.append(filename)
                print(f"  ✅ Generated {filename}")

                doc_counter += 1

    print(f"\n🎉 Generated {len(generated)} documents in {output_dir}/")

    # Print summary
    print("\nDocument Distribution:")
    for dept, config in DOCUMENT_COUNTS.items():
        print(f"  {dept}: {config['total']} documents")
        for category, count in config["categories"].items():
            print(f"    - {category}: {count}")


if __name__ == "__main__":
    main()
