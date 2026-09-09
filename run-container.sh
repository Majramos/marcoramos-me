#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
image_name="marcoramos-me-wrangler:latest"

if ! podman image exists "$image_name"; then
    printf 'Build the image first: %s/build-container.sh\n' "$project_root" >&2
    exit 1
fi

podman run --rm --interactive --tty --userns=keep-id \
    --volume "$project_root:/workspace:Z" \
    --workdir /workspace \
    "$image_name" \
    bash
