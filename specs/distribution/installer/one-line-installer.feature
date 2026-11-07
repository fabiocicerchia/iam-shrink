@domain:distribution @area:installer @from:iam-shrink/install
Feature: Installing iam-shrink with the one-line installer
  Lets an operator install the iam-shrink CLI from GitHub with a single piped command, without cloning the repository.

  Background:
    Given the operator runs the installer script published at https://raw.githubusercontent.com/fabiocicerchia/iam-shrink/main/install.sh

  @id:distribution.installer.001 @rule:distribution.installer.prefers-pipx-then-user-pip @inferred @source:install.sh#install.sh
  Scenario Outline: The installer uses pipx when present and falls back to a per-user pip install
    Given <installer> is the Python package installer available on the operator's machine
    When the operator runs the installer
    Then iam-shrink is installed with "<install_command>"
    And the operator sees "iam-shrink installed. Run: iam-shrink --help"

    Examples:
      | installer                   | install_command                                                     |
      | pipx                        | pipx install git+https://github.com/fabiocicerchia/iam-shrink       |
      | pip only (pipx not on PATH) | pip install --user git+https://github.com/fabiocicerchia/iam-shrink |

  @id:distribution.installer.002 @rule:distribution.installer.failure-stops-without-success-message @inferred @source:install.sh#install.sh
  Scenario: A failed installation stops the installer without claiming success
    Given the package installer cannot install iam-shrink, for example because GitHub is unreachable or pip is missing
    When the operator runs the installer
    Then the installer exits with a non-zero status
    And the operator does not see "iam-shrink installed. Run: iam-shrink --help"

  @id:distribution.installer.003 @rule:distribution.installer.installs-unpinned-default-branch @inferred @source:install.sh#install.sh @questionable
  Scenario: The installer installs whatever is on the repository's default branch, not a released version
    Given the default branch of github.com/fabiocicerchia/iam-shrink contains unreleased changes
    When the operator runs the installer
    Then the installed iam-shrink is built from the current default branch
    And no release tag, version or checksum is verified
