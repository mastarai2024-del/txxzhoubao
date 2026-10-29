# 新电脑接入与授权

## 先复用现有环境

在当前电脑检查 `lark-cli --help`、`lark-cli whoami`、`lark-cli auth status --json --verify`，以及 `meegle version`、`meegle auth status --format json`。通过 PATH 查找命令，或给检查脚本传 `--lark-cli` / `--meegle` 指定本机入口。不要引用另一台电脑的用户目录。

有现成 CLI、应用或登录时继续使用。`needs_refresh` 且服务器校验通过，可能会在下次用户请求自动刷新；不能只凭此标签要求重新登录。配置存在也不证明已经登录或能读业务资源。

## 安装与应用配置

缺少 CLI 时才安装官方发行版。运行需要 Node.js/npm；可通过官方向导或 npm 安装工具，然后验证命令可用。开始前说明安装目标；已有工具不要顺手升级。

```sh
npm install -g @larksuite/cli
npm install -g @lark-project/meegle
```

npm 包本身安装 CLI；完整 `install` 向导还可能安装官方技能、配置站点并启动登录。需要向导时先检查 `--help`，支持时分别使用 `--no-skills`、`--no-auth` 避免重复技能和阻塞登录。也可以安装到用户指定的本地 npm prefix，再将该目录命令加入 PATH。

协作 CLI 未配置应用时，读当前 `lark-cli config init --help` 和 `lark-cli skills read lark-shared`，按该版本支持的非交互/分离流程完成绑定。只有确实没有可复用应用时才创建；不要为了读不到某个资源更换账号或应用。不同电脑的系统凭据不能通过复制技能、配置文件或聊天传输。

## 飞书协作：按需申请用户读取权限

个人消息、文档、日历和妙记显式 `--as user`。应用后台开通权限、用户授予权限、用户对具体对象可见是不同层级；报错缺用户 scope 不能直接判定机器人需要重新申请。待管理员审批时保留状态，继续其他来源；审批完成后核对实际授权，再决定是否需要新用户授权。

本周报流程曾遇到以下读取权限，实际以当前命令报错、内置说明及 schema 为准：

| 路线 | 按需检查的 scope |
|---|---|
| 文档搜索/正文 | `search:docs:read`、`docs:document.content:read`；部分读取接口使用 `docx:document:readonly` |
| 知识空间/节点 | `wiki:space:read` / `wiki:space:retrieve`、`wiki:node:read` / `wiki:node:retrieve`，由具体接口决定 |
| 消息搜索 | `search:message`；部分 CLI 即使禁用 reactions 也在预检要求 `im:message.reactions:read` |
| 消息正文（用户身份） | 当前批量读取和群历史命令均要求 `im:message.group_msg:get_as_user`、`im:message.p2p_msg:get_as_user`；即使只查询群聊，工具也会同时校验两项，授权前向用户说明 |
| 日历事件 | `calendar:calendar.event:read` |
| 妙记搜索/详情 | `minutes:minutes.search:read`、`minutes:minutes.basic:read`；逐字稿额外权限依实际接口处理 |
| 妙记产物 | `minutes:minutes.artifacts:read`，用于摘要、待办及逐字稿；基础详情权限只返回标题等信息 |

先从当前帮助、内置说明和实际错误把拟用的搜索、正文、产物命令分别核对，再合并必要权限。`messages-search` 可能返回 `ok:true`，却只有消息ID及“正文获取失败”说明；妙记搜索或标题读取成功也不代表产物可读。上述两种情况均不能记为正文验收通过。授权后每一路仍做真实读取，若接口再报权限缺口，保留原错误并说明，不预先扩大到全部权限。

同一次协作授权可合并已确认缺失的读取 scope。每个接口返回的候选权限可能是任选其一，勿机械把全部候选都申请。不要申请整个域或 `all`，也不为周报预先申请发送、删除、移动和成员管理权限。

```sh
lark-cli auth login --scope '所需且缺失的读取scope，使用空格分隔' --no-wait --json
```

将返回的原始验证链接和有效期交用户，支持时生成二维码；结束本轮，待用户完成后由 Codex 执行 `lark-cli auth login --device-code <本次设备码>`。设备码仅在当前授权会话保留，不写仓库、日志或长期配置。过期后先看当前权限是否已生效；仍缺时用相同必要范围生成新链接，不重复使用旧码。用户授权后重新读回身份与 scope，并做真实读取。

## 飞书项目：独立认证

Meegle 与协作 CLI 使用独立认证；不能并入上一条链接。站点来自用户已确认的“飞书项目”或实际 URL（通常 `project.feishu.cn`），国际 Meegle 或自建站点需按实际目标选择。

```sh
meegle auth login --device-code --phase init --host <目标站点> --format json
```

将 `verification_uri_complete` 原样交用户，保留本次 `device_code` 和 `client_id` 于当前会话，结束本轮。用户确认后再执行：

```sh
meegle auth login --device-code --phase poll --once --host <目标站点> --device-code-value <本次设备码> --client-id <本次client_id> --format json
meegle auth status --format json
```

`--once` 返回码为 0 也可能仍是 `authorization_pending`，必须看状态；只有认证成功后继续。认证失效只处理对应一套登录，不要求两边一起重来。已授权后逐项验证当前用户、项目空间、需求、缺陷详情；登录成功或缓存里有命令不代表已读到工作项。

## 完成条件

运行 `scripts/check_access.py` 只证明前置状态。接着按信息源指南记录各路实际读取、时间、身份、分页和限制。新电脑首次完成后，将周报地址、本人行、站点、关键词保存在本机私有 profile；凭据继续由官方工具和系统凭据存储管理。

官方依据：[lark-cli](https://github.com/larksuite/cli)、[meegle-cli](https://github.com/larksuite/meegle-cli)。命令随版本变化，以已安装版本帮助为准。
