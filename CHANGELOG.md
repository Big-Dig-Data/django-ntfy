# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.0] - 2023-11-16

### Added
- NtfyBackend with topic, icon, tags, actions and priority signals
- NtfyBackendExponentialRateLimitBackend - NtfyBackend wit exponential rate limit
- SmtpExponentialRateLimitEmailBackend - django's smtp.EmailBackend with exponentila rate limt
- ExponentialRateLimitBackends - backend which groups multiple email backends into one and adds exponential rate limit
