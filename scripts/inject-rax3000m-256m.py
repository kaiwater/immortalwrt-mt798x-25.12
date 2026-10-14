#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""为 chasey-dev/immortalwrt-mt798x-rebase 的 25.12 分支增加 256 MiB NAND profile。

用法（在 make defconfig 之前，在全新克隆的源码中运行）：
    python3 ../scripts/inject-rax3000m-256m.py .

然后启用：
    CONFIG_TARGET_DEVICE_mediatek_filogic_DEVICE_cmcc_rax3000m-256m=y
    CONFIG_PACKAGE_u-boot-mt7981_cmcc_rax3000m-nand-256m=y

注册内容：Linux NAND overlay、独立 U-Boot defconfig / DTS / 默认环境、
U-Boot package variant、NAND 专用 device profile。原 128M / RAX3000Me 不修改。
输出名称包含 cmcc_rax3000m-256m：nand-preloader.bin、nand-bl31-uboot.fip、
initramfs-recovery.itb（需启用 initramfs）、squashfs-sysupgrade.itb。

硬件前提与边界：
* 采用原生 SPI-NAND + UBI；UBI 范围 [0x580000, 0x10000000)。
  不为旧 BMT/NMBM 预留尾部空间，不处理旧映射表 / 数据的迁移。
* 延用 upstream spim-nand-ddr4 BL2，未添加 NAND 芯片 ID、ECC 或 DDR 参数。
  必须分别验证 BL2、U-Boot、Linux 对实装 NAND 的支持及 1 GiB RAM 的识别。
* 保留 cmcc,rax3000m 运行时板型，复用网络、升级等板级脚本；因此固件元数据
  不会自动阻止 128M / 256M 互刷。新 profile 名称不是容量检测机制。
* 新 FIP 默认 bootconf 指向新 overlay；闪存中已保存的旧 U-Boot 环境可能覆盖它。
  部署时需检查 printenv bootconf，不能仅依赖编译进 FIP 的默认环境。
* 不修改 Linux / U-Boot 的 RAM 静态字段，不把 IMAGE_SIZE 当作分区大小。

