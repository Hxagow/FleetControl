# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added


### Changed


### Fixed


---


## [0.0.1] - 2025-12-12
### Added
- Invitation roles now exist end-to-end: new role field on invitations, selection in the invite form, automatic persistence when creating invites, and role-aware acceptance logic.
- Invitations surface their assigned role everywhere (members list, pending invitation table, notification emails) so admins know the expected permissions before accepting.
- Invitation emails and UI now display a delete action, enabling admins to revoke pending invites directly from the dashboard.
- Global toast notifications and supporting styles provide consistent feedback for invitation actions and other system messages.

### Changed
- Invitation and member management UIs received multiple layout/style passes: centered action columns, improved badges, clarified wording, and consistent button sizing.
- Invitation messages explicitly mention the organization and apply the Europe/Paris timezone to all timestamps for clarity.
- Role downgrade/promote buttons and invitation controls share the same button styling for visual consistency across actions.
- Duplicate role-update checks in invitation views were removed to simplify the flow.

### Fixed
- The “Rétrograder” action now uses the shared button theme, preventing the mismatched gray button that previously appeared in the members table.
- Miscellaneous styling regressions around invitation status/role chips and action alignment were resolved while tuning the UI.
