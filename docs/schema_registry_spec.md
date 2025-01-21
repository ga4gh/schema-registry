---
title: Schema registry specification version 0.1.0
---

<!-- Table of contents: 
* The generated Toc will be an unordered list
{:toc} -->

# Schema registry version 0.1.0

<!-- Table of contents:

[TOC] -->

## Specification version

This specification is in **DRAFT** form. This is **NOT YET AN APPROVED GA4GH specification**. This document is **formal technical explanation for implementers**. See also:

- [Architectural decision record](decision_record.md), a chronological record of spec decisions.

## Introduction

GA4GH Workstreams gather experts from a particular area of interest and develop standards, frameworks and tools.  Workstreams operate independently and often define different vocabulary and data representation (schema) standards. This presents challenges when bringing together products from different workstreams and hinders adoption of GA4GH products.

A schema defines the structure used to store or exchange data. It is often an implementation of a data model either implicitly or explicitly but usually includes optimizations/restrictions that are not relevant to the data model. 

A GA4GH Schema Registry is an online location where the GA4GH community can find schemas that are in use within and/or recommended by the GA4GH community.

The goal of the schema registry specification is to provide a standard for representation and exchange of schemas. 

## Use cases

To be added

## Definitions of key terms

### General terms

- **Namespace**: The name of a user or organization that owns schemas. Analogous to a github user or organization name. The namespace forms part of the registry path for a schema.
- **Schema**: A document that defines the structure used to store or exchange data.
- **Schema Registry**: A web location where schemas are stored.
- **Semantic Version**: A string like, `MAJOR.MINOR.PATCH` (e.g. `0.4.3`) that uses following the semantic versioning standard, used to version a schema.
- **Registry path**: A name used to identify a schema, consisting of the namespace and schema name, like `{namespace}/{schema_name}`. Analogous to a repository name on GitHub. Schema registry paths uniquely identify a particular schema within a given implementation/provider.


## 1. API Specification

### GET /schemas/{namespace}/?attr1=val1&lifecycle_stage=released

#### Params: 

- {namespace}: as above
- {attr1}: query key-value pairs provided will filter 

#### Response: 200

Content: A list of schemas within a namespace.

Example: 

```
{
  "namespace": "some-namespace",
  "schemas": [
    {
      "schema_name": "my_schema_name",
      "latest_version": "0.5.4",
      "maintainer": ["...", "...."],
      "lifecycle_stage": "released"
    }
  ]
}
```

---

### GET /schemas/{namespace}/{schema_name}/versions

#### Params: 

- `{namespace}`: as above  
- `{schema_name}`: as above  

#### Response: 200  

Content: Object with `schema_name` and `versions`, containing an array of objects holding version and label information.  

Example:  

```json
{
  "schema_name": "some-schema-name",
  "versions": [
    {
      "version": "0.1.0",
      "status": "current|deprecated|latest",
      "release_date": "2024-10-31T12:34:56Z",
      "contributors": ["The DaMaSC working group", "..."],
      "release_notes": "Markdown Text"
    }
  ]
}
```

---

### GET /schemas/{namespace}/{schema_name}/versions/{semantic_version}

#### Params: 

- `{semantic_version}`: A string indicating `MAJOR.MINOR.PATCH` version following semver (e.g., `"0.17.4"`)  
- `{namespace}`: A string indicating the organization/user who owns this schema (e.g., `"ga4gh"` for GA4GH-sponsored/approved schemas)  
- `{schema_name}`: Name of this schema, following the same naming rules as GitHub repositories  

#### Response: 200  

Content: The JSON Schema.  

If `{semantic_version} == "latest"`, this endpoint should return the maximum version number currently in the database.  

---

### GET /namespaces

#### Params:  

- None  

#### Response: 200  

Content: A list of namespaces hosted by this server.  

Example:  

```json
{
  "server": "service.url.org",
  "namespaces": [
    {
      "namespace_name": "my_namespace_name",
      "latest_version": "0.5.4",
      "contact_url": "http://..."
    }
  ]
}
```  
