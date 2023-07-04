#!/usr/bin/env bash

repo=$(realpath $(dirname "$0"))
tags=(
    0.25.5
    0.26.0
    0.27.5
    0.28.2
    0.29.1
    0.30.1
    0.31.0
    HEAD
)
echo "Testing tags: ${tags[@]}"

mkdir /tmp/griffe-benchmark &>/dev/null
cd /tmp/griffe-benchmark

echo "Preparing environments"
for tag in ${tags[@]}; do
    (
        if ! [ -d "venv${tag}" ]; then
            python3.11 -m venv venv${tag}
            if [ "${tag}" = "HEAD" ]; then
                venv${tag}/bin/python -m pip install -e "${repo}" &>/dev/null
            else
                venv${tag}/bin/python -m pip install griffe==${tag} &>/dev/null
            fi
        fi
    ) &
done
wait

cat <<EOF >benchmark.py
import sys
from griffe.loader import GriffeLoader
stblib_packages = sorted([m for m in sys.stdlib_module_names if not m.startswith("_")])
loader = GriffeLoader(allow_inspection=False)
for package in stblib_packages:
    try:
        loader.load_module(package)
    except Exception:
        pass
loader.resolve_aliases(implicit=False, external=False)
EOF

commands=$(
    for tag in ${tags[@]}; do
        echo "'venv${tag}/bin/python benchmark.py'"
    done
)

eval hyperfine --runs 3 ${commands} --export-json benchmark.json
