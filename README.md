# Sentry Dingtalk Bot

> Credits to https://github.com/GaoYuJian/sentry-dingtalk

Setup the Dingtalk Bot for Sentry Alerts.

## Installation

1. Install with `pip` command

```bash
- pip install https://github.com/lostncg/sentry-dingtalk/archive/master.zip
```

2. Write in Sentry on premise's `requirements.txt`

```bash
  echo https://github.com/lostncg/sentry-dingtalk/archive/master.zip >> requirements.txt
```

## Features

- Support send message with Dingtalk whitelisted keyword.
- Support send message with Dingtalk signature.
- List event tags in Dingtalk message, support whitelist.
