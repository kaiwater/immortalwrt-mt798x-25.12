# ImmortalWrt - MT798x

> [!IMPORTANT]
> **固件构建请使用 `chasey-dev/immortalwrt-mt798x-rebase` 25.12（kernel 6.12.116）。**
> 本仓库只维护 `defconfig/`、workflow 和文档，内部源码树是 6.12.87，不能用于最终发布。
> 详见 [BUILDING.md](BUILDING.md)。

```
This repository is worked on ImmortalWrt with MTK OpenWrt Feeds patches imported.
```

## Commit Cutoff Revisions

### ImmortalWrt: [e660cbc](https://github.com/immortalwrt/immortalwrt/commit/e660cbc917924389164967211777106020b3cd56) - OpenWrt 25.12.4

```
Merge Official Source

Signed-off-by: Tianling Shen <cnsztl@immortalwrt.org>
```

### MTK OpenWrt Feeds: [9372bc8](https://git01.mediatek.com/plugins/gitiles/openwrt/feeds/mtk-openwrt-feeds/+/9372bc8b1266463da068e5e9a59136d91fd004fb)

```
[][openwrt-25][common][bsp][Add the extra_firmware variable to facilitate appending built-in firmware names in other rules scripts]

[Description]
Add the extra_firmware variable to facilitate appending built-in
firmware names in other rules scripts.

[Release-log]
N/A


Change-Id: Ie471c6e3fcf85103ade3d547efdb34ad117e5d77
Reviewed-on: https://gerrit.mediatek.inc/c/openwrt/feeds/mtk_openwrt_feeds/+/12086920
```

### l1parser: [081bb31](https://github.com/chasey-dev/l1parser/commit/081bb31211efc74594d25bfd1bb5811f3408a205)

```
feat(ucode): add get all device map support
```
## About External Devices HNAT
> [!WARNING]
> Current HNAT support for external devices is basic and lack of complete test for various types. Please use with caution.

> [!IMPORTANT]
> Please keep interface `rxppd` in your bridge device (e.g. `br-lan`) while using external device HNAT.

### Support Matrix:
|               |  Ext as WAN   | Ext as LAN                |
|   :----:      |   :----:      | :----:                    |
|  **Ethernet** |      ✔️       |   ❌                     |
| **AP/ApCli**  |      ✔️       |   ⚠️(**Untested**)       |

## Acknowledgements
HNAT support for external devices is adapted from [Padavanonly's repo](https://github.com/padavanonly/immortalwrt-mt798x-6.6). 
## Local build (Lima)

日常构建在本地 Lima（`qnap-test`）里完成，复用 `/mnt/qnap/dl` 与 `/mnt/qnap/ccache`；
GitHub Actions 仅作为可选备份，受额度限制不作为常规验证手段。

详见 [docs/lima-local-build.md](docs/lima-local-build.md)，其中写明：

- Lima 环境与 `/mnt/qnap` 目录布局
- `rax-builder`（本仓库）与 `rax-src`（chasey-dev 上游参照）的关系
- Redmi AX6000 (`xiaomi_redmi-router-ax6000-stock`, mtwifi) 的本地构建步骤与产物
- 本地构建与 `redmi_ax6000.yml` 的对应关系、两套缓存如何区分
