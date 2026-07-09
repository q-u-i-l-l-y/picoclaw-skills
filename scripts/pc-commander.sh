#!/data/data/com.termux/files/usr/bin/bash
export PC_WORKSPACE="$HOME/.picoclaw/workspace"
export PC_HISTORY="$HOME/.picoclaw/history.log"
export PC_MODEL="tinyllama"
export PC_OLLAMA_URL="http://127.0.0.1:11434/api/generate"
export PC_VERSION="1.0"
mkdir -p "$PC_WORKSPACE/ingestions"
touch "$PC_HISTORY"
_pc_llm() {
    local system_prompt="$1"
    local user_prompt="$2"
    local temp="${3:-0.2}"
    local max_tokens="${4:-256}"
    local tmpjson="$HOME/.picoclaw/tmp/pc_llm_$$.json"
    printf "{\"model\":\"%s\",\"system\":%s,\"prompt\":%s,\"stream\":false,\"options\":{\"temperature\":%s,\"num_ctx\":512,\"num_predict\":%s}}" "$PC_MODEL" "$(echo "$system_prompt" | jq -Rs .)" "$(echo "$user_prompt" | jq -Rs .)" "$temp" "$max_tokens" > "$tmpjson"
    curl -s --max-time 30 "$PC_OLLAMA_URL" -H "Content-Type: application/json" -d @"$tmpjson" | jq -r ".response // empty"
    rm -f "$tmpjson"
}
pc_ask() {
    local prompt="$*"
    local system="You are PicoClaw, a local AI node in the QuillyOS mesh running on Termux. Be concise. You have 800MB RAM. Answer in 3 sentences or less."
    echo "PicoClaw thinking..."
    local response
    response=$(_pc_llm "$system" "$prompt" 0.4 256)
    echo ""
    echo "$response"
    echo ""
    echo "[ask] $prompt" >> "$PC_HISTORY"
}
pc_do() {
    local prompt="$*"
    local system="You are PicoClaw command executor. User describes task in plain English. Output ONLY exact shell command for Termux. Rules: output in single bash code block, use absolute paths, prefer git curl python3 jq grep awk sed find, multi-step as one-liner with && or ;, NEVER rm -rf or dangerous wildcards, NEVER delete files unless asked, keep short."
    echo "Generating command..."
    local raw
    raw=$(_pc_llm "$system" "$prompt" 0.1 128)
    local cmd
    cmd=$(echo "$raw" | grep -A999 "^```" | grep -B999 "^```" | tail -n +2 | head -n -1)
    if [ -z "$cmd" ]; then
        echo "Could not parse command. Raw:"
        echo "$raw"
        return 1
    fi
    echo ""
    echo "Proposed command: $cmd"
    echo -n "Execute? [y/N/dry] > "
    read -r answer
    case "$answer" in
        y|Y|yes) echo "[EXEC] $cmd" >> "$PC_HISTORY"; eval "$cmd" ;;
        d|dry) echo "[DRY] Would run: $cmd" ;;
        *) echo "[CANCELLED]"; return 1 ;;
    esac
    echo "[do] $prompt -> $cmd" >> "$PC_HISTORY"
}
pc_run() {
    echo "PicoClaw Commander v$PC_VERSION"
    echo "ask <q> -- Chat | do <task> -- Command | exit"
    while true; do
        echo -n "pc> "
        read -r line
        [ -z "$line" ] && continue
        [ "$line" = "exit" ] && echo "Goodbye." && break
        local subcmd
        subcmd=$(echo "$line" | awk "{print \$1}")
        local rest
        rest=$(echo "$line" | cut -d" " -f2-)
        case "$subcmd" in
            ask) pc_ask "$rest" ;;
            do) pc_do "$rest" ;;
            help|h) echo "ask/do/exit" ;;
            *) echo "Unknown: $subcmd" ;;
        esac
    done
}
alias pc="pc_run"
alias pca="pc_ask"
alias pcd="pc_do"
echo "PicoClaw Commander v$PC_VERSION loaded. Type pc to start."
