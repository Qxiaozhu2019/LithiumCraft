# Data Model

## Source

来源配置。字段包括名称、类型、入口 URL、域名、状态、抓取间隔、解析策略、域名访问间隔、单次最大页数、每日上限、失败次数、最近成功时间和最近错误。

类型：`announcement`、`policy`、`media`、`paper`、`patent`、`rss`、`webpage`。

状态：`enabled`、`disabled`、`manual_only`、`blocked_by_policy`。

## IntelligenceItem

内部情报条目。字段包括标题、规范化标题、摘要、正文片段、来源 URL、来源名称、来源发布时间、抓取时间、分类、标签、重要性评分、状态、阻断原因。

状态：`active`、`blocked`、`archived`。

## DailyBrief

每日摘要。字段包括日期、标题、总览摘要、重点条目、分类摘要、生成状态、生成时间。

生成状态：`pending`、`success`、`failed`。

## CrawlTask

抓取任务记录。字段包括任务类型、来源、状态、抓取数量、入库数量、阻断数量、错误信息、耗时、开始时间、结束时间。

## Category

分类。默认包括企业动态、政策监管、价格材料、设备工艺、产能项目、技术路线、投融资、专利论文、行业快讯。

## SystemSetting

系统设置。存储键值配置，例如每日摘要时间、默认抓取频率、敏感词列表。

## SystemLog

系统日志。记录抓取、AI、摘要、错误和登录等事件。
