# dotCMS Agent Toolkit

[![skills.sh](https://skills.sh/b/dotCMS/agent-toolkit)](https://skills.sh/dotCMS/agent-toolkit)

Agent skills and an MCP server for building and maintaining **dotCMS** sites — content types,
pages, templates, containers, content placement, VTL, and headless Next.js. Works with Claude Code,
Cursor, Codex, and any [Agent Skills](https://agentskills.io)-compatible agent.

## What's inside

| Skill | What it does |
|---|---|
| **`dotcms-best-practices`** | Reference for doing any single thing correctly — create a content type, page, template or container; place content; author VTL; wire a headless Next.js frontend; or debug a page that renders blank. Indexed by intent, so the agent loads one file for the task at hand. |
| **`dotcms-create-sites`** | Plans and builds a complete site in two phases: an interview that writes `PLAN.md` and `DESIGN.md`, then a build that hands off to `dotcms-best-practices` and holds a verify-and-fix loop until every page type renders. |

Both support **VTL-rendered** and **headless (Next.js)** delivery.

> **Why a skill and not just docs:** in dotCMS a missing piece renders blank or shell-only with
> **HTTP 200**, never an error. A successful response is not evidence that anything rendered. Every
> build path in these skills ends in a verify step for that reason.

## Install

### Skills — any agent

```bash
npx skills add dotCMS/agent-toolkit
```

Installs both skills. Add `-g` for all projects, `--list` to preview without installing, or
`--skill dotcms-best-practices` for just one.

### Plugin — Claude Code

Bundles the skills and the MCP server together.

```
/plugin marketplace add dotCMS/agent-toolkit
/plugin install dotcms@dotcms
```

Then `/reload-plugins` to activate without restarting.

### Plugin — Cursor and Codex

The repo ships `.cursor-plugin/` and `.codex-plugin/` manifests. Point your client at this
repository.

### Agent Plugins

`plugin.json` and `mcp.json` conform to
[Agent Plugins 1.0.0](https://agent-plugins.org/specification). Any conforming client can install
this repo directly.

## MCP server

The plugin declares one server, **`dotcms`**, run over stdio:

```json
{
  "mcpServers": {
    "dotcms": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@dotcms/mcp-server@latest"],
      "env": {
        "DOTCMS_URL": "https://your-instance.dotcms.com",
        "AUTH_TOKEN": "your-api-token"
      }
    }
  }
}
```

| Variable | Required | What it is |
|---|---|---|
| `DOTCMS_URL` | yes | Your dotCMS instance URL |
| `AUTH_TOKEN` | yes | API token — create one under **System → Users → API Access Tokens** |

**Export both before launching your client.** The bundled `.mcp.json` reads `${DOTCMS_URL}` and
`${AUTH_TOKEN}` from the environment, and Claude Code expands those **only** from the shell it was
launched in. An unset variable is passed through as the literal string `${AUTH_TOKEN}`, which comes
back as a confusing `401` rather than a missing-configuration error.

The skills work without the MCP server — it makes the agent faster, not functional.

## Contributing

```bash
npm install
npm run validate
```

That runs the same three checks CI does: skill frontmatter and manifest drift, the Claude Code
manifests (`claude plugin validate . --strict`), and the Agent Plugins manifests against the
published JSON schemas.

Adding a skill means a directory under `skills/` with a `SKILL.md` whose `name` frontmatter equals
the directory name, plus an entry in `.claude-plugin/marketplace.json`. `validate:skills` enforces
both — `npx skills add` silently *skips* a skill with malformed frontmatter and still exits 0, so
the check is what stops a broken skill shipping as a no-op.

The `description` field is the trigger contract: it decides whether an agent invokes the skill at
all. State what it does **and** when to use it.

## License

MIT — see [LICENSE](LICENSE).
