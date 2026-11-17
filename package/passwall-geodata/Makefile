include $(TOPDIR)/rules.mk

PKG_NAME:=passwall-geodata
PKG_VERSION:=20261118
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

GEOIP_VER:=202611162204
GEOSITE_VER:=20261009101206

GEOIP_FILE:=geoip.dat.$(GEOIP_VER)
GEOSITE_FILE:=dlc.dat.$(GEOSITE_VER)

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

define Package/passwall-geodata
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=IP Addresses and Names
  TITLE:=GeoSite/GeoIP data for PassWall
  PKGARCH:=all
endef

define Package/passwall-geodata/description
  Bundle geosite.dat and geoip.dat for PassWall (default /usr/share/v2ray path).
endef

define Build/Prepare
	$(call Build/Prepare/Default)
	$(call Download,geoip)
	$(call Download,geosite)
endef

define Build/Compile
endef

define Package/passwall-geodata/install
	$(INSTALL_DIR) $(1)/usr/share/v2ray $(1)/usr/share/xray
	$(INSTALL_DATA) $(DL_DIR)/$(GEOIP_FILE) $(1)/usr/share/v2ray/geoip.dat
	$(INSTALL_DATA) $(DL_DIR)/$(GEOSITE_FILE) $(1)/usr/share/v2ray/geosite.dat
	$(LN) ../v2ray/geoip.dat $(1)/usr/share/xray/geoip.dat
	$(LN) ../v2ray/geosite.dat $(1)/usr/share/xray/geosite.dat
endef

define Package/passwall-geodata/postinst
#!/bin/sh
[ -x /etc/init.d/passwall ] && /etc/init.d/passwall restart >/dev/null 2>&1
exit 0
endef

$(eval $(call BuildPackage,passwall-geodata))
