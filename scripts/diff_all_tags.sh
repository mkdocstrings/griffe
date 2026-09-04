#!/usr/bin/env bash
# SPDX-License-Identifier: ISC

set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(git -C "$script_dir" rev-parse --show-toplevel)
cd "$repo_root"

tags=()
while IFS= read -r tag; do
  tags+=("$tag")
done < <(git tag --list --sort=version:refname)

if ((${#tags[@]} < 2)); then
  echo "At least two tags are required." >&2
  exit 1
fi

uv run griffe diff -s src -s packages/griffelib/src griffe "${tags[@]}"
