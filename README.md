# Sentry Dingtalk Bot

> Credits to https://github.com/GaoYuJian/sentry-dingtalk

Setup the Dingtalk Bot for Sentry Alerts.

## Requirements

- Sentry >= 20.12.1

## Installation

1. Install with `pip` command

```bash
- pip install https://github.com/lostncg/sentry-dingtalk/archive/master.zip
```

2. Write in Sentry on premise's `requirements.txt`

```bash
  echo https://github.com/lostncg/sentry-dingtalk/archive/master.zip >> requirements.txt
```

## Envrioment Variables

Setup in `sentry/sentry.config.py`

DINGTALK_WEBHOOK: `Required (String) - https://oapi.dingtalk.com/robot/send?access_token=**********`

DINGTALK_CUSTOM_KEYWORD: `Optional (String) - A custom keyword as the prefix of the event title`

DINGTALK_SIGNATURE: `Optional (String) - Attach Dingtalk webhook signature to the request headers.`

DINGTALK_INCLUDE_TAGS: `Optional (Boolean) - Include tags with notifications`

DINGTALK_INCLUDE_TAG_KEYS: `Optional (String) - Only include these tags (comma separated list). Leave empty to include all.`

DINGTALK_INCLUDE_RULES: `Optional (Boolean) - Include triggering rules with notifications.`

## Features

- Support send message with Dingtalk whitelisted keyword.
- Support send message with Dingtalk signature.
- List event tags in Dingtalk message, support whitelist.
