# Seven Coffee — Node.js / Vite website

A static website for Belfast and Uphall, preserving the new branding, location-specific socials, shared opening hours, Irish/local supplier copy and dog-friendly welcome.

This branch is `nodejs-vite-linode`, based on the latest `brand-refresh-uphall` branch. It replaces Django with HTML, CSS and a small JavaScript file. No Python, database, secret key, React, PM2 or production Node process is required. Node.js runs the development/build tools; Caddy serves the built files on Linode.

## 1. Test on your Mac

Install **Node.js 24.x** from https://nodejs.org/en/download (includes npm). If you already use nvm, run `nvm install` then `nvm use` inside this checkout; `.nvmrc` selects 24. Check `node --version` starts with `v24`.

For a separate checkout, which avoids disturbing your Django copy:

```bash
git clone --branch nodejs-vite-linode https://github.com/ledgey/seven.git seven-node
cd seven-node
npm ci
npm run dev
```

Open http://127.0.0.1:5173/. Changes to `index.html` and `src/brand.css` update the preview. Stop with Ctrl+C. If a port is already in use, stop the old process or use `npm run dev -- --port 5174`.

If switching your existing checkout instead, commit or stash your own changes first, then use `git fetch origin` and `git switch nodejs-vite-linode`. You can leave the Python environment with `deactivate`; it is not used here.

Test the actual production files before deploying:

```bash
npm run build
npm run check
npm run preview
```

Open http://127.0.0.1:4173/. Check desktop and phone-sized layouts, both shops' hours, all four social links and directions links. `npm run check` checks built asset references, anchors and key content; it does not verify third-party profile availability. `vite preview` is for local testing, not production hosting.

## 2. What to edit and how routing works

| File | Purpose |
| --- | --- |
| `index.html` | Copy, locations, hours, social links and metadata |
| `src/brand.css` | Brand styles and responsive layouts |
| `src/main.js` | Updates the copyright year |
| `public/images/` | Logos, favicon and photos |
| `deploy/Caddyfile.example` | Example HTTPS server configuration |
| `PHOTO-CREDITS.md` | Stock-photo sources |
| `dist/` | Generated deployment files; do not edit or commit |

Navigation uses `/#our-coffee`, `/#locations` and `/#socials`. No client-side router is needed. Unknown paths return 404 rather than silently loading the homepage. Old Django `/admin/` routes are not carried over. Future separate pages must be added as HTML build entries and built explicitly; this is not an automatic dynamic-routing framework.

The source branch referenced `coffee_photO.png` and `seven-favicon.png`, but neither file was committed. This branch uses the existing `latte-art.jpg` and `seven-favicon.svg` to avoid broken images. To use your replacements, add them under `public/images/`, change their references in `index.html`, and set the favicon MIME type correctly (`image/png` for PNG).

Existing Google Fonts and analytics snippets are preserved. Font loading and analytics require external network access. The old `UA-…` analytics ID has not been upgraded or verified; this conversion does not change tracking configuration.

## 3. Linode deployment approach

Build on your Mac and upload **only the contents of `dist/`**. The server does not need Node or npm. Caddy serves the files, redirects HTTP to HTTPS, and obtains/renews certificates when DNS and network access are correct.

The commands below assume **Ubuntu 24.04 LTS**, SSH access, and a user called `deploy` with sudo access. Replace `SERVER_IP` with your Linode IP address. The configuration uses your actual domains, with `https://seven-coffee.com` as the canonical address. No server reset or deployment is performed by this repository.

### Existing server versus a fresh server

**Existing server:** first back up site files, web-server configuration, any databases, environment settings and other hosted services. Record current DNS and the server's SSH port. Inspect the listeners with `sudo ss -ltnp` and services with `systemctl status nginx apache2 caddy --no-pager`. Do not overwrite an existing multi-site Caddyfile or stop a web server that serves other sites.

If nginx/Apache already owns ports 80/443, plan the handover before enabling Caddy. You can instead serve `dist/` using your existing web server and HTTPS setup; the build is independent of Caddy. The Caddy instructions below assume those ports are available. Stop the old server only during your planned cutover, after preserving its configuration and checking its other sites.

