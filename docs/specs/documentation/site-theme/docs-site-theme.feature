@domain:documentation @area:site-theme @from:stylesheets/extra
Feature: Branding the documentation site
  Gives readers of the iam-shrink docs and splash page one consistent, offline-safe visual identity in both light and dark schemes.

  Background:
    Given the iam-shrink documentation site is published with its splash page at / and the rendered docs at /docs/

  @id:docs.documentation.site-theme.001 @rule:docs.theme.single-accent-palette @inferred @source:docs/stylesheets/extra.css#:root @questionable
  Scenario: The splash page and the docs share one orange-red accent palette
    Given the theme's accent pair is orange #fb923c and red #ef4444
    When a reader opens the splash page and then the rendered docs
    Then the docs primary colour and links on a light background use red #ef4444
    And the interactive accent and feature-card icons use orange #fb923c
    And the home hero title and primary buttons show an orange-to-red gradient
    And the splash page title and its GitHub button show the same orange-to-red gradient

  @id:docs.documentation.site-theme.002 @rule:docs.theme.no-network-assets @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: The docs theme loads no web fonts or third-party assets
    Given a reader's browser has no access to font or CDN hosts
    When the reader opens any docs page
    Then text renders in the operating system's own sans-serif font
    And code renders in the operating system's own monospace font
    And the page requests no font, CDN or analytics resource

  @id:docs.documentation.site-theme.003 @rule:docs.theme.dark-scheme-legibility @inferred @source:docs/stylesheets/extra.css#[data-md-color-scheme="slate"]
  Scenario Outline: Links switch to the accent colour that stays readable on each scheme
    Given the reader's scheme is <scheme>
    When the reader views a docs page
    Then the page background is <background>
    And links are shown in <link colour>

    Examples:
      | scheme | background                                    | link colour    |
      | light  | the theme's default white                     | red #ef4444    |
      | dark   | near-black #0b0f1a, including header and tabs | orange #fb923c |

  @id:docs.documentation.site-theme.004 @rule:docs.theme.no-placeholder-logo @inferred @source:docs/stylesheets/extra.css#.md-header__button.md-logo
  Scenario: The docs show no stand-in logo while the project has none
    Given the project has no logo configured
    When a reader views the docs header and navigation
    Then no logo icon is shown in the header
    And no logo icon is shown in the navigation title
