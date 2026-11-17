---
id: interface
title: Language, theme and mobile
---

# Language, theme and mobile

## Language

The selector at the top switches between **Portuguese** and **English**. The choice is also sent to the API, which returns the sign messages in the same language. It is the **only** thing the app stores in the browser.

![Result in English](/img/screenshots/app-resultado-empresa-en.png)

## Light and dark theme

The app follows the system theme, with enough contrast in both.

![Result in the dark theme](/img/screenshots/app-escuro-en.png)

## On mobile

The layout adapts to narrow screens: the menu gets its own row and the data stacks.

![Result on mobile](/img/screenshots/app-celular-en.png)

## Other pages

**Explore** (open-data explorer; see [Explore open data](explorar.md)):

![Explore page](/img/screenshots/app-explorar-en.png)

**API and CLI** (API usage examples; the CLI arrives in M4):

![API and CLI page](/img/screenshots/app-api-en.png)

**Privacy** (plain-language summary of the policy):

![Privacy page](/img/screenshots/app-privacidade-en.png)

## Accessibility and browser privacy

There is a skip-to-content link, visible focus, labels on every field, the result is announced to screen readers and focus moves to the result heading. Fields use `autocomplete="off"`, the lookup never goes into the URL and the page sends `Referrer-Policy: no-referrer`. The build includes a Content Security Policy (CSP) that only allows resources from the site itself: no CDN, no external fonts.
