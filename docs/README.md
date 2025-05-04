# Schema registry specification

## What is the schema registry specification?

The GA4GH Schema registry specification provides a standard for representing and sharing schemas. It can be implemented by independent provides, which can then interoperate to share schemas across domains.

## Can I see a demo?

The specification itself is still under development.  Once the spec is developed, we anticipate independent implementations that conform to the specification will be available. These services can then be used to share schemas.

## Specification version

This specification is in **DRAFT** form. This is **NOT AN APPROVED GA4GH specification**. 

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
- **Schema**: A document that defines the structure used to store or exchange data. It is often an implementation of a conceptual data model either implicitly or explicitly but usually includes optimizations/restrictions that are not relevant to the data model. 
- **Schema Registry**: A resource on the web (URL) where a [GA4GH] community can find schemas that are in use within and/or recommended by the community.
- **Semantic Version**: A string like, `MAJOR.MINOR.PATCH` (e.g. `0.4.3`) that uses following the [semantic versioning standard](https://semver.org/), used to version a schema.
- **Registry path**: A name used to identify a schema, consisting of the namespace and schema name, like `{namespace}/{schema_name}`. Analogous to a repository name on GitHub. Schema registry paths uniquely identify a particular schema within a given Schema Registry.
