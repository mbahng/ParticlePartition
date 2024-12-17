from src.readers.reader import * 
from src.coverers.data_structs import * 
from src.coverers.line import * 
from src.coverers.wedgecover import *
from src.testers.test import *
from src.debug import * 
import matplotlib.pyplot as plt 
import numpy as np
from multiprocessing import Process, Manager
from tqdm import tqdm
import glob, os 

filepath = "python/data/wedgeData_v3_128.txt"
filedata = readFile(filepath, stop=128, performance=False)
env, points = filedata[0] 
env = Environment(50)
ds = DataSet(env)
ds.importData(points)
ds.addBoundaryPoint()
cov = wedgeCover(env, ds, output_dir="temp_image_dir_david")

NULL = open("/dev/null", "w")
# STOUT = sys.stdout


# acc, used, tested = wedge_test(
#     lining = 'makePatches_ShadowQuilt_fromEdges', 
#     apexZ0=0, top_layer_cutoff=50, wedges=[0,1],
#     z0_spacing=0.05, leftRightAlign=True,
#     show_acceptance_of_cover=False, accept_cutoff=15,
#     movie = True, movieFigSizeScale=3,
#     output_dir="temp_image_dir_david",
#     dbg_output=False, early_ret=True,
#     unary=True
# )
# exit()

def wedge_proc_bin(wedge_ix, null_fd, min_accs, useds, testeds):
    import sys
    sys.stdout = null_fd
    acc, used, tested = wedge_test(
        lining = 'makePatches_ShadowQuilt_fromEdges_BinarySearch', 
        apexZ0=0, top_layer_cutoff=50, wedges=[wedge_ix,wedge_ix+1],
        z0_spacing=0.05, leftRightAlign=True,
        show_acceptance_of_cover=False, accept_cutoff=15,
        movie = False, movieFigSizeScale=3,
        output_dir="temp_image_dir_david",
        dbg_output=False, early_ret=True,
        unary=True
    )
    min_accs.append(np.min(acc))
    useds.append(float(used))
    testeds.append(float(tested))

def wedge_proc_old(wedge_ix, null_fd, min_accs, useds, testeds):
    import sys
    sys.stdout = null_fd
    acc, used, tested = wedge_test(
        lining = 'makePatches_ShadowQuilt_fromEdges', 
        apexZ0=0, top_layer_cutoff=50, wedges=[wedge_ix,wedge_ix+1],
        z0_spacing=0.05, leftRightAlign=True,
        show_acceptance_of_cover=False, accept_cutoff=15,
        movie = False, movieFigSizeScale=3,
        output_dir="temp_image_dir_david",
        dbg_output=False, early_ret=True,
        unary=True
    )
    min_accs.append(np.min(acc))
    useds.append(float(used))
    testeds.append(float(tested))

BATCH_SIZE = 100
BATCH_COUNT = 5
with Manager() as manager:
    bin_min_accs = []
    binused =      []
    bintested =    []
    old_min_accs = []
    oldused =      []
    oldtested =    []
    for batch in range(BATCH_COUNT):
        procs = []
        batch_bin_min_accs = manager.list()
        batch_binused = manager.list()
        batch_bintested = manager.list()
        batch_old_min_accs = manager.list()
        batch_oldused = manager.list()
        batch_oldtested = manager.list()
        for ix in tqdm(range(BATCH_SIZE), f"Creation (batch {batch + 1}/{BATCH_COUNT})"):
            i = ix + batch * BATCH_SIZE
            procs.append(Process(target=wedge_proc_bin, args=(i, NULL, batch_bin_min_accs, batch_binused, batch_bintested)))
            procs.append(Process(target=wedge_proc_old, args=(i, NULL, batch_old_min_accs, batch_oldused, batch_oldtested)))

        for p in procs:
            p.start()

        for p in tqdm(procs, f"Join (batch {batch + 1}/{BATCH_COUNT})"):
            p.join()
        
        bin_min_accs += batch_bin_min_accs
        binused += batch_binused
        bintested += batch_bintested
        old_min_accs += batch_old_min_accs
        oldused += batch_oldused
        oldtested += batch_oldtested

    plt.plot(range(len(bin_min_accs)), bin_min_accs, "ro-", label="Binary min(acceptance)")
    plt.plot(range(len(old_min_accs)), old_min_accs, label="Old min(acceptance)")
    plt.xlabel("Wedge #")
    plt.ylabel("Acceptance (%)")
    plt.ylim([0, 102])
    plt.legend()
    plt.show()
# cleanup:
for f in glob.glob("python/temp_txt_dir/*"):
    os.remove(f)
