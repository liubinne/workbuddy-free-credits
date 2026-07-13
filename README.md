# WorkBuddy 全自动免费领积分

免费开源、免费分享，每天自动领取自己 WorkBuddy 账号的签到积分。每位用户只操作自己电脑上当前登录的账号；工具不收集、不上传、不保存账号凭证。

## 安装方法

根目录里的 `安装说明-复制给WorkBuddy.txt` 已经分别写好两套复制话术，macOS 和 Windows 通用：

1. **能访问 GitHub**：把 GitHub 在线安装话术复制给 WorkBuddy。WorkBuddy 会下载仓库、识别当前系统、检查环境、安装并验证。
2. **不能访问 GitHub 或使用微信收到的 ZIP**：先解压 ZIP，在 WorkBuddy 中打开解压后的 `workbuddy-auto-checkin` 文件夹，再把本地安装话术复制给 WorkBuddy。这个过程不需要访问 GitHub。

ZIP 本地安装必须使用当前文件夹中已经提供的文件，不允许 AI 猜测或重写代码。电脑还需要已经安装 Python 3；如果缺少 Python 3 且电脑不能联网，需要先通过其他方式取得 Python 安装程序。

无论使用哪种安装方式，WorkBuddy 都会先识别 macOS 或 Windows，再调用对应的安装流程。本地方式解决的是“不能访问 GitHub”，不是“电脑完全断网”；完全断网时 WorkBuddy 的 AI 可能无法工作，每日领取也无法连接腾讯服务。

## 备用方法：双击安装

- macOS：双击 `install-macos.command`。
- Windows：双击 `install-windows.cmd`。

默认每天 `06:05` 运行。需要其他时间时，让 AI 执行：

```bash
python3 scripts/install.py --time 08:30 --run-now
```

Windows 可用 `py -3` 替换 `python3`。

## 安装前提

- 已安装并登录 WorkBuddy 桌面端。
- 已安装 Python 3。
- 电脑在计划时间开机或之后再次唤醒。

## 隐私

- 除本文末尾主动公开的作者名和微信号外，仓库不包含邮箱、账号、Token、Cookie、个人绝对路径或其他个人信息。
- Token 只在签到进程内存中短暂使用，不写入本工具目录和日志。
- 日志只记录时间和脱敏后的成功/失败结果。
- 不要向任何人发送 `workbuddy-desktop.info`。

## 卸载

```bash
python3 scripts/install.py --uninstall
```

卸载不会删除 WorkBuddy 登录信息。日志和旧任务备份会保留，便于排查或恢复。

## 当前验证范围

- macOS：核心请求、登录文件探测、LaunchAgent 生成、安装与卸载流程均可验证。
- Windows：支持 `%LOCALAPPDATA%` 与 `%APPDATA%` 候选路径；计划任务使用完整 Python 路径、支持带空格路径、错过后补跑并保存日志。
- 真实 Windows 账号领取仍应在已登录 WorkBuddy 的 Windows 10/11 电脑上完成最终验收。

## 说明

这是非官方社区工具，与腾讯云、WorkBuddy 或 CodeBuddy 没有隶属、合作或背书关系。接口、登录文件位置和活动规则可能随产品更新而变化，使用者自行决定是否使用并承担账号与服务规则风险。

## License

MIT。详见 `LICENSE`。

作者：鹿游｜微信号：Agent2603
