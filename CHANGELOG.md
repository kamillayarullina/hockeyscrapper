# Changelog

## [1.5.0]

### Added
- Added email notification
- Added Architecture Decision Records (ADR-001, ADR-002, ADR-003)
- Email now shows source site name instead of generic link
- Team name matching now supports grammatical cases (e.g. "Спартака")

### Fixed
- Fixed parser crash: `run()` signature made compatible with `ParserRunner` caller
- Removed duplicate match persistence in parser (runner already saves)
- Moved heavy imports to local scope to avoid circular import risk and slow startup
- Team matcher no longer misses inflected team names in titles

## [1.4.3]

### Added
- Interface improving

## [1.4.2]

### Added
- Profile avatar adding

## [1.4.1]

### Added
- Added validation of password

## [1.4.0]

### Added
- Added password recovery

## [1.3.1]

### Added
- Team icons to the team subscriptions

## [1.3.0]

### Added
- telegram account can be linked to web account
- telegram bot

## [1.2.0]

### Added
- account registration
- subscription to the teams

## [1.1.0]

### Added
- Main, Register and Enter pages
