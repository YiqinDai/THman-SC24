import random
import time

all_index = 0
workflow_count = 40

class task:
    def __init__(self, id, time, node_num, proc_num, read_files_size, write_files_size, name):
        self.id = id
        self.time = time
        self.node_num = node_num
        self.proc_num = proc_num
        self.read_files_size = read_files_size
        self.write_files_size = write_files_size
        self.read_files_name = []
        self.write_files_name = []
        self.name = name


batch_flag = -1
task_list = []
# low I/O density
task_list.append(task(0, 27, 1, 16, 0.13, 0.15, "lowio1"))
task_list.append(task(1, 82, 2, 32, 0.7, 0.6, "lowio2"))
task_list.append(task(2, 125, 4, 64, 1.9, 1.9, "lowio3"))

# medium I/O density
task_list.append(task(3, 25, 1, 16, 18, 18, "mediumio1"))
task_list.append(task(4, 82, 2, 32, 72, 72, "mediumio2"))
task_list.append(task(5, 156, 4, 64, 187, 187, "mediumio3"))
# high I/O density
task_list.append(task(6, 15, 1, 16, 66, 60, "highio1"))
task_list.append(task(7, 70, 2, 32, 152, 144, "highio2"))
task_list.append(task(8, 97, 4, 64, 380, 350, "highio3"))
# batch job
task_list.append(task(9, 10, 1, 64, 0.1, 0.1, "sleep 10"))
task_list.append(task(10, 20, 1, 64, 0.1, 0.1, "sleep 20"))
task_list.append(task(11, 40, 1, 64, 0.1, 0.1, "sleep 40"))
task_list.append(task(12, 10, 2, 64, 0.1, 0.1, "sleep 10"))
task_list.append(task(13, 20, 2, 64, 0.1, 0.1, "sleep 20"))
task_list.append(task(14, 40, 2, 64, 0.1, 0.1, "sleep 40"))
task_list.append(task(15, 10, 4, 64, 0.1, 0.1, "sleep 10"))
task_list.append(task(16, 20, 4, 64, 0.1, 0.1, "sleep 20"))
task_list.append(task(17, 40, 4, 64, 0.1, 0.1, "sleep 40"))

for file_index in range(workflow_count):
    bf = random.randint(0, batch_flag + 1)
    #bf = 0
    if bf == 0:  # workflow job
        N = random.randint(5, 30)
        #N = 100
    else:  # batch job
        N = 1
    DAG = [[0 for j in range(0, N + 2)] for i in range(0, N + 2)]
    for i in range(1, N + 1):
        for j in range(i + 1, N + 1):
            # if random.randint(0, int(N / 4) + 3) == 0:
            if random.randint(0, int(N / 2)) == 0:
                DAG[i][j] = 1
            else:
                DAG[i][j] = 0
    write_file_index = 1 + all_index
    test_file_index = 1 + all_index
    # task_file_index = [0]
    I = []
    O = []
    with open("Generated_Tasks/" + str(file_index) + ".txt", 'w') as f:
        # f.write("BBUsage 1\n")
        # f.write("BBSize 1500g\n")
        f.write("Partition ft3k\n")
        f.write("FSReadBandwidth 16\n")
        f.write("FSWriteBandwidth 14\n")
        # f.write("BBReadBandwidth 8\n")
        # f.write("BBWriteBandwidth 7.5\n")
        f.write("Nodes Nodelist=cn[0-63]\n")
        for i in range(9):
            f.write("File testoriginfile" + str(i) + " " + str(task_list[i].read_files_size) + "g\n")
        f.write("File testfile0 0.01g\n")
        for i in range(1, N + 1):
            if bf == 0:  # workflow job
                #j = random.randint(0, 8)
                j = random.randint(0, 17)
                if j >= 9:
                    j = random.randint(0, 3)
            else:  # batch job
                j = random.randint(9, len(task_list) - 1)
            f.write("Task -N " + str(task_list[j].node_num) + " -n " + str(task_list[j].proc_num) + " -wt " + str(
                task_list[j].time) + ' ')
            f.write(task_list[j].name + " ")
            print(bf, j, task_list[j].name)

            I.append(task_list[j].read_files_size)
            O.append(task_list[j].write_files_size)
            if bf == 0:  # workflow job
                f.write("-wr testoriginfile" + str(j) + ' ')
                for k in range(0, i):
                    if DAG[k][i] == 1:
                        f.write("-wr testfile" + str(k + all_index) + ' ')  
                f.write(" -ww testwritefile" + str(write_file_index) + ' ' + str(task_list[j].write_files_size) + 'g')
                f.write(" -ww testfile" + str(test_file_index) + ' 0.1g')  

            elif bf > 0 and j <= 8:
                f.write("-wr testoriginfile" + str(j) + ' ')
                f.write(" -ww testwritefile" + str(write_file_index) + ' ' + str(task_list[j].write_files_size) + 'g')

            else:
                print()
                pass
            test_file_index += 1
            write_file_index += 1
            # task_file_index.append(test_file_index)

            f.write('\n')
        all_index += N
    print(all_index)
    # for i in range(0, N + 1):
    #     for j in range(0, N + 1):
    #         if DAG[i][j] == 1:
    #             print(i, "=>", j)
    # print(I)
    print(sum(O))

