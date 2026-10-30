# dsh-fmea-table-check — FMEA 分析表要素齐备性与风险顺序数一致性核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　FMEA 分析表核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　质量工程师、工艺工程师；不用懂命令行。
> **你交什么**　这项核对用到的原始材料（表格、清单或文书）；不改原件。Excel 可先转成 JSON/YAML，对话里也能代转。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　在 WorkBuddy / 扣子搜「职业文档核对全集」（总包，本检查是其中一项；上架以商城为准）；或命令行：
> `dsh plugin --profile <name> add dsh-fmea-table-check`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-fmea-table-check?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-fmea-table-check?ref=badge)

`dsh-fmea-table-check` 读取一份 FMEA 分析表——以表自身的列名为键，中英文均可——核对一张表在机械层面能够被要求的东西：基本分析链是否记录在案、严重度/频度/探测度是否为可运算的数值、风险顺序数是否等于三者之积、高风险条目是否有带责任人与完成期限的建议措施、措施状态是否取自本机构的口径、失效模式栏是否残留未替换的模板占位符。

## Install

```sh
dsh plugin --profile <name> add dsh-fmea-table-check
dsh --profile <name> --dump-config | grep 'dsh-fmea-table-check'
```

## 实际输出长什么样

![dsh-fmea-table-check 工作流图：文档 → 规则包 → 核对结果。](docs/assets/dsh-fmea-table-check-flow.svg)

*工作流概览：文档 → 规则包 → 核对结果。下面的示例使用实际命令面。*


本插件对自己 `FM-002` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。


#### 详细输出

**工具** `fmea_table_check`

**输入**

~~~json
{"rows":[{"失效模式":"密封面泄漏","严重度":"8","频度":"4","探测度":"3","风险优先数":"100"}]}
~~~
 
**输出**

~~~json
{
  "id": "dsh-fmea-table-check.FM-003.de09b5a6",
  "ruleId": "FM-003",
  "severity": "warn",
  "locator": {
    "field": "rpn",
    "row": 1
  },
  "found": "第 1 行「rpn」填报 100，而 8 × 4 × 3 = 96",
  "expected": "「rpn」应等于 severity × occurrence × detection",
  "fix": "核对是否抄错或漏改；本条只做算术核对，不判断各因子是否正确"
}
~~~

*来源 `tests/fixtures/FM-003/FM-003-unsafe.json (cases.json expects FM-003 count 1); run via lib/index.mjs rules/fmea-table-check.yaml`*

| 你会问 | 它怎么答 |
|---|---|
| RPN 栏跟严重度 × 频度 × 探测度对不上，能查出来吗？ | 能。`FM-003` 用严重度 × 频度 × 探测度重算 `rpn`，容差为 `0`，逐行报出与表内所填不一致的条目。它只在四个字段都能解析为数值时执行；频度填的不是数字时，本条报 `skipped` 而不是通过。按 AIAG-VDA 手册打分的表用 AP 而非 RPN，请改 `resultField` 与 `factorFields`，或停用本条。 |
| 严重度栏填的是「高」而不是分数，会怎样？ | `FM-002` 要求严重度为可运算的正数，填不出来即报出该行。它的核对只指向 `severity` 一个字段，频度与探测度要另加一条换 `field` 的规则；它不设分值范围，既不强制 1～10 的口径，也不判断打分是否恰当。分数解析不出来时 `FM-003` 同样进 `skipped`，因为乘不出来。 |
| 某行提了建议措施，但责任人与完成期限都是空的。 | `FM-005` 在凡是填了建议措施的行上执行，要求同时有 `owner`（责任人）与 `dueAt`（完成期限），缺其一即报出该行。字段名是别名解析后的规范名，本机构表式栏名不同时，请把别名加进列映射或调整 `requiredFields`。它只核对这两栏是否填写，不判断期限是否现实、责任人是否认可。措施栏为空的行由 `FM-004` 负责。 |
| 分析表里根本没写分析的是哪个产品或过程。 | `FM-007` 读表头的 `item`，分析对象缺失即报出：FMEA 是针对特定产品或过程开展的，没有它结论无法追溯，也无法判断该用哪一套评分表。这是存在性核对，填了但填错不报。若本机构还要求写明所用分析方法，把 `method` 加进它的 `fields`。 |
| 有些行的失效模式栏还写着「待填」或 `XXX`，另一些行干脆什么都没填。 | `FM-008` 报出失效模式栏仍含本规则库占位符词条（`【`、`】`、`{{`、`}}`、`XXX`、`xxx`、`待填`、`待补充`、`TBD`、`todo`、`示例`）的行，因为照模板抄来的表看上去像是分析已完成；它只看失效模式栏，词条可随本机构模板调整。`FM-001` 报出失效模式、后果与原因三项全空的行，但它只要求三者填了至少一项——填着「待填」的行能通过 `FM-001`，由 `FM-008` 报出。两条都不判断失效模式是否找全、后果是否分析到位。 |
| 报告里 `FM-004` 与 `FM-006` 显示为 `skipped`，是出问题了吗？ | 不是。这两条出厂都未配置，规则库如实报出未能执行，而不是静默通过。`FM-004` 的 `threshold` 为 `0`，即未配置，未设本机构风险准则前没有任何行算高风险——例如配 `triggerField: severity` 加 `threshold: 9`，或 `triggerField: rpn` 加 `threshold: 100`。`FM-006` 的 `values` 为空，未列本机构口径前不核对措施状态取值。配置之后，`FM-004` 只核对高风险行的建议措施栏是否填写，不判断措施是否有效、是否可行；`FM-006` 只核对状态值是否在册，不判断措施是否真的落实。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《系统可靠性分析技术 失效模式和影响分析（FMEA）程序》 | GB/T 7826（现行版本号与条号本次未核实） | FM-001, FM-002, FM-003, FM-004, FM-005, FM-006, FM-007, FM-008 |

**边界（中文译文，以英文原文为准）：** 本插件核对一份 **FMEA 分析表** 在表格层面可以机械要求到的事项——分析链是否记录在案，严重度 / 频度 / 探测度是否为可运算的数值，风险顺序数是否等于三者之积，高风险条目是否带有含责任人与完成期限的建议措施，措施状态是否取自你配置的取值口径，以及是否残留模板占位符。它**不**判定失效模式是否完整、后果分析是否足够深入、评分是否正确，也不判定风险是否可以接受。**那些是研究团队的判断，也正是 FMEA 的价值所在。**

> ### ⚠️ 在采信报告中的引文之前，请先读这一段
>
> **每条 `excerpt` 的状态逐条不同，不是统一的。** 有的规则引用逐字条文（`kind: direct`），有的按条文原则推导（`kind: derived-from-principle`，最高 `warn`），有的阈值由本机构配置（`kind: institutional-configuration`，最高 `info`）。规则包从不概括引文：取不到原文时，`excerpt` 会如实写明，推理写在 `note` 里；并有测试断言没有任何规则声称拥有它并不拥有的引文。**对仍标为「未取得原文」的规则，取得文本后必须把 `excerpt` 换成真实条款，并把 `kind` 提升为 `direct`。**
>
> 结论性判断留给审核人：本插件只列出材料内部可以逐条指认的差异，不判断事实真伪，也不评价合规性。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/fmea-table-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-fmea-table-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-fmea-table-check contributors.
