# encoding:utf-8
from __future__ import absolute_import

import requests
from sentry import tagstore
from sentry.plugins.bases import notify
from sentry.utils import json
from sentry.utils.http import absolute_uri
from sentry.integrations import FeatureDescription, IntegrationFeatures
from sentry_plugins.base import CorePluginMixin

# for dingtalk signature
import time
import hmac
import hashlib
import base64
import urllib


class DingtalkPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = "Sentry Dingtalk Bot"
    slug = "sentry-dingtalk"
    description = "Post notifications to a Dingtalk webhook."
    conf_key = "sentry-dingtalk"
    required_field = "webhook"
    author = "Ang Yi Quan"
    author_url = "https://github.com/lostncg/sentry-dingtalk"
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
    resource_links = [
        ("Report Issue", "https://github.com/lostncg/sentry-dingtalk/issues"),
        ("View Source", "https://github.com/lostncg/sentry-dingtalk"),
    ]

    def is_configured(self, project):
        return bool(self.get_option("webhook", project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "Webhook URL",
                "type": "url",
                "placeholder": "https://oapi.dingtalk.com/robot/send?access_token=**********",
                "required": True,
                "help": "Your custom dingding webhook URL.",
            },
            {
                "name": "custom_keyword",
                "label": "Custom Keyword",
                "type": "string",
                "placeholder": "e.g. [Sentry] Error title",
                "required": False,
                "help": "Optional - A custom keyword as the prefix of the event title",
            },
            {
                "name": "signature",
                "label": "Additional Signature",
                "type": "string",
                "required": False,
                "help": "Optional - Attach Dingtalk webhook signature to the request headers.",
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
                    "Only include these tags (comma separated list). "
                    "Leave empty to include all."
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
            (tagstore.get_tag_key_label(k), tagstore.get_tag_value_label(k, v))
            for k, v in tag_list
        )

    def get_tag_list(self, keys):
        if not keys:
            return None
        return set(tag.strip().lower() for tag in keys.split(","))

    def notify(self, notification, raise_exception=False):
        event = notification.event
        group = event.group
        project = group.project

        if not self.is_configured(project):
            return

        webhookUrl = self.get_option("webhook", project)
        custom_keyword = self.get_option("custom_keyword", project)
        signature = self.get_option("signature", project)
        include_tags = self.get_option("include_tags", project)
        included_tag_keys = self.get_option("included_tag_keys", project)
        include_rules = self.get_option("include_rules", project)

        # title
        title = event.title.encode("utf-8")
        if custom_keyword:
            title = u"[{}] {}".format(custom_keyword, title)

        # issue
        issue_link = group.get_absolute_url(params={"referrer": "dingtalk"})

        if signature:
            timestamp = long(round(time.time() * 1000))
            secret = signature
            secret_enc = bytes(secret).encode("utf-8")
            string_to_sign = "{}\n{}".format(timestamp, secret)
            string_to_sign_enc = bytes(string_to_sign).encode("utf-8")
            hmac_code = hmac.new(
                secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
            ).digest()
            sign = urllib.quote_plus(base64.b64encode(hmac_code))
            webhookUrl = u"{}&timestamp={}&sign={}".format(webhookUrl, timestamp, sign)

        # 报警规则
        ruleStr = ""
        if include_rules:
            if notification.rules:
                rule = notification.rules[0]
                rule_link = "/%s/%s/settings/alerts/rules/%s/" % (
                    group.organization.slug,
                    project.slug,
                    rule.id,
                )
                rule_link = absolute_uri(rule_link)
                ruleStr = (u"\n> 由报警规则[{}]({})触发".format(rule.label, rule_link)).encode(
                    "utf-8"
                )

        # 标签
        tagStr = ""
        if include_tags:
            included_tags = set(self.get_tag_list(included_tag_keys) or [])
            for tag_key, tag_value in self._get_tags(event):
                key = tag_key.lower()
                std_key = tagstore.get_standardized_key(key)
                if (
                    included_tags
                    and key not in included_tags
                    and std_key not in included_tags
                ):
                    continue
                tagStr = tagStr + "\n- {}:{} ".format(
                    tag_key.encode("utf-8"), tag_value.encode("utf-8")
                )

        payload = ""

        if ruleStr:
            payload = payload + ruleStr
        if tagStr:
            payload = payload + tagStr

        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        data = {
            "actionCard": {
                "title": title,
                "text": payload,
                "btnOrientation": "0",
                "singleTitle": "Visit Issue Link",
                "singleURL": issue_link,
            },
            "msgtype": "actionCard",
        }
        requests.post(webhookUrl, data=json.dumps(data), headers=headers)
