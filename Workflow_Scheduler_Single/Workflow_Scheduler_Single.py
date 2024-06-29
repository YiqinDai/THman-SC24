# coding=utf-8
from ClusterShell.NodeSet import NodeSet
import os
import time


class workflow:
    def __init__(self, index):
        self.index = index
        self.arrive_time = time.time()
        self.start_time = ()
        self.running_time = 0
        self.end_time = 0
        self.tasks = []
        self.uncompleted_tasks = []
        self.uncompleted_bl = []
        self.completed_tasks = []
        self.max_bl = 0
        self.start = 0
        self.end = 0
        self.avg_task_wait_time = 0
        self.slowdown = 1
        self.batch_flag = 1


class task:
    def __init__(self):
        self.location = ""
        self.id = 0
        self.time = 0
        self.node_num = 0
        self.proc_num = 0
        self.read_files = []
        self.read_job_id = []
        self.write_files = []
        self.write_files_memory = []
        self.parameter = ''
        self.preprocess_script = ''


def Get_single_task_and_configure(line, task_index, task_list, files, origin_files, origin_files_memory, cmd_list,
                                  cmd_flag, workflow_index, first_flag):
    global Het_flag
    global BB_usage_flag
    global BB_size
    global Partition_name
    global SchedulingAlgo
    global R_f, W_f, R_b, W_b
    global BB_path
    global task_workflow_index
    global Uncompleted_Job_Set
    l = line.split()
    if "Task" in l:
        task_tmp = task()
        task_tmp.id = task_index
        tmp = l.index("Task")
        l.pop(tmp)
        if '-cmd' in l:
            tmp = l.index('-cmd')
            cmd_list.append(str(l[tmp + 1].replace('\\', ' ')))
            cmd_flag.append(1)
            l.pop(tmp)
            l.pop(tmp)
            # print(cmd_list)
        else:
            cmd_flag.append(0)
            cmd_list.append("")
        if '-wf' in l:
            tmp = l.index('-wf')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -wf does not specify content')
                return 0
            task_tmp.location = l[tmp + 1]
            l.pop(tmp)
            l.pop(tmp)
        if '-wt' in l:
            tmp = l.index('-wt')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -wt does not specify content')
                return 0
            task_tmp.time = int(l[tmp + 1])
            l.pop(tmp)
            l.pop(tmp)
        if '-N' in l:
            tmp = l.index('-N')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -N does not specify content')
                return 0
            task_tmp.node_num = int(l[tmp + 1])
            l.pop(tmp)
            l.pop(tmp)
        else:
            task_tmp.node_num = 1
        if '-n' in l:
            tmp = l.index('-n')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -n does not specify content')
                return 0
            task_tmp.proc_num = int(l[tmp + 1])
            l.pop(tmp)
            l.pop(tmp)
        else:
            task_tmp.proc_num = task_tmp.node_num
        if '-ps' in l:
            tmp = l.index('-ps')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -ps does not specify content')
                return 0
            task_tmp.preprocess_script = l[tmp + 1]
            l.pop(tmp)
            l.pop(tmp)
        while 1:
            if l.count('-wr') == 0:
                break
            tmp = l.index('-wr')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -wr does not specify content')
                return 0
            task_tmp.read_files.append(l[tmp + 1])
            l.pop(tmp)
            l.pop(tmp)
        while 1:
            if l.count('-ww') == 0:
                break
            tmp = l.index('-ww')
            if l[tmp + 1][0] == '-':
                print('File parsing error: -ww does not specify content')
                return 0
            task_tmp.write_files.append(l[tmp + 1])
            files.append(l[tmp + 1])
            if l[tmp + 2][0] != '-':
                mem_tmp = l[tmp + 2]
                if mem_tmp[len(mem_tmp) - 1] == 'g' or mem_tmp[len(mem_tmp) - 1] == 'G':
                    mem_tmp = float(mem_tmp[:len(mem_tmp) - 1])
                elif mem_tmp[len(mem_tmp) - 1] == 'm' or mem_tmp[len(mem_tmp) - 1] == 'M':
                    mem_tmp = float(mem_tmp[:len(mem_tmp) - 1]) / 1000
                else:
                    mem_tmp = float(mem_tmp)
                task_tmp.write_files_memory.append(mem_tmp)
                l.pop(tmp)
            else:
                task_tmp.write_files_memory.append(0.1)
            l.pop(tmp)
            l.pop(tmp)
        for i in range(0, len(l)):
            task_tmp.parameter += l[i]
            task_tmp.parameter += ' '
        task_list.append(task_tmp)
        task_workflow_index[task_tmp.id - 1] = workflow_index
        Workflow_list[workflow_index].tasks.append(task_tmp.id)
        if len(Workflow_list[workflow_index].tasks) > 1:
            Workflow_list[workflow_index].batch_flag = 0
        Workflow_list[workflow_index].uncompleted_tasks.append(task_tmp.id)
        Uncompleted_Job_Set.append(task_tmp.id)
        return 2
    elif "File" in l:
        if l[1] not in origin_files:
            origin_files.append(l[1])
            mem_tmp = l[2]
            if mem_tmp[len(mem_tmp) - 1] == 'g' or mem_tmp[len(mem_tmp) - 1] == 'G':
                mem_tmp = float(mem_tmp[:len(mem_tmp) - 1])
            elif mem_tmp[len(mem_tmp) - 1] == 'm' or mem_tmp[len(mem_tmp) - 1] == 'M':
                mem_tmp = float(mem_tmp[:len(mem_tmp) - 1]) / 1000
            else:
                mem_tmp = float(mem_tmp)
            origin_files_memory.append(mem_tmp)
            return 1
    elif "HetFlag" in l and first_flag == 1:
        if int(l[1]) == 1:
            Het_flag = 1
        elif int(l[1]) == 0:
            Het_flag = 0
        else:
            print("File parsing error: HetFlag should only be 0 or 1")
            return 0
    elif "BBUsage" in l and first_flag == 1:
        if int(l[1]) == 1:
            BB_usage_flag = 1
        elif int(l[1]) == 0:
            BB_usage_flag = 0
        else:
            print("File parsing error: BBUsage should only be 0 or 1")
            return 0
    #elif "SchedulingAlgo" in l and first_flag == 1:
    #if int(l[1]) < 8:
    #        SchedulingAlgo = int(l[1])
    #        print('SchedulingAlgo = ', SchedulingAlgo)
    #    else:
    #        print("File parsing error: SchedulingAlgo should be smaller than 8")
    #        return 0
    elif "BBSize" in l and first_flag == 1:
        mem_tmp = l[1]
        if mem_tmp[len(mem_tmp) - 1] == 'g' or mem_tmp[len(mem_tmp) - 1] == 'G':
            mem_tmp = int(mem_tmp[:len(mem_tmp) - 1])
        elif mem_tmp[len(mem_tmp) - 1] == 'm' or mem_tmp[len(mem_tmp) - 1] == 'M':
            mem_tmp = int(mem_tmp[:len(mem_tmp) - 1]) / 1000
        else:
            mem_tmp = int(mem_tmp)
        BB_size = mem_tmp
    elif "Partition" in l and first_flag == 1:
        Partition_name = str(l[1])
    elif "Nodes" in l and first_flag == 1:
        for i in range(1, len(l)):
            c = l[i].split('=')
            if c[0] == 'Nodelist':
                Nodelists.append(NodeSet(c[1]))
            elif c[0] == 'S':
                Het_node_capability.append(int(c[1]))
            else:
                print(c[0])
                print("File parsing error: Non-resolvable options appear in the node configuration")
                return 0
    elif "FSReadBandwidth" in l and first_flag == 1:
        R_f = float(l[1])
    elif "FSWriteBandwidth" in l:
        W_f = float(l[1])
    elif "BBReadBandwidth" in l:
        R_b = float(l[1])
    elif "BBWriteBandwidth" in l:
        W_b = float(l[1])
    # elif "FileSystemPath" in  l:
    #     File_system_path = str(l[1])
    elif "BBPath" in l and first_flag == 1:
        BB_path = str(l[1])
    else:
        # if len(l) > 0:
        #     print(l)
        #     print("File parsing error: An disallowed reserved word appears at the beginning of the file line")
        #     return 0
        pass


