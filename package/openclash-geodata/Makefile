include $(TOPDIR)/rules.mk

PKG_NAME:=openclash-geodata
PKG_VERSION:=20261118
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

GEOIP_VER:=202611162204
GEOSITE_VER:=20261009101206
MMDB_COMMIT:=4364177bc53a2c6f50c967d685f46de2406fc2be

GEOIP_FILE:=geoip.dat.$(GEOIP_VER)
GEOSITE_FILE:=dlc.dat.$(GEOSITE_VER)
MMDB_FILE:=Country.mmdb.$(MMDB_COMMIT)

define Download/geoip
  URL:=https://github.com/Loyalsoldier/v2ray-rules-dat/releases/download/$(GEOIP_VER)/
  URL_FILE:=geoip.dat
  FILE:=$(GEOIP_FILE)
  HASH:=304ac8a1cbcc8166e4f5a4f32955e4d0fb77a1bd713583e371b30ee27f3659d8
endef
$(eval $(call Download,geoip))

define Download/geosite
  URL:=https://github.com/v2fly/domain-list-community/releases/download/$(GEOSITE_VER)/
  URL_FILE:=dlc.dat
  FILE:=$(GEOSITE_FILE)
  HASH:=51fcbfa2bf420e678a4c1f764ad8b2e668f99ac95fae147bb7aea7f75f96a641
endef
$(eval $(call Download,geosite))

define Download/mmdb
  URL:=https://raw.githubusercontent.com/alecthw/mmdb_china_ip_list/$(MMDB_COMMIT)/lite/
  URL_FILE:=Country.mmdb
  FILE:=$(MMDB_FILE)
  HASH:=11f4ae676cdbc8e8567570c0cf4632d85b2b06537b69a953be47c76ebf82766f
endef
$(eval $(call Download,mmdb))

define Package/openclash-geodata
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=IP Addresses and Names
  TITLE:=GeoSite/GeoIP/Country data for OpenClash
  PKGARCH:=all
endef

define Package/openclash-geodata/description
  Bundle GeoSite.dat, GeoIP.dat and Country.mmdb for OpenClash.
endef

define Build/Prepare
	$(call Build/Prepare/Default)
	$(call Download,geoip)
	$(call Download,geosite)
	$(call Download,mmdb)
endef

define Build/Compile
endef

define Package/openclash-geodata/install
	$(INSTALL_DIR) $(1)/etc/openclash
	$(INSTALL_DATA) $(DL_DIR)/$(GEOIP_FILE) $(1)/etc/openclash/GeoIP.dat
	$(INSTALL_DATA) $(DL_DIR)/$(GEOSITE_FILE) $(1)/etc/openclash/GeoSite.dat
	$(INSTALL_DATA) $(DL_DIR)/$(MMDB_FILE) $(1)/etc/openclash/Country.mmdb
endef

define Package/openclash-geodata/postinst
#!/bin/sh
[ -x /etc/init.d/openclash ] && /etc/init.d/openclash restart >/dev/null 2>&1
exit 0
endef

$(eval $(call BuildPackage,openclash-geodata))
