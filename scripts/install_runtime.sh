#!/bin/sh
# Pinned upstream release; installs locally without modifying shell profiles.
set -eu
mkdir -p runtime
cd runtime
base=https://github.com/carloslfu/slotstream/releases/download/v0.2.17
curl -fL "$base/slotstream-arm64.tar.gz" -o slotstream-arm64.tar.gz
curl -fL "$base/slotstream-arm64.tar.gz.sha256" -o slotstream-arm64.tar.gz.sha256
shasum -a 256 -c slotstream-arm64.tar.gz.sha256
tar -xzf slotstream-arm64.tar.gz
./slotstream --version
