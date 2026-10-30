# Security

Reporch handles research data, which often includes personal information. It is built to keep that data
on your machine.

## What Reporch does

- Runs locally with the Python standard library. It installs nothing without asking.
- Anonymises participants before analysis and never writes real names into outputs.
- Makes no network request unless you agree: the optional update check asks GitHub for the latest
  release, and sends nothing about you or your work.
- Never writes your projects or assets into the skill folder, so `git pull` can't publish them.
- Builds self-contained HTML files that load nothing from the network.

## Reporting a vulnerability

Please don't open a public issue. Use GitHub's
[private vulnerability reporting](https://github.com/mobo-kun/reporch/security/advisories/new) for this
repository. Include steps to reproduce and the version (`python3 scripts/reporch.py version`). You'll get a
reply within a week.

## Supported versions

| Version | Supported |
| --- | --- |
| 1.x | yes |
