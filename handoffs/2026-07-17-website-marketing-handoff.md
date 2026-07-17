# Handoff — 2026-07-17 · Sito: analytics, share e anteprime social

## Obiettivo della sessione
Rendere il sito pronto al lancio: monitorare gli accessi, migliorare i pulsanti di
condivisione e ottenere anteprime social ricche quando si condividono i link.

## Fatto (tutto pubblicato su `main`)
| Commit | Contenuto |
|--------|-----------|
| `1ac648a` | Cloudflare Web Analytics (beacon) in tutte le 15 pagine pubbliche |
| `bcb100d` | Pulsanti share con post pre-compilati: #FabricArcade + #Gioco + link |
| `8bb8a9a` | Open Graph/Twitter Card + 6 social card 1200×630 per gioco |
| `18b6db2` | Card hub + Open Graph su home e 6 pagine feature |

- **Analytics:** token Cloudflare inserito e attivo. Dashboard: dash.cloudflare.com → Web Analytics.
- **Share:** logica in `website/js/feedback.js` (nome gioco dall'`<h1>`). LinkedIn=compositore
  `feed/?shareActive=true`, X=`intent/tweet` con `hashtags=`, Reddit=`title`.
- **Anteprime:** meta OG con URL ASSOLUTI GitHub Pages; card generate da `dev/gen_social_cards.py`
  in `website/images/social/`.

## Verificato
- OG tag + immagine live e corretti (HTTP 200) su monster-breach; card LinkedIn OK dopo Post Inspector.
- href dei pulsanti share testati in browser: corretti su tutte le 6 pagine gioco.

## Punti di attenzione
- **Cache LinkedIn (~7gg):** per gli URL condivisi PRIMA degli OG tag serve il
  [Post Inspector](https://www.linkedin.com/post-inspector/) una volta per URL. I nuovi mostrano la card subito.
- `shareActive` di LinkedIn è un endpoint **non documentato**: se cambia, fallback a `share-offsite?url=`.
- `netlify.toml` è presente ma NON usato (il sito è su GitHub Pages).

## Open loops (vedi `actions/action-register.md`)
- #4 Giscus (repo-id/category-id) · #6 piano editoriale LinkedIn · #7 fix job `deploy-website`
- #8 4 test preesistenti falliti · #9 trattamento racing agli altri giochi RTI
- #10 riscaldare le anteprime social prima del lancio

## Prossima azione suggerita
Preparare/rifinire i testi dei post di lancio (`marketing/posts/00-launch.md`) ora che
anteprime e share sono pronti, poi eseguire il piano editoriale del 2026-07-20.

## Per aggiungere un nuovo gioco (checklist sito)
1. Pagina in `website/games/<slug>.html` con `<h1>` = nome gioco + snippet Cloudflare prima di `</body>`.
2. Aggiungi il gioco alla lista `GAMES` in `dev/gen_social_cards.py` e rilancia lo script.
3. Aggiungi i meta OG/Twitter (URL assoluti) nella `<head>` puntando a `images/social/<slug>.png`.
4. Includi `../js/feedback.js` e i pulsanti `share-linkedin`/`share-x`/`share-reddit`.
