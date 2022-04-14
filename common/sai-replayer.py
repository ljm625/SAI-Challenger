import subprocess
import time

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
    recording_file = "sairedis.rec"
    sai = SaiNpu(exec_params)
    import pydevd_pycharm
    pydevd_pycharm.settrace('10.79.96.73', port=7999, stdoutToServer=True, stderrToServer=True)
    records = __parse_rec(recording_file)
    sai.r.flushall()
    subprocess.Popen("sudo systemctl restart syncd",shell=True)
    time.sleep(15)
    # sai.reset()
    sai.apply_rec_init(records)



