#!/bin/bash

################################################################################
# Script: diagnose_github_connection.sh
# Description: Diagnose GitHub API connectivity issues for gh CLI
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

print_header() {
    echo -e "${BOLD}${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_separator() {
    echo -e "${CYAN}───────────────────────────────────────────────────────────────────${NC}"
}

echo ""
print_header "═══════════════════════════════════════════════════════════════════"
print_header "  GitHub API Connectivity Diagnostics"
print_header "═══════════════════════════════════════════════════════════════════"
echo ""

# Track issues
ISSUES_FOUND=0

################################################################################
# Test 1: Check if gh CLI is installed
################################################################################
print_header "Test 1: GitHub CLI Installation"
print_separator

if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version 2>&1 | head -n 1)
    print_success "GitHub CLI installed: ${GH_VERSION}"
else
    print_error "GitHub CLI (gh) not found"
    print_info "Install from: https://cli.github.com/"
    ((ISSUES_FOUND++))
    exit 1
fi
echo ""

################################################################################
# Test 2: Check gh authentication
################################################################################
print_header "Test 2: GitHub Authentication"
print_separator

AUTH_STATUS=$(gh auth status 2>&1)
if echo "$AUTH_STATUS" | grep -q "Logged in"; then
    USERNAME=$(echo "$AUTH_STATUS" | grep "Logged in" | sed -n 's/.*account \(.*\) (.*/\1/p' | head -n 1)
    print_success "Authenticated as: ${USERNAME}"

    # Check scopes
    if echo "$AUTH_STATUS" | grep -q "Token scopes:"; then
        print_info "Token scopes:"
        echo "$AUTH_STATUS" | grep "Token scopes:" | sed 's/.*Token scopes://' | tr ',' '\n' | while read -r scope; do
            echo "  - $(echo $scope | xargs)"
        done
    fi
else
    print_error "Not authenticated with GitHub"
    print_info "Run: gh auth login"
    ((ISSUES_FOUND++))
    exit 1
fi
echo ""

################################################################################
# Test 3: Check DNS resolution
################################################################################
print_header "Test 3: DNS Resolution"
print_separator

if command -v nslookup &> /dev/null; then
    if nslookup api.github.com > /dev/null 2>&1; then
        IP=$(nslookup api.github.com 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | head -n 1)
        print_success "DNS resolution working: api.github.com → ${IP}"
    else
        print_error "Cannot resolve api.github.com"
        print_warning "DNS issue detected - check your DNS settings"
        ((ISSUES_FOUND++))
    fi
elif command -v dig &> /dev/null; then
    if dig api.github.com +short > /dev/null 2>&1; then
        IP=$(dig api.github.com +short | head -n 1)
        print_success "DNS resolution working: api.github.com → ${IP}"
    else
        print_error "Cannot resolve api.github.com"
        print_warning "DNS issue detected - check your DNS settings"
        ((ISSUES_FOUND++))
    fi
else
    print_warning "nslookup/dig not found - skipping DNS test"
fi
echo ""

################################################################################
# Test 4: Check network connectivity to GitHub
################################################################################
print_header "Test 4: Network Connectivity"
print_separator

# Try ping
if command -v ping &> /dev/null; then
    if timeout 5s ping -c 1 github.com > /dev/null 2>&1; then
        print_success "Can reach github.com via ICMP"
    else
        print_warning "Cannot ping github.com (ICMP may be blocked)"
    fi
else
    print_warning "ping command not found"
fi

# Try curl/wget for HTTPS
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}" -m 10 https://github.com 2>&1)
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        print_success "HTTPS connection to github.com successful (HTTP ${HTTP_CODE})"
    else
        print_error "Cannot connect to github.com via HTTPS (got: ${HTTP_CODE})"
        ((ISSUES_FOUND++))
    fi
elif command -v wget &> /dev/null; then
    if timeout 10s wget -q --spider https://github.com 2>&1; then
        print_success "HTTPS connection to github.com successful"
    else
        print_error "Cannot connect to github.com via HTTPS"
        ((ISSUES_FOUND++))
    fi
else
    print_warning "curl/wget not found - cannot test HTTPS"
