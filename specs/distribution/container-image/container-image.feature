@domain:distribution @area:container-image @from:iam-shrink/dockerfile
Feature: Running iam-shrink from the container image
  Lets operators run the iam-shrink CLI from a Docker image without a local Python install, under an unprivileged account.

  Background:
    Given the operator has the iam-shrink container image

  @id:distribution.container-image.001 @rule:distribution.container-image.runs-cli-as-entrypoint @inferred @source:Dockerfile#ENTRYPOINT
  Scenario: The container image runs the iam-shrink command with the arguments it is given
    When the operator runs the image with the arguments "analyze app-role --usage events.json"
    Then the iam-shrink command runs with "analyze app-role --usage events.json"
    And its output and exit status are those of the iam-shrink CLI

  @id:distribution.container-image.002 @rule:distribution.container-image.runs-as-non-root @inferred @source:Dockerfile#USER
  Scenario: The CLI in the container runs as an unprivileged user, not root
    When the operator runs the image without overriding the user
    Then the iam-shrink process runs as user "app" with uid 10001
    And the process does not have root privileges inside the container
