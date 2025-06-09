# Architectural Decision Record

*This is a record of decisions made during specification development. Each entry describes a decision that has been approved by the team members. Collectively, this ADR describes an institutional memory for decisions and their rationales, including known limitations. The goal is to avoid repeated discussion of previous decisions, formally acknowledge limitations, preserve and articulate reasons behind the decisions, and share this information with the broader community.* 

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.


## 2025-04-15 Pagination
### Category: Pagination

### Decision
Include pagination for all endpoints that return a list. 

### Rationale
 Follows GA4GH standard; good form because it allows the user to see the total of results without having to page through to the end. 

### Linked issues
- https://github.com/ga4gh/schema-registry/issues/11

## 2025-02-04 Latest snapshot

### Category: Versioning

### Decision
Postpone including "latest snapshot" as part of the spec for now

In the `{version}` field of the endpoint that returns a schema content, we will allow `latest`, which will return the latest version, but not other special tags like `1.1.x`, which would return the latest within a specific constraint.

### Rationale
Most users will just want `latest`, or a specific version. While there is some utility in a constrained version of the latest, it will add more parsing work. The latest one can just be found from the metadata on the schema which defines that as a property of the metdata. We want to keep the initial spec pretty low key, and adding additional constrained tags like this would add some complexity without a major benefit. We can revisit in the future if we want to make the spec more complex.

### Linked issues
- None

## 2024-11-15 Schema Metadata

### Category: Schema Metadata

### Decision
A minimal set of metadata (data about the schema itself) will be required by the API Specification, implemented as REST API query parameters.  Individual implementations may optionally add parameters.  

The supported parameters will include but not be limited to:
1. Maturity_level
2. Semantic_version
3. Release_date
4. Release_notes
5. Status
6. Version
7. Contact
8. Namespace_name
9. Schema_name

The API Specification provides an up-to-date list of supported parameters and indicates whether they are required or optional.

### Rationale
Basic principle: Keep it as simple as possible.

2025-02-18
Discussions about additional optional metadata for implementers of the Schema Registry.

2024-11-15
Namespace-level metadata should remain minimal…Jonathan suggested providing a "contact URL", agreed on `contact_URL`. Nathan argued for distinct roles for schema maintainers versus organizational contacts. They decided to include both concepts.

2024-09-20
Metadata examples that we could capture
- Workstream (for GA4GH SR)
- status – draft, approved – maturity levels (GKS?)
- source (source URL) – for schemas in original format
- More information – home page for schema
- Attachments -- Use DRS standards for URI.

2024-08-20
Agreed to define a minimal set of metadata in the specification.  Individual namespace implementations MAY choose to require additional metadata (tags) as part of admitting a schema into their namespace.

### Linked issues
- None

## 2024-10-18 Semantic Versioning

### Category: Versioning

### Decision
Following GKS’s lead on versioning in the [GKS Technical Specification Maintenance](https://docs.google.com/document/d/1pqxeB9abRpLe0j6PiRBjmPYPKO9URyBY2QYVcyqO-m8/edit?tab=t.0#heading=h.42y3vv3v3vb)document, the Schema Registry will adopt semantic versioning.

### Rationale
2024-10-18
The proposed versioning scheme is based on [Semantic Versioning 2](https://semver.org/), which uses a "Major.Minor.Patch" format commonly used in open-source software to manage version updates. The rationale behind incrementing different parts of the version number (patch for backward-compatible bug fixes, minor for backward-compatible feature additions, and major for changes that break compatibility) was outlined.

For initial Spec and Prototype, we will not implement the Pre-release naming.  Subject to further review.

### Linked issues
- None

## 2024-10-18 What formats shall we share in a Schema Registry?
### Category: Schema format

### Decision
Schema Registry returns JSON schema by default, although a schema may be originally crafted in any format.

### Rationale
The team ultimately agreed that submitters may write their schema in any format, but that the Schema Registry (SR) MUST return JSON schema to facilitate interoperability across schemas.  Schema Registry providers may accept valid JSON schema only or opt to support other formats as long as the requirement for returning JSON schema is is met.  Additional formats may be returned SR using optional tags.  

### Discussions
2024-10-18
From the perspective on how GA4GH might govern a Schema Registry, the group addressed whether JSON is the right format for schemas in a GA4GH working document. Kathy argued for sticking with JSON in the short term to avoid complicating implementation, though acknowledging that formats may evolve over time. Jonathan supported being explicit about the format, while Nathan proposed a flexible approach allowing users to request different formats (e.g., protobuf or LinkML) via a query parameter. Kathy highlighted that PhenoPackets used LinkML, which auto-generates JSON Schema, making it a potentially solved problem for PhenoPackets. 
The group considered adding format as metadata for future-proofing, and debated whether multiple schema formats should be included in the registry. Nathan emphasized the importance of computability for the Schema Registry, advocating for including multiple formats to support diverse use cases. The format should be a required metadata component if we choose this approach, but the approach to handling schema distribution (either via direct API access or additional metadata endpoints) needs further discussion.

2024-09-20 -- Andy Yates previously raised an issue about JSON Schema lacking full expressivity for schema descriptions. 

2024-08-02 – From the perspective of the spec, we can support anything, and thus don’t need to require or enforce a specific format but for usability and interoperability, it’s better to be in JSON schema.  For the Prototype, we will limit to JSON schema.  Subject to further review.

Note: changes to this decision would modify the definition of Registry path.

### Linked issues
- [GKS namespace questions](https://github.com/ga4gh/schema-registry/issues/6)


## 2024-08-20 Write/Insert/Update Functionality
### Category: API Scope

### Decision
Write/Insert/Update out-of-scope for the API


### Rationale
The Schema Registry API is intended to facilitate finding and sharing schemas while allowing schema and repository implementers the freedom to set their own governance rules and manage user access.   While implementations need a method for inserting schemas, the specification itself should only standardize the reading and sharing aspects, not the insertion process.

An example of the power of this decision is the fact that a single client implementation could access schemas in multiple schema collections.

Possible back-ends for schema collections
- GitHub repository
- Relational database
- Document store (e.g. Mongodb)
- Artifact repository (e.g. Github Packages, pypi, npm)
- S3-compatible object storage

### Linked issues
- None

## 2024-08-09 GitHub-style Principles
### Category: Governance

### Decision
The API Specification will follow a GitHub-style governance model (self-registered "organization" namespaces) combined with unique identifiers that include the organization ID.  


### Rationale
Basic Principle: Keep it as simple as possible.

Advantages of GitHub-style model:
- Well known interface & toolset
- Can use Github authentication
- Independent of vendors
- Model is simple - domain/namespace/schemaName

### Linked issues
- None

## 20xx-xx-xx {Decision title}
### Category:

### Decision
{Decision text}


### Rationale
{Rationale text}

### Linked issues
- {github issues}
