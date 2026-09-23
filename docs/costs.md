# Costs

Checked 23 September 2026. This project requires no new subscription, hosted server, database, API key or deployment provider.

| Item | Cost for this workflow |
| --- | --- |
| Iron Engine and local Python | No project fee; standard-library code |
| GitHub repository | GitHub Free provides public and private repositories |
| Automated checks | Standard hosted runner minutes are free for public repositories; private repositories have plan allowances and possible overages |
| Chatbot | Your chosen chat's plan and usage limits; the repository cannot determine your account's price |
| Model API | Not used directly; the engine calls no model. API billing is separate if you later add an integration |

No model is called automatically. Turns consume the chosen chat's normal context/output allowance; the tenth-turn review runs a second, fresh-context agent and uses more of it. Narrative length, research and retrieved history affect usage, so a fixed price per turn would be misleading. Focused context and compact operations reduce repeated input; the full history stays in the repository.

The checks workflow uses a standard Ubuntu runner, no paid larger runner, artifact upload or cache. No billing setting was changed. GitHub's actual plan and repository visibility govern its charges.

Official references: [GitHub plans](https://github.com/pricing), [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions). Provider prices and quotas may change; consult those pages when purchasing a plan.