def Get_tasks_and_configures(task_file, task_list, files, origin_files, origin_files_memory, cmd_list, cmd_flag,
                             workflow_index, first_flag):
    task_index = TASK_NUM + 1
    tasks_file = open(task_file, 'r')
    for line in tasks_file:
        fflag = Get_single_task_and_configure(line, task_index, task_list, files, origin_files, origin_files_memory,
                                              cmd_list, cmd_flag, workflow_index, first_flag)
        if fflag == 0:
            return 0
        elif fflag == 2:
            task_index += 1
    tasks_file.close()
    return 1


def Data_initialization(TASK_NUM_OLD, TASK_NUM, task_list, files, origin_files, origin_files_memory, first_flag):
    global Het_flag
    global BB_usage_flag
    global BB_size
    global Partition_name
    global SchedulingAlgo
    global Nodelists
    global Node_num
    global Het_node_num
    global Het_node_capability
    global R_f, W_f, R_b, W_b, sumE
    global DAG, I, O, E, w, p

    if first_flag == 0:
        for i in range(0, TASK_NUM_OLD):
            if E[task_list[i].id][TASK_NUM_OLD + 1] > 0:
                E[task_list[i].id][TASK_NUM_OLD + 1] = 0
                E[task_list[i].id][TASK_NUM + 1] = E[task_list[i].id][TASK_NUM_OLD + 1]
            if DAG[task_list[i].id][TASK_NUM_OLD + 1] == 1:
                DAG[task_list[i].id][TASK_NUM_OLD + 1] = 0
                DAG[task_list[i].id][TASK_NUM + 1] = 1

    if first_flag == 1:
        # 首先检查配置项是否合法
        if Partition_name == "":
            print("Data initialization error: The node partition must be specified")
            return 0
        if BB_size <= 0 and BB_usage_flag == 1:
            print("Data initialization error: The size of burst buffer must be greater than 0 or equal to 0")
            return 0
        if Het_flag == 0:
            if len(Nodelists) > 1 or len(Nodelists) < 1:
                print("Data initialization error: A homogeneous partition must specify one type of node")
                return 0
        else:
            if len(Nodelists) <= 1:
                print("Data initialization error: Heterogeneous partitions require multiple types of nodes")
        if len(Nodelists) >= 2:
            for i in range(0, len(Nodelists)):
                for j in range(i + 1, len(Nodelists)):
                    # tmp_A = Nodelists[i]
                    # tmp_B = Nodelists[j]
                    # A_list = NodeSet(tmp_A)
                    # B_list = NodeSet(tmp_B)
                    C_list = Nodelists[i].intersection(Nodelists[j])
                if len(C_list) > 0:
                    print("Data initialization error: Different types of node lists have intersections")
                    return 0
        if R_f <= 0:
            print("Data initialization error: the read bandwidth of file system should be larger than 0")
            return 0
        if W_f <= 0:
            print("Data initialization error: the write bandwidth of file system should be larger than 0")
            return 0

        for i in range(0, len(Nodelists)):
            Node_num += len(NodeSet(Nodelists[i]))
            Het_node_num.append(len(NodeSet(Nodelists[i])))
        for i in range(TASK_NUM_OLD, TASK_NUM):  # 遍历所有任务
            if int(task_list[i].time) <= 0:
                print("Data initialization error: The task " + str(i) + " does not specify a correct run time")
                return 0
            # if TA == 0:
            if task_list[i].node_num <= 0:
                print("Data initialization error: The number of required nodes should be larger than 0")
            if task_list[i].proc_num <= 0:
                print("Data initialization error: The number of required processors should be larger than 0")
            if task_list[i].time <= 0:
                print("Data initialization error: The number of required time should be larger than 0")
        for i in range(0, len(origin_files)):
            for j in range(i + 1, len(origin_files)):
                if origin_files[i] == origin_files[j]:
                    print("Data initialization error: Duplicate file definitions exist")
                    return 0

    # 解析文件以得到任务依赖关系并初始化工作流结构体
    for i in range(TASK_NUM_OLD, TASK_NUM):  # 遍历所有任务读的文件
        w[task_list[i].id] = task_list[i].time
        p[task_list[i].id] = task_list[i].node_num
        for j in range(0, len(task_list[i].write_files_memory)):
            if task_list[i].write_files_memory[j] == 0:
                print("Data initialization error: The file " + task_list[i].write_files_memory[
                    j] + " does not specify a size")
                return 0
            else:
                O[task_list[i].id] += task_list[i].write_files_memory[j]
        for j in range(0, len(task_list[i].read_files)):
            if task_list[i].read_files[j] in files:
                # print(task_list[i].read_files[j])
                pre_task = -1
                for k in range(i - 1, -1, -1):
                    for m in range(0, len(task_list[k].write_files)):
                        # print(k, m, task_list[k].write_files[m], task_list[i].read_files[j])
                        if task_list[k].write_files[m] == task_list[i].read_files[j]:
                            pre_task = k + 1
                            break
                    if pre_task > -1:
                        break
                if pre_task == -1:
                    print(task_list[i].read_files[j])
                    print("Data initialization error!")
                    # if task_list[i].read_files[j] in origin_files:
                    #     E[0][task_list[i].id] += origin_files_memory[origin_files.index(task_list[i].read_files[j])]
                    #     DAG[0][task_list[i].id] = 1
                    #     task_list[i].read_job_id.append(0)
                else:
                    pre_task_file_index = task_list[pre_task - 1].write_files.index(task_list[i].read_files[j])
                    E[pre_task][task_list[i].id] += task_list[pre_task - 1].write_files_memory[pre_task_file_index]
                    I[task_list[i].id] += task_list[pre_task - 1].write_files_memory[pre_task_file_index]
                    DAG[pre_task][task_list[i].id] = 1
                    task_list[i].read_job_id.append(pre_task)
            elif task_list[i].read_files[j] in origin_files:
                E[0][task_list[i].id] += origin_files_memory[origin_files.index(task_list[i].read_files[j])]
                # print(first_flag, TASK_NUM_OLD, task_list[i].id, origin_files_memory[origin_files.index(task_list[i].read_files[j])])
                I[task_list[i].id] += origin_files_memory[origin_files.index(task_list[i].read_files[j])]
                DAG[0][task_list[i].id] = 1
                task_list[i].read_job_id.append(0)
            else:
                print('Data initialization error: the file ' + task_list[i].read_files[
                    j] + ' of the ' + str(i) + ' task ' + 'should be specified as the original files')
                E[0][task_list[i].id] = 0
                DAG[0][task_list[i].id] = 1
                return 0

    # for key in files_csm:  # 如果有文件没有任何任务读，那么它要么是初始文件（这是错误配置，在流程中会被忽略，因为初始文件不在files/files_csm中），要么是最后输出的文件
    #     if files_csm[key] == 0:
    #         task_id = -1
    #         for i in range(len(task_list) - 1, -1, -1):
    #             for j in range(0, len(task_list[i].write_files)):
    #                 if task_list[i].write_files[j] == key:
    #                     task_id = i + 1
    #                     break
    for i in range(TASK_NUM_OLD, TASK_NUM):  # 遍历所有任务
        # remain_write_mem = O[task_list[i].id]
        # for j in range(i + 1, TASK_NUM):
        #     remain_write_mem -= E[task_list[i].id][task_list[j].id]
        if DAG[0][task_list[i].id] == 0:
            DAG[0][task_list[i].id] = 1
            E[0][task_list[i].id] = 0.1
        E[task_list[i].id][TASK_NUM + 1] = 0.1
        DAG[task_list[i].id][TASK_NUM + 1] = 1

    # non_pre = [1 for i in range(0, TASK_NUM + 2)]
    # non_suc = [1 for i in range(0, TASK_NUM + 2)]
    # for i in range(1, TASK_NUM + 1):
    #     for j in range(1, TASK_NUM + 1):
    #         if DAG[j][i] == 1:
    #             non_pre[i] = 0
    #         if DAG[i][j] == 1:
    #             non_suc[i] = 0
    # for i in range(1, TASK_NUM + 1):
    #     if non_pre[i] == 1:
    #         DAG[0][i] = 1
    #     if non_suc[i] == 1:
    #         DAG[i][TASK_NUM + 1] = 1

    # for i in range(1, TASK_NUM + 1):
    #     for j in range(0, TASK_NUM + 2):
    #         if DAG[j][i] == 1:
    #             I[i] += E[j][i]
    # for i in range(1, TASK_NUM + 1):
    #     for j in range(0, TASK_NUM + 2):
    #         if DAG[i][j] == 1:
    #             O[i] += E[i][j]
    for i in range(TASK_NUM_OLD, TASK_NUM):
        if w[task_list[i].id] == 0:
            rI[task_list[i].id] = rO[task_list[i].id] = 0
        else:
            rI[task_list[i].id] = I[task_list[i].id] / w[task_list[i].id]
            rO[task_list[i].id] = O[task_list[i].id] / w[task_list[i].id]
    for i in range(TASK_NUM_OLD, TASK_NUM):
        sumE += O[task_list[i].id]
    return 1


