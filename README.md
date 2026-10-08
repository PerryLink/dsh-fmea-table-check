# dsh-fmea-table-check — FMEA worksheet element completeness and risk priority number consistency check

`dsh-fmea-table-check` reads one FMEA worksheet — rows keyed by the sheet's own column names, in Chinese or English — and checks in it what a sheet can be held to mechanically: that the analysis chain is recorded, that the severity, occurrence and detection scores are operable numbers, that the risk priority number equals their product, that a high-risk row carries an action with an owner and a due date, that action statuses come from your own vocabulary, and that no template placeholder survives in the failure mode.

## What it answers

| You ask | What it answers |
|---|---|
| The RPN cell does not equal severity × occurrence × detection — is that caught? | Yes. `FM-003` recomputes `rpn` from severity × occurrence × detection with a tolerance of `0` and reports the row whose stored value differs. It runs only when all four cells hold parseable numbers; if the occurrence score is not a number the rule reports `skipped` rather than a pass. A worksheet built on the AIAG-VDA handbook scores with AP instead of RPN, so repoint `resultField` and `factorFields`, or disable the rule. |
| The severity cell holds `高` instead of a score. What happens? | `FM-002` requires severity to be an operable positive number and reports the row when it is not. Its check names the `severity` field only, so occurrence and detection need the same rule added with a different `field`; it sets no score range, so it does not enforce a scale from 1 to 10 and does not judge whether a score is appropriate. A score it cannot parse also sends `FM-003` to `skipped`, because the product cannot be recomputed. |
| A row recommends an action, but the owner and the due date are blank. | `FM-005` runs on every row whose recommended-action cell is filled and requires both `owner` and `dueAt`; it reports the row missing either one. Those are the canonical names after alias resolution, so a sheet with other column headers needs the alias in the column mapping or `requiredFields` adjusted. It checks that the two cells are filled — not that the date is realistic or that the owner has accepted it. Rows with an empty action cell are `FM-004`'s business. |
| Our worksheet never says which product or process it is analysing. | `FM-007` reads the sheet header's `item` and reports it when the analysis subject is missing: an FMEA is carried out for a specific product or process, and without it the conclusions cannot be traced back or matched to a scoring table. It is a presence check — an analysis subject that is filled in but wrong is not reported. If your sheets must also name the method used, add `method` to its `fields`. |
| Some rows still read `待填` or `XXX` in the failure-mode column, and other rows have nothing there at all. | `FM-008` reports a row whose failure-mode cell still contains one of the pack's placeholder terms (`【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例`), because a sheet copied from a template reads as a finished analysis; it reads the failure-mode column only, and `terms` follows your template. `FM-001` reports a row where failure mode, effect and cause are all blank, but it only requires one of the three to be filled — a cell holding `待填` satisfies `FM-001` and is caught by `FM-008` instead. Neither rule judges whether the failure modes are complete or the consequences analysed far enough. |
| The report lists `FM-004` and `FM-006` as `skipped`. Is something wrong? | No. Both ship unconfigured and the pack reports that instead of passing silently. `FM-004`'s `threshold` is `0`, which reads as not configured, so no row counts as high-risk until you set your own risk criterion — for example `triggerField: severity` with `threshold: 9`, or `triggerField: rpn` with `threshold: 100`. `FM-006`'s `values` list is empty, so the action-status vocabulary is not checked until you list your own values. Once configured, `FM-004` only checks that a high-risk row's action cell is filled — not that the action is effective or feasible — and `FM-006` only checks that a status is in the configured list, not that the action was carried out. |

## Standards it follows

| Document | Number | Cited by rules |
|---|---|---|
| 《系统可靠性分析技术 失效模式和影响分析（FMEA）程序》 | GB/T 7826（现行版本号与条号本次未核实） | FM-001, FM-002, FM-003, FM-004, FM-005, FM-006, FM-007, FM-008 |

**Boundary:** this plugin checks an **FMEA worksheet** for what a sheet can be held to mechanically — that
the analysis chain is recorded, that the severity / occurrence / detection scores are operable numbers,
that the risk priority number equals their product, that a high-risk row carries an action with an owner and
a due date, that action statuses come from your vocabulary, and that no template placeholder survives. It
does **not** judge whether the failure modes are complete, whether the consequences are analysed far enough,
whether the scores are right, or whether the risk is acceptable. **Those are the study team's judgements,
and they are where FMEA's value lies.**

