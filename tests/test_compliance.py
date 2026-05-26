# Pytest wrapper for the GA4GH Schema Registry compliance suite.
#
# The canonical compliance checks live in compliance/compliance.py.
# This file parametrizes them for pytest execution.
#
# Run against an external server:
#   pytest tests/ --api-root https://schema-registry.databio.org/api

import pytest

import compliance.compliance as compliance_module
from compliance.compliance import (
    build_checks,
    check_content_type,
    check_cors_headers,
    check_filter_schema_name,
    check_filter_unknown_returns_empty,
    check_latest_alias,
    check_latest_matches_listed,
    check_list_namespaces_structure,
    check_list_schemas_structure,
    check_list_versions_structure,
    check_listed_namespaces_resolvable,
    check_listed_schemas_resolvable,
    check_listed_versions_resolvable,
    check_namespace_record_fields,
    check_openapi_available,
    check_pagination_defaults,
    check_schema_document_id_consistency,
    check_schema_record_fields,
    check_schema_version_fields,
    check_service_info,
    check_unknown_namespace_404,
    check_unknown_schema_404,
    check_unknown_version_404,
)


def pytest_generate_tests(metafunc):
    """Parametrize dynamic compliance checks at collection time."""
    if "check_name" in metafunc.fixturenames:
        api_root = metafunc.config.getoption("--api-root")
        if not api_root:
            metafunc.parametrize("check_name,check_func,check_args", [])
            return
        checks = build_checks(api_root.rstrip("/"))
        params = [
            pytest.param(
                name, func, args,
                marks=[pytest.mark.recommended, pytest.mark.xfail(strict=False, reason="RECOMMENDED check")]
            ) if recommended
            else pytest.param(name, func, args)
            for name, func, args, recommended in checks
        ]
        metafunc.parametrize(
            "check_name,check_func,check_args",
            params,
            ids=[c[0] for c in checks],
        )


@pytest.mark.require_service
class TestAPI:
    """GA4GH Schema Registry compliance tests."""

    # ---- Structure checks ----

    def test_service_info(self, api_root):
        check_service_info(api_root)

    def test_list_namespaces_structure(self, api_root):
        check_list_namespaces_structure(api_root)

    def test_namespace_record_fields(self, api_root):
        check_namespace_record_fields(api_root)

    def test_pagination_defaults(self, api_root):
        check_pagination_defaults(api_root)

    # ---- Negative checks ----

    def test_unknown_namespace_404(self, api_root):
        check_unknown_namespace_404(api_root)

    # ---- Cross-reference checks ----

    def test_listed_namespaces_resolvable(self, api_root):
        check_listed_namespaces_resolvable(api_root)

    # ---- RECOMMENDED checks ----

    @pytest.mark.recommended
    @pytest.mark.xfail(strict=False, reason="RECOMMENDED check")
    def test_cors_headers(self, api_root):
        check_cors_headers(api_root)

    @pytest.mark.recommended
    @pytest.mark.xfail(strict=False, reason="RECOMMENDED check")
    def test_openapi_available(self, api_root):
        check_openapi_available(api_root)

    @pytest.mark.recommended
    @pytest.mark.xfail(strict=False, reason="RECOMMENDED check")
    def test_content_type(self, api_root):
        check_content_type(api_root)


@pytest.mark.require_service
class TestDynamic:
    """Dynamically-parametrized checks built from the server's own data."""

    def test_dynamic_check(self, api_root, check_name, check_func, check_args):
        check_func(*check_args)
