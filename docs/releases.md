# Redmi AX6000 Release 说明

## 命名约定

- **`k616` = kernel 6.12.116**。早期临时 tag `redmi-ax6000-*-k616` 已删除，内容合并回不带 `k616` 的正式 tag。
- 正式 tag 不带 `k616`，但内容与 k616 构建完全一致。
- 早期 6.12.87 构建已清理，不再发布。

## 当前发布（4 个 tag，内容两两相同）

| Tag | 变体 | 内核 | rootfs | overlay | geodata apk |
| --- | --- | --- | --- | --- | --- |
| `redmi-ax6000-passwall-20261118` | passwall slim | 6.12.116 | ~40.4 MiB | ~36 MiB | `passwall-geodata` |
| `redmi-ax6000-passwall-slim-20261118` | passwall slim | 6.12.116 | ~40.4 MiB | ~36 MiB | `passwall-geodata` |
| `redmi-ax6000-openclash-20261118` | OpenClash slim | 6.12.116 | ~45.2 MiB | ~31 MiB | `openclash-geodata` |
| `redmi-ax6000-openclash-slim-20261118` | OpenClash slim | 6.12.116 | ~45.2 MiB | ~31 MiB | `openclash-geodata` |

说明：两个不带 `-slim` 的历史 tag 现在也指向 slim 内容（USB/SMB/diskman 已移除），保留只是为了不破坏旧链接。

## 构建来源

- 源码：`chasey-dev/immortalwrt-mt798x-rebase` 25.12
- 内核：`6.12.116~9aee1ecb35a921847e27b3039087cb06-r1`
- 无线：mtwifi `6.12.116.7.6.7.3`
- kaiwater 仓库只维护 `defconfig/`、workflow 与文档；其内部树是 6.12.87，不用于最终发布

## 资产清单

每个 release 包含：

```
config.buildinfo
<...>-initramfs-factory.ubi
<...>-initramfs-kernel.bin
<...>-squashfs-sysupgrade.bin
immortalwrt-mediatek-filogic.manifest
<variant>-geodata-20261118-r1.apk
RELEASE.txt
SHA256SUMS
```

`SHA256SUMS` 包含 geodata apk；`RELEASE.txt` 记录 variant / kernel / 文件大小。

## 构建缓存（ccache）

- openclash 6.12.116 阶段：392 / 393 cacheable = **99.75%** 命中（1 miss）
- passwall 阶段：起跑前未清零，无法精确还原；累计 33.10%（含历史构建），且该阶段的 sing-box/passwall 不走 ccache

## 相关文档

- 本地构建：[lima-local-build.md](lima-local-build.md)
- geodata apk：[geodata-apk.md](geodata-apk.md)
