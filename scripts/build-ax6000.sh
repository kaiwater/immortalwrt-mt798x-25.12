#!/bin/sh
# Build Redmi AX6000 (stock layout) from a chasey-dev tree.
# Usage: ./scripts/build-ax6000.sh [passwall|openclash] [source-tree]
set -eu

VARIANT=${1:-passwall}
SRC=${2:-/mnt/qnap/projects/wrt/rax-src}
REPO_DIR=$(cd "$(dirname "$0")/.." && pwd)
DL_DIR=${DL_DIR:-/mnt/qnap/dl}
CCACHE_DIR=${CCACHE_DIR:-/mnt/qnap/ccache}

case "$VARIANT" in
    passwall)  CONFIG=$REPO_DIR/defconfig/redmi-ax6000-stock.config ;;
    openclash) CONFIG=$REPO_DIR/defconfig/redmi-ax6000-stock-openclash.config ;;
    *) echo "usage: $0 [passwall|openclash] [source-tree]" >&2; exit 1 ;;
esac

[ -d "$SRC" ] || { echo "ERROR: source tree not found: $SRC" >&2; exit 1; }

KVER=$(awk -F'= ' '/^LINUX_VERSION-6\.12/ {print $2}' "$SRC/target/linux/generic/kernel-6.12")
if [ "$KVER" != ".116" ]; then
    echo "ERROR: $SRC is kernel 6.12$KVER, required 6.12.116." >&2
    echo "       Use chasey-dev/immortalwrt-mt798x-rebase 25.12, not this kaiwater fork." >&2
    exit 1
fi

grep -q 'xiaomi_redmi-router-ax6000-stock' "$SRC/target/linux/mediatek/image/filogic.mk" || {
    echo "ERROR: AX6000 device definition not found in $SRC" >&2
    exit 1
}

cd "$SRC"
cp "$CONFIG" .config

# local-only settings
sed -i 's|^CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT=.*|CONFIG_GOLANG_EXTERNAL_BOOTSTRAP_ROOT="/opt/go-bootstrap"|' .config
grep -q '^CONFIG_CCACHE=y' .config || echo 'CONFIG_CCACHE=y' >> .config
sed -i '/^CONFIG_CCACHE_DIR=/d' .config
echo "CONFIG_CCACHE_DIR=\"$CCACHE_DIR\"" >> .config

[ -d "$DL_DIR" ] && ln -sfn "$DL_DIR" dl

if [ ! -d feeds ]; then
    ./scripts/feeds update -a
    ./scripts/feeds install -a
fi

make defconfig
grep -qx 'CONFIG_TARGET_DEVICE_mediatek_filogic_DEVICE_xiaomi_redmi-router-ax6000-stock=y' .config || {
    echo "ERROR: AX6000 device was dropped by defconfig" >&2
    exit 1
}
grep -qx 'CONFIG_PACKAGE_kmod-mt_wifi=y' .config || {
    echo "ERROR: kmod-mt_wifi missing" >&2
    exit 1
}

if [ "$VARIANT" = "openclash" ]; then
    sh "$REPO_DIR/scripts/prepare-openclash.sh"
fi

if [ "${CLEAN_ROOTFS:-0}" = "1" ]; then
    rm -rf staging_dir/target-*/root-mediatek staging_dir/target-*/stamp
    rm -f bin/targets/mediatek/filogic/*ax6000*
fi

export CCACHE_DIR
make download -j"$(nproc)"
make -j"$(nproc)"