def Getsinglebl(i):
    global DAG
    global w
    global bl
    global TASK_NUM
    if bl[i] != -1:
        return bl[i]
    m = 0
    for j in range(0, TASK_NUM + 2):
        if DAG[i][j] == 1:
            m = max(m, Getsinglebl(j))
    m += w[i]
    return m


def Getbl():
    global bl
    global TASK_NUM
    for i in range(TASK_NUM + 1, -1, -1):
        bl[i] = Getsinglebl(i)


def Monitor_Jobs(Nodelists, Running_Job_Set, Running_Job_ID, Running_Job_Nodelist, Ready_Job_Set, Finish_Job_Set):
    global Partition_name
    global DAG
    global TASK_NUM
    global Node_num
    global Het_node_num
    global Het_flag
    global Het_schedule
    global Workflow_slowdown_list
    global Uncompleted_Job_Set
    change_flag = 0
    # print("Ready_Job_Set after adding", Ready_Job_Set)
    i = 0
    while i < len(Running_Job_ID):
        job_id_system = Running_Job_ID[i]
        job_id_workflow = Running_Job_Set[i]
        cmd = 'sacct -j ' + str(job_id_system) + " -o state"
        # print(cmd)
        # val = "COMPLETED"
        return_val = os.popen(cmd)
        r = return_val.readlines()
        if len(r) <= 2:
            val = 'RUNNING'
        else:
            val = r[2].strip()
        # print(val)
        if val == 'COMPLETED' or val == 'FAILED':
            if val == 'FAILED':
                print('Task ' + str(job_id_workflow) + ' in a wrong state ' + val + ' (job id is ' + str(job_id_system) + ')')

            change_flag = 1
            # print('Task ' + str(job_id_workflow) + ' has finished successfully (job id is ' + str(job_id_system) + ')')
            Running_Job_ID.pop(i)
            Running_Job_Set.pop(i)
            if Het_flag == 1:
                Nodelists[Het_schedule[job_id_workflow]] = Nodelists[Het_schedule[job_id_workflow]].union(
                    Running_Job_Nodelist.pop(i))
            Node_num += p[job_id_workflow]
            if Het_flag == 1:
                Het_node_num[Het_schedule[job_id_workflow]] += p[job_id_workflow]
            Finish_Job_Set.append(job_id_workflow)
            # print(job_id_workflow)
            # if job_id_workflow == 405:
                # print("------------------------")
            Uncompleted_Job_Set.remove(job_id_workflow)

            Workflow_list[task_workflow_index[job_id_workflow - 1]].completed_tasks.append(job_id_workflow)
            Workflow_list[task_workflow_index[job_id_workflow - 1]].uncompleted_tasks.remove(job_id_workflow)
            Workflow_list[task_workflow_index[job_id_workflow - 1]].uncompleted_bl.remove(bl[job_id_workflow])
            if (len(Workflow_list[task_workflow_index[job_id_workflow - 1]].completed_tasks) == len(
                    Workflow_list[task_workflow_index[job_id_workflow - 1]].tasks)):
                Workflow_list[task_workflow_index[job_id_workflow - 1]].end_time = time.time()
                Workflow_list[task_workflow_index[job_id_workflow - 1]].end = 1
                task_wait_time_sum = 0
                for j in range(len(Workflow_list[task_workflow_index[job_id_workflow - 1]].completed_tasks)):
                    task_wait_time_sum += Task_wait_time[
                        Workflow_list[task_workflow_index[job_id_workflow - 1]].completed_tasks[j]]
                Workflow_list[task_workflow_index[job_id_workflow - 1]].avg_task_wait_time = task_wait_time_sum / len(
                    Workflow_list[task_workflow_index[job_id_workflow - 1]].completed_tasks)
                Workflow_slowdown_list.append((Workflow_list[task_workflow_index[job_id_workflow - 1]].end_time -
                                               Workflow_list[task_workflow_index[job_id_workflow - 1]].arrive_time) /
                                              Workflow_list[task_workflow_index[job_id_workflow - 1]].max_bl)
                Workflow_list[task_workflow_index[job_id_workflow - 1]].slowdown = (Workflow_list[task_workflow_index[
                    job_id_workflow - 1]].end_time -
                                                                                    Workflow_list[task_workflow_index[
                                                                                        job_id_workflow - 1]].arrive_time) / \
                                                                                   Workflow_list[task_workflow_index[job_id_workflow - 1]].max_bl

            for j in range(0, TASK_NUM + 2):
                if DAG[job_id_workflow][j] == 1:
                    ready_flag = 1
                    for k in range(0, TASK_NUM + 2):
                        if DAG[k][j] == 1:
                            if k in Finish_Job_Set:
                                ready_flag = 1
                            else:
                                ready_flag = 0
                                break
                    if ready_flag == 1:
                        Ready_Job_Set.append(j)
        #elif val == 'FAILED':
        #    print('Task ' + str(job_id_workflow) + ' in a wrong state ' + val + ' (job id is ' + str(job_id_system) + ')')
        #    Node_num += p[job_id_workflow]
        #    change_flag = 1
        #    Running_Job_ID.pop(i)
        #    Running_Job_Set.pop(i)
        #    Ready_Job_Set.append(job_id_workflow)
        elif val == 'RUNNING' or val == 'PENDING' or val == "COMPLETING":
            i += 1
        else:
            print(
                'Task ' + str(job_id_workflow) + ' in a wrong state ' + val + ' (job id is ' + str(job_id_system) + ')')
            return 0
    for j in range(0, TASK_NUM + 2):
        if j not in Finish_Job_Set and DAG[0][j] == 1:
            ready_flag = 1
            for k in range(0, j):
                if DAG[k][j] == 1:
                    if k in Finish_Job_Set:
                        ready_flag = 1
                    else:
                        ready_flag = 0
                        break
            if ready_flag == 1 and j not in Ready_Job_Set and j not in Running_Job_Set:
                Ready_Job_Set.append(j)
                change_flag = 1
    if change_flag:
        return 2
    else:
        return 1


