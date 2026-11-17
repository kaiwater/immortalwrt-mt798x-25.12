# Geodata APK（OpenClash / PassWall）

固件默认不内置 GeoSite / GeoIP 数据库，避免“内置即过期”和占满 overlay。
需要开箱即用时，安装对应变体的 geodata apk 即可。

## 包与路径

| 包 | 适用 | 安装路径 | apk 大小 | 安装后占用 |
| --- | --- | --- | --- | --- |
| `openclash-geodata` | OpenClash | `/etc/openclash/{GeoIP.dat,GeoSite.dat,Country.mmdb}` | 4.1 MB | ~18.5 MB |
| `passwall-geodata` | PassWall | `/usr/share/v2ray/{geoip.dat,geosite.dat}` + `/usr/share/xray/` 软链 | 4.0 MB | ~18.3 MB |

数据来源（固定版本）：

- GeoIP：Loyalsoldier/v2ray-rules-dat `202611162204`
- GeoSite：v2fly/domain-list-community `20261009101206`（`dlc.dat`，比 Loyalsoldier 的 10MB 小很多）
- Country.mmdb：alecthw/mmdb_china_ip_list `4364177bc53a2c6f50c967d685f46de2406fc2be`（lite，264 KB，仅 OpenClash 包）

路径依据：

- OpenClash：`openclash_geo.sh` 固定写 `/etc/openclash/...`
- PassWall：`GEO_DIR=$(config_n_get @global_rules[0] v2ray_location_asset "/usr/share/v2ray/")`

## 安装

```sh
apk add --allow-untrusted /tmp/openclash-geodata-20261118-r1.apk
# 或
apk add --allow-untrusted /tmp/passwall-geodata-20261118-r1.apk
```

- 当前构建产出的 apk 未签名，必须带 `--allow-untrusted`
- `postinst` 会在服务存在时重启 OpenClash / PassWall
- 安装后不要保留 /tmp 里的 apk（会额外占 overlay）

## 构建

```sh
cd /mnt/qnap/projects/wrt/rax-builder

# 让包进入构建图（=m 只编译、不装进固件）
echo 'CONFIG_PACKAGE_openclash-geodata=m' >> .config
echo 'CONFIG_PACKAGE_passwall-geodata=m' >> .config
make defconfig

make package/openclash-geodata/compile
make package/passwall-geodata/compile
```

产物：

```
bin/packages/aarch64_cortex-a53/base/openclash-geodata-20261118-r1.apk
bin/packages/aarch64_cortex-a53/base/passwall-geodata-20261118-r1.apk
```

校验：

```sh
staging_dir/host/bin/apk verify --allow-untrusted <apk>
```

## 发布位置

- OpenClash：`redmi-ax6000-openclash-slim-20261118` release
- PassWall：`redmi-ax6000-passwall-slim-20261118` release

## 空间提示

- OpenClash slim：overlay ≈ 31 MiB，装 geodata 后约剩 12.5 MiB
- PassWall slim：overlay ≈ 36 MiB，装 geodata 后约剩 17.7 MiB
- 之后如果还要更新数据，建议先删旧包或直接覆盖安装新版本 apk
