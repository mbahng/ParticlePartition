index = open("python/data/wdata_index.bin", "wb+")
wdata = open("python/data/wedgeData_v3_128.txt", "r")

line = " "
# ith dword:
# < 4 bytes == .seek posn in file
index.write(b'\x00\x00\x00\x00')
while line:
    line = wdata.readline()
    index.write(wdata.tell().to_bytes(4, "big"))

wdata.close()
index.close()