#!/bin/sh
set -eu
OC=
for p in package/feeds/*/luci-app-openclash; do
    if [ -e "$p" ]; then
        OC=$(readlink -f "$p")
        break
    fi
done
if [ -z "$OC" ]; then
    echo "luci-app-openclash is not installed in package/feeds" >&2
    exit 1
fi
CORE_DIR=$OC/root/etc/openclash/core
CORE_CACHE=dl/openclash-core-meta-arm64.tar.gz
mkdir -p $CORE_DIR
if [ ! -s $CORE_CACHE ]; then
    curl -fL --retry 3 -o $CORE_CACHE https://raw.githubusercontent.com/vernesong/OpenClash/core/master/meta/clash-linux-arm64.tar.gz
fi
rm -rf $CORE_DIR/.extract
mkdir -p $CORE_DIR/.extract
tar -xzf $CORE_CACHE -C $CORE_DIR/.extract
mv $CORE_DIR/.extract/clash $CORE_DIR/clash_meta
rm -rf $CORE_DIR/.extract
chmod 0755 $CORE_DIR/clash_meta
RULES=feeds/luci/applications/luci-app-passwall/root/usr/share/passwall/rules
cp -f $RULES/gfwlist $OC/root/etc/openclash/gfwlist
cp -f $RULES/chnlist $OC/root/etc/openclash/chnlist
echo "package: $OC"
ls -lh $CORE_DIR/clash_meta $OC/root/etc/openclash/gfwlist $OC/root/etc/openclash/chnlist
