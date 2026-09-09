#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
image_name="marcoramos-me-wrangler:latest"

podman build --tag "$image_name" --file "$project_root/Containerfile" "$project_root"
