# Dropbear 2025.89 安全回移

25.12 分支当前使用 Dropbear 2025.89。上游在 2026.90 到 2026.93 之间修复了若干
安全问题，其中与我们的构建相关的是：

- CVE-2026-3706：curve25519 缺少 RFC 8032 要求的 `S < L` / `y < p` 检查，
  属于 Ed25519 签名可延展性。上游认为 SSH 协议下不可利用，但仍按上游修复回移。
- `-t`（双因素）下可绕过 authorized_keys 的 `forced_command`。
- `-t` 与 `-B`（允许空密码）组合时的认证逻辑问题。
- 超长 authorized_keys 行会被拆成新行，可能绕过 `command=` 等限制。

## 文件

| 文件 | 上游提交 |
|---|---|
| `0009-curve25519-add-s-l-check.patch` | 578c834e |
| `0010-curve25519-check-y-lt-p.patch` | 58dafa6e |
| `0011-disallow-two-factor-with-blank-passwords.patch` | 23ec7828 |
| `0012-avoid-splitting-long-authorized-keys-lines.patch` | 8d8e1930 |

`0001` 到 `0008` 是 OpenWrt 25.12 已回移的 2026.90/2026.91 修复。部分构建树
（例如本仓库的旧分支）没有这些补丁，因此这里一并保留，构建时整体复制。

## 使用

构建脚本在 `package/network/services/dropbear/Makefile` 的 `PKG_VERSION` 为
`2025.89` 时，会把本目录所有 `*.patch` 复制到
`package/network/services/dropbear/patches/`，然后由 OpenWrt 的补丁机制应用。

上游升级到 2026.94 或更高版本后，这些回移补丁不再需要，脚本会自动跳过。
