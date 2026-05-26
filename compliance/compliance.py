"""
GA4GH Schema Registry API Compliance Suite.

Can be run two ways:
1. Via pytest: tests/test_compliance.py wraps these checks
2. Via CLI: python -m compliance <url>

All check functions take an api_root URL and raise AssertionError on failure.
The runner functions execute checks and return structured results.

CHECK INVENTORY (keep in sync with schema-registry-site/worker/src/checks.ts):
- check_service_info
- check_list_namespaces_structure
- check_namespace_record_fields
- check_pagination_defaults
- check_list_schemas_structure
- check_schema_record_fields
- check_list_versions_structure
- check_schema_version_fields
- check_get_schema_document
- check_latest_alias
- check_filter_schema_name
- check_filter_maintainer
- check_filter_maturity_level
- check_filter_unknown_returns_empty
- check_unknown_namespace_404
- check_unknown_schema_404
- check_unknown_version_404
- check_listed_namespaces_resolvable
- check_listed_schemas_resolvable
- check_listed_versions_resolvable
- check_latest_matches_listed
- check_schema_document_id_consistency
- check_cors_headers
- check_openapi_available
- check_content_type
"""

import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable

import requests

COMPLIANCE_TIMEOUT = 5  # seconds per request
MAX_NAMESPACES = 5
MAX_SCHEMAS_PER_NS = 5
MAX_VERSIONS_PER_SCHEMA = 3


# ============================================================
# Result types
# ============================================================


@dataclass
class CheckResult:
    """Result of a single compliance check."""

    name: str
    passed: bool
    duration_ms: float
    description: str | None = None
    message: str | None = None
    error: str | None = None
    recommended: bool = False


@dataclass
class ComplianceReport:
    """Full compliance report for a server."""

    server_url: str
    timestamp: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    recommended_failed: int = 0
    results: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _timed_check(name: str, func: Callable, *args, recommended: bool = False, **kwargs) -> CheckResult:
    """Run a check function and capture timing and errors."""
    description = (func.__doc__ or "").strip().split("\n")[0] or None
    start = time.monotonic()
    try:
        func(*args, **kwargs)
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            name=name, passed=True, duration_ms=round(elapsed, 2), description=description,
            recommended=recommended,
        )
    except AssertionError as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            name=name,
            passed=False,
            duration_ms=round(elapsed, 2),
            description=description,
            error=str(e),
            recommended=recommended,
        )
    except requests.exceptions.RequestException as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            name=name,
            passed=False,
            duration_ms=round(elapsed, 2),
            description=description,
            error=f"Connection error: {e}",
            recommended=recommended,
        )
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            name=name,
            passed=False,
            duration_ms=round(elapsed, 2),
            description=description,
            error=f"Unexpected error: {e}",
            recommended=recommended,
        )


# ============================================================
# Structure checks -- validate response format
# ============================================================