def Schedule_Job_BB_HCF(Running_Job_Set, Submit_Job_Set, job_id, index):
    pass
    # global BB_usage_record
    # global BB_size
    # global BB_total
    # global FI, FO, BI, BO
    # global rFI, rFO, rBI, rBO
    # global R_f, W_f
    # global sumE
    # sumrFO = 0
    # for job in Running_Job_Set:
    #     sumrFO += rFO[job]
    # for i in range(0, index):
    #     sumrFO += rFO[Submit_Job_Set[i]]
    # for i in range(0, TASK_NUM + 2):
    #     if DAG[i][job_id] == 1:
    #         if BB_usage_record[i] == 0 or i == 0:
    #             FI[job_id] += E[i][job_id]
    #         elif BB_usage_record[i] == 1:
    #             BI[job_id] += E[i][job_id]
    # rFI[job_id] = FI[job_id] / w[job_id]
    # rBI[job_id] = BI[job_id] / w[job_id]
    #
    # if min(1, float(BB_total / sumE + 0.5)) * (sumrFO + O[job_id] / w[job_id]) > W_f:
    #     if BB_size > O[job_id]:
    #         BB_size -= O[job_id]
    #         BB_usage_record[job_id] = 1
    #         FO[job_id] = 0
    #         BO[job_id] = O[job_id]
    #         rFO[job_id] = FO[job_id] / w[job_id]
    #         rBO[job_id] = BO[job_id] / w[job_id]
    #         return 0
    # FO[job_id] = O[job_id]
    # BO[job_id] = 0
    # rFO[job_id] = FO[job_id] / w[job_id]
    # rBO[job_id] = BO[job_id] / w[job_id]
    # return 0


def Schedule_Job_BB_SBA(Running_Job_Set, Submit_Job_Set, job_id, index):
    global BB_usage_record
    global BB_size
    global BB_total
    global FI, FO, BI, BO
    global rFI, rFO, rBI, rBO
    global R_f, W_f
    global sumE
    global BB_usage_record

    pass
    # tmp_list = sorted(Submit_Job_Set, key=lambda x: O[x])
    # for


    # sumrFO = 0
    # for job in Running_Job_Set:
    #     sumrFO += rFO[job]
    # for i in range(0, index):
    #     sumrFO += rFO[Submit_Job_Set[i]]
    # for i in range(0, TASK_NUM + 2):
    #     if DAG[i][job_id] == 1:
    #         if BB_usage_record[i] == 0 or i == 0:
    #             FI[job_id] += E[i][job_id]
    #         elif BB_usage_record[i] == 1:
    #             BI[job_id] += E[i][job_id]
    # rFI[job_id] = FI[job_id] / w[job_id]
    # rBI[job_id] = BI[job_id] / w[job_id]
    #
    # if min(1, float(BB_total / sumE + 0.5)) * (sumrFO + O[job_id] / w[job_id]) > W_f:
    #     if BB_size > O[job_id]:
    #         BB_size -= O[job_id]
    #         BB_usage_record[job_id] = 1
    #         FO[job_id] = 0
    #         BO[job_id] = O[job_id]
    #         rFO[job_id] = FO[job_id] / w[job_id]
    #         rBO[job_id] = BO[job_id] / w[job_id]
    #         return 0
    # FO[job_id] = O[job_id]
    # BO[job_id] = 0
    # rFO[job_id] = FO[job_id] / w[job_id]
    # rBO[job_id] = BO[job_id] / w[job_id]
    return 0


