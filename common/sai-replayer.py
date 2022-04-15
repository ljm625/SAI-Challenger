import subprocess
import time
import argparse
from sai_npu import SaiNpu

exec_params = {
    "server": "localhost",
    "traffic": False,
    "saivs": False,
    "loglevel": "NOTICE",
    "sku": None
}


def __parse_rec(fname):
    cnt = 0
    rec = {}
    fp = open(fname, 'r')
    for line in fp:
        cnt += 1
        rec[cnt] = line.strip().split("|")[1:]
    return rec



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--rec-file", type=str, help="Path of sairedis.rec", required=True)
    parser.add_argument("-c", "--continue-with-swss", help="skip restart syncd, useful when using with swss", action="store_true")
    parser.add_argument("-s", "--sync-mode", help="Enable gSync", action="store_true")
    args = parser.parse_args()
    import pydevd_pycharm
    pydevd_pycharm.settrace('10.79.96.73', port=7999, stdoutToServer=True, stderrToServer=True)
    recording_file = args.rec_file
    sai = SaiNpu(exec_params)
    records = __parse_rec(recording_file)
    full_record = False
    if not args.continue_with_swss:
        print("Starting flush ASICDB")
        sai.r.flushdb()
        subprocess.Popen("sudo systemctl restart syncd",shell=True)
        time.sleep(15)
        full_record = True
    if args.sync_mode:
        for i in range(0,len(records)):
            if "SAI_OBJECT_TYPE_SWITCH" in records[i][1]:
                if "SAI_REDIS_SWITCH_ATTR_SYNC_MODE" in records[i]:
                    records[i][records[i].index("SAI_REDIS_SWITCH_ATTR_SYNC_MODE")+1] = "true"
                else:
                    records[i].append("SAI_REDIS_SWITCH_ATTR_SYNC_MODE")
                    records[i].append("true")
                break
    sai.apply_rec_init(records,full_record)



