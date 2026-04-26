from pathlib import Path
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).parent.parent
COMMANDS_DIR = BASE_DIR / ".claude" / "commands"
AGENTS_DIR = BASE_DIR / "agents"

mcp = FastMCP("devops-ai-toolkit")


def _prompt(subpath: str, **kwargs) -> str:
    content = (COMMANDS_DIR / subpath).read_text(encoding="utf-8")
    inputs = {k.replace("_", " "): v for k, v in kwargs.items() if v}
    if inputs:
        content += "\n\n---\n" + "\n".join(f"**{k}:** {v}" for k, v in inputs.items())
    return content


def _resource(name: str) -> str:
    return (AGENTS_DIR / f"{name}.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# App development
# ---------------------------------------------------------------------------

@mcp.prompt()
def api_design(mode: str = "", service: str = "", consumers: str = "",
               auth: str = "", constraints: str = "") -> str:
    """Design or review a REST / GraphQL API."""
    return _prompt("app-dev/api-design.md", mode=mode, service=service,
                   consumers=consumers, auth=auth, constraints=constraints)


@mcp.prompt()
def implement_story(story: str = "", appetite: str = "", stack: str = "",
                    service: str = "", context: str = "") -> str:
    """Turn a shaped Shape Up story into an implementation plan with code scaffolding."""
    return _prompt("app-dev/implement-story.md", story=story, appetite=appetite,
                   stack=stack, service=service, context=context)


@mcp.prompt()
def pr_review(pr: str = "", focus: str = "", context: str = "") -> str:
    """Full PR review; auto-routes to IAM and Terraform reviewers when .tf files are detected."""
    return _prompt("app-dev/pr-review.md", pr=pr, focus=focus, context=context)


@mcp.prompt()
def schema_review(db: str = "", service: str = "", tenancy: str = "") -> str:
    """Database schema review: normalization, indexes, multi-tenancy isolation."""
    return _prompt("app-dev/schema-review.md", db=db, service=service, tenancy=tenancy)


# ---------------------------------------------------------------------------
# CI/CD
# ---------------------------------------------------------------------------

@mcp.prompt()
def debug_pipeline(run: str = "", repo: str = "", context: str = "") -> str:
    """Diagnose a failed GitHub Actions run and deliver a concrete fix."""
    return _prompt("cicd/debug-pipeline.md", run=run, repo=repo, context=context)


@mcp.prompt()
def generate_workflow(service: str = "", trigger: str = "", steps: str = "",
                      environments: str = "", aws_role: str = "", context: str = "") -> str:
    """Generate a production-ready GitHub Actions workflow with OIDC auth and pinned SHAs."""
    return _prompt("cicd/generate-workflow.md", service=service, trigger=trigger,
                   steps=steps, environments=environments, aws_role=aws_role, context=context)


@mcp.prompt()
def review_workflow(file: str = "", context: str = "") -> str:
    """Security and best-practices audit of a GitHub Actions workflow file."""
    return _prompt("cicd/review-workflow.md", file=file, context=context)


# ---------------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------------

@mcp.prompt()
def incident_triage(service: str = "", cluster: str = "", alert: str = "",
                    impact: str = "", logs: str = "", last_change: str = "") -> str:
    """Structured triage → RCA → remediation. Invokes the incident-responder agent."""
    return _prompt("incidents/triage.md", service=service, cluster=cluster,
                   alert=alert, impact=impact, logs=logs, last_change=last_change)


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

@mcp.prompt()
def dockerfile_review(path: str = "", service: str = "", context: str = "") -> str:
    """Dockerfile security and layer-efficiency review using Trivy."""
    return _prompt("infra/dockerfile-review.md", path=path, service=service, context=context)


@mcp.prompt()
def ecs_debug(service: str = "", cluster: str = "", error: str = "",
              logs: str = "", context: str = "") -> str:
    """Diagnose a failed or stuck ECS / ArgoCD deployment. Invokes the deploy-debugger agent."""
    return _prompt("infra/ecs-debug.md", service=service, cluster=cluster,
                   error=error, logs=logs, context=context)


@mcp.prompt()
def ecs_task_def(mode: str = "", service: str = "", image: str = "",
                 port: str = "", cpu: str = "", memory: str = "",
                 secrets: str = "", env_vars: str = "", context: str = "") -> str:
    """Generate or review an ECS Fargate task definition with proper role separation."""
    return _prompt("infra/ecs-task-def.md", mode=mode, service=service, image=image,
                   port=port, cpu=cpu, memory=memory, secrets=secrets,
                   env_vars=env_vars, context=context)


@mcp.prompt()
def iam_audit(target: str = "", context: str = "") -> str:
    """Least-privilege IAM audit of roles, policies, and trust relationships."""
    return _prompt("infra/iam-audit.md", target=target, context=context)


@mcp.prompt()
def terraform_review(path: str = "", pr: str = "", context: str = "") -> str:
    """Multi-pass Terraform review: security, cost flags, drift risk, module hygiene."""
    return _prompt("infra/terraform-review.md", path=path, pr=pr, context=context)


@mcp.prompt()
def terraform_security(path: str = "", context: str = "") -> str:
    """Security scan for Terraform using Trivy: misconfigurations, IAM wildcards, public exposure."""
    return _prompt("infra/terraform-security.md", path=path, context=context)


# ---------------------------------------------------------------------------
# Observability
# ---------------------------------------------------------------------------

@mcp.prompt()
def generate_alerts(service: str = "", slos: str = "", metrics: str = "",
                    dashboard: str = "", context: str = "") -> str:
    """Generate Grafana alert rules from SLOs or a service description."""
    return _prompt("observability/generate-alerts.md", service=service, slos=slos,
                   metrics=metrics, dashboard=dashboard, context=context)


@mcp.prompt()
def write_runbook(service: str = "", alert: str = "", severity: str = "",
                  context: str = "", template: str = "") -> str:
    """Generate a structured, actionable runbook for alert response or incident handling."""
    return _prompt("observability/write-runbook.md", service=service, alert=alert,
                   severity=severity, context=context, template=template)


# ---------------------------------------------------------------------------
# Shape Up
# ---------------------------------------------------------------------------

@mcp.prompt()
def scope_hammer(appetite: str = "", pitch: str = "", status: str = "",
                 days_remaining: str = "") -> str:
    """Identify scope to cut so work ships on time without slipping the cycle."""
    return _prompt("shape-up/scope-hammer.md", appetite=appetite, pitch=pitch,
                   status=status, days_remaining=days_remaining)


@mcp.prompt()
def shape_work(idea: str = "", appetite: str = "", context: str = "") -> str:
    """Turn a raw idea into a fully shaped pitch ready for the betting table."""
    return _prompt("shape-up/shape-work.md", idea=idea, appetite=appetite, context=context)


@mcp.prompt()
def write_pitch(problem: str = "", appetite: str = "", notes: str = "") -> str:
    """Turn a problem statement into a full Shape Up pitch with rabbit holes and no-gos."""
    return _prompt("shape-up/write-pitch.md", problem=problem, appetite=appetite, notes=notes)


# ---------------------------------------------------------------------------
# Agent resources
# ---------------------------------------------------------------------------

@mcp.resource("resource://agents/iam-reviewer")
def iam_reviewer() -> str:
    """IAM least-privilege auditor agent definition."""
    return _resource("iam-reviewer")


@mcp.resource("resource://agents/terraform-reviewer")
def terraform_reviewer() -> str:
    """Multi-pass Terraform reviewer agent definition."""
    return _resource("terraform-reviewer")


@mcp.resource("resource://agents/pr-reviewer")
def pr_reviewer() -> str:
    """PR reviewer orchestrator agent definition."""
    return _resource("pr-reviewer")


@mcp.resource("resource://agents/incident-responder")
def incident_responder() -> str:
    """Incident triage and RCA agent definition."""
    return _resource("incident-responder")


@mcp.resource("resource://agents/deploy-debugger")
def deploy_debugger() -> str:
    """ECS / ArgoCD deployment failure debugger agent definition."""
    return _resource("deploy-debugger")


if __name__ == "__main__":
    mcp.run()
