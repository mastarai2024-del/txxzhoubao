# txxzhoubao

适用于 Codex 的飞书周报、月报整理技能。从文档、知识库、会议、群聊、日历及飞书项目收集本人工作，沿用上期格式，交付有来源的草稿。

## 在另一台电脑安装

登录有权访问本私有仓库的 GitHub 账号后，把下面这段话发给那台电脑的 Codex：

```text
使用 skill-installer，将 GitHub 仓库 mastarai2024-del/txxzhoubao 根目录的技能安装为 txxzhoubao。按 references/setup.md 检查并接入飞书协作和飞书项目，复用本机已有应用与登录；只申请周报必需且尚未授予的读取权限。运行 scripts/check_access.py，说明哪些来源仍需实际读取验证。个人周报地址和身份只保存在本机私有配置，不提交到仓库。
```

也可调用 Codex 自带安装器，参数为 `--repo mastarai2024-del/txxzhoubao --path . --name txxzhoubao`。技能在下一轮对话可用。

新电脑仍需分别核验飞书协作和飞书项目登录。技能文件不包含凭据、设备授权码或账号权限，也不迁移公司数据。个人周报链接、本人行和项目空间可按 [私有配置模板](assets/profile-template.md) 在新电脑补充一次。

## 使用

```text
$txxzhoubao 帮我整理本周周报，先给草稿，沿用上期格式。
$txxzhoubao 汇总这个月的工作，并列出还没覆盖的信息源。
```

已有上期周报时保留其模块和字段；没有格式时使用事项、目标、进展、风险、需要的资源、下周计划。写入飞书、发送或定时运行需用户明确要求。

## 检查

使用 Python 3（Windows 可使用 `py -3`）：

```sh
python3 scripts/check_access.py
python3 -m unittest discover -s tests -v
```

接入检查只核验工具、认证和已授予权限，输出脱敏结果；退出码 `2` 表示尚有缺口。它不会申请权限或读取业务正文，也不证明全部来源已可用。正式验收见 [信息源指南](references/info-sources.md)。

## 边界与依据

本技能不依赖豆包、某台电脑的绝对路径或其他自定义技能。命令由官方 CLI 的当前帮助和内置说明提供：[飞书协作 CLI](https://github.com/larksuite/cli)、[飞书项目 CLI](https://github.com/larksuite/meegle-cli)。历史版本的验证情况见 [CHANGELOG.md](CHANGELOG.md)；新电脑和后续版本须重新做真实读取验证。
