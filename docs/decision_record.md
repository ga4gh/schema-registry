# Architectural Decision Record

*This is a record of decisions made during specification development. Each entry describes a decision that has been approved by the team members. Collectively, this ADR describes an institutional memory for decisions and their rationales, including known limitations. The goal is to avoid repeated discussion of previous decisions, formally acknowledge limitations, preserve and articulate reasons behind the decisions, and share this information with the broader community.* 

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## Contents

[TOC]



## 2025-02-04

### We will postpone including "latest snapshot" as part of the spec for now

In the `{version}` field of the endpoint that returns a schema content, we will allow `latest`, which will return the latest version, but not other special tags like `1.1.x`, which would return the latest within a specific constraint.

### Rationale

Most users will just want `latest`, or a specific version. While there is some utility in a constrained version of the latest, it will add more parsing work. The latest one can just be found from the metadata on the schema which defines that as a property of the metdata. We want to keep the initial spec pretty low key, and adding additional constrained tags like this would add some complexity without a major benefit. We can revisit in the future if we want to make the spec more complex.


## 2025-01-01 {Decision title}

### Decision

{Decision text}

### Rationale

{Rationale text}

### Linked issues

- {github issues}