fi
echo ""

################################################################################
# Test 5: Check GitHub API directly
################################################################################
print_header "Test 5: GitHub API Access (Direct)"
print_separator

if command -v curl &> /dev/null; then
    API_RESPONSE=$(curl -s -m 10 https://api.github.com/rate_limit 2>&1)
    CURL_EXIT=$?

    if [ $CURL_EXIT -eq 0 ]; then
        if echo "$API_RESPONSE" | grep -q "rate"; then
            REMAINING=$(echo "$API_RESPONSE" | grep -o '"remaining":[0-9]*' | head -n 1 | cut -d':' -f2)
            print_success "GitHub API accessible via curl"
            if [ -n "$REMAINING" ]; then
                print_info "Rate limit remaining: ${REMAINING}"
            fi
        else
            print_error "API returned unexpected response"
            print_info "Response: ${API_RESPONSE}"
            ((ISSUES_FOUND++))
        fi
    else
        print_error "curl failed with exit code: ${CURL_EXIT}"
        ((ISSUES_FOUND++))
    fi
else
    print_warning "curl not found - skipping direct API test"
fi
echo ""

################################################################################
# Test 6: Check GitHub API via gh CLI
################################################################################
print_header "Test 6: GitHub API Access (via gh CLI)"
print_separator

print_info "Testing: gh api /rate_limit"

# Try with timeout
if command -v timeout &> /dev/null; then
    TIMEOUT_CMD="timeout 15s"
elif command -v gtimeout &> /dev/null; then
    TIMEOUT_CMD="gtimeout 15s"
else
    TIMEOUT_CMD=""
    print_warning "No timeout command available - test may hang"
fi

GH_OUTPUT=$(mktemp)
if [ -n "$TIMEOUT_CMD" ]; then
    $TIMEOUT_CMD gh api /rate_limit > "$GH_OUTPUT" 2>&1
    GH_EXIT=$?
else
    gh api /rate_limit > "$GH_OUTPUT" 2>&1 &
    GH_PID=$!
    sleep 15
    if ps -p $GH_PID > /dev/null 2>&1; then
        kill $GH_PID 2>/dev/null
        GH_EXIT=124  # Simulate timeout
        echo "Timeout" > "$GH_OUTPUT"
    else
        wait $GH_PID
        GH_EXIT=$?
    fi
fi

if [ $GH_EXIT -eq 0 ]; then
    print_success "gh CLI can access GitHub API"

    if grep -q "rate" "$GH_OUTPUT"; then
        LIMIT=$(grep -o '"limit":[0-9]*' "$GH_OUTPUT" | head -n 1 | cut -d':' -f2)
        REMAINING=$(grep -o '"remaining":[0-9]*' "$GH_OUTPUT" | head -n 1 | cut -d':' -f2)

        if [ -n "$LIMIT" ] && [ -n "$REMAINING" ]; then
            print_info "Rate limit: ${REMAINING}/${LIMIT} remaining"
        fi
    fi
elif [ $GH_EXIT -eq 124 ]; then
    print_error "gh API command timed out (15s)"
    print_warning "This is the same issue affecting issue creation"
    ((ISSUES_FOUND++))
else
    print_error "gh CLI cannot access GitHub API (exit code: ${GH_EXIT})"
    ERROR_MSG=$(cat "$GH_OUTPUT")
    if [ -n "$ERROR_MSG" ]; then
        print_info "Error: ${ERROR_MSG}"
    fi
    ((ISSUES_FOUND++))
fi

rm -f "$GH_OUTPUT"
echo ""

################################################################################
# Test 7: Check proxy settings
################################################################################
print_header "Test 7: Proxy Configuration"
print_separator

PROXY_FOUND=false

if [ -n "$HTTP_PROXY" ] || [ -n "$http_proxy" ]; then
    print_info "HTTP_PROXY: ${HTTP_PROXY:-$http_proxy}"
    PROXY_FOUND=true
fi

if [ -n "$HTTPS_PROXY" ] || [ -n "$https_proxy" ]; then
    print_info "HTTPS_PROXY: ${HTTPS_PROXY:-$https_proxy}"
    PROXY_FOUND=true
fi

if [ -n "$NO_PROXY" ] || [ -n "$no_proxy" ]; then
    print_info "NO_PROXY: ${NO_PROXY:-$no_proxy}"
    PROXY_FOUND=true
fi

if [ "$PROXY_FOUND" = true ]; then
    print_warning "Proxy settings detected - may affect GitHub API access"
    print_info "If behind a corporate proxy, ensure it allows GitHub API access"
else
    print_success "No proxy environment variables set"
fi
echo ""

################################################################################
# Test 8: Check gh CLI configuration
################################################################################
print_header "Test 8: GitHub CLI Configuration"
print_separator

GH_CONFIG_DIR="${GH_CONFIG_DIR:-$HOME/.config/gh}"

if [ -d "$GH_CONFIG_DIR" ]; then
    print_success "Config directory exists: ${GH_CONFIG_DIR}"

    # Check config.yml
    if [ -f "$GH_CONFIG_DIR/config.yml" ]; then
        print_info "Configuration file found"

        # Check for git_protocol
        if grep -q "git_protocol:" "$GH_CONFIG_DIR/config.yml"; then
            PROTOCOL=$(grep "git_protocol:" "$GH_CONFIG_DIR/config.yml" | awk '{print $2}')
            print_info "Git protocol: ${PROTOCOL}"
        fi

        # Check for custom API endpoint
        if grep -q "api.github.com" "$GH_CONFIG_DIR/config.yml"; then
            print_info "Using GitHub.com API"
        elif grep -q "api_endpoint:" "$GH_CONFIG_DIR/config.yml"; then
            ENDPOINT=$(grep "api_endpoint:" "$GH_CONFIG_DIR/config.yml" | awk '{print $2}')
            print_warning "Custom API endpoint: ${ENDPOINT}"
        fi
    fi

    # Check hosts.yml
    if [ -f "$GH_CONFIG_DIR/hosts.yml" ]; then
        print_info "Hosts configuration found"
    fi
else
    print_warning "Config directory not found: ${GH_CONFIG_DIR}"
fi
echo ""

################################################################################
# Summary and Recommendations
################################################################################
print_header "═══════════════════════════════════════════════════════════════════"
print_header "  Diagnosis Summary"
print_header "═══════════════════════════════════════════════════════════════════"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    print_success "No issues detected - GitHub API should be accessible"
    echo ""
    print_info "If create_github_issues.sh still fails, try:"
    echo "  1. Run with --verbose flag for detailed output"
    echo "  2. Check your firewall settings"
    echo "  3. Try from a different network"
else
    print_error "Found ${ISSUES_FOUND} issue(s) that may prevent API access"
    echo ""
    print_header "Recommended Actions:"
    echo ""

    if echo "$AUTH_STATUS" | grep -q -v "Logged in"; then
        echo "  1. Authenticate with GitHub:"
        echo "     ${YELLOW}gh auth login${NC}"
        echo ""
    fi

    if grep -q "Cannot resolve" <<< "$(nslookup api.github.com 2>&1)"; then
        echo "  2. Fix DNS resolution:"
        echo "     - Check /etc/resolv.conf"
        echo "     - Try a different DNS server (8.8.8.8, 1.1.1.1)"
        echo ""
    fi

    if [ $GH_EXIT -eq 124 ] || [ $GH_EXIT -ne 0 ]; then
        echo "  3. GitHub API connectivity issues:"
        echo "     - Check if you're behind a firewall/proxy"
        echo "     - Verify network allows HTTPS to api.github.com"
        echo "     - Try: ${YELLOW}curl -v https://api.github.com/rate_limit${NC}"
        echo ""
    fi

    if [ "$PROXY_FOUND" = true ]; then
        echo "  4. Proxy configuration:"
        echo "     - Ensure proxy allows GitHub API (api.github.com)"
        echo "     - Check if GitHub needs to be in NO_PROXY"
        echo "     - Try temporarily: ${YELLOW}unset HTTP_PROXY HTTPS_PROXY${NC}"
        echo ""
    fi
fi

print_separator
echo ""
print_info "For more help, see: https://cli.github.com/manual/troubleshooting"
echo ""
