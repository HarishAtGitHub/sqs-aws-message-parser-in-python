from common.task.task import Task

class JiraIssueCreatorTask(Task):

    @classmethod
    def run(cls, data):
        try:
            from jira import JIRA
            import os
            jira = JIRA(server=os.environ['JIRA_SERVER_URL'], basic_auth=(os.environ['JIRA_USERNAME'],
                                                                    os.environ['JIRA_PASSWORD']))

            new_issue = jira.create_issue(project=os.environ['JIRA_PROJECT_KEY'], summary=data,
                                      description=data, issuetype={'name': os.environ['JIRA_ISSUE_TYPE']})
        except Exception as e:
            return False

        print("Jira issue creation successful")
        return True