**Fresh server:** a Linode rebuild erases the server disk. Take and verify an off-server backup first. Select Ubuntu 24.04 LTS, add your SSH key, and follow the setup below. A new Linode alongside the old one lets you test before changing DNS. A rebuilt server will have a different SSH host key; verify the new fingerprint through Linode's console before replacing your known-hosts entry.

### Fresh-server user and firewall setup

Log in as root using your SSH key:

```bash
ssh root@SERVER_IP
apt update
apt upgrade -y
apt install -y sudo ufw curl gnupg ca-certificates
adduser deploy
usermod -aG sudo deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
install -m 600 -o deploy -g deploy /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
```

The key-copy command assumes root login already uses the public key you want for `deploy`. In a **second terminal**, verify `ssh deploy@SERVER_IP` and `sudo -v` work before closing your root connection.

On the server, permit SSH before enabling the firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 443/udp
sudo ufw enable
sudo ufw status
```

If SSH uses a nonstandard port, allow that actual TCP port before enabling UFW. If a Linode Cloud Firewall is attached, permit the same web ports there and allow SSH from your management IP. Caddy also needs outbound DNS and HTTPS access for certificate issuance. UDP 443 is optional for HTTP/3; TCP 80/443 must be reachable.

### Install Caddy on the server

Use Caddy's official stable package repository:

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

Installation starts a systemd service. If this server already has Caddy installed from this repository, skip repository setup. If installation reports ports in use, resolve the existing-server handover above rather than killing an unknown process.

### Build and upload from your Mac

Inside `seven-node`:

```bash
npm ci
npm run build
npm run check
tar -czf /tmp/seven-site.tar.gz -C dist .
scp /tmp/seven-site.tar.gz deploy@SERVER_IP:/home/deploy/seven-site.tar.gz
scp deploy/Caddyfile.example deploy@SERVER_IP:/home/deploy/seven-Caddyfile.example
```

### Install a versioned release on the server

Log in as `deploy`, then run:

```bash
SEVEN_RELEASE=$(date -u +%Y%m%dT%H%M%SZ)
sudo mkdir -p "/srv/seven/releases/$SEVEN_RELEASE"
sudo tar -xzf /home/deploy/seven-site.tar.gz -C "/srv/seven/releases/$SEVEN_RELEASE"
sudo chown -R root:root "/srv/seven/releases/$SEVEN_RELEASE"
sudo find "/srv/seven/releases/$SEVEN_RELEASE" -type d -exec chmod 755 {} +
sudo find "/srv/seven/releases/$SEVEN_RELEASE" -type f -exec chmod 644 {} +
sudo test -f "/srv/seven/releases/$SEVEN_RELEASE/index.html"
readlink /srv/seven/current || true
sudo ln -s "/srv/seven/releases/$SEVEN_RELEASE" /srv/seven/current.next
sudo mv -Tf /srv/seven/current.next /srv/seven/current
```

Record the old `current` target printed by `readlink` for rollback. The final rename atomically switches the website. `/srv/seven/current` must be a symlink (or absent on first deployment), not a real directory. If `current.next` already exists from an interrupted deployment, inspect it before removing that temporary symlink and retrying. Keep old release directories until you are happy with the update.

### DNS and HTTPS

The canonical website is **https://seven-coffee.com**. The other five hostnames redirect permanently to it, preserving the path and query string. HTTP requests are upgraded to HTTPS automatically. Domain names are case-insensitive, so `SevenCoffee.co.uk` and `sevencoffee.co.uk` behave identically.

Configure these records at the authoritative DNS provider for **each** domain:

| DNS zone | Name | Type | Value |
| --- | --- | --- | --- |
| seven-coffee.com | @ | A | Your Linode IPv4 address |
| seven-coffee.com | www | CNAME | seven-coffee.com |
| seven-belfast.co.uk | @ | A | Your Linode IPv4 address |
| seven-belfast.co.uk | www | CNAME | seven-coffee.com |
| sevencoffee.co.uk | @ | A | Your Linode IPv4 address |
| sevencoffee.co.uk | www | CNAME | seven-coffee.com |

Some DNS providers use a blank name instead of `@`. A CNAME cannot coexist with other records at the same name: replace conflicting `www` records, rather than adding duplicates. Do not use a standard CNAME at the root domain. DNS directs requests to the server; **Caddy performs the address-bar redirect**, so DNS records alone are not sufficient.

Only retain AAAA records if IPv6 reaches this same server and the firewall allows it. Remove stale AAAA records on all six hostnames. Keep mail/MX and unrelated records unchanged. If using a DNS proxy, initially use DNS-only mode to test direct access. Restrictive CAA records must permit Caddy's certificate issuer. Disable any old registrar URL-forwarding service for these hostnames once using this setup.

All six hostnames need valid HTTPS certificates, including those that only redirect. Caddy obtains and renews these automatically once their DNS resolves to the Linode and public TCP 80/443 reaches Caddy. Do not enable this configuration until all six names are ready; otherwise certificate issuance for unconfigured names will fail.

On the server, review the supplied configuration (the domain names are already filled in) and back up your existing file:

```bash
nano /home/deploy/seven-Caddyfile.example
sudo cp -a /etc/caddy/Caddyfile /etc/caddy/Caddyfile.before-seven
```

On a fresh, dedicated server, install the file:

```bash
sudo install -m 644 /home/deploy/seven-Caddyfile.example /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo systemctl enable --now caddy
sudo systemctl reload caddy
```

On a shared/existing Caddy server, add both supplied site blocks to its existing Caddyfile and preserve unrelated blocks. Avoid duplicate blocks for the same domain. Run validation after editing and **do not reload if validation fails**.

No Certbot commands or manual certificate files are required. No public access to ports 5173 or 4173 is needed.

### Verify deployment

From your Mac:

```bash
curl -I http://seven-coffee.com
curl -I https://seven-coffee.com
curl -I https://seven-coffee.com/images/seven-green.webp
curl -I https://seven-coffee.com/not-a-real-page

