# /generate-alerts

Generate Grafana alert rules from SLOs or a service description. Produces ready-to-import alert JSON or YAML and a plain-English explanation of each rule.

## Usage

```
/generate-alerts
Service: <service name>
SLOs:
  - Availability: 99.9% over 30 days
  - P95 latency: < 300ms
  - Error rate: < 0.1%
[Metrics: <Prometheus metric names if known>]
[Dashboard: <Grafana dashboard UID or URL>]
[Context: additional service details, traffic patterns, dependencies]
```

Or describe the service without formal SLOs:

```
/generate-alerts
Service: lease-processor
Context: Processes lease applications — calls RDS, Stripe, and Docusign. Peaks on the 1st and 15th of every month. A failure means tenants can't sign leases.
```

## What Happens

1. Extracts or infers SLO targets from the provided context
2. Maps SLO targets to concrete Prometheus/Grafana alert expressions
3. Assigns severity (`critical` / `warning`) and appropriate `for` durations
4. Outputs alert rules in Grafana-compatible format (JSON for Grafana API, or YAML for Grafana Alerting-as-code)
5. Explains each rule in plain English so on-call engineers know what it means

---

## Alert Categories

Generate rules across these categories. Omit any that are not applicable to the service.

### Availability / Uptime

```promql
# Alert when success rate drops below SLO threshold
(
  sum(rate(http_requests_total{service="<service>", status!~"5.."}[5m]))
  /
  sum(rate(http_requests_total{service="<service>"}[5m]))
) < 0.999
```

| Severity | Condition | For |
|---|---|---|
| `critical` | Success rate < 99% | 2m |
| `warning` | Success rate < 99.9% | 5m |

### Latency

```promql
# P95 latency exceeds threshold
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{service="<service>"}[5m])) by (le)
) > 0.3
```

| Severity | Condition | For |
|---|---|---|
| `critical` | P99 > 1s | 2m |
| `warning` | P95 > 300ms | 5m |

### Error Rate

```promql
# 5xx error rate
sum(rate(http_requests_total{service="<service>", status=~"5.."}[5m]))
/
sum(rate(http_requests_total{service="<service>"}[5m])) > 0.001
```

| Severity | Condition | For |
|---|---|---|
| `critical` | Error rate > 1% | 2m |
| `warning` | Error rate > 0.1% | 5m |

### Saturation

```promql
# ECS task CPU saturation
avg(ecs_task_cpu_utilized{service="<service>"}) > 80

# ECS task memory saturation
avg(ecs_task_memory_utilized{service="<service>"}) > 85
```

| Severity | Condition | For |
|---|---|---|
| `critical` | CPU > 90% or Memory > 90% | 5m |
| `warning` | CPU > 80% or Memory > 85% | 10m |

### Queue Depth / Lag (if applicable)

```promql
# SQS queue depth
aws_sqs_approximate_number_of_messages_visible_average{queue_name="<queue>"} > 1000
```

### Database Health (if RDS-backed)

```promql
# RDS connection count approaching max
aws_rds_database_connections_average{dbidentifier="<db>"} > 80

# RDS CPU
aws_rds_cpuutilization_average{dbidentifier="<db>"} > 80
```

---

## Output Format

### Alert Rule Summary

```
## Alert Rules: <service>

SLO Targets:
- Availability: <X>%
- P95 latency: <Xms>
- Error rate: <X>%

Generated rules:
1. <service>-availability-critical  [CRITICAL] Fires when 5xx rate pushes availability below 99%
2. <service>-availability-warning   [WARNING]  Fires when success rate < 99.9% for 5m
3. <service>-latency-p95-warning    [WARNING]  Fires when P95 > 300ms for 5m
4. <service>-latency-p99-critical   [CRITICAL] Fires when P99 > 1s for 2m
5. <service>-error-rate-critical    [CRITICAL] Fires when error rate > 1% for 2m
6. <service>-cpu-warning            [WARNING]  Fires when avg CPU > 80% for 10m
7. <service>-memory-critical        [CRITICAL] Fires when avg memory > 90% for 5m
```

### Grafana Alert Rule JSON (Alerting API v1)

```json
{
  "name": "<service>-availability-critical",
  "interval": "1m",
  "rules": [
    {
      "grafana_alert": {
        "title": "<service> availability critical",
        "condition": "A",
        "no_data_state": "Alerting",
        "exec_err_state": "Alerting",
        "for": "2m",
        "labels": {
          "severity": "critical",
          "service": "<service>",
          "team": "devops"
        },
        "annotations": {
          "summary": "{{ $labels.service }} availability below 99%",
          "description": "Success rate is {{ humanizePercentage $values.A }}. SLO breach imminent.",
          "runbook_url": "https://wiki.internal/runbooks/<service>"
        }
      }
    }
  ]
}
```

### Grafana Alerting-as-Code YAML

Output a `rules.yaml` file importable via `grafana-cli` or the Grafana Terraform provider (`grafana_rule_group`).

---

## On-Call Guidance per Rule

For each generated rule, include:

- **What it means**: plain English, no jargon
- **First action**: the first thing on-call should do when it fires
- **False positive signals**: conditions that can trigger the alert without a real outage (e.g., deploy rollout, scheduled batch job)
- **Runbook link placeholder**: `https://wiki.internal/runbooks/<service>`

---

## Examples

```
/generate-alerts
Service: payment-api
SLOs:
  - Availability: 99.95% over 30 days
  - P95 latency: < 200ms
  - Error rate: < 0.05%
Metrics: http_requests_total, http_request_duration_seconds
Context: Stripe integration — latency spikes when Stripe is slow. Peaks at end of month billing run.
```

```
/generate-alerts
Service: tenant-sync
Context: Background worker that syncs tenant data to S3. No user-facing SLA but failures cause stale data in reports. Runs every 5 minutes via scheduled ECS task.
```
