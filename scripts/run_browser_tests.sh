#!/usr/bin/env bash
# Run every independently executable browser regression.
#
# Fighter 6-8 are continuation files loaded by browser-fighter5.test.cjs.
# Executing those three files directly bypasses their shared browser harness.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

test_count=0
for test_file in frontend/*.test.cjs; do
  case "$(basename "$test_file")" in
    browser-fighter6.test.cjs|browser-fighter7.test.cjs|browser-fighter8.test.cjs)
      continue
      ;;
  esac

  echo "--- node $test_file"
  node "$test_file"
  test_count=$((test_count + 1))
done

echo "Browser regressions passed: $test_count independent entrypoints."
