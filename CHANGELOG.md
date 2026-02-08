# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-08

### Added

- **General-purpose proxying:** no longer limited to Telegram. Any hostname can be proxied.
- `hosts` parameter — specify a list of hostnames to intercept.
- `intercept_all` parameter — route every outgoing request through the forwarder.
- `get_intercepted_hosts()` — query which hosts are currently being intercepted.
- Loop guard — requests to the forwarder itself are never intercepted.
- New examples: `general_api_proxy.py`, `intercept_all.py`, `mixed_bot.py`.
- Expanded test suite (24 tests covering all modes).

### Changed

- `extra_hosts` is now deprecated in favor of `hosts`.
- Default behavior unchanged: without `hosts`/`intercept_all`, only `api.telegram.org` is intercepted.

## [1.0.0] - 2026-02-08

### Added

- Initial release.
- `setup_proxy()` — activate the Telegram proxy with a single function call.
- `disable_proxy()` — deactivate the proxy and restore direct access.
- `is_active()` — check whether the proxy is currently active.
- `get_proxy_url()` — retrieve the current forwarder base URL.
- Transparent monkey-patching of `requests.Session.request`.
- Support for all Telegram Bot API methods (messages, photos, files, inline, callbacks, …).
- Support for both **polling** and **webhook** modes.
- Thread-safe header/param copying.
- Dual authentication headers (`Authorization: Bearer` + `X-Api-Token`).
- `extra_hosts` parameter for intercepting additional domains.
- Comprehensive examples (echo bot, photo bot, environment variables, webhook).
- Full test suite with `pytest` + `responses`.