def Schedule_Jobs(Running_Job_Set, Ready_Job_Set, Submit_Job_Set):
    global Het_flag
    global BB_usage_flag
    global BB_size
    global SchedulingAlgo
    global Node_num
    global Het_flag
    global Het_node_num
    global Het_node_capability
    global Het_schedule
    global rI, rO, rFI, rFO
    global sumE
    global Workflow_list
    global task_workflow_index
    # print("***************start scheduling*************")
    # print('Ready_Job_Set', Ready_Job_Set)
    # print('Submit_Job_Set', Submit_Job_Set)
    if len(Ready_Job_Set) == 1 and Ready_Job_Set[0] == TASK_NUM + 1:
        Ready_Job_Set.remove(TASK_NUM + 1)
        Submit_Job_Set.append(TASK_NUM + 1)
        return 1
    if Het_flag == 0:
        if BB_usage_flag == 0:  # 同构节点，没有burst buffer资源，使用各种调度方案
            if SchedulingAlgo == 0:  # 同构节点，没有burst buffer资源，使用FCFS
                tmp_list = sorted(Ready_Job_Set, key=lambda x: x, reverse = True)
                for i in range(len(tmp_list) - 1, -1, -1):
                    if Node_num >= p[tmp_list[i]]:
                        new_id = tmp_list[i]
                        Submit_Job_Set.append(new_id)
                        Node_num -= p[new_id]
                        Ready_Job_Set.remove(new_id)
            elif SchedulingAlgo == 1:  # 同构节点，没有burst buffer资源，使用HEFT
                tmp_list = sorted(Ready_Job_Set, key=lambda x: bl[x])
                # tmp_list = sorted(Ready_Job_Set, key=lambda x: bl[x])
                for i in range(len(tmp_list) - 1, -1, -1):
                    if Node_num >= p[tmp_list[i]]:
                        new_id = tmp_list[i]
                        Submit_Job_Set.append(new_id)
                        Node_num -= p[new_id]
                        Ready_Job_Set.remove(new_id)
            elif SchedulingAlgo == 2:  # 同构节点，没有burst buffer资源，使用HCF
                srI = 0
                srO = 0
                bf = [-10000 for j in range(0, TASK_NUM + 2)]
                bl_tmp = []
                for job in Running_Job_Set:
                    srI += rI[job]
                    srO += rO[job]
                while 1:
                    bl_tmp.clear()
                    for job in Ready_Job_Set:
                        bl_tmp.append(bl[job])
                    blmax = max(bl_tmp)
                    for job in Ready_Job_Set:
                        if srI + rI[job] <= R_f:
                            if blmax == 0:
                                bfi = 1
                            else:
                                bfi = bl[job] / blmax
                        else:
                            bfi = (bl[job] / blmax) - ((srI + rI[job]) - max(R_f, srI)) / max(R_f, srI)
                        if srO + rO[job] <= W_f:
                            if blmax == 0:
                                bfo = 1
                            else:
                                bfo = bl[job] / blmax
                        else:
                            bfo = (bl[job] / blmax) - ((srO + rO[job]) - max(W_f, srO)) / max(W_f, srO)
                        bf[job] = min(bfi, bfo)
                    tmp_list = sorted(Ready_Job_Set, key=lambda x: bf[x])
                    schedule_flag = 0
                    for i in range(len(tmp_list) - 1, -1, -1):
                        if Node_num >= p[tmp_list[i]]:
                            new_id = tmp_list[i]
                            if schedule_flag == 0:
                                Submit_Job_Set.append(new_id)
                                Node_num -= p[new_id]
                                Ready_Job_Set.remove(new_id)
                                schedule_flag = 1
                                srI += rI[new_id]
                                srO += rO[new_id]
                                break
                    if schedule_flag == 0 or len(Ready_Job_Set) == 0:
                        break
        else:  # 同构节点，有burst buffer资源，使用LBF或MCP
            if SchedulingAlgo == 0:  # 同构节点，有burst buffer资源，使用FCFS
                tmp_list = sorted(Ready_Job_Set, key=lambda x: x, reverse=True)
                for i in range(len(tmp_list) - 1, -1, -1):
                    if Node_num >= p[tmp_list[i]]:
                        new_id = tmp_list[i]
                        Submit_Job_Set.append(new_id)
                        Node_num -= p[new_id]
                        Ready_Job_Set.remove(new_id)
            elif SchedulingAlgo == 1:  # 同构节点，有burst buffer资源，使用HEFT
                tmp_list = sorted(Ready_Job_Set, key=lambda x: bl[x])
                # tmp_list = sorted(Ready_Job_Set, key=lambda x: bl[x])
                for i in range(len(tmp_list) - 1, -1, -1):
                    if Node_num >= p[tmp_list[i]]:
                        new_id = tmp_list[i]
                        Submit_Job_Set.append(new_id)
                        Node_num -= p[new_id]
                        Ready_Job_Set.remove(new_id)
                for job_id_workflow in Submit_Job_Set:
                    Schedule_Job_BB_SBA(Running_Job_Set, Submit_Job_Set, job_id_workflow,
                                        Submit_Job_Set.index(job_id_workflow))
            elif SchedulingAlgo == 2:  # 同构节点，有burst buffer资源，使用HCF
                # srI = 0
                # srO = 0
                srIf = 0
                srOf = 0
                srIb = 0
                srOb = 0
                bf = [-10000 for j in range(0, TASK_NUM + 2)]
                bl_tmp = []
                for job in Running_Job_Set:
                    # srI += rI[job]
                    # srO += rO[job]
                    srIf += rFI[job]
                    srOf += rFO[job]
                    srIb += rBI[job]
                    srOb += rBO[job]
                BB_tmp = BB_size
                while 1:
                    bl_tmp.clear()
                    for job in Ready_Job_Set:
                        bl_tmp.append(bl[job])
                    blmax = max(bl_tmp)
                    for job in Ready_Job_Set:

                        if blmax == 0:
                            bl_file_input = 1 - 0.5 * ((srIf + I[job] / w[job]) - max(R_f, srIf)) / max(R_f, srIf) 
                            bl_file_output = 1 - 0.5 * ((srOf + O[job] / w[job]) - max(W_f, srOf)) / max(W_f, srOf) 
                            if BB_tmp >= O[job]:  # with bb
                                bl_bb_input = 1 - 0.5 * ((srIb + I[job] / w[job]) - max(R_b, srIb)) / max(R_b, srIb) 
                                bl_bb_output = 1 - 0.5 * ((srOb + O[job] / w[job]) - max(W_b, srOb)) / max(W_b, srOb) 
                            else:  # without bb
                                bl_bb_input = bl_file_input
                                bl_bb_output = bl_file_output

                            b_without = min(bl_file_input, bl_file_output, 1)
                            b_with = min(bl_file_input, bl_bb_input, bl_file_input, bl_bb_output, 1)
                        else:
                            bl_file_input = bl[job] / blmax - 0.5 * ((srIf + I[job] / w[job]) - max(R_f, srIf)) / max(R_f, srIf) 
                            bl_file_output = bl[job] / blmax - 0.5 * ((srOf + O[job] / w[job]) - max(W_f, srOf)) / max(W_f, srOf)
                            if BB_tmp >= O[job]:  # with bb
                                bl_bb_input = bl[job] / blmax - 0.5 * ((srIb + I[job] / w[job]) - max(R_b, srIb)) / max(R_b, srIb) 
                                bl_bb_output = bl[job] / blmax - 0.5 *((srOb + O[job] / w[job]) - max(W_b, srOb)) / max(W_b, srOb) 
                            else:  # without bb
                                bl_bb_input = bl_file_input
                                bl_bb_output = bl_file_output

                            b_without = min(bl_file_input, bl_file_output, bl[job] / blmax)
                            b_with = min(bl_file_input, bl_bb_output, bl[job] / blmax)
                        if min(1, BB_total / sumE + 0.5) * b_with > b_without:
                            # if b_with > b_without:
                            bf[job] = b_with
                            BB_usage_record[job] = 1
                        else:
                            bf[job] = b_without
                            BB_usage_record[job] = 0

                    tmp_list = sorted(Ready_Job_Set, key=lambda x: bf[x])
                    schedule_flag = 0
                    for i in range(len(tmp_list) - 1, -1, -1):
                        if Node_num >= p[tmp_list[i]]:
                            new_id = tmp_list[i]
                            if schedule_flag == 0:
                                Submit_Job_Set.append(new_id)
                                Node_num -= p[new_id]
                                Ready_Job_Set.remove(new_id)
                                schedule_flag = 1
                                if BB_usage_record[new_id] == 0:
                                    rFI[new_id] = I[new_id] / w[new_id]
                                    rFO[new_id] = O[new_id] / w[new_id]
                                    rBI[new_id] = 0
                                    rBO[new_id] = 0
                                else:
                                    # print('----------------------------------', new_id, O[new_id], BB_size)
                                    BB_tmp -= O[new_id]
                                    rFI[new_id] = 0
                                    rFO[new_id] = 0
                                    rBI[new_id] = I[new_id] / w[new_id]
                                    rBO[new_id] = O[new_id] / w[new_id]
                                srIf += rFI[new_id]
                                srOf += rFO[new_id]
                                srIb += rBI[new_id]
                                srOb += rBO[new_id]
                                break
                    if schedule_flag == 0 or len(Ready_Job_Set) == 0:
                        break

