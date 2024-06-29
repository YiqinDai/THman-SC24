We have updated AD and uploaded the new code to github.

The first part is a simulation experiment, just run the specified program under windows and wait for the output result.

The second and third parts are real experiments. If you need to verify the superiority of our proposed algorithm (HCF), you need more computing resources (e.g., 64 compute nodes used in the paper) and storage resources (parallel filesystems and burst buffers used in the paper), as well as a good understanding of the system information (e.g., the bandwidth of the filesystem, etc.), and the complete experiment will take up to ten hours.

If you do not have the conditions described above, the following adjustments can be made to the process described in AD when reproducing Parts II and III. They can help you reproduce our experiments in the shortest possible time to prove that the code we uploaded runs correctly and schedules the workflow using a different algorithm.

    In the second part of the experiment, 4 compute nodes were used (achieved by modifying the Nodelists parameter in Workflow_Generator.py), and the default configuration was used for the other parameters.
    In the third part of the experiment, use 4 compute nodes and change the value of workflow_count to 2 (or some other smaller value), which will only run two workflows. Then, use the default configuration for the other parameters. Further, you can schedule the workflows using only some of the key algorithms, such as FCFS, HEFT, and HCF, instead of all of them.

If you have any questions, you can always ask us and we will answer you as fast as we can. Additionally, we are happy to provide raw data from our recently completed experiment on multiple workflow scheduling if you require it. The experiment used a total of 40 workflows, scheduled on 64 nodes and on a shared file system using the FCFS, HEFT, and HCF algorithms. The raw data is able to demonstrate the superiority of the HCF algorithm.
