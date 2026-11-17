# Lima 本地构建（Redmi AX6000 / MT7986）

本文说明本仓库在本地 Lima 虚拟机里的构建方式，以及它和 GitHub Actions（`.github/workflows/redmi_ax6000.yml`）的关系。

> **默认走本地构建。** GitHub Actions 有额度和分钟数限制，日常编译、验证、出固件都在 Lima 里完成；workflow 只作为可选备份/分发渠道，不作为验证手段。

## 1. 环境

| 项目 | 值 |
| --- | --- |
| Lima 实例 | `qnap-test`（`limactl shell qnap-test`） |
| 后端 / 架构 | Apple Virtualization (vz) / aarch64 |
| 规格 | 8 vCPU / 8 GiB RAM / 20 GiB 系统盘 |
| 构建盘 | `/mnt/qnap`，iSCSI multipath + ext4，约 300 GiB |
| 共享下载 | `/mnt/qnap/dl` |
| ccache | `/mnt/qnap/ccache` |
| 日志 | `/mnt/qnap/logs` |
| Go 引导编译器 | `/opt/go-bootstrap` → `/mnt/qnap/toolchains/go-bootstrap`（go1.24.13 linux-arm64） |

构建目录全部落在 `/mnt/qnap`，系统盘只放 VM 本身。

## 2. 目录与仓库关联

| 路径 | 远端 | 分支 | 用途 |
| --- | --- | --- | --- |
| `/mnt/qnap/projects/wrt/rax-builder` | `kaiwater/immortalwrt-mt798x-25.12` | `25.12` | **本地构建树 + 维护仓库**（defconfig、workflow、AX6000 device 补丁） |
| `/mnt/qnap/projects/wrt/rax-src` | `chasey-dev/immortalwrt-mt798x-rebase` | `25.12` | 上游参照树；用于验证 defconfig 兼容性、对照 device 定义 |

关系要点：

- **本地构建直接使用 `rax-builder` 的工作区**，包括尚未推送的改动。
- CI 不使用 `rax-builder` 的本地状态：workflow 会重新 clone `chasey-dev` 的上游树，再把触发分支 checkout 里的 `defconfig/` 注入进去。因此配置改动要先 push 到 `25.12`，CI 才能读到。
- `rax-builder` 的 `target/linux/mediatek/image/filogic.mk` 里补了 AX6000 的 device 定义，只用于**本地编 kaiwater 树**；CI clone 的 chasey-dev 树本身自带该定义，不依赖这个补丁。

## 3. Redmi AX6000 的构建配置

- 设备：`xiaomi_redmi-router-ax6000-stock`（保留小米原厂 bootloader / 原厂分区布局）
- 配置文件：`defconfig/redmi-ax6000-stock.config`
- 无线：mtwifi（`kmod-mt_wifi` + `mt7986-fw-20250408`）
- 非平台软件包：与 rax3000m 相同的一套（passwall、sing-box、AdGuardHome、diskman、samba4、vlmcsd、USB/文件系统工具等）
- 首次刷机：`initramfs-factory.ubi` → 进入 initramfs 后刷 `squashfs-sysupgrade.bin`

## 4. 本地构建步骤

```sh
limactl shell qnap-test

cd /mnt/qnap/projects/wrt/rax-builder

# 共享下载缓存
ln -sfn /mnt/qnap/dl dl

# 可选：同步上游（保持与 CI 一致）
git fetch origin
git rebase origin/25.12

# feeds
./scripts/feeds update -a
./scripts/feeds install -a

# 套配置
cp defconfig/redmi-ax6000-stock.config .config

# 仅本地：打开 ccache 并指向 QNAP 缓存（不要提交这两行）
grep -q '^CONFIG_CCACHE=y' .config || echo 'CONFIG_CCACHE=y' >> .config
sed -i '/^CONFIG_CCACHE_DIR=/d' .config
echo 'CONFIG_CCACHE_DIR="/mnt/qnap/ccache"' >> .config

# 仅本地（arm64 宿主）：使用 QNAP 里预置的 Go 1.24.13 作为引导编译器。
# 不设置时 OpenWrt 会去编 go1.4 bootstrap，而它不支持 linux/arm64，直接报错。
sed -i 's|^CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT=.*|CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT="/opt/go-bootstrap"|' .config

make defconfig

# 确认设备和无线没有被 defconfig 丢掉
grep -qx 'CONFIG_TARGET_DEVICE_mediatek_filogic_DEVICE_xiaomi_redmi-router-ax6000-stock=y' .config
grep -qx 'CONFIG_PACKAGE_kmod-mt_wifi=y' .config
grep -qx 'CONFIG_MTK_CHIP_MT7986=y' .config

make download -j8
CCACHE_DIR=/mnt/qnap/ccache make -j8
```

