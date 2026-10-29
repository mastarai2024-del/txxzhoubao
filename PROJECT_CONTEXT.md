# 项目维护

唯一可发布源码是本 Git 仓库；用 `git rev-parse --show-toplevel` 确认当前副本。Codex 已安装目录是运行副本，不是独立源码。新任务从最新集成分支建立 `codex/` 分支及 `.worktrees/` 下的独占 worktree。

核心入口为 SKILL.md；按需说明在 references/，输出和私有配置模板在 assets/；scripts/check_access.py 为只读认证与权限预检。需要 Python 3；运行时读取依赖官方 lark-cli / meegle。没有服务、端口或生产数据。

验证：标准库 unittest；Codex skill-creator 的 quick_validate；相对引用、可移植路径与隐私检查；必要时在已有授权下真实只读验收。测试输出、依赖和工作记录放已忽略的 .local/ 或系统临时目录。每次维护使用 .local/PROJECT_STATUS.md 保存动态状态。

仅在用户明确要求时推送。推送前复核远端基线与在途修改，从干净已提交版本集成；检查暂存内容不包含个人配置、企业信息、认证数据或输出。GitHub是技能源码交付，不代表任何飞书业务操作或生产部署已获授权。
