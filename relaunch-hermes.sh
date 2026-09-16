#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# relaunch-hermes.sh  (run ON oci2)
#
# Purpose: restart the Hermes muta gateway on the Hermes host after applying a
#          Telegram-adapter patch.  The gateway refuses to restart *itself*
#          (systemd blocks it from inside the process), so we signal it from a
#          separate machine over SSH.
#
# Usage:
#   ./relaunch-hermes.sh
#
# Assumptions (edit the HOST/USER/PASS/SERVICE vars below):
#   * oci2 can reach the Hermes host over SSH.
#   * SSH auth is via password (sshpass) or a pre-installed key.
#   * The service is a systemd unit running as the specified user.
# ---------------------------------------------------------------------------
set -euo pipefail

# ---- configuration --------------------------------------------------------
HOST="${HOST:-hermes-host}"          # resolves from oci2 to the Hermes host
USER="${USER:-ubuntu}"
PASS="${PASS:-Intel@123!}"
SERVICE="${SERVICE:-hermes-gateway-muta.service}"
SSH_TIMEOUT="${SSH_TIMEOUT:-30}"
WAIT_SECS="${WAIT_SECS:-25}"
# ---------------------------------------------------------------------------

# Pick an auth method: prefer a key if one is configured/available, else sshpass.
SSH=(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new
         -o ConnectTimeout="${SSH_TIMEOUT}" "${USER}@${HOST}")
if ! "${SSH[@]}" true >/dev/null 2>&1; then
    if command -v sshpass >/dev/null 2>&1; then
        SSH=(sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=accept-new
             -o ConnectTimeout="${SSH_TIMEOUT}" "${USER}@${HOST}")
    else
        echo "ERROR: key auth failed and sshpass is not installed on oci2." >&2
        echo "       Install sshpass:  (apt) sudo apt install -y sshpass" >&2
        echo "                         (brew) brew install sshpass" >&2
        exit 1
    fi
fi

echo "==> Checking reachability of ${USER}@${HOST} ..."
if ! "${SSH[@]}" 'echo ok' >/dev/null 2>&1; then
    echo "ERROR: cannot SSH to ${HOST}. Check HOST/USER/PASS or network." >&2
    exit 1
fi
echo "    reachable."

# The remote restart must run as root (sudo).  sudo needs a TTY on some hosts;
# -tt allocates a pseudo-terminal over the SSH channel so the sudo prompt can
# be answered non-interactively (we pass the password to sudo via -S).
REMOTE="echo '${PASS}' | sudo -S -p '' systemctl restart '${SERVICE}' && \
        sleep 4 && \
        systemctl is-active '${SERVICE}'"

echo "==> Restarting ${SERVICE} on ${HOST} ..."
RESULT="$("${SSH[@]}" -tt "bash -lc \"${REMOTE}\"" 2>&1 || true)"
echo "${RESULT}" | sed 's/^/    /'

if echo "${RESULT}" | grep -q '^active'; then
    echo "==> SUCCESS: ${SERVICE} is active."
else
    echo "==> FAILED: service did not report active. Check:"
    echo "      ${SERVICE} status / 'systemctl status ${SERVICE}' on ${HOST}"
    exit 1
fi

# Brief settle period, then confirm it is still up.
echo "==> Waiting ${WAIT_SECS}s for the gateway to attach to Telegram ..."
sleep "${WAIT_SECS}"
STATUS="$( "${SSH[@]}" "systemctl is-active '${SERVICE}'" 2>&1 || true )"
echo "    post-wait status: ${STATUS}"
if [ "${STATUS}" = "active" ]; then
    echo "==> Done. The Hermes muta gateway is running with the patched code."
else
    echo "==> WARNING: service not active after wait (status='${STATUS}')."
    exit 1
fi
