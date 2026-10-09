# dsh-fmea-table-check — Verificación de la completitud de los elementos de la hoja de FMEA y de la consistencia del número de prioridad de riesgo

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-fmea-table-check` lee una hoja de FMEA —filas indexadas por los propios nombres de columna de la hoja, en chino o en inglés— y comprueba en ella lo que a una hoja se le puede exigir mecánicamente: que la cadena de análisis esté registrada, que las puntuaciones de severidad, ocurrencia y detección sean números operables, que el número de prioridad de riesgo sea igual a su producto, que una fila de riesgo alto lleve una acción con responsable y fecha límite, que los estados de las acciones procedan de su propio vocabulario y que no sobreviva ningún marcador de plantilla en el modo de fallo.

## Cómo se ve la salida

![Terminal demo of dsh-fmea-table-check: real output over its FM-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-fmea-table-check/main/docs/assets/dsh-fmea-table-check-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `FM-002` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| La celda del RPN no coincide con severidad × ocurrencia × detección, ¿se detecta? | Sí. `FM-003` recalcula `rpn` como severidad × ocurrencia × detección con una tolerancia de `0` y señala la fila cuyo valor almacenado difiere. Solo se ejecuta cuando las cuatro celdas contienen números analizables; si la puntuación de ocurrencia no es un número, la regla informa `skipped` en lugar de aprobar. Una hoja puntuada con el manual AIAG-VDA usa AP en vez de RPN: reoriente `resultField` y `factorFields`, o desactive la regla. |
| La celda de severidad contiene `高` en lugar de una puntuación. ¿Qué ocurre? | `FM-002` exige que la severidad sea un número positivo operable e informa de la fila cuando no lo es. Su comprobación apunta solo al campo `severity`, así que ocurrencia y detección requieren la misma regla añadida con otro `field`; no fija rango de valores, de modo que no impone una escala de 1 a 10 ni juzga si la puntuación es adecuada. Una puntuación que no puede analizar también envía `FM-003` a `skipped`, porque el producto no puede recalcularse. |
| Una fila propone una acción, pero el responsable y la fecha límite están vacíos. | `FM-005` se ejecuta en toda fila cuya celda de acción recomendada esté rellena y exige `owner` (responsable) y `dueAt` (fecha límite); informa de la fila a la que le falta uno de los dos. Son los nombres canónicos tras resolver los alias, así que una hoja con otros encabezados necesita el alias en el mapeo de columnas o `requiredFields` ajustado. Comprueba que las dos celdas estén rellenas, no que la fecha sea realista ni que el responsable la haya aceptado. Las filas sin acción son competencia de `FM-004`. |
| Nuestra hoja nunca dice qué producto o proceso analiza. | `FM-007` lee el `item` de la cabecera y lo informa cuando falta el sujeto de análisis: un FMEA se realiza para un producto o proceso concreto y sin él las conclusiones no se pueden rastrear ni asociar a una tabla de puntuación. Es una comprobación de presencia: un sujeto relleno pero equivocado no se informa. Si sus hojas deben indicar también el método empleado, añada `method` a sus `fields`. |
| Algunas filas todavía dicen `待填` o `XXX` en la columna de modo de fallo, y otras no tienen nada. | `FM-008` informa de la fila cuyo modo de fallo aún contiene uno de los términos marcadores del paquete (`【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例`), porque una hoja copiada de una plantilla se lee como análisis terminado; solo lee la columna del modo de fallo, y `terms` se ajusta a su plantilla. `FM-001` informa de la fila en la que modo de fallo, efecto y causa están los tres vacíos, pero solo exige uno de los tres: una celda con `待填` satisface `FM-001` y la detecta `FM-008`. Ninguna de las dos juzga si los modos de fallo están completos o si los efectos se analizaron lo suficiente. |
| El informe muestra `FM-004` y `FM-006` como `skipped`. ¿Hay algún problema? | No. Ambas vienen sin configurar y el paquete lo informa en lugar de aprobar en silencio. El `threshold` de `FM-004` es `0`, que se lee como no configurado, así que ninguna fila cuenta como riesgo alto hasta que fije su criterio de riesgo: por ejemplo `triggerField: severity` con `threshold: 9`, o `triggerField: rpn` con `threshold: 100`. La lista `values` de `FM-006` está vacía, así que el vocabulario de estados no se comprueba hasta que enumere sus propios valores. Una vez configuradas, `FM-004` solo comprueba que la celda de acción de una fila de riesgo alto esté rellena —no que la acción sea eficaz o viable— y `FM-006` solo comprueba que el estado figure en la lista configurada, no que la acción se haya llevado a cabo. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-fmea-table-check
dsh --profile <name> --dump-config | grep 'dsh-fmea-table-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/fmea-table-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-fmea-table-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-fmea-table-check contributors.
