#!/usr/bin/env bash
curl -fsSL https://deno.land/install.sh | sh
export DENO_INSTALL="/opt/render/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
pip install -r requirements.txt