def Submit_Jobs(Nodelists, Running_Job_Set, Running_Job_Nodelist, Submit_Job_Set, cmd_list, cmd_flag):
    global BB_usage_record
    # global File_system_path
    global BB_path
    global BB_size
    if len(Submit_Job_Set) == 1 and Submit_Job_Set[0] == TASK_NUM + 1:
        Submit_Job_Set.remove(TASK_NUM + 1)
        Finish_Job_Set.append(TASK_NUM + 1)
        return 1
    if Het_flag == 0:
        for job in Submit_Job_Set:
            with open('task_' + str(job) + '.sh', 'w', encoding='utf-8') as f:
                f.write("#!/bin/bash\n")
                #f.write("#SBATCH -o ~/dyq/slurm-log/slurm-%j.out\n")
                f.write("#SBATCH -p " + str(Partition_name) + "\n")
                f.write("#SBATCH -N " + str(task_list[job - 1].node_num) + "\n")
                f.write("#SBATCH -n " + str(task_list[job - 1].proc_num) + "\n")
                #f.write("#SBATCH -w " + str(Nodelists[0]) + "\n")
                # f.write("#SBATCH -t " + str(task_list[job - 1].time * 1.2) + "\n")
                #if BB_usage_flag == 1:
                #    f.write("#DW persistentdw name=test\n")
                if cmd_flag[job - 1] == 1:
                    f.write(str(cmd_list[job - 1]) + "\n")
                parameter_string = task_list[job - 1].parameter
                if BB_usage_flag == 1:
                    # while "$FILEPATH" in parameter_string:
                    #     tmp_index = parameter_string.index("$FILEPATH")
                    #     end_index = tmp_index
                    #     for i in range(tmp_index + 9, len(parameter_string)):
                    #         if parameter_string[i] != " ":
                    #             end_index = i
                    #         else:
                    #             break
                    #     tmp_filename = parameter_string[tmp_index + 9:end_index + 1]
                    #     if tmp_filename in task_list[job - 1].read_files:
                    #         pre_task = task_list[job - 1].read_job_id[task_list[job - 1].read_files.index(tmp_filename)]
                    #         bb_usage = BB_usage_record[pre_task]
                    #         if bb_usage == 1:
                    #             parameter_string = parameter_string.replace("$FILEPATH", BB_path, 1)
                    #         else:
                    #             parameter_string = parameter_string.replace("$FILEPATH", "", 1)
                    #     elif tmp_filename in task_list[job - 1].write_files:
                    #         bb_usage = BB_usage_record[job]
                    #         if bb_usage == 1:
                    #             parameter_string = parameter_string.replace("$FILEPATH", BB_path, 1)
                    #         else:
                    #             parameter_string = parameter_string.replace("$FILEPATH", "", 1)
                    #     else:
                    #         print("wrong!！！！！！！！！！！！！！！！！！！！")
                    #         exit()
                    # f.write("srun " + parameter_string + "\n")
                    bb_usage = BB_usage_record[job]
                    if bb_usage == 1:
                        f.write("#DW persistentdw name=test\n")
                        #f.write("srun " + str(task_list[job - 1].parameter.strip()) + "bb-random " + str(job) + "\n")
                        f.write("srun --mpi=pmix " + str(task_list[job - 1].parameter.strip()) + "bb " + str(job) + "\n")
                        BB_size -= O[job]
                    else:
                        #f.write("srun --mpi=pmix" + str(task_list[job - 1].parameter) + "-random " +str(job) + "\n")
                        f.write("srun --mpi=pmix" + str(task_list[job - 1].parameter) + " " + str(job) + "\n")
                else:
                    f.write("srun --mpi=pmix " + str(task_list[job - 1].parameter) + " " + str(job) + "\n")
            cmd = 'sbatch task_' + str(job) + '.sh'
            # print(cmd)
            # val = "COMPLETED"
            return_val = os.popen(cmd)
            val = return_val.readlines()[0].split()[3]
            Running_Job_Set.append(job)
            Running_Job_ID.append(val)
            # print("We schedule the job" + str(job) + " to the HPC system")
    else:
        for job in Submit_Job_Set:
            Nodelist_index = Het_schedule[job]
            current_Nodelist = Nodelists[Nodelist_index]
            tmp_Nodelist = current_Nodelist[0:task_list[job - 1].node_num]
            Nodelists[Nodelist_index].remove(tmp_Nodelist)
            with open('task_' + str(job) + '.sh', 'w', encoding='utf-8') as f:
                f.write("#!/bin/bash\n")
                f.write("#SBATCH -o /tmp/job.%j.out\n")
                f.write("#SBATCH -p " + str(Partition_name) + "\n")
                f.write("#SBATCH -N " + str(task_list[job - 1].node_num) + "\n")
                f.write("#SBATCH -n " + str(task_list[job - 1].proc_num) + "\n")
                # f.write("#SBATCH -t " + str(task_list[job - 1].time) + "\n")
                f.write("#SBATCH -w " + str(tmp_Nodelist) + "\n")
                parameter_string = task_list[job - 1].parameter
                if BB_usage_flag == 1:
                    f.write("#DW persistentdw name=mytestbuffer\n")
                    while "$FILEPATH" in parameter_string:
                        tmp_index = parameter_string.index("$FILEPATH")
                        end_index = tmp_index
                        for i in range(tmp_index + 9, len(parameter_string)):
                            if parameter_string[i] != " ":
                                end_index = i
                            else:
                                break
                        tmp_filename = parameter_string[tmp_index + 9:end_index + 1]
                        print("job = ", job)
                        if tmp_filename in task_list[job - 1].read_files:
                            pre_task = task_list[job - 1].read_job_id[task_list[job - 1].read_files.index(tmp_filename)]
                            bb_usage = BB_usage_record[pre_task]
                            if bb_usage == 1:
                                parameter_string = parameter_string.replace("$FILEPATH", BB_path, 1)
                            else:
                                parameter_string = parameter_string.replace("$FILEPATH", "", 1)
                        elif tmp_filename in task_list[job - 1].write_files:
                            bb_usage = BB_usage_record[job]
                            if bb_usage == 1:
                                parameter_string = parameter_string.replace("$FILEPATH", BB_path, 1)
                            else:
                                parameter_string = parameter_string.replace("$FILEPATH", "", 1)
                        else:
                            print("wrong!！！！！！！！！！！！！！！！！！！！")
                            exit()
                    f.write("srun " + parameter_string + "\n")
                else:
                    f.write("srun " + str(task_list[job - 1].parameter) + " " + str(job) +"\n")
            cmd = 'sbatch task_' + str(job) + '.sh'
            print(cmd)
            #val = "COMPLETED"
            return_val = os.popen(cmd)
            val = return_val.readlines()[0].split()[3]
            Running_Job_Set.append(job)
            Running_Job_ID.append(int(val))
            #Running_Job_ID.append(int(123))
            Running_Job_Nodelist.append(tmp_Nodelist)
            # print("We schedule the job" + str(job) + " to the HPC system")
    Submit_Job_Set.clear()
    return 1


