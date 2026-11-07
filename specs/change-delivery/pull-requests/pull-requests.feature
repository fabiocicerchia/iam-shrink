@domain:change-delivery @area:pull-requests @from:iam-shrink/iam-shrink
Feature: Opening a pull request with the proposed change
  Lets an operator running inside their IaC repo turn the Terraform proposal straight into a reviewable pull request.

  Background:
    Given the operator is in a clone of the IaC repository with git and gh signed in

  @id:change-delivery.pull-requests.001 @rule:pr.open-with-tf-diff @verified @source:iam_shrink.py#open_pr @test:tests/test_iam_shrink.py#test_open_pr_writes_file_and_shells_out_in_order
  Scenario: The Terraform proposal is committed on its own branch and opened as a pull request
    When the operator analyzes "my-app-role" with format "tf-diff" and asks to open a pull request
    Then the file "my-app-role-minimized.tf" holds the Terraform
    And it is committed as "iam-shrink: minimize my-app-role" on branch "iam-shrink/my-app-role" and pushed
    And a pull request titled "iam-shrink: minimize my-app-role" is opened
    And the Terraform is printed on standard output and the pull request URL on standard error

  @id:change-delivery.pull-requests.002 @rule:pr.failed-step-aborts @gap @source:iam_shrink.py#_run_checked @questionable
  Scenario: A failing git or gh step stops the pull request and leaves earlier steps in place
    Given a branch "iam-shrink/my-app-role" already exists
    When the operator analyzes "my-app-role" with format "tf-diff" and asks to open a pull request
    Then no pull request is opened and no URL is printed
    And the Terraform has already been printed on standard output
    And "my-app-role-minimized.tf" remains written in the working tree
    And the command exits with a non-zero status and an error traceback
