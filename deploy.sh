#!/usr/bin/env

set -e

readonly SCRIPTDIR=$(readlink -f "$(dirname "$0")")
readonly VENV="$SCRIPTDIR"/.env
readonly OWNER=$(whoami)

(
  cd "$SCRIPTDIR"
  python3 -m venv "$VENV"
  source "$VENV"/bin/activate
  pip install -r "$SCRIPTDIR"/requirements.txt
  python setup.py install
) || { echo 'ERROR: bootstrap failed' >&2; exit 1; }

cat >"$SCRIPTDIR"/run.sh <<EOF
#!/bin/bash
source "$VENV/bin/activate"
"\$@"
exit \$?
EOF

chown "$OWNER:$OWNER" -- "$SCRIPTDIR"/run.sh
chmod 0755 -- "$SCRIPTDIR"/run.sh

exit 0
