#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
NEED_INSTALL=()

info()  { printf "\033[1m%s\033[0m\n" "$*"; }
warn()  { printf "\033[33m%s\033[0m\n" "$*"; }
fail()  { printf "\033[31m%s\033[0m\n" "$*"; exit 1; }

# ── Check required tools ─────────────────────────────────────────────

check_bin() {
    command -v "$1" &>/dev/null
}

check_python() {
    if ! check_bin python3; then
        fail "python3 not found. Install Python 3.12+ first."
    fi
    local ver
    ver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local major minor
    major=${ver%%.*}
    minor=${ver##*.}
    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 12 ]]; }; then
        fail "Python >= 3.12 required (found $ver)"
    fi
    info "✓ python3 $ver"
}

check_uv() {
    if check_bin uv; then
        info "✓ uv $(uv --version 2>/dev/null | head -1)"
        return
    fi
    NEED_INSTALL+=(uv)
}

check_node() {
    if check_bin node && check_bin npm; then
        info "✓ node $(node --version)"
        return
    fi
    NEED_INSTALL+=(node)
}

check_mmdc() {
    if check_bin mmdc; then
        info "✓ mmdc (mermaid-cli)"
    else
        warn "⚠ mmdc not found — diagram validation will use Level-1 only"
    fi
}

# ── Install missing tools ────────────────────────────────────────────

prompt_install() {
    if [[ ${#NEED_INSTALL[@]} -eq 0 ]]; then
        return
    fi
    echo ""
    warn "Missing: ${NEED_INSTALL[*]}"
    read -rp "Install them now? [y/N] " answer
    if [[ "$answer" != [yY]* ]]; then
        fail "Cannot continue without: ${NEED_INSTALL[*]}"
    fi
    for tool in "${NEED_INSTALL[@]}"; do
        install_"$tool"
    done
    echo ""
}

install_uv() {
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    check_bin uv || fail "uv install failed"
    info "✓ uv installed"
}

install_node() {
    if [[ "$(uname)" == "Darwin" ]]; then
        if check_bin brew; then
            info "Installing node via brew..."
            brew install node
        else
            fail "Install Node.js manually: https://nodejs.org"
        fi
    else
        if check_bin apt-get; then
            info "Installing node via apt..."
            sudo apt-get update -qq && sudo apt-get install -y -qq nodejs npm
        elif check_bin dnf; then
            info "Installing node via dnf..."
            sudo dnf install -y nodejs npm
        elif check_bin pacman; then
            info "Installing node via pacman..."
            sudo pacman -Sy --noconfirm nodejs npm
        else
            fail "Install Node.js manually: https://nodejs.org"
        fi
    fi
    check_bin node || fail "node install failed"
    info "✓ node installed"
}

# ── Setup deps ────────────────────────────────────────────────────────

setup_backend() {
    info "Installing backend deps..."
    (cd "$ROOT" && uv sync --quiet)
    info "✓ backend ready"
}

setup_frontend() {
    info "Installing frontend deps..."
    (cd "$ROOT/frontend" && npm install --silent)
    info "✓ frontend ready"
}

# ── .env check ────────────────────────────────────────────────────────

check_env() {
    if [[ ! -f "$ROOT/.env" ]]; then
        warn "No .env file found — copying from .env.example..."
        cp "$ROOT/.env.example" "$ROOT/.env"
        warn "→ Edit .env and set your OPENAI_API_KEY before using."
    fi
}

# ── Start ─────────────────────────────────────────────────────────────

cleanup() {
    echo ""
    info "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

start() {
    trap cleanup INT TERM

    info "Starting backend on :8000..."
    (cd "$ROOT" && exec uv run text-to-uml-api) &
    BACKEND_PID=$!

    info "Starting frontend on :5173..."
    (cd "$ROOT/frontend" && exec npx vite --open) &
    FRONTEND_PID=$!

    info ""
    info "Backend:  http://localhost:8000"
    info "Frontend: http://localhost:5173"
    info "Press Ctrl+C to stop both."

    # exit if either process dies
    while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; do
        wait -n 2>/dev/null || true
    done
    cleanup
}

# ── Main ──────────────────────────────────────────────────────────────

main() {
    info "text-to-UML setup"
    echo ""

    check_python
    check_uv
    check_node
    check_mmdc

    prompt_install

    setup_backend
    setup_frontend
    check_env

    echo ""
    start
}

main
