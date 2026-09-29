# RB — ReBorN tracker (E4K Polska 1)

Statyczna strona + automatyczne snapshoty sojuszu **- ReBorN -** (AID **115**).

- Serwer: `EmpirefourkingdomsExGG2_3` (E4K PL1)
- API: `https://empire-api.fly.dev/EmpirefourkingdomsExGG2_3/ain/%22AID%22:115`
- Ranking w grze / empire-rankings: tryb **E4K** → **druga** „Pologne 1”

## Co robi

1. `scripts/fetch_reborn.py` pobiera 63 graczy (honor, moc, łupy).
2. Zapisuje `data/latest.json` (+ porównanie z poprzednim = aktywność).
3. `index.html` wyświetla tabelę (GitHub Pages).
4. GitHub Action odświeża dane co ~15 minut.

## Link po wdrożeniu

`https://TWOJ_NICK.github.io/reborn-tracker/`