for domain in www.seven-coffee.com seven-belfast.co.uk www.seven-belfast.co.uk sevencoffee.co.uk www.sevencoffee.co.uk; do
  curl -I "https://$domain/?source=redirect-test"
  curl -IL "http://$domain/?source=redirect-test"
done
```

Expect an HTTP-to-HTTPS redirect, 200 for the canonical homepage and logo, and 404 for the missing page. Each alternate HTTPS hostname should return 301 with `Location: https://seven-coffee.com/?source=redirect-test`; the HTTP chain should ultimately end at that same address. The target homepage should return 200. Unknown paths remain unchanged by the redirect and can still return 404 on the main site.

Open all six addresses in a browser to confirm HTTPS and the final address bar. Also test navigation, mobile layout and both shops' links. A certificate for a domain is not a certificate for its raw IP address.

For diagnostics on the server:

```bash
sudo systemctl status caddy --no-pager
sudo journalctl -u caddy --since '15 minutes ago' --no-pager
sudo -u caddy test -r /srv/seven/current/index.html
```

- Certificate failures: check A/AAAA records, CAA restrictions, both firewalls, ports in use and Caddy logs. Avoid repeatedly restarting certificate requests.
- 403/404 for existing files: check the `current` symlink, directory traversal/read permissions and extraction location.
- Broken local setup: use Node 24, run `npm ci`, and check that you're on `nodejs-vite-linode`.

## 4. Updating and rolling back

For later releases, on your Mac run `git pull --ff-only`, then repeat **Build and upload** and **Install a versioned release**. Caddy does not need a restart when only site files change. Test after each release. Node dependency updates should be deliberate; commit the updated lockfile and rebuild.

To roll back, use the exact previous release path recorded earlier:

```bash
sudo ln -s /srv/seven/releases/PREVIOUS_RELEASE /srv/seven/current.rollback
sudo mv -Tf /srv/seven/current.rollback /srv/seven/current
```

Replace `PREVIOUS_RELEASE` before running. Confirm its `index.html` exists first. If you changed Caddy's configuration too, restore the saved configuration, validate it and reload Caddy. A rollback cannot restore an erased Linode disk; keep your off-server backups.

## References

- [Vite local setup](https://vite.dev/guide/)
- [Vite build and preview](https://vite.dev/guide/static-deploy)
- [Caddy installation](https://caddyserver.com/docs/install)
- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https)
- [Caddy static files](https://caddyserver.com/docs/quick-starts/static-files)
