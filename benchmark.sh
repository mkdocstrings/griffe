#!/usr/bin/env bash

repo=$(realpath $(dirname "$0"))
tags=(
    # 0.25.5
    # 0.26.0
    # 0.27.5
    # 0.28.2
    # 0.29.1
    # 0.30.1
    # 0.31.0
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
            venv${tag}/bin/python -m pip install pyinstrument scalene memray &>/dev/null
        fi
    ) &
done
wait

cat <<EOF >benchmark.py
import sys
import griffe
from griffe.loader import GriffeLoader
from griffe.extensions import load_extensions
from griffe.extensions import Extension
stdlib_packages = sorted([m for m in sys.stdlib_module_names if not m.startswith("_")])
# extensions = load_extensions([
#     Extension, Extension, Extension, Extension,
#     Extension, Extension, Extension, Extension,
#     Extension, Extension, Extension, Extension,
#     Extension, Extension, Extension, Extension,
# ])
extensions = None
loader = GriffeLoader(allow_inspection=False, extensions=extensions)
for package in stdlib_packages:
    try:
        loader.load(package)
    except:
        pass
loader.resolve_aliases(implicit=False, external=False)
EOF

if [ "$1" = "hyperfine" ]; then
    commands=$(
        for tag in ${tags[@]}; do
            echo "'venv${tag}/bin/python benchmark.py'"
        done
    )

    eval hyperfine --show-output --runs 2 ${commands} --export-json benchmark.json
elif [ "$1" = "scalene" ]; then
    for tag in ${tags[@]}; do
        venv${tag}/bin/python -m scalene --cli --cpu --memory --profile-all benchmark.py
    done
elif [ "$1" = "memray" ]; then
    for tag in ${tags[@]}; do
        venv${tag}/bin/python -m memray run -o report${tag}.bin benchmark.py
        # venv${tag}/bin/python -m memray flamegraph report${tag}.bin
        # venv${tag}/bin/python -m memray tree report${tag}.bin
        # venv${tag}/bin/python -m memray summary report${tag}.bin
        venv${tag}/bin/python -m memray stats report${tag}.bin
    done
elif [ "$1" = "pyinstrument" ]; then
    for tag in ${tags[@]}; do
        venv${tag}/bin/pyinstrument benchmark.py
    done
fi