后台构建示例（日志落到 QNAP）：

```sh
TS=$(date +%Y%m%d-%H%M%S)
LOG=/mnt/qnap/logs/redmi-ax6000-build-$TS.log
CCACHE_DIR=/mnt/qnap/ccache nohup sh -c 'make download -j8; make -j8' > "$LOG" 2>&1 &
```

产物：

```
bin/targets/mediatek/filogic/
├── *xiaomi_redmi-router-ax6000-stock-squashfs-sysupgrade.bin
├── *xiaomi_redmi-router-ax6000-stock-initramfs-kernel.bin
├── *xiaomi_redmi-router-ax6000-stock-initramfs-factory.ubi
└── config.buildinfo / feeds.buildinfo
```

## 5. 与 GitHub Actions 的关联（可选备份）

`redmi_ax6000.yml` 的流程：

1. `actions/checkout`（触发分支）
2. `git clone chasey-dev/immortalwrt-mt798x-rebase 25.12 --depth 1` → `openwrt/`
3. 若 dropbear 版本为 2025.89，从 checkout 的 `patches/dropbear/` 回移补丁
4. restore `openwrt/dl`、`openwrt/.ccache`、`openwrt/staging_dir` 缓存
5. `cp ../defconfig/redmi-ax6000-stock.config .config`（**来自 checkout，不是 clone**）
6. `make defconfig` + 校验 device / mtwifi 符号
7. `make download` → `make -j$(nproc) V=s || make -j1 V=sc`
8. 成功后回写 `.last_sync_commit`，保存缓存，上传 artifact 并发布 Release

对照表：

| 维度 | 本地 Lima | GitHub Actions |
| --- | --- | --- |
| 源码 | `rax-builder` 工作区（含未推送改动） | 重新 clone `chasey-dev` 25.12 |
| 配置来源 | 本地 `defconfig/` | 触发 ref 的 checkout 里的 `defconfig/` |
| 下载缓存 | `/mnt/qnap/dl`（symlink 到 `dl`） | `openwrt/dl` 的 Actions cache |
| 编译缓存 | `/mnt/qnap/ccache` | `openwrt/.ccache` 的 Actions cache |
| 增量缓存 | 树内 `staging_dir` / `build_dir` | `openwrt/staging_dir` 的 Actions cache |
| AX6000 device 定义 | `rax-builder` 的 `filogic.mk` 补丁 | 上游 chasey-dev 自带 |
| 触发 | 手动 | `workflow_dispatch` |

注意：

- 日常不依赖 CI：本地编译产物即最终产物；只有确实要走 Actions 时才需要下面的 push 约束。
- **改 defconfig / workflow 后必须 push 到 `25.12`**，否则 CI 的 checkout 取不到；本地构建不受影响。
- 本地与 Actions 的缓存互不共享，两套缓存各自独立。
- 该仓库是 fork，Actions 默认被禁用；首次使用需在仓库 Actions 页面启用（或关闭账号级 “Disable actions on forked repositories”）。
- 若上游 `chasey-dev` 把 AX6000 定义移除或改名，CI 会在 Configure 步骤的 `grep -qx` 校验处直接失败，而不是产出空镜像。

## 6. 故障排查

### `go-bootstrap cannot be installed on linux/arm64`

```
Makefile:336: *** go-bootstrap cannot be installed on linux/arm64.  Stop.
ERROR: package/feeds/packages/golang-bootstrap [host] failed to build.
```

原因：`golang-bootstrap` 的默认引导编译器是 go1.4，只有 amd64/386/arm 版本；aarch64 宿主必须用外部 Go。

处理：

```sh
sed -i 's|^CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT=.*|CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT="/opt/go-bootstrap"|' .config
make defconfig
make package/feeds/packages/golang-bootstrap/host/compile -j8
make -j8
```

`/opt/go-bootstrap` 在 VM 里已软链到 `/mnt/qnap/toolchains/go-bootstrap`，版本为 go1.24.13 linux-arm64。

> `CONFIG_CCACHE_DIR` 与 `CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT` 都是**本机专属**，不要写进提交的 `defconfig/`。

## 7. 常见维护操作

```sh
# 只重新生成 defconfig（改包后）
cp defconfig/redmi-ax6000-stock.config .config
make defconfig
cp .config defconfig/redmi-ax6000-stock.config   # 提交前确认已去掉 CONFIG_CCACHE_DIR

# 全量重编
make clean

# 只重编固件（不动工具链）
make target/linux/install

# 查看当前配置是否选中设备
grep -n 'DEVICE_xiaomi_redmi-router-ax6000-stock' .config
```

提交 `defconfig` 前请确认：

```sh
grep -n 'CONFIG_CCACHE' defconfig/redmi-ax6000-stock.config   # 应为空
```
