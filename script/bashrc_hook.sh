# ~/.bashrc_hook.sh
# 简单 JSON 转义函数（处理核心特殊字符，保证 JSON 合法）
function _json_escape() {
    local input="$1"
    input="${input//\\/\\\\}"   # 反斜杠 -> \\
    input="${input//\"/\\\"}"   # 双引号 -> \"
    input="${input//$'\n'/\\n}" # 换行符 -> \n
    input="${input//$'\r'/\\r}" # 回车符 -> \r
    input="${input//$'\t'/\\t}" # 制表符 -> \t
    echo "$input"
}

function _cmd_input_notify() {
    local input_cmd="${READLINE_LINE}"
    # 过滤空命令和纯空格命令（避免无效请求）
    [[ -z "$input_cmd" || "$input_cmd" =~ ^[[:space:]]+$ ]] && return 0

    local escaped_cmd="$(_json_escape "$input_cmd")"
    local json_payload="{\"type\":\"input\",\"cmd\":\"$escaped_cmd\"}"

    # curl 静默超时请求（不阻塞终端）
    curl -s --connect-timeout 1 --max-time 2 \
         -X POST -H "Content-Type: application/json" \
         -d "$json_payload" http://127.0.0.1:8765 \
         >/dev/null 2>&1
}

function _cmd_exec_notify() {
    local error=$?  # 捕获用户命令的真实退出码
    local error_str=$([ $error -ne 0 ] && echo "true" || echo "false")

    # 关键：直接读取终端最后一条真实执行的命令（去掉行号和空格）
    local real_last_cmd
    real_last_cmd=$(history 1 | sed 's/^[[:space:]]*[0-9]*[[:space:]]*//' 2>/dev/null)

    # 强化过滤：只保留用户真实命令，排除钩子/系统命令
    if [[ -z "$real_last_cmd" || "$real_last_cmd" =~ ^[[:space:]]+$ ||
          "$real_last_cmd" == "_cmd_exec_notify" || "$real_last_cmd" == "_cmd_input_notify" ||
          "$real_last_cmd" =~ ^history || "$real_last_cmd" =~ ^source ]]; then
        return 0
    fi

    local escaped_cmd="$(_json_escape "$real_last_cmd")"
    local json_payload="{\"type\":\"exec\",\"cmd\":\"$escaped_cmd\",\"error\":$error_str}"

    # curl 静默超时请求
    curl -s --connect-timeout 1 --max-time 2 \
         -X POST -H "Content-Type: application/json" \
         -d "$json_payload" http://127.0.0.1:8765 \
         >/dev/null 2>&1
}

# 绑定执行钩子（命令执行后触发）
export PROMPT_COMMAND="_cmd_exec_notify;"

# 绑定输入钩子（Ctrl+G 触发输入通知，不覆盖 Tab 补全）
bind -x '"\C-g":"_cmd_input_notify"'
