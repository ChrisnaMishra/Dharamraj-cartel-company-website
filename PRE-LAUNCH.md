# Dharamraj Cartel — Pre-launch checklist

This is a static website. Product enquiries open WhatsApp with a prepared message; there is no online checkout, payment processing, inventory database, or order-management backend.

## Branch workflow

- `main` is intended to be the public/production version.
- `development` is the working branch for design and code changes.
- Review and test changes on `development` before merging a pull request into `main`.
- Before connecting a paid domain, check **Settings → Pages** and confirm which branch/folder is actually being published.

## Current website structure

- `index.html` — homepage, retail Store, import/export information, enquiry form, contact.
- `products.html` — searchable/filterable construction and hardware catalogue.
- `favicon.svg`, `logo-emblem.svg`, and the bull emblem image — brand artwork.
- `product-placeholder.svg` — local fallback artwork for catalogue images that fail to load.

## Checks to complete before public launch

- [ ] Test the homepage, Store, product search/filter, enquiry form, and WhatsApp buttons on desktop and a real phone.
- [ ] Confirm the WhatsApp number is correct and belongs to the business.
- [ ] Confirm the products shown can actually be sourced; add accurate specifications, prices, stock status, delivery details, and warranty/return terms where relevant.
- [ ] Confirm all photos are owned, licensed, or used with permission. Several catalogue and Store photos are remotely hosted; use controlled, properly licensed assets for a production launch.
- [ ] Verify every public claim about response times, supplier verification, quality checks, trade terms, and documentation before publishing it as a guarantee.
- [ ] Add verified business contact details and any required business/registration details. Do not publish guessed or unverified information.
- [ ] Add suitable privacy, terms, delivery, cancellation/return, and warranty information for the actual business model.
- [ ] After choosing the domain, update the site’s canonical URL, social-sharing image/metadata, sitemap, and robots file to the final domain.
- [ ] Run a final link, image, and responsive-layout review after the domain is connected.

## Connecting a custom domain

Follow GitHub’s current official instructions: [Managing a custom domain for a GitHub Pages site](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

In general, verify control of the domain, add it in the repository’s **Settings → Pages**, then configure the DNS records at the domain provider. Enable HTTPS when GitHub Pages makes it available. Do not configure DNS for a domain until you have selected and verified the exact domain name.
