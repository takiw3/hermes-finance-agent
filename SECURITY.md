# Security policy

Report vulnerabilities privately to the repository owner. Do not include real financial data or credentials in a report. Supported security fixes target the current 1.x release line.

This distribution has no external finance-system client and no credential path. Terminal deny globs are defense in depth, not a sandbox, and do not cover browsers or added MCP tools. Use one business per profile, restrict local filesystem permissions, review memory/skill writes, and redact handoffs. If sensitive data enters memory, Kanban, a log, or version control, stop use, preserve minimal evidence, remove access, rotate affected credentials through the system owner, and follow the business incident process.
