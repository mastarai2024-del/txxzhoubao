# Codex 读取路线

优先使用官方 CLI 自带说明：`lark-cli skills read lark-shared`，再按需要加载 `lark-doc`、`lark-wiki`、`lark-im`、`lark-calendar` 或 `lark-meeting`。不用额外安装其他个人技能，也不依赖豆包企业搜索。先读当前命令 `--help`，短示例中的值均由本次实际来源取得。

## 文档与知识库

- `lark-cli docs +search --query <真实关键词> --as user` 找周报及本期文档，逐页查看 `has_more` / `page_token`。
- `wiki +node-get --node-token <实际URL> --as user` 解析对象类型与空间；`wiki +space-list` / `wiki +node-list` 浏览目录时继续显式 user 身份。空间 ID、节点 token 与文档 token 分开使用。
- `docs +fetch --doc <实际URL> --as user` 读正文。大表格可按关键字定位本人，但要保留表头、上期和本期单元格上下文。节点列表、搜索摘要不是正文。
- 修改时间只说明对象被更新。结合编辑者、版本、历史或文内明确日期确认本人工作；旧文章本周打开不算本周新增成果。

## 群聊

`im +messages-search` 使用 `--start`、`--end` 和当前用户 `--sender`；另查 `--is-at-me`，再沿实际 chat/thread 读取讨论。`query` 只放真实关键词，不能把“本周我做了什么”当成字面查询。

汇总前完成分页。使用 `--page-all` / 当前版本支持的页数上限；仍有下一页则续读或说明未覆盖，不能只看首屏就称完整。核对决策、责任、期限与后续消息，去掉重复讨论。缺权限不切 bot 冒充本人视角。

搜索结果必须有正文才能提炼进展。如果返回只有 `message_ids`，或提示详情获取失败，使用真实ID调用 `im +messages-mget` 检查正文权限。当前工具对 `mget` 和已知群历史读取都同时要求群聊、私聊两项用户读取权限；这是工具预检范围，不能偷偷扩大实际采集范围。向用户说明后按所需授权，仍只读取本次约定的工作内容。

通过工具预检后，消息服务还可能返回 `im:message:readonly` / `im:message` 缺口，新增只申请其中的只读项。真正的业务验收须读到项目群的人类消息或可核对的项目事件；与助手打招呼、测试接入和让机器人写报告的对话只作连通性证据，不计入个人工作进展。自动项目状态通知可作状态来源，但不能据此把他人的动作写成本人完成。

## 日历和会议

`calendar +agenda --start <带时区起点> --end <带时区终点> --as user` 查漏。会议可用 `minutes +search`（参与人使用本版本支持的当前用户选择器），或搜索会议纪要文档。

从真实结果拿到 minute token 后，`minutes +detail --minute-tokens <token> --summary --todo --as user` 读产物；需要逐字稿时先核对 `--transcript` 帮助及最小权限，并指定本任务目录。注意 `minutes +summary` 在部分版本是改写摘要，不能拿它当读取命令。

纪要文档可读而妙记原文缺权限时分开标注。AI 纪要是来源记载，重要数字和完成结论与需求、消息或项目状态交叉核对。

`minutes +detail` 不带产物flag只返回基础信息；请求摘要、待办或逐字稿还需核对 `minutes:minutes.artifacts:read`。只有实际取得产物正文或核验逐字稿文件内容后，才记为对应路线通过。

## 项目需求和缺陷

1. 先 `meegle auth status --format json`，再 `user me`、`project search`；身份需与协作用户对应，两个系统 ID 不能互换。
2. 用 `workitem meta-types` 确认真实类型 key，再 `workitem meta-fields` 取得字段。多个同名空间或对象无法唯一确定时先消歧。
3. 当前 CLI 的 `workitem query --help` / `inspect` 为参数和 MQL 依据。优先 key，并用完整 SELECT/FROM；反引号包住字段和表名，字符串用单引号。通过参数数组或正确 shell 引号传 SQL，避免反引号被 shell 执行。
4. 可用本人全部参与人筛选：`array_contains(all_participate_persons(), current_login_user())`。按当前 schema 取得实际字段后选择 ID、名称、时间和状态，再读取候选详情。不能只靠待办：`mywork todo --action this_week` 返回 0 不证明没有本期工作。
5. 使用本期创建、变更时间或操作记录过滤；相关条目不等于本人做完。只看到“更新时间”不能推断本周由什么状态迁移到什么状态。必要时 `list-op-records` 核对。
6. 以详情结构化状态、优先级、角色和节点为准。标题中的旧 P1 标签可能与当前字段 P2 不同；保留冲突证据，不据标题宣布等级或完成。
7. 查询分页以当前 `session_id`、`group_id` 和分页参数为准。LIMIT 只截断结果，不是完整分页；未获取全部候选时注明范围。

## 输出检查

协作命令判断 `ok` 与实际数据，不检查不存在的成功 `code`。Meegle 结合退出码、`error` 和具体状态；`list: null` 可以是无结果。每条素材能回溯到原对象和本期时间、本人关系；查询失败和成功无结果分开记录。
