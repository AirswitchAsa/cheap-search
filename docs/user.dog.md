# Actor: User

## Description

A developer who installs the `cheap-search` CLI to perform provider-specific web or social search from the terminal, or to configure provider credentials. The `@User` interacts with the system directly through shell commands, or indirectly through a coding agent that invokes the same CLI on their behalf.

## Notes

- Primary actor for credential setup (`!SetGrokApiKey`, `!UnsetGrokApiKey`, `!ShowGrokApiKeyStatus`).
- The `@User` chooses the provider explicitly; the CLI does not route queries across providers.