该脚本仅修改构建源码，不执行刷机。已针对 2026-10-14 读取的上游文件结构验证；
上游相关结构变化、文件冲突或未预期布局会报错退出。重复运行可校验并复用同一结果。
"""

import argparse
import re
import sys
from pathlib import Path


DEVICE = "cmcc_rax3000m-256m"
UBOOT = "mt7981_cmcc_rax3000m-nand-256m"
OVERLAY = "mt7981b-cmcc-rax3000m-nand-256m"
BEGIN = "# BEGIN local RAX3000M 256MiB NAND v1\n"
END = "# END local RAX3000M 256MiB NAND v1\n"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def replace_one(text, old, new, label):
    require(text.count(old) == 1, f"{label}: expected exactly one {old!r}")
    return text.replace(old, new, 1)


def get_block(text, name):
    matches = re.findall(
        rf"^define {re.escape(name)}\n.*?^endef\n", text, re.M | re.S
    )
    require(len(matches) == 1, f"expected one exact Makefile block: {name}")
    return matches[0]


def remove_owned_block(text, label):
    if BEGIN not in text and END not in text:
        return text
    require(text.count(BEGIN) == text.count(END) == 1,
            f"{label}: invalid local injection markers")
    start = text.index(BEGIN)
    finish = text.index(END) + len(END)
    require(finish > start, f"{label}: reversed markers")
    return text[:start] + text[finish:]


def extract_added_file(patch, path):
    """Only accept a single, complete new-file hunk from the upstream patch."""
    header = f"--- /dev/null\n+++ b/{path}\n"
    require(patch.count(header) == 1, f"upstream patch: missing/duplicate {path}")
    tail = patch.split(header, 1)[1]
    lines = tail.splitlines(keepends=True)
    match = re.fullmatch(r"@@ -0,0 \+1,(\d+) @@\n", lines[0])
    require(match is not None, f"upstream patch: unexpected hunk for {path}")
    count = int(match.group(1))
    body = lines[1:count + 1]
    require(len(body) == count and all(line.startswith("+") for line in body),
            f"upstream patch: incomplete new file {path}")
    require(len(lines) == count + 1 or lines[count + 1].startswith("--- /dev/null"),
            f"upstream patch: extra hunks for {path}")
    return "".join(line[1:] for line in body)


def expand_ubi(text, label):
    require('label = "ubi";' in text, f"{label}: missing ubi partition")
    require(not re.search(r"mediatek,(?:bmt-v2|nmbm|bbt)", text),
            f"{label}: BMT/NMBM layout needs separate review")
    return replace_one(text, "reg = <0x580000 0x7200000>;",
                       "reg = <0x580000 0xfa80000>;", label)


def new_file_patch(files):
    chunks = []
    for path, body in files.items():
        require(body.endswith("\n"), f"missing final newline: {path}")
        lines = body.splitlines(keepends=True)
        chunks.append(f"--- /dev/null\n+++ b/{path}\n@@ -0,0 +1,{len(lines)} @@\n")
        chunks.extend("+" + line for line in lines)
    return "".join(chunks)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="OpenWrt source directory")
    args = parser.parse_args()
    root = args.source.resolve()
    image_path = root / "target/linux/mediatek/image/filogic.mk"
    uboot_path = root / "package/boot/uboot-mediatek/Makefile"
    patch_dir = root / "package/boot/uboot-mediatek/patches"
    dts_dir = root / "target/linux/mediatek/dts"
    image = image_path.read_text()
    uboot = uboot_path.read_text()
    patch = (patch_dir / "437-add-cmcc_rax3000m.patch").read_text()
    overlay = (dts_dir / "mt7981b-cmcc-rax3000m-nand.dtso").read_text()
    require((dts_dir / "mt7981b-cmcc-rax3000m.dts").is_file(), "missing base DTS")

    clean_image = remove_owned_block(image, "filogic.mk")
    clean_uboot = remove_owned_block(uboot, "U-Boot Makefile")
    require(DEVICE not in clean_image, "device already exists outside this script's block")
    require(UBOOT not in clean_uboot, "U-Boot target already exists outside this script's block")
    base = get_block(clean_image, "Device/cmcc_rax3000m")
    common = get_block(clean_image, "Device/cmcc_rax3000m_common")
    require("DEVICE_DTS := mt7981b-cmcc-rax3000m\n" in base, "base DTS changed")
    require("$(call Device/cmcc_rax3000m_common)" in base, "base inheritance changed")
    require("ARTIFACT/nand-preloader.bin := mt7981-bl2 spim-nand-ddr4" in base,
            "BL2 recipe changed")
    require("ARTIFACT/nand-bl31-uboot.fip := mt7981-bl31-uboot cmcc_rax3000m-nand" in base,
            "FIP recipe changed")
    require("IMAGES := sysupgrade.itb" in common and "DEVICE_DTS_OVERLAY :=" in common,
            "FIT/overlay recipe changed")

    profile = f"""define Device/{DEVICE}
  $(call Device/cmcc_rax3000m)
  DEVICE_MODEL := RAX3000M
  DEVICE_VARIANT := 256MiB NAND mod
  DEVICE_DTS_OVERLAY := {OVERLAY}
  SUPPORTED_DEVICES := cmcc,rax3000m
  ARTIFACTS := nand-preloader.bin nand-bl31-uboot.fip
  ARTIFACT/nand-bl31-uboot.fip := mt7981-bl31-uboot cmcc_rax3000m-nand-256m