def Abnormal_termination_output(Running_Job_Set, Running_Job_ID, Finish_Job_Set):
    print("*************Abnormal Termination*************:")
    print("Finish_Job_Set:", Finish_Job_Set)
    print("Running_Job_Set:", Running_Job_Set)
    print("Running_Job_ID:", Running_Job_ID)



def Read_file(task_list, files, origin_files, origin_files_memory, cmd_list, cmd_flag):
    global All_Task_files
    global Completed_Task_files
    global TASK_NUM
    global Workflow_list
    global BB_usage_record
    global BB_size
    task_num_tmp = len(task_list)
    # task_list.clear()
    # files.clear()
    # origin_files.clear()
    # origin_files_memory.clear()
    # cmd_flag.clear()
    # cmd_list.clear()
    New_Task_files = []
    for i in range(len(All_Task_files)):
        if All_Task_files[i] not in Completed_Task_files:
            New_Task_files.append(All_Task_files[i])

    if len(New_Task_files) == 0:
        return TASK_NUM
    print(New_Task_files)

    if len(Completed_Task_files) == 0:
        workflow_index = len(Workflow_list)
        Workflow_list.append(workflow(workflow_index))
        sparse_flag = Get_tasks_and_configures(New_Task_files[0], task_list, files, origin_files, origin_files_memory,
                                               cmd_list, cmd_flag, len(Workflow_list) - 1, 1)
        if sparse_flag == 0:
            print('File parsing failed.')
            exit()
        TASK_NUM_OLD = TASK_NUM
        TASK_NUM = len(task_list)
        initialize_flag = Data_initialization(TASK_NUM_OLD, TASK_NUM, task_list, files, origin_files,
                                              origin_files_memory, 1)
        if initialize_flag == 0:
            print('Data initialization failed')
            exit()
        Completed_Task_files.append(New_Task_files[0])
        New_Task_files.remove(New_Task_files[0])

    for i in range(len(New_Task_files)):
        workflow_index = len(Workflow_list)
        Workflow_list.append(workflow(workflow_index))

        sparse_flag = Get_tasks_and_configures(New_Task_files[i], task_list, files, origin_files, origin_files_memory,
                                               cmd_list, cmd_flag, len(Workflow_list) - 1, 0)
        if sparse_flag == 0:
            print('File parsing failed.')
            exit()
        TASK_NUM_OLD = TASK_NUM
        TASK_NUM = len(task_list)
        initialize_flag = Data_initialization(TASK_NUM_OLD, TASK_NUM, task_list, files, origin_files,
                                              origin_files_memory, 0)
        if initialize_flag == 0:
            print('Data initialization failed')
            exit()
        TASK_NUM = len(task_list)
        Completed_Task_files.append(New_Task_files[i])

    Getbl()

    for i in range(task_num_tmp, len(task_list)):
        Workflow_list[task_workflow_index[i]].uncompleted_bl.append(bl[i + 1])
    for i in range(task_workflow_index[task_num_tmp], len(Workflow_list)):
        Workflow_list[i].max_bl = max(Workflow_list[i].uncompleted_bl)

    tmp_list = sorted(Uncompleted_Job_Set, key=lambda x: O[x], reverse=True)
    BB_tmp = BB_size
    if BB_usage_flag == 1:
        for i in range(len(tmp_list)):
            if BB_tmp > O[tmp_list[i]]:
                BB_usage_record[tmp_list[i]] = 1
                BB_tmp -= O[tmp_list[i]]
                print("BB_tmp", BB_tmp)
            else:
                break
                BB_usage_record[tmp_list[i]] = 0

    return TASK_NUM


