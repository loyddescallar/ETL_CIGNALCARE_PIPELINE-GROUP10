# CignalCare+ Lab 4 — S-01 Transformation Results

## Rule

- **Rule ID:** `S-01`
- **Rule Version:** `S-01-v1.0.0`
- **Rule Type:** Standardization
- **Target:** `troubleshoot_outcomes.model_id`, `troubleshoot_outcomes.model_name`
- **Canonical Output:** `canonical_model_id`

## Input

- **Parent extraction batch:** `20261018T170820026121Z`
- **Input file:** `C:\Users\loydd\Downloads\ETL_CIGNALCARE_PIPELINE-GROUP10\data\extracted\20261018T170820768165Z_troubleshoot_outcomes.csv`
- **Input records:** 138
- **Input SHA-256:** `ad6dda69cd0f5904ca7fc964090005aadf7e5a19f7154f4b8274cf960fec0085`

## Processing Results

- **Records read:** 138
- **Records output:** 138
- **Records rejected/quarantined:** 0
- **Records modified by S-01:** 138
- **Issue-affected source records:** 137
- **Issue-affected percentage:** 99.28%
- **Distinct canonical models:** 6

## Model Standardization Mapping

| Standardized Model Name | Canonical Model ID | Source Model IDs | Records |
|---|---|---|---:|
| Arion HD Cardless Zapper | `model_arion_hd_cardless_zapper` | model_1, model_2, model_4, model_6, model_8 | 30 |
| Changhong Silver HD | `model_changhong_silver_hd` | changhong-silver-hd, model_1, model_3, model_5, model_7 | 20 |
| GIEC HD | `model_giec_hd` | model_1, model_3, model_5, model_7 | 23 |
| Humax HD | `model_humax_hd` | model_1, model_3, model_5, model_7 | 21 |
| Pace HD | `model_pace_hd` | model_2, model_4, model_6, model_8 | 24 |
| Samsung HD | `model_samsung_hd` | model_2, model_4, model_6, model_8 | 20 |

## Output

- **Transformed output:** `C:\Users\loydd\Downloads\ETL_CIGNALCARE_PIPELINE-GROUP10\data\transformed\20261023T055811218622Z_S01_troubleshoot_outcomes.csv`
- **Quarantine:** None
- **Output SHA-256:** `f97776d421369b28c4af56859dda9ff9a714491b8d25e459bcc9d486ef66ea32`

## Validation

- **Validation status:** **PASS**
- **Record reconciliation:** 138 = 138 + 0
- **Source values preserved:** PASS
- **Output ID uniqueness:** PASS
- **Model name → canonical ID:** PASS
- **Canonical ID → model name:** PASS
- **Deterministic canonicalization:** PASS

## Execution

- **Run ID:** `TRN-20261023T055811210068Z`
- **Started:** `2026-10-23T05:58:11.210Z`
- **Finished:** `2026-10-23T05:58:11.250Z`
- **Duration:** 0.040 seconds
- **Status:** `PASS`
