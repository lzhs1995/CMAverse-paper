# 原准备包来源映射的范围说明

SOURCE_BINDINGS.json 是原始小型准备包的不可变来源快照；其中 included_in_this_package 只描述那个准备包，不能用于判断本轮扩展包是否包含报告全文。

本轮 cf90d5982da4ed4b82eee1ed78287253a9ced399 的 repair_feedback_part01.zip 已实际包含两份完整 Claude 报告：
- CLAUDE_NATIVE_REVIEW.md：13,394 字节，SHA-256 b841595bf006d4df0159197f5f094dea26f01f64c69dc5e2e9863c869629b823。
- CLAUDE_BIBLIOGRAPHY_REVIEW.md：15,182 字节，SHA-256 3bf4c8cd01aa3dc9bbec0709d9621cc8ed84ba8239f0ccc42c7f4735f804ae94。

当前包内成员以 MANIFEST.json 和 DELIVERY_MANIFEST.json 为准。固定提交回下载已验证17个公开文件、ZIP全部15成员及CRC；见 REMOTE_VERIFICATION_CF90D59.json。

本说明与回下载记录是包外追加件，不修改旧ZIP及其清单。审阅资料完整性通过不代表最终Word/PDF/NLM验收完成。
