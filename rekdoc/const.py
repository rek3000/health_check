##### DEFAULT PATHS #####
## INTERGRATED LIGHT OUT MANAGEMENT
FAULT = "/fma/@usr@local@bin@fmadm_faulty.out"
PRODUCT = "/ilom/@usr@local@bin@collect_properties.out"
SERIAL = "/ilom/@usr@local@bin@collect_properties.out"
TEMP = "/ilom/@usr@local@bin@collect_properties.out"
FIRMWARE = "/ilom/@usr@local@bin@collect_properties.out"
##
## ORACLE LINUX
IMAGE_LINUX = ""
PARTITION_LINUX = "/disks/df-kl.out"
RAID = ""
NETWORK = "/sysconfig/ifconfig-a.out"
CPU_ULTILIZATION = ""
CPU_LOAD_LINUX = ""
MEM_LINUX = ""
SWAP_SOL = ""
EXTRACT_LOCATION = "./temp/"
# HugePages = HugePages_Total * 2 /1024 = ~ 67.8% physical Memory
##
## ORACLE SOLARIS
IMAGE_SOL = "/etc/release"
PARTITION_SOL = "/disks/df-kl.out"
RAID_SOL = "/disks/zfs/zpool_status_-v.out"
NETWORK_SOL = "/netinfo/ipadm.out"
CPU_ULTILIZATION_SOL = "/sysconfig/vmstat_3_3.out"
CPU_LOAD_SOL = "/sysconfig/prstat-L.out"
# VCPU_SOL = "/sysconfig/ldm_list_-l.out"
VCPU_SOL = "/sysconfig/psrinfo-v.out"
MEM_SOL = "/disks/zfs/mdb/mdb-memstat.out"
SWAP_SOL = "/disks/swap-s.out"
##
##### END_PATHS #####

##### COLOR #####
SUCCESS = "green"
ERROR = "red"
SECTION = "cyan"
##### COLOR #####
