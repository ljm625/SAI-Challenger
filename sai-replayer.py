from common.sai_npu import SaiNpu

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


def apply_rec(sai,records):
    oids = []
    inited = False
    for cnt, rec in records.items():
        print("#{}: {}".format(cnt, rec))
        if rec[0] == 'c':
            if "SAI_OBJECT_TYPE_SWITCH" in rec[1] and inited:
                print("Object \"{}\" already exists!".format(rec[1]))
                continue
            elif "SAI_OBJECT_TYPE_SWITCH" in rec[1]:
                print("Starting Switch")
                inited = True

            attrs = []
            if len(rec) > 2:
                for attr in rec[2:]:
                    attrs += attr.split('=')

            # Update OIDs in the attributes
            for idx in range(1, len(attrs), 2):
                if "oid:" in attrs[idx]:
                    attrs[idx] = sai.rec2vid[attrs[idx]]

            sai.create(sai.__update_key(rec[0], rec[1]), attrs)

        elif rec[0] == 's':
            data = rec[2].split('=')
            if "oid:" in data[1]:
                data[1] = sai.rec2vid[data[1]]

            sai.set(sai.__update_key(rec[0], rec[1]), data)
        elif rec[0] == 'r':
            sai.remove(sai.__update_key(rec[0], rec[1]))
        elif rec[0] == 'g':
            attrs = []
            if len(rec) > 2:
                for attr in rec[2:]:
                    attrs += attr.split('=')

            data = sai.get(sai.__update_key(rec[0], rec[1]), attrs)

            jdata = data.to_json()
            for idx in range(1, len(jdata), 2):
                if ":oid:" in jdata[idx]:
                    oids += data.oids(idx)
                elif "oid:" in jdata[idx]:
                    oids.append(data.oid(idx))
        elif rec[0] == 'G':
            attrs = []
            for attr in rec[2:]:
                attrs += attr.split('=')

            G_oids = []

            for idx in range(1, len(attrs), 2):
                G_output = attrs[idx]

                if ":oid:" in G_output:
                    start_idx = G_output.find(":") + 1
                    G_oids += G_output[start_idx:].split(",")
                elif "oid:" in G_output:
                    G_oids.append(G_output)
            assert len(oids) == len(G_oids)

            for idx, oid in enumerate(G_oids):
                sai.rec2vid[oid] = oids[idx]
            oids = []
        else:
            print("Ignored line {}: {}".format(cnt, rec))

    print("Current SAI objects: {}".format(sai.rec2vid))


if __name__ == '__main__':
    recording_file = "sairedis.rec"
    sai = SaiNpu(exec_params)