> ### ⚠️ Read this before trusting a citation in the report
>
> **Every `excerpt` in this plugin's rule pack says, in so many words, that the clause text was not
> obtained.** The method's homes are **GB/T 7826《系统可靠性分析技术 失效模式和影响分析（FMEA）程序》**,
> IEC 60812, and the automotive AIAG-VDA handbook. The verification pass could not retrieve verbatim clause
> text from them, so rather than paraphrase a quotation the pack states the gap in the `excerpt` field
> itself and puts the honest reasoning in `note`. Every rule is therefore `warn` or `info`, and a test
> asserts that no rule claims a quotation it does not have. **When the texts are in hand, two things must be
> done: replace each `excerpt` with the real clause, and raise `kind` to `direct`.**
>
> Two settings are yours. **FM-003's RPN arithmetic assumes the S×O×D method**; a worksheet built on the
> AIAG-VDA handbook uses **AP (action priority)** instead, so repoint `resultField` and `factorFields` — or
> disable the rule. And **FM-004's threshold ships as `0`, meaning "not configured"**: what counts as high
> risk is your risk criterion, and the rule reports that it could not run rather than inventing a number.

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a workbook of sheets use `ptc` |

## What it does

Registers the `fmea_table_check` tool. It reads one worksheet — rows keyed by the sheet's own column names,
in Chinese or English — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `FM-001` | the failure mode, effect or cause is recorded | warn | principle |
| `FM-002` | the severity score is an operable positive number | warn | principle |
| `FM-003` | RPN equals severity × occurrence × detection | warn | principle |
| `FM-004` | a high-risk row carries a recommended action (off by default) | info | local |
| `FM-005` | a row with an action names its owner and due date | warn | principle |
| `FM-006` | the action status comes from your vocabulary (off by default) | info | local |
| `FM-007` | the sheet names its analysis subject | warn | principle |
| `FM-008` | no template placeholder survives in the failure mode | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-fmea-table-check
dsh --profile <name> --dump-config | grep 'dsh-fmea-table-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/fmea-table-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `FM-003` `resultField` / `factorFields` / `tolerance` — the RPN arithmetic. Repoint it at an AP column if
  your worksheet follows the AIAG-VDA handbook.
- `FM-004` `triggerField` / `threshold` / `requiredField` — your high-risk criterion. A threshold of `0`
  means the rule does not run; typical settings are `severity` at `9`, or `rpn` at `100`.
- `FM-005` `conditionField` / `requiredFields` — which fields an action row must carry.
- `FM-006` `values` — your action-status vocabulary.
- `FM-002` `min` / `max` — score bounds, if your scoring table fixes them. The rule sets none by default,
  because the tables differ between handbooks and analysis types.

## Material format

The tool accepts JSON or YAML:

```yaml
item: 某型阀体加工过程
rows:
  - { 项目: 某型阀体加工过程, 功能: 在规定压力下保持密封, 失效模式: 密封面泄漏,
      失效后果: 介质外泄，影响安全, 严重度: '8', 失效原因: 密封面加工粗糙度超差,
      频度: '4', 探测度: '3', 风险优先数: '96', 建议措施: 增加密封面粗糙度在线检测,
      责任人: 张工, 完成期限: 2026-06-30, 措施状态: 进行中 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens, so `严重度` and
`severity` resolve to the same field; the sheet's own column names are kept, so a finding names the column
it read. Scores may arrive as strings.

## Rule sources

Rule data lives in `rules/fmea-table-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`FM-004` or `FM-006` report themselves as skipped.** Their configuration is empty. Both depend on your
  risk criterion and your management procedure, and the plugin will not guess them.
- **`FM-003` fires on every row.** The worksheet uses AP rather than RPN; repoint `resultField` and
  `factorFields`, or disable the rule.
- **`FM-002` accepts a score of 99.** The rule checks that a score is an operable positive number and
  deliberately sets no range; add `min` and `max` if your scoring table fixes them.
- **`FM-005` fires on an action with no owner.** That is the check: an action without an owner and a due
  date cannot be tracked.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-fmea-table-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-fmea-table-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-fmea-table-check contributors.
