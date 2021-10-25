import re

# Parsing external metrics generated by db_bench for further processes.
def parsing_external(input_file: str):
    
    f = open(input_file)
    lines = f.readlines()
    f.close()

    parser = {}
    data = {}
    size = {
        "KB" : 1/1024,
        "MB" : 1,
        "GB" : 1024
    }

    # Read
    for l in range(len(lines)):
        if (
            "** Compaction Stats [default] **" in lines[l]
            and data.get("compaction_stat", []) == []
        ):

            idx = lines.index("\n", l, len(lines))
            data["compaction_stat"] = lines[l:idx]

        if "** DB Stats **" in lines[l]:

            idx = lines.index("\n", l, len(lines))
            data["db_stat"] = lines[l:idx]


    # Parsing
    for line in data["db_stat"]:
        line = line.strip("\n")
        if "Uptime(secs)" in line:
            parser["TIME"] = float(line.split(' ')[1])
        if "Cumulative writes" in line:
            parser["RATE"] = float(line.split(' ')[-2])


    level_compaction = {}
    tmp = re.sub(" +", " ", data["compaction_stat"][1].strip("\n")).split(" ")

    sa_unit = 0
    for line in data["compaction_stat"]:
        level_data = {}
        line = re.sub(" +", " ", line.strip("\n").strip(" "))

        if len(line.split(" ")) == len(tmp) + 1:
            d = line.split(" ")
            if d[0] == 'Sum':
                sa_unit = d.pop(3)
            else:
                d.pop(3)

            for i in range(len(tmp)):
                level_data[tmp[i]] = d[i]
            level_compaction[level_data["Level"]] = level_data


    parser["WAF"] = float(level_compaction["Sum"]["W-Amp"])
    parser["SA"] = float(level_compaction["Sum"]["Size"]) * size.get(sa_unit, 0)

    return parser



# Parsing internal metrics generated by db_bench for further processes.
def parsing_internal(input_file: str):
    f = open(input_file)
    lines = f.readlines()
    f.close()

    parser = {}

    # Read
    data = []
    for l in range(len(lines)):

        if "STATISTICS" in lines[l]:
            data = lines[l + 1:]
            break

    for line in data:
        if len(line.split(" : ")) != 2:
            line = line.strip("\n").replace(" : ", ":").replace(" ", "|")
            key = line.split("|")[0]
            value = line.split("|")[1:]

            for v in value:
                tmp_key = key + "_" + v.split(":")[0]
                parser[tmp_key] = v.split(":")[1]

        else:
            key, value = line.strip("\n").split(" : ")
            parser[key] = value
    
    return parser
