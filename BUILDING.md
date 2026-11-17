# 构建 Redmi AX6000（必读）

> [!IMPORTANT]
> **最终固件必须用 `chasey-dev/immortalwrt-mt798x-rebase` 25.12 构建（kernel 6.12.116）。**
>
> 本仓库（`kaiwater/immortalwrt-mt798x-25.12`）只维护 `defconfig/`、workflow 和文档；
> 它的内部源码树是 **6.12.87**，不能用于最终发布。

## 为什么容易搞错

内核版本由**源码树**决定，不是设备：

| 树 | kernel-6.12 |
| --- | --- |
| `kaiwater/immortalwrt-mt798x-25.12`（本仓库） | 6.12.87 |
| `chasey-dev/immortalwrt-mt798x-rebase` | 6.12.116 |

在 kaiwater 树里直接 `make` 会得到 6.12.87，和 rax3000 系列的 6.12.116 不一致。

## 一键构建（推荐）

```sh
# 默认从 /mnt/qnap/projects/wrt/rax-src 取 chasey-dev 树
./scripts/build-ax6000.sh passwall
./scripts/build-ax6000.sh openclash

# 指定其他 chasey-dev 树
./scripts/build-ax6000.sh passwall /path/to/chasey-dev-25.12
```

脚本会先做硬校验，不符合就直接退出：

- `target/linux/generic/kernel-6.12` 必须是 `.116`
- `target/linux/mediatek/image/filogic.mk` 必须包含 `xiaomi_redmi-router-ax6000-stock`
- `make defconfig` 后必须选中 AX6000 device 和 `kmod-mt_wifi`

## 手动构建

```sh
SRC=/path/to/chasey-dev-25.12
REPO=/path/to/this/repo

grep '^LINUX_VERSION-6.12' "$SRC/target/linux/generic/kernel-6.12"   # 必须是 .116

cd "$SRC"
cp "$REPO/defconfig/redmi-ax6000-stock.config" .config          # 或 openclash 版
ln -sfn /mnt/qnap/dl dl

# 仅本地：ccache + arm64 Go 引导
sed -i 's|^CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT=.*|CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT="/opt/go-bootstrap"|' .config
grep -q '^CONFIG_CCACHE=y' .config || echo 'CONFIG_CCACHE=y' >> .config
sed -i '/^CONFIG_CCACHE_DIR=/d' .config
echo 'CONFIG_CCACHE_DIR="/mnt/qnap/ccache"' >> .config

make defconfig
grep -qx 'CONFIG_TARGET_DEVICE_mediatek_filogic_DEVICE_xiaomi_redmi-router-ax6000-stock=y' .config

# openclash 变体额外执行
sh "$REPO/scripts/prepare-openclash.sh"

make download -j"$(nproc)"
make -j"$(nproc)"
```

## 变体

| 变体 | defconfig | 内容 |
| --- | --- | --- |
| passwall | `defconfig/redmi-ax6000-stock.config` | passwall + sing-box |
| openclash | `defconfig/redmi-ax6000-stock-openclash.config` | OpenClash + core + gfwlist，无 passwall/sing-box |

两个变体都已移除 USB / SMB / diskman。

## 发布命名

- `k616` = kernel **6.12.116**
- 正式 tag 不带 `k616`，但内容一致；旧的 `*-k616` 临时 tag 已删除
- 6.12.87 的构建已清理，不再发布

Release 清单与容量见 [docs/releases.md](docs/releases.md)。

## 相关文档

- [docs/lima-local-build.md](docs/lima-local-build.md)：Lima 环境、目录关联、缓存
- [docs/releases.md](docs/releases.md)：tag 对照、资产、ccache
- [docs/geodata-apk.md](docs/geodata-apk.md)：geodata apk 的路径与安装
