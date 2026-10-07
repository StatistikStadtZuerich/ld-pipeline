#!/usr/bin/env bash
set -euo pipefail

TEAMS_HOOK_URL="${TEAMS_HOOK_URL:-}"
[ -n "$TEAMS_HOOK_URL" ] || exit 0

SELF="$(readlink -f "$0")"
SCRIPT_HOME="$(dirname "$SELF")"
TEMPLATE_DIR="${TEMPLATE_DIR:-${SCRIPT_HOME}/msteams}"

# Usage: ./teams-notify.sh <json-template> [--<arg> <value> ...]
usage() {
    echo "Usage: $0 <json-template> [--<arg> <value> ...]" >&2
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

TEMPLATE="$1"
shift

if [ -f "$TEMPLATE" ]; then
  true
elif [ -f "${TEMPLATE}.json" ]; then
  TEMPLATE="${TEMPLATE}.json"
elif [ -f "${TEMPLATE_DIR}/${TEMPLATE}" ]; then
  TEMPLATE="${TEMPLATE_DIR}/${TEMPLATE}"
elif [ -f "${TEMPLATE_DIR}/${TEMPLATE}.json" ]; then
  TEMPLATE="${TEMPLATE_DIR}/${TEMPLATE}.json"
fi

if [ ! -f "$TEMPLATE" ]; then
    echo "Template file not found: $TEMPLATE" >&2
    usage
    exit 1
fi

JQ_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --*)
            ARG_NAME="${1#--}"
            shift
            if [ $# -gt 0 ]; then
                ARG_VALUE="$1"
                shift
                JQ_ARGS+=(--arg "$ARG_NAME" "$ARG_VALUE")
            else
                echo "Missing value for argument --$ARG_NAME" >&2
                usage
                exit 1
            fi
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 1
            ;;
    esac
done

# Construct jq filter to replace variables
# shellcheck disable=SC2016
FILTER_EXPR='walk(if type == "string" then reduce ($ARGS.named | keys_unsorted[]) as $k (.; gsub("\\$" + $k + "|\\$\\{" + $k + "\\}"; $ARGS.named[$k])) else . end)'

PAYLOAD="$(jq "${JQ_ARGS[@]}" "$FILTER_EXPR" "$TEMPLATE")"

body_file=$(mktemp)
http_code=$(curl -sS -o "$body_file" -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$TEAMS_HOOK_URL")
if [ "$http_code" -ge 400 ]; then
  echo "Sending Teams-Notification failed with HTTP-$http_code:" >&2
  echo "##################" >&2
  cat "$body_file" >&2
  echo "##################" >&2
  # Do not exit with an error-code
fi
rm -f "$body_file"