# exit()

# for i in tqdm(range(500)):
#     sys.stdout = NULL
#     acc, used, tested = wedge_test(
#         lining = 'makePatches_ShadowQuilt_fromEdges_BinarySearch', 
#         apexZ0=0, top_layer_cutoff=50, wedges=[i,i+1],
#         z0_spacing=0.05, leftRightAlign=True,
#         show_acceptance_of_cover=False, accept_cutoff=15,
#         movie = False, movieFigSizeScale=3,
#         output_dir="temp_image_dir_david",
#         dbg_output=False, early_ret=True
#     )
#     bin_min_accs.append(np.min(acc))
#     bin_max_accs.append(np.max(acc))
#     binused.append(float(used))
#     bintested.append(float(tested))

#     acc, used, tested = wedge_test(
#         lining = 'makePatches_ShadowQuilt_fromEdges', 
#         apexZ0=0, top_layer_cutoff=50, wedges=[i,i+1],
#         z0_spacing=0.05, leftRightAlign=True,
#         show_acceptance_of_cover=False, accept_cutoff=15,
#         movie = False, movieFigSizeScale=3,
#         output_dir="temp_image_dir_david",
#         dbg_output=False, early_ret=True
#     )
#     old_min_accs.append(np.min(acc))
#     old_max_accs.append(np.max(acc))
#     oldused.append(float(used))
#     oldtested.append(float(tested))
#     sys.stdout = STOUT


# plt.plot(range(len(bin_min_accs)), bin_min_accs, "ro-", label="Binary min(acceptance)")
# plt.plot(range(len(old_min_accs)), old_min_accs, label="Old min(acceptance)")
# plt.xlabel("Wedge #")
# plt.ylabel("Acceptance (%)")
# plt.ylim([0, 102])
# plt.legend()
# plt.show()

fig, axs = plt.subplots(2,2, figsize=(24,13))
# max used freq:
used_bins = np.linspace(0, 40, 40)
test_bins = np.linspace(0, 120, 60)
muse_fq = np.max([np.max(np.histogram(binused, used_bins)[0]), np.max(np.histogram(oldused, used_bins)[0])]) + 5
mtest_fq = np.max([np.max(np.histogram(bintested, test_bins)[0]), np.max(np.histogram(oldtested, test_bins)[0])]) + 5
axs[0,0].hist(binused, bins=used_bins)
axs[0,0].plot([],[])
axs[0,0].set_title("Binary Patches Used")
axs[0,0].legend([
    r"$\mu = $" + str(np.average(binused)),
    r"$\sigma = $" + str(np.std(binused)),
])
axs[0,0].set_ylim([0,muse_fq])

axs[1,0].hist(bintested, bins=test_bins)
axs[1,0].plot([],[])
axs[1,0].set_title("Binary Patches Tested")
axs[1,0].set_ylim([0,mtest_fq])
axs[1,0].legend([
    r"$\mu = $" + str(np.average(bintested)),
    r"$\sigma = $" + str(np.std(bintested)),
])

axs[0,1].hist(oldused, bins=used_bins)
axs[0,1].plot([],[])
axs[0,1].set_title("Old Patches Used")
axs[0,1].set_ylim([0,muse_fq])
axs[0,1].legend([
    r"$\mu = $" + str(np.average(oldused)),
    r"$\sigma = $" + str(np.std(oldused)),
])

axs[1,1].hist(oldtested, bins=test_bins)
axs[1,1].plot([],[])
axs[1,1].set_title("Old Patches Tested")
axs[1,1].set_ylim([0,mtest_fq])
axs[1,1].legend([
    r"$\mu = $" + str(np.average(oldtested)),
    r"$\sigma = $" + str(np.std(oldtested)),
])
# HISTOGRAMS + subplots !! 
# plt.plot(range(len(binused)),   binused,   label="Binary used")
# plt.plot(range(len(bintested)), bintested, label="Binary tested")
# plt.plot(range(len(oldused)),   oldused,   label="Old used")
# plt.plot(range(len(oldtested)), oldtested, label="Old tested")
# plt.xlabel("Patches")
# plt.ylabel("Frequency")
# plt.legend()
plt.show()

# wedge_test(
#     lining = 'makePatches_ShadowQuilt_fromEdges', 
#     apexZ0=0, top_layer_cutoff=50, wedges=wedges,
#     z0_spacing=0.05, leftRightAlign=True,
#     show_acceptance_of_cover=False, accept_cutoff=15,
#     movie = False, movieFigSizeScale=3
# )