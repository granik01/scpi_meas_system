def outputEnable(channel=1, polarity=1, load="HZ"):
        command = b''
        if channel == 1:
            command += b'C1'
        elif channel == 2:
            command += b'C2'

        command += b':OUTP ON,LOAD,'
        if load == "HZ":
            command += b'HZ,'
        else:
            command += bytes(str(load), encoding="ASCII")
            command += b','

        if polarity:
            command += b'PLTR,NOR'
        else:
            command += b'PLTR,INVT'
        return command



command = outputEnable()
print(command)