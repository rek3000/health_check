# ------------------------------------
# INTERGRATED LIGHT OUT MANAGEMENT
# ------------------------------------
FAULT = "/fma/@usr@local@bin@fmadm_faulty.out"
TEMP = "/ilom/@usr@local@bin@collect_properties.out"
FIRMWARE = "/ilom/@usr@local@bin@collect_properties.out"
# PRODUCT = "/ilom/@usr@local@bin@collect_properties.out"
# SERIAL = "/ilom/@usr@local@bin@collect_properties.out"
# ------------------------------------
# END INTERGRATED LIGHT OUT MANAGEMENT
# ------------------------------------


# -----------------------
# SYSTEM STATUS CHECK
# -----------------------
# ORACLE LINUX (SOSREPORT)
# TODO
IMAGE_LINUX = ""
PARTITION_LINUX = "/disks/df-kl.out"
# RAID is NOT require for VMs or Physical Server Boot from SAN
RAID = ""
NETWORK = "/sysconfig/ifconfig-a.out"

# HugePages = HugePages_Total * 2 /1024 = ~ 67.8% physical Memory

# ORACLE SOLARIS (EXPLORER)
IMAGE_SOL = "/patch+pkg/pkg_info-l.out"
PARTITION_SOL = "/disks/df-kl.out"
# RAID is NOT require for VMs or Physical Server Boot from SAN
RAID_SOL = "/disks/zfs/zpool_status_-v.out"
NETWORK_SOL = "/netinfo/ipadm.out"

# EXADATA/SUPPER CLUSTER (sundiag)
# TODO
# -----------------------
# END SYSTEM STATUS CHECK
# -----------------------

# ---------------------
# PERFORMANCE CHECK
# ---------------------
# STANDALONE SERVER
# TODO (replace below with OSWatcher path)
CPU_ULTILIZATION = ""
CPU_LOAD_LINUX = ""
MEM_LINUX = ""
SWAP_SOL = ""
EXTRACT_LOCATION = "./temp/"
# SOLARIS
# CPU_ULTILIZATION_SOL = "/sysconfig/vmstat_3_3.out"
CPU_ULTILIZATION_SOL = "/oswtop/"
CPU_LOAD_SOL = "/sysconfig/prstat-L.out"
VCPU_SOL = "/sysconfig/psrinfo-v.out"
MEM_SOL = "/oswtop/"
MEM_SOL2 = "/disks/zfs/mdb/mdb-memstat.out"
IO_SOL = "/oswiostat/"
SWAP_SOL = "/disks/swap-s.out"

# EXADATA/SUPPER CLUSTER (Exawatcher)
# TODO
# ---------------------
# END PERFORMANCE CHECK
# ---------------------

# ---------
# COLOR
# ---------
SUCCESS = "green"
ERROR = "red"
SECTION = "cyan"
# ---------
# END COLOR
# ---------
