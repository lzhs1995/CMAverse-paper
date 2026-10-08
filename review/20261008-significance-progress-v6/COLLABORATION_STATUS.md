# 协作维护状态（阶段记录）

本文件解释等待原因和已核定版本，不是原生Word验收凭证；任务资源状态不得从本文件推断为实时空闲。

- 两个原Claude与Codex均属workspace13。不得用共享daemon的环境误报跨工作区。
- r19已由主管核收、裁定并结束；原会话工具恢复。旧CALLBACK_UNCONFIRMED提示不代表当前仍受锁。
- r20已armed而未有正式task-pack／ACK；219分钟idle升级说明派工生命周期存在待处理问题，不能解释为API连续失败。
- multi-agent-collaboration PR20已合并：ea91ab6df50ff972725cdc3151a6f00c5dca7e32。
- thesis-refiner PR21已合并：180d6b838a804946e46c71d8a6716d085a6f62d4。
- 对这两个新合并版本的安装后继仍为准备态，未apply；不能宣称所有客户端已加载。
- idle-pull候选MC PR22（56ef0a076358e1825fadb7fc983c946da8ed80fd）及TR PR23（e6e0d677da5043be9a588a07ad0361f1710905fc）CI通过，但独审发现两项P1：失败派发可能误清idle请求；ACK未核实际caller。当前不合并，准备最小修补及固定HEAD独审。
- 300秒连续真实API失败门槛、成功重置，以及主管可独立继续，仍适用。提交PR、合并、安装、原会话运行验证是不同状态。
- 网页端研究反馈无需审查整套协作源码；有技术疑点时只请求对应最小原始证据，不扩成协作系统重构。
