/**
 * dsh-fmea-table-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'fmea_table_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  item: ['项目', '产品', '系统', '过程', '分析对象', 'item'],
  function: ['功能', '功能要求', 'function'],
  failureMode: ['失效模式', '潜在失效模式', '故障模式', 'failureMode', 'mode'],
  effect: ['失效后果', '后果', '潜在后果', '影响', 'effect'],
  severity: ['严重度', '严重性', 'S', 'severity'],
  cause: ['失效原因', '原因', '潜在原因', 'cause'],
  occurrence: ['频度', '发生度', '发生频度', 'O', 'occurrence'],
  prevention: ['预防措施', '现行预防措施', '预防控制', 'prevention'],
  detection: ['探测度', '检出度', '不可探测度', 'D', 'detection'],
  detectionControl: ['探测措施', '现行探测措施', '探测控制', 'detectionControl'],
  rpn: ['风险优先数', 'RPN', 'AP', 'rpn'],
  action: ['建议措施', '建议改进措施', 'action'],
  owner: ['责任人', '负责人', 'owner'],
  dueAt: ['完成期限', '目标完成日期', '完成日期', 'dueAt'],
  status: ['措施状态', '状态', 'status'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'failures', '失效'],
  columns: COLUMNS,
  header: {
  item: ['item', '项目名称', '产品名称', '过程名称'],
  team: ['team', '分析小组', '编制人'],
  method: ['method', '分析方法', '方法'],
  signedAt: ['signedAt', '编制日期', '日期'],
  revision: ['revision', '版本', '版次'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '失效模式',
  'failureMode',
  '失效后果',
  'effect',
  '失效原因',
  'cause',
  '管控措施',
  'prevention',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
