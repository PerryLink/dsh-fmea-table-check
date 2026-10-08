# dsh-fmea-table-check

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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-fmea-table-check
dsh --profile <name> --dump-config | grep 'dsh-fmea-table-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`. As chaves e os parâmetros de cada regra estão em [README.md](README.md#configuration) (versão principal em inglês).

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-fmea-table-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-fmea-table-check contributors.
