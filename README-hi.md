# dsh-fmea-table-check — FMEA कार्यपत्रक के तत्वों की पूर्णता और जोखिम प्राथमिकता संख्या की संगति की जाँच

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-fmea-table-check` एक FMEA कार्यपत्रक पढ़ता है — पंक्तियाँ शीट के अपने स्तंभ-नामों से जुड़ी, चीनी या अंग्रेज़ी में — और उसमें वह जाँचता है जो एक शीट से यांत्रिक रूप से अपेक्षित किया जा सकता है: क्या विश्लेषण-शृंखला दर्ज है, क्या `severity`, `occurrence` और `detection` के अंक संक्रियात्मक संख्याएँ हैं, क्या `rpn` उनके गुणनफल के बराबर है, क्या ऊँचे जोखिम वाली पंक्ति में ज़िम्मेदार और समय-सीमा सहित सुझाई गई कार्रवाई है, क्या कार्रवाई की स्थितियाँ आपकी अपनी शब्दावली से आती हैं, और क्या विफलता-प्रकार स्तंभ में कोई टेम्पलेट प्लेसहोल्डर शेष नहीं है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-fmea-table-check: real output over its FM-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-fmea-table-check/main/docs/assets/dsh-fmea-table-check-demo.png)

इस प्लगइन का अपने ही `FM-002` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| `rpn` का मान severity × occurrence × detection के बराबर नहीं है — क्या यह पकड़ में आता है? | हाँ। `FM-003` severity × occurrence × detection से `rpn` दोबारा निकालता है, सहनशीलता `0`, और जिस पंक्ति का दर्ज मान उससे भिन्न हो उसे दर्ज करता है। यह तभी चलता है जब चारों खानों में पढ़ने योग्य संख्याएँ हों; occurrence का अंक संख्या न हो तो यह नियम पास होने के बजाय `skipped` बताता है। AIAG-VDA पुस्तिका पर बनी शीट RPN के बजाय AP से अंक देती है: `resultField` और `factorFields` बदलें, या यह नियम बंद कर दें। |
| severity के खाने में अंक के बजाय `高` लिखा है। क्या होगा? | `FM-002` अपेक्षा करता है कि severity एक संक्रियात्मक धनात्मक संख्या हो, और ऐसा न होने पर उस पंक्ति को दर्ज करता है। इसकी जाँच केवल `severity` क्षेत्र को देखती है, इसलिए occurrence और detection के लिए वही नियम दूसरे `field` के साथ जोड़ना पड़ेगा; यह कोई अंक-सीमा तय नहीं करता, इसलिए 1 से 10 का पैमाना लागू नहीं करता और अंक उचित है या नहीं यह नहीं आँकता। जो अंक पढ़ा न जा सके वह `FM-003` को भी `skipped` में भेजता है, क्योंकि गुणनफल दोबारा नहीं निकाला जा सकता। |
| एक पंक्ति में कार्रवाई सुझाई गई है, पर ज़िम्मेदार और समय-सीमा खाली हैं। | `FM-005` हर उस पंक्ति पर चलता है जिसमें सुझाई गई कार्रवाई का खाना भरा है, और `owner` तथा `dueAt` दोनों की अपेक्षा करता है; जिस पंक्ति में एक भी न हो उसे दर्ज करता है। ये alias हल होने के बाद के मानक नाम हैं, इसलिए दूसरे शीर्षकों वाली शीट के लिए alias स्तंभ-मानचित्रण में जोड़ें या `requiredFields` बदलें। यह देखता है कि दोनों खाने भरे हैं — यह नहीं कि समय-सीमा व्यावहारिक है या ज़िम्मेदार ने उसे स्वीकार किया है। कार्रवाई खाली वाली पंक्तियाँ `FM-004` के दायरे में हैं। |
| हमारी शीट में कहीं नहीं लिखा कि यह किस उत्पाद या प्रक्रिया का विश्लेषण है। | `FM-007` शीट-शीर्ष के `item` को पढ़ता है और विश्लेषण-विषय न होने पर उसे दर्ज करता है: FMEA किसी विशिष्ट उत्पाद या प्रक्रिया के लिए किया जाता है, और उसके बिना निष्कर्ष न पीछे तक जोड़े जा सकते हैं न किसी अंकन-तालिका से मिलाए जा सकते हैं। यह उपस्थिति की जाँच है: भरा हुआ पर गलत विषय दर्ज नहीं होता। यदि आपकी शीट में प्रयुक्त विधि भी लिखनी हो, तो उसके `fields` में `method` जोड़ें। |
| कुछ पंक्तियों के विफलता-प्रकार खाने में अब भी `待填` या `XXX` लिखा है, और कुछ में कुछ भी नहीं। | `FM-008` उस पंक्ति को दर्ज करता है जिसके विफलता-प्रकार खाने में अब भी इस नियम-संग्रह के प्लेसहोल्डर शब्दों में से कोई है (`【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo`, `示例`), क्योंकि टेम्पलेट से उतारी गई शीट पूरी हो चुकी जाँच जैसी पढ़ी जाती है; यह केवल विफलता-प्रकार स्तंभ देखता है, और `terms` आपके टेम्पलेट के अनुसार बदले जा सकते हैं। `FM-001` उस पंक्ति को दर्ज करता है जिसमें विफलता-प्रकार, परिणाम और कारण तीनों खाली हैं, पर वह तीनों में से एक भरे होने की ही अपेक्षा करता है — `待填` लिखा खाना `FM-001` पास कर देता है और `FM-008` उसे पकड़ता है। दोनों में से कोई यह नहीं आँकता कि विफलता-प्रकार पूरे हैं या परिणाम पर्याप्त विश्लेषित हैं। |
| रिपोर्ट में `FM-004` और `FM-006` `skipped` दिख रहे हैं। क्या कुछ गड़बड़ है? | नहीं। दोनों बिना कॉन्फ़िगर के आते हैं और नियम-संग्रह चुपचाप पास होने के बजाय यही बताता है। `FM-004` का `threshold` `0` है, जिसका अर्थ अकॉन्फ़िगर है, इसलिए जब तक आप अपना जोखिम-मानदंड तय न करें कोई पंक्ति ऊँचे जोखिम में नहीं गिनी जाती — उदाहरण `triggerField: severity` के साथ `threshold: 9`, या `triggerField: rpn` के साथ `threshold: 100`। `FM-006` की `values` सूची खाली है, इसलिए अपनी शब्दावली दर्ज करने तक कार्रवाई-स्थिति के मान जाँचे नहीं जाते। कॉन्फ़िगर होने पर `FM-004` केवल यह देखता है कि ऊँचे जोखिम वाली पंक्ति का कार्रवाई-खाना भरा है — यह नहीं कि कार्रवाई प्रभावी या व्यवहार्य है — और `FM-006` केवल यह देखता है कि स्थिति दर्ज सूची में है, यह नहीं कि कार्रवाई वास्तव में लागू हुई। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-fmea-table-check
dsh --profile <name> --dump-config | grep 'dsh-fmea-table-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/fmea-table-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-fmea-table-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-fmea-table-check contributors.