def check_service_info(api_root):
    """Service-info returns 200 with required GA4GH fields."""
    res = requests.get(f"{api_root}/service-info", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, f"service-info returned HTTP {res.status_code}"
    data = res.json()
    for field_name in ("id", "name", "type", "organization", "version"):
        assert field_name in data, f"service-info missing '{field_name}' field"


def check_list_namespaces_structure(api_root):
    """GET /namespaces returns 200 with results array and pagination object."""
    res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, f"/namespaces returned HTTP {res.status_code}"
    data = res.json()
    assert "results" in data, "/namespaces missing 'results' field"
    assert isinstance(data["results"], list), "/namespaces 'results' should be a list"
    assert "pagination" in data, "/namespaces missing 'pagination' field"
    assert "page" in data["pagination"], "pagination missing 'page'"
    assert "page_size" in data["pagination"], "pagination missing 'page_size'"


def check_namespace_record_fields(api_root):
    """Each namespace record has server, namespace_name matching [a-z0-9-]+, and contact_url."""
    res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    data = res.json()
    for ns in data["results"]:
        assert "server" in ns, f"Namespace record missing 'server': {ns}"
        assert "namespace_name" in ns, f"Namespace record missing 'namespace_name': {ns}"
        assert re.match(r"^[a-z0-9-]+$", ns["namespace_name"]), (
            f"namespace_name '{ns['namespace_name']}' does not match [a-z0-9-]+"
        )
        assert "contact_url" in ns, f"Namespace record missing 'contact_url': {ns}"


def check_pagination_defaults(api_root):
    """Pagination fields have valid types: page >= 0 and page_size > 0."""
    res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    pag = res.json()["pagination"]
    assert isinstance(pag["page"], int), f"pagination.page must be int, got {type(pag['page'])}"
    assert isinstance(pag["page_size"], int), (
        f"pagination.page_size must be int, got {type(pag['page_size'])}"
    )
    assert pag["page"] >= 0, f"pagination.page must be >= 0, got {pag['page']}"
    assert pag["page_size"] > 0, f"pagination.page_size must be > 0, got {pag['page_size']}"


def check_list_schemas_structure(api_root, namespace):
    """GET /schemas/{ns} returns 200 with PagedResponse of SchemaRecords."""
    res = requests.get(f"{api_root}/schemas/{namespace}", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, f"/schemas/{namespace} returned HTTP {res.status_code}"
    data = res.json()
    assert "results" in data, f"/schemas/{namespace} missing 'results'"
    assert isinstance(data["results"], list), f"/schemas/{namespace} 'results' should be a list"
    assert "pagination" in data, f"/schemas/{namespace} missing 'pagination'"
    assert "page" in data["pagination"], "pagination missing 'page'"
    assert "page_size" in data["pagination"], "pagination missing 'page_size'"


def check_schema_record_fields(api_root, namespace):
    """Each schema record has namespace, schema_name [a-z0-9-]+, latest_released_version, maintainers[], maturity_level."""
    res = requests.get(f"{api_root}/schemas/{namespace}", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    for schema in res.json()["results"]:
        assert "namespace" in schema, f"Schema record missing 'namespace': {schema}"
        assert "schema_name" in schema, f"Schema record missing 'schema_name': {schema}"
        assert re.match(r"^[a-z0-9-]+$", schema["schema_name"]), (
            f"schema_name '{schema['schema_name']}' does not match [a-z0-9-]+"
        )
        assert "latest_released_version" in schema, (
            f"Schema record missing 'latest_released_version': {schema}"
        )
        assert "maintainers" in schema, f"Schema record missing 'maintainers': {schema}"
        assert isinstance(schema["maintainers"], list), "maintainers must be a list"
        assert "maturity_level" in schema, f"Schema record missing 'maturity_level': {schema}"
        valid_levels = {"draft", "trial_use", "normative", "deprecated"}
        assert schema["maturity_level"] in valid_levels, (
            f"maturity_level '{schema['maturity_level']}' not in {valid_levels}"
        )


def check_list_versions_structure(api_root, namespace, schema_name):
    """GET /schemas/{ns}/{schema}/versions returns 200 with PagedResponse."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, f"{url} returned HTTP {res.status_code}"
    data = res.json()
    assert "results" in data, f"Versions response missing 'results'"
    assert isinstance(data["results"], list), "versions 'results' should be a list"
    assert "pagination" in data, "Versions response missing 'pagination'"


def check_schema_version_fields(api_root, namespace, schema_name):
    """Each version has schema_name, version, status in {current, deprecated, latest}."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    valid_statuses = {"current", "deprecated", "latest"}
    for ver in res.json()["results"]:
        assert "schema_name" in ver, f"Version record missing 'schema_name': {ver}"
        assert "version" in ver, f"Version record missing 'version': {ver}"
        assert "status" in ver, f"Version record missing 'status': {ver}"
        assert ver["status"] in valid_statuses, (
            f"status '{ver['status']}' not in {valid_statuses}"
        )
        assert "contributors" in ver, f"Version record missing 'contributors': {ver}"
        assert isinstance(ver["contributors"], list), "contributors must be a list"
        assert "tags" in ver, f"Version record missing 'tags': {ver}"
        assert isinstance(ver["tags"], dict), "tags must be an object"


def check_get_schema_document(api_root, namespace, schema_name, version):
    """GET /schemas/{ns}/{schema}/versions/{ver} returns 200 and valid JSON Schema."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions/{version}"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, f"{url} returned HTTP {res.status_code}"
    data = res.json()
    assert isinstance(data, dict), "Schema document must be a JSON object"
    json_schema_keywords = {"$schema", "type", "properties", "$defs", "allOf", "anyOf", "oneOf"}
    has_schema_marker = bool(json_schema_keywords & data.keys())
    assert has_schema_marker, (
        f"Schema document does not look like a JSON Schema (missing $schema, type, properties, $defs, etc.): "
        f"keys={list(data.keys())}"
    )


def check_latest_alias(api_root, namespace, schema_name, latest_released_version):
    """GET /schemas/{ns}/{schema}/versions/latest body equals the latest_released_version document."""
    latest_url = f"{api_root}/schemas/{namespace}/{schema_name}/versions/latest"
    versioned_url = f"{api_root}/schemas/{namespace}/{schema_name}/versions/{latest_released_version}"
    latest_res = requests.get(latest_url, timeout=COMPLIANCE_TIMEOUT)
    assert latest_res.status_code == 200, f"/versions/latest returned HTTP {latest_res.status_code}"
    versioned_res = requests.get(versioned_url, timeout=COMPLIANCE_TIMEOUT)
    assert versioned_res.status_code == 200, (
        f"/versions/{latest_released_version} returned HTTP {versioned_res.status_code}"
    )
    assert latest_res.json() == versioned_res.json(), (
        "/versions/latest response does not match /versions/{latest_released_version}"
    )


# ============================================================
# Query filter checks
# ============================================================


def check_filter_schema_name(api_root, namespace, schema_name):
    """?schema_name=<known> returns exactly that schema in results."""
    res = requests.get(
        f"{api_root}/schemas/{namespace}",
        params={"schema_name": schema_name},
        timeout=COMPLIANCE_TIMEOUT,
    )
    assert res.status_code == 200, f"Filter by schema_name returned HTTP {res.status_code}"
    data = res.json()
    names = [s["schema_name"] for s in data["results"]]
    assert schema_name in names, (
        f"schema_name filter '{schema_name}' not in results: {names}"
    )
    for name in names:
        assert name == schema_name, (
            f"Filter returned unexpected schema_name '{name}' when filtering for '{schema_name}'"
        )


def check_filter_maintainer(api_root, namespace, maintainer):
    """?maintainers=<known> includes schemas with that maintainer."""
    res = requests.get(
        f"{api_root}/schemas/{namespace}",
        params={"maintainers": maintainer},
        timeout=COMPLIANCE_TIMEOUT,
    )
    assert res.status_code == 200, f"Filter by maintainers returned HTTP {res.status_code}"
    data = res.json()
    for schema in data["results"]:
        assert maintainer in schema.get("maintainers", []), (
            f"Filter by maintainer '{maintainer}' returned schema without that maintainer: {schema}"
        )


def check_filter_maturity_level(api_root, namespace, level):
    """?maturity_level=<val> returns only schemas with that maturity_level."""
    res = requests.get(
        f"{api_root}/schemas/{namespace}",
        params={"maturity_level": level},
        timeout=COMPLIANCE_TIMEOUT,
    )
    assert res.status_code == 200, f"Filter by maturity_level returned HTTP {res.status_code}"
    for schema in res.json()["results"]:
        assert schema.get("maturity_level") == level, (
            f"Filter by maturity_level='{level}' returned schema with '{schema.get('maturity_level')}'"
        )


def check_filter_unknown_returns_empty(api_root, namespace):
    """?schema_name=__missing__ returns 200 with empty results (not 404)."""
    res = requests.get(
        f"{api_root}/schemas/{namespace}",
        params={"schema_name": "__missing__"},
        timeout=COMPLIANCE_TIMEOUT,
    )
    assert res.status_code == 200, (
        f"Filter with unknown schema_name returned HTTP {res.status_code} (expected 200)"
    )
    data = res.json()
    assert data["results"] == [], (
        f"Filter with unknown schema_name should return empty results, got {data['results']}"
    )


# ============================================================
# Negative checks
# ============================================================


def check_unknown_namespace_404(api_root):
    """GET /schemas/__missing__ returns 404."""
    res = requests.get(f"{api_root}/schemas/__missing__", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 404, (
        f"/schemas/__missing__ returned HTTP {res.status_code} (expected 404)"
    )


def check_unknown_schema_404(api_root, namespace):
    """GET /schemas/{ns}/__missing__/versions returns 404."""
    url = f"{api_root}/schemas/{namespace}/__missing__/versions"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 404, f"{url} returned HTTP {res.status_code} (expected 404)"


def check_unknown_version_404(api_root, namespace, schema_name):
    """GET /schemas/{ns}/{schema}/versions/9999.9.9 returns 404."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions/9999.9.9"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 404, f"{url} returned HTTP {res.status_code} (expected 404)"


# ============================================================
# Content / cross-reference checks
# ============================================================


def check_listed_namespaces_resolvable(api_root):
    """Every namespace_name from /namespaces resolves at /schemas/{ns}."""
    res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    for ns in res.json()["results"][:MAX_NAMESPACES]:
        ns_name = ns["namespace_name"]
        r = requests.get(f"{api_root}/schemas/{ns_name}", timeout=COMPLIANCE_TIMEOUT)
        assert r.status_code == 200, (
            f"Namespace '{ns_name}' from /namespaces does not resolve: HTTP {r.status_code}"
        )


def check_listed_schemas_resolvable(api_root, namespace, schema_name):
    """Schema from /schemas/{ns} resolves at /schemas/{ns}/{schema}/versions."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, (
        f"Schema '{namespace}/{schema_name}' listed but does not resolve: HTTP {res.status_code}"
    )


def check_listed_versions_resolvable(api_root, namespace, schema_name, version):
    """Version from /versions list resolves and parses as JSON."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions/{version}"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200, (
        f"Version '{namespace}/{schema_name}/{version}' listed but returned HTTP {res.status_code}"
    )
    data = res.json()
    assert isinstance(data, dict), "Schema document must be a JSON object"


def check_latest_matches_listed(api_root, namespace, schema_name):
    """latest_released_version appears in the versions list."""
    schemas_res = requests.get(f"{api_root}/schemas/{namespace}", timeout=COMPLIANCE_TIMEOUT)
    assert schemas_res.status_code == 200
    schema = next(
        (s for s in schemas_res.json()["results"] if s["schema_name"] == schema_name), None
    )
    assert schema is not None, f"Schema '{schema_name}' not found in namespace '{namespace}'"
    latest = schema["latest_released_version"]
    versions_res = requests.get(
        f"{api_root}/schemas/{namespace}/{schema_name}/versions", timeout=COMPLIANCE_TIMEOUT
    )
    assert versions_res.status_code == 200
    version_ids = [v["version"] for v in versions_res.json()["results"]]
    assert latest in version_ids, (
        f"latest_released_version '{latest}' not found in versions list: {version_ids}"
    )


def check_schema_document_id_consistency(api_root, namespace, schema_name, version):
    """$id field (if present) is consistent with the schema_name."""
    url = f"{api_root}/schemas/{namespace}/{schema_name}/versions/{version}"
    res = requests.get(url, timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    data = res.json()
    if "$id" in data:
        assert schema_name in data["$id"], (
            f"$id '{data['$id']}' does not contain schema_name '{schema_name}'"
        )


# ============================================================
# RECOMMENDED checks
# ============================================================


def check_cors_headers(api_root):
    """CORS header Access-Control-Allow-Origin: * present on /namespaces (RECOMMENDED)."""
    res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    cors = res.headers.get("Access-Control-Allow-Origin", "")
    assert cors == "*", (
        f"Expected Access-Control-Allow-Origin: *, got '{cors}'"
    )


def check_openapi_available(api_root):
    """OpenAPI spec is accessible at /openapi.json or /openapi.yaml (RECOMMENDED)."""
    for path in ("/openapi.json", "/openapi.yaml"):
        res = requests.get(f"{api_root}{path}", timeout=COMPLIANCE_TIMEOUT)
        if res.status_code == 200:
            return
    raise AssertionError("Neither /openapi.json nor /openapi.yaml returned 200")


def check_content_type(api_root):
    """JSON endpoints return Content-Type: application/json (RECOMMENDED)."""
    res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
    assert res.status_code == 200
    ct = res.headers.get("Content-Type", "")
    assert "application/json" in ct, (
        f"Expected Content-Type application/json, got '{ct}'"
    )


# ============================================================
# Check registry -- builds the full compliance suite
# ============================================================


def build_checks(api_root: str) -> list[tuple[str, Callable, tuple, bool]]:
    """Build the complete list of compliance checks for the server at api_root.

    Returns list of (name, function, args, recommended) tuples. Self-bootstraps
    by walking the server's own data, capped by MAX_* constants.
    """
    R = True   # recommended
    checks: list[tuple[str, Callable, tuple, bool]] = []

    # --- Static structure checks ---
    checks.append(("service_info", check_service_info, (api_root,), False))
    checks.append(("list_namespaces_structure", check_list_namespaces_structure, (api_root,), False))
    checks.append(("namespace_record_fields", check_namespace_record_fields, (api_root,), False))
    checks.append(("pagination_defaults", check_pagination_defaults, (api_root,), False))

    # --- Negative checks (static) ---
    checks.append(("unknown_namespace_404", check_unknown_namespace_404, (api_root,), False))

    # --- RECOMMENDED checks (static) ---
    checks.append(("cors_headers", check_cors_headers, (api_root,), R))
    checks.append(("openapi_available", check_openapi_available, (api_root,), R))
    checks.append(("content_type", check_content_type, (api_root,), R))

    # --- Cross-ref: all listed namespaces resolve ---
    checks.append(("listed_namespaces_resolvable", check_listed_namespaces_resolvable, (api_root,), False))

    # Walk the server to build per-namespace/schema/version checks
    try:
        ns_res = requests.get(f"{api_root}/namespaces", timeout=COMPLIANCE_TIMEOUT)
        namespaces = ns_res.json().get("results", [])[:MAX_NAMESPACES]
    except Exception:
        return checks

    first_ns = None
    first_schema = None

    for ns_record in namespaces:
        ns = ns_record["namespace_name"]
        if first_ns is None:
            first_ns = ns

        tag = ns
        checks.append((f"list_schemas_structure[{tag}]", check_list_schemas_structure, (api_root, ns), False))
        checks.append((f"schema_record_fields[{tag}]", check_schema_record_fields, (api_root, ns), False))
        checks.append((f"unknown_schema_404[{tag}]", check_unknown_schema_404, (api_root, ns), False))
        # Filtering is RECOMMENDED — static sites may not support query params
        checks.append((f"filter_unknown_returns_empty[{tag}]", check_filter_unknown_returns_empty, (api_root, ns), R))

        try:
            schemas_res = requests.get(f"{api_root}/schemas/{ns}", timeout=COMPLIANCE_TIMEOUT)
            schemas = schemas_res.json().get("results", [])[:MAX_SCHEMAS_PER_NS]
        except Exception:
            continue

        for schema_record in schemas:
            schema_name = schema_record["schema_name"]
            if first_schema is None and first_ns == ns:
                first_schema = schema_name
                # Filter checks — RECOMMENDED; use first known namespace+schema
                checks.append((
                    f"filter_schema_name[{ns}/{schema_name}]",
                    check_filter_schema_name,
                    (api_root, ns, schema_name),
                    R,
                ))
                if schema_record.get("maintainers"):
                    checks.append((
                        f"filter_maintainer[{ns}/{schema_name}]",
                        check_filter_maintainer,
                        (api_root, ns, schema_record["maintainers"][0]),
                        R,
                    ))
                if schema_record.get("maturity_level"):
                    checks.append((
                        f"filter_maturity_level[{ns}/{schema_name}]",
                        check_filter_maturity_level,
                        (api_root, ns, schema_record["maturity_level"]),
                        R,
                    ))

            stag = f"{ns}/{schema_name}"
            checks.append((f"list_versions_structure[{stag}]", check_list_versions_structure, (api_root, ns, schema_name), False))
            checks.append((f"schema_version_fields[{stag}]", check_schema_version_fields, (api_root, ns, schema_name), False))
            checks.append((f"listed_schemas_resolvable[{stag}]", check_listed_schemas_resolvable, (api_root, ns, schema_name), False))
            checks.append((f"latest_matches_listed[{stag}]", check_latest_matches_listed, (api_root, ns, schema_name), False))
            checks.append((f"unknown_version_404[{stag}]", check_unknown_version_404, (api_root, ns, schema_name), False))

            latest = schema_record.get("latest_released_version")
            if latest:
                checks.append((
                    f"latest_alias[{stag}]",
                    check_latest_alias,
                    (api_root, ns, schema_name, latest),
                    False,
                ))

            try:
                vers_res = requests.get(
                    f"{api_root}/schemas/{ns}/{schema_name}/versions",
                    timeout=COMPLIANCE_TIMEOUT,
                )
                versions = vers_res.json().get("results", [])[:MAX_VERSIONS_PER_SCHEMA]
            except Exception:
                continue

            for ver_record in versions:
                ver = ver_record["version"]
                vtag = f"{ns}/{schema_name}/{ver}"
                checks.append((f"get_schema_document[{vtag}]", check_get_schema_document, (api_root, ns, schema_name, ver), False))
                checks.append((f"listed_versions_resolvable[{vtag}]", check_listed_versions_resolvable, (api_root, ns, schema_name, ver), False))
                checks.append((f"schema_document_id_consistency[{vtag}]", check_schema_document_id_consistency, (api_root, ns, schema_name, ver), False))

    return checks


# ============================================================
# Runner
# ============================================================


def run_compliance(api_root: str) -> ComplianceReport:
    """Run all compliance checks and return a ComplianceReport."""
    api_root = api_root.rstrip("/")
    report = ComplianceReport(
        server_url=api_root,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    for name, func, args, recommended in build_checks(api_root):
        result = _timed_check(name, func, *args, recommended=recommended)
        report.results.append(asdict(result))
        report.total += 1
        if result.passed:
            report.passed += 1
        elif recommended:
            report.recommended_failed += 1
        else:
            report.failed += 1

    return report