endef
TARGET_DEVICES += {DEVICE}
"""
    image_out = replace_one(clean_image, "TARGET_DEVICES += cmcc_rax3000m\n",
                            "TARGET_DEVICES += cmcc_rax3000m\n" + BEGIN + profile + END,
                            "device registration")

    old_variant = get_block(clean_uboot, "U-Boot/mt7981_cmcc_rax3000m-nand")
    variant = old_variant.replace("mt7981_cmcc_rax3000m-nand", UBOOT)
    variant = replace_one(variant, "BUILD_DEVICES:=cmcc_rax3000m\n",
                          f"BUILD_DEVICES:={DEVICE}\n", "U-Boot BUILD_DEVICES")
    variant = replace_one(variant, "NAME:=CMCC RAX3000M\n",
                          "NAME:=CMCC RAX3000M (256MiB NAND)\n", "U-Boot name")
    # Put the append after the original complete UBOOT_TARGETS assignment.
    target_list = re.search(r"^UBOOT_TARGETS :=[^\n]*\\\n(?:[^\n]*\\\n)*[^\n]*\n",
                            clean_uboot, re.M)
    require(target_list is not None, "missing UBOOT_TARGETS assignment")
    require("mt7981_cmcc_rax3000m-nand" in target_list.group(0),
            "upstream NAND U-Boot registration missing")
    pos = target_list.end()
    uboot_out = (clean_uboot[:pos] + BEGIN + variant + f"UBOOT_TARGETS += {UBOOT}\n"
                 + END + clean_uboot[pos:])

    config = extract_added_file(patch, "configs/mt7981_cmcc_rax3000m-nand_defconfig")
    require(config.count("rax3000m-nand") == 3, "U-Boot defconfig references changed")
    config = config.replace("rax3000m-nand", "rax3000m-nand-256m")
    boot_dts = expand_ubi(extract_added_file(
        patch, "arch/arm/dts/mt7981-cmcc-rax3000m-nand.dts"), "U-Boot DTS")
    boot_dts = boot_dts.replace("partition@160000 {", "partition@180000 {")
    env = extract_added_file(patch, "defenvs/cmcc_rax3000m-nand_env")
    env = replace_one(env, "bootconf=config-1#mt7981b-cmcc-rax3000m-nand\n",
                      f"bootconf=config-1#{OVERLAY}\n", "FIT bootconf")
    require(env.count("immortalwrt-mediatek-filogic-cmcc_rax3000m-") == 4,
            "U-Boot TFTP file names changed")
    env = env.replace("immortalwrt-mediatek-filogic-cmcc_rax3000m-",
                      f"immortalwrt-mediatek-filogic-{DEVICE}-")
    boot_patch = new_file_patch({
        f"configs/{UBOOT}_defconfig": config,
        "arch/arm/dts/mt7981-cmcc-rax3000m-nand-256m.dts": boot_dts,
        "defenvs/cmcc_rax3000m-nand-256m_env": env,
    })
    generated = {
        dts_dir / f"{OVERLAY}.dtso": expand_ubi(overlay, "Linux overlay"),
        patch_dir / "437-cmcc_rax3000m-nand-256m.patch": boot_patch,
    }
    # Preflight every output before writing anything; reject conflicting local edits.
    for path, content in generated.items():
        require(not path.exists() or path.read_text() == content,
                f"existing generated file differs: {path}")
    require(BEGIN not in image or image == image_out, "existing device block differs")
    require(BEGIN not in uboot or uboot == uboot_out, "existing U-Boot block differs")
    outputs = {**generated, image_path: image_out, uboot_path: uboot_out}
    for path, content in outputs.items():
        if path.exists() and path.read_text() == content:
            print(f"unchanged: {path.relative_to(root)}")
        else:
            path.write_text(content)
            print(f"written: {path.relative_to(root)}")
    print(f"Registered {DEVICE}; run make defconfig and check the device/U-Boot selections.")
    print("Source injection only: NAND driver support and 1GiB RAM still require hardware validation.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f"ERROR: {exc}")
