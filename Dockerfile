FROM python:3.8-alpine

COPY requirements.lock ./requirements.txt
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev python3-dev \
     && pip install --no-cache-dir -r requirements.txt \
     && apk del .build-deps gcc musl-dev libffi-dev openssl-dev python3-dev

ENV PYTHONPATH="."

COPY check_pr_comment/*.py check_pr_comment/

ENTRYPOINT ["action-entrypoint", "check_pr_comment.action.CheckPRCommentAction"]
