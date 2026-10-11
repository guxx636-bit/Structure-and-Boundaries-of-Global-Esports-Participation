# Data collection (provenance only)

Nothing in this folder is needed to reproduce any table or figure in the paper.
It documents where the raw country-level values came from, so that a reader can
audit the inputs to `esports_sem_final_v2.csv`.

| File | What it records |
|---|---|
| `step1_worldbank.py` | Pulls internet penetration (`IT.NET.USER.ZS`) and GDP per capita (`NY.GDP.PCAP.CD`) from the World Bank Open Data API. |
| `worldbank_verified.csv`, `worldbank_real.csv` | Frozen World Bank extracts used for the three-year averages. |
| `hofstede.csv` | Hofstede six-dimension matrix (2015) as used in the cultural-openness composite. |
| `players_raw.csv` | Raw Liquipedia player counts by nationality, as returned by the API. |
| `mobile_tourneys.json`, `mobile_prizepool.json` | Mobile-title tournament counts and prize pools (League of Legends, Valorant, Dota 2, Counter-Strike, Mobile Legends, PUBG Mobile; S-Tier and A-Tier; Jan 2022 - Jul 2026). |
| `liquipedia_fields.json` | Field list used for the LiquipediaDB API v3 queries. |
| `step5_liquipedia_collect.py`, `rebuild_final.py` | The collection and assembly scripts. **The Liquipedia API key has been removed** from these archived copies; it is read from the `LIQUIPEDIA_API_KEY` environment variable. The frozen output of `rebuild_final.py` is `esports_sem_final_v2.csv` in the repository root. |
| `esports_sem_data_collection.py` | Early collection scaffold, kept for completeness. |

## Not scriptable

The outcome variable is the country-level all-time **peak viewers** figure taken
from the Esports Charts interactive map. That figure is read off an interactive
map rather than an API, so it was extracted manually on 6 July 2026 and
independently re-verified on 7 July 2026; the extracted values are the
`Viewership_*` column of `esports_sem_final_v2.csv`. No discrepancies were found
between the two readings.

## Licensing

Liquipedia-derived fields are used under CC BY-SA 3.0 and must keep that
attribution if redistributed. World Bank fields are CC BY 4.0.