# I and O need to be calculated from Files instead of Edges
task_list = []  
files = []  
origin_files = []  
origin_files_memory = []
# task_file = '/home/daiyiqin3/Desktop/task.txt'
# task_file = "C:\\Users\\戴屹钦\\PycharmProjects\\ICS2023\\Generated_Tasks.txt"
Het_flag = 0
BB_usage_flag = 0
BB_size = 0
SchedulingAlgo = 0
Partition_name = ""
Nodelists = []
Node_num = 0
Het_node_num = []
Het_node_capability = []
# File_system_path = ""
BB_path = ""
cmd_list = []
R_f = 0
W_f = 0
R_b = 0
W_b = 0
sumE = 0
cmd_flag = []
NUM_SUM = 1000
DAG = [[0 for j in range(0, NUM_SUM + 2)] for i in range(0, NUM_SUM + 2)]
E = [[0 for j in range(0, NUM_SUM + 2)] for i in range(0, NUM_SUM + 2)]
p = [0 for j in range(0, NUM_SUM + 2)]
I = [0 for j in range(0, NUM_SUM + 2)]
O = [0 for j in range(0, NUM_SUM + 2)]
FI = [0 for j in range(0, NUM_SUM + 2)]
FO = [0 for j in range(0, NUM_SUM + 2)]
BI = [0 for j in range(0, NUM_SUM + 2)]
BO = [0 for j in range(0, NUM_SUM + 2)]
rI = [0 for j in range(0, NUM_SUM + 2)]
rO = [0 for j in range(0, NUM_SUM + 2)]
rFI = [0 for j in range(0, NUM_SUM + 2)]
rFO = [0 for j in range(0, NUM_SUM + 2)]
rBI = [0 for j in range(0, NUM_SUM + 2)]
rBO = [0 for j in range(0, NUM_SUM + 2)]
bl = [-1 for j in range(0, NUM_SUM + 2)]  
w = [0 for j in range(0, NUM_SUM + 2)]
Het_schedule = [0 for j in range(0, NUM_SUM + 2)]
BB_usage_record = [0 for j in range(0, NUM_SUM + 2)]
Task_wait_time = [0 for j in range(0, NUM_SUM + 2)]
Workflow_list = []  
task_workflow_index = [0 for j in range(0, NUM_SUM + 2)]  

Running_Job_Set = []
Running_Job_ID = []
Running_Job_Nodelist = []
Uncompleted_Job_Set = []
Ready_Job_Set = []
Finish_Job_Set = []
Submit_Job_Set = []
Finish_Job_Set.append(0)
All_Task_files = []
Completed_Task_files = []
Workflow_slowdown_list = []
TASK_NUM = 0


All_Task_files.append("workflow_dcp.input")

TASK_NUM = Read_file(task_list, files, origin_files, origin_files_memory, cmd_list, cmd_flag)
print("TASK_NUM", TASK_NUM)
BB_total = BB_size
alpha = 0.5

print(task_workflow_index)

SchedulingAlgo = int(sys.argv[1])

time_start = time.time()
time_s = time_e = 0
time_in = 0
scheduling_time = 0
num = 0
while len(Ready_Job_Set) > 0 or len(Running_Job_Set) > 0 or len(Finish_Job_Set) < TASK_NUM:

    num += 1
    job_monitor_flag = Monitor_Jobs(Nodelists, Running_Job_Set, Running_Job_ID, Running_Job_Nodelist, Ready_Job_Set,
                                    Finish_Job_Set)

    if job_monitor_flag == 2:
        print("********************************************************************")
        #print("Uncompleted_Job_Set", Uncompleted_Job_Set)
        print("Running_Job_Set:", Running_Job_Set)
        print("Finish_Job_Set:", Finish_Job_Set)
        print("Ready_Job_Set:", Ready_Job_Set)
        print("Node_num:", Node_num)

    if job_monitor_flag == 0:
        Abnormal_termination_output(Running_Job_Set, Running_Job_ID, Finish_Job_Set)
        exit()
    # Getbl()
    if num == 3:
        for i in range(31, 60):
            pass
    if len(Ready_Job_Set) > 0:
        time_s = time.time()
        job_schedule_flag = Schedule_Jobs(Running_Job_Set, Ready_Job_Set, Submit_Job_Set)
        time_e = time.time()
        time_in += float(time_e - time_s)
        scheduling_time += 1
        if job_schedule_flag == 0:
            Abnormal_termination_output(Running_Job_Set, Running_Job_ID, Finish_Job_Set)
            exit()
    if len(Submit_Job_Set) > 0:
        print("Submit_Job_Set:", Submit_Job_Set)
    for i in range(len(Submit_Job_Set)):
        if Submit_Job_Set[i] < len(task_list) + 1 and Workflow_list[
            task_workflow_index[Submit_Job_Set[i] - 1]].start == 0:
            Workflow_list[task_workflow_index[Submit_Job_Set[i] - 1]].start = 1
            Workflow_list[task_workflow_index[Submit_Job_Set[i] - 1]].start_time = time.time()
        if Submit_Job_Set[i] > 0 and Submit_Job_Set[i] <= len(task_list):
            Task_wait_time[Submit_Job_Set[i]] = time.time() - Workflow_list[
                task_workflow_index[Submit_Job_Set[i] - 1]].start_time

    job_submit_flag = Submit_Jobs(Nodelists, Running_Job_Set, Running_Job_Nodelist, Submit_Job_Set, cmd_list, cmd_flag)
    if job_submit_flag == 0:
        Abnormal_termination_output(Running_Job_Set, Running_Job_ID, Finish_Job_Set)
        exit()

    for i in range(len(Workflow_list)):
        if Workflow_list[i].start == 1 and Workflow_list[i].end == 0:
            Workflow_list[i].running_time = time.time() - Workflow_list[i].arrive_time

time_end = time.time()
print("**************************************************")
print("makespan:", float(time_end - time_start))

