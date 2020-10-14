# encoding:utf-8
from __future__ import absolute_import

import requests
from sentry import tagstore
from sentry.plugins.bases import notify
from sentry.utils import json
from sentry.utils.http import absolute_uri
from sentry.integrations import FeatureDescription, IntegrationFeatures
from sentry_plugins.base import CorePluginMixin


class DingtalkPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = "Sentry Dingtalk Bot"
    slug = "sentry-dingtalk"
    description = "Post notifications to a Dingtalk webhook."
    conf_key = "sentry-dingtalk"
    required_field = "webhook"
    author = 'Ang Yi Quan'
    author_url = 'https://github.com/getsentry/sentry-pivotal'
    version = "1.0.0"
    feature_descriptions = [
        FeatureDescription(
            """
            Configure rule based Dingtalk notifications to automatically be posted into a
            specific channel.
            """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]

    def is_configured(self, project):
        return bool(self.get_option("webhook", project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "Webhook URL",
                "type": "url",
                "placeholder": "https://oapi.dingtalk.com/robot/send?access_token=abcdefg",
                "required": True,
                "help": "Your custom dingding webhook URL.",
            },
            {
                "name": "custom_message",
                "label": "Custom Message",
                "type": "string",
                "placeholder": "e.g. Hey <!everyone> there is something wrong",
                "required": False,
                "help": "Optional - dingding message formatting can be used",
            },
            {
                "name": "include_tags",
                "label": "Include Tags",
                "type": "bool",
                "required": False,
                "help": "Include tags with notifications",
            },
            {
                "name": "included_tag_keys",
                "label": "Included Tags",
                "type": "string",
                "required": False,
                "help": (
                    "Only include these tags (comma separated list). " "Leave empty to include all."
                ),
            },
            {
                "name": "include_rules",
                "label": "Include Rules",
                "type": "bool",
                "required": False,
                "help": "Include triggering rules with notifications.",
            },
        ]

    def _get_tags(self, event):
        tag_list = event.tags
        if not tag_list:
            return ()

        return (
            (tagstore.get_tag_key_label(k), tagstore.get_tag_value_label(k, v)) for k, v in tag_list
        )

    def get_tag_list(self, name, project):
        option = self.get_option(name, project)
        if not option:
            return None
        return set(tag.strip().lower() for tag in option.split(","))

    def notify(self, notification, raise_exception=False):
        event = notification.event
        group = event.group
        project = group.project

        if not self.is_configured(project):
            return

        project_name = project.get_full_name().encode("utf-8")

        # title
        title = event.title.encode("utf-8")
        if self.get_option("custom_message", project):
            title = u"{} ({})".format(
                title, self.get_option("custom_message", project))

        # issue
        issue_link = group.get_absolute_url(params={"referrer": "dingding"})
        issueStr = "\n> #### [issue]({})".format(issue_link)

        # 报警规则
        ruleStr = ""
        if self.get_option("include_rules", project):
            if notification.rules:
                rule = notification.rules[0]
                rule_link = "/%s/%s/settings/alerts/rules/%s/" % (
                    group.organization.slug,
                    project.slug,
                    rule.id,
                )
                rule_link = absolute_uri(rule_link)
                ruleStr = (u"\n> 由报警规则[{}]({})触发".format(
                    rule.label, rule_link)).encode('utf-8')

        # 标签
        tagStr = ""
        if self.get_option("include_tags", project):
            included_tags = set(self.get_tag_list(
                "included_tag_keys", project) or [])
            excluded_tags = set(self.get_tag_list(
                "excluded_tag_keys", project) or [])
            for tag_key, tag_value in self._get_tags(event):
                key = tag_key.lower()
                std_key = tagstore.get_standardized_key(key)
                if included_tags and key not in included_tags and std_key not in included_tags:
                    continue
                tagStr = tagStr + \
                    "\n> ###### {}:{} ".format(tag_key.encode(
                        "utf-8"), tag_value.encode("utf-8"))

        payload = title
        if ruleStr:
            payload = title + ruleStr
        payload = payload + issueStr
        if tagStr:
            payload = payload + tagStr

        webhookUrl = self.get_option("webhook", project)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {"msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": payload
                }
                }
        requests.post(webhookUrl, data=json.dumps(data), headers=headers)
