#include<stdio.h>
#include<mpi.h>
#include<string.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char** argv){
	MPI_Init(&argc, &argv);
	char fn[120] ="files_runtime/";
	char s[100];
	char str[100];
	int rank;
	FILE *f = NULL;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	strcpy(s,argv[1]);
        strcat(fn, s);
        strcat(fn, "-");
	if (rank % 2 == 0){
		char rank_str[100];
		sprintf(rank_str, "%d", rank);
		strcat(fn, rank_str);
		f = fopen( fn,"a+");
		for (int j = 0; j < 80000000; j++){
			if (j % 100000 == 0) {
                                usleep(1000);
                        }
			fputs("1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111", f);
		}
		fclose(f);
	}
	else if(rank % 2 == 1){
		rank -= 1;
		char rank_str[100];
                sprintf(rank_str, "%d", rank);
                strcat(fn, rank_str);
                f = fopen( fn,"a+");
		for (int j = 0; j < 90000000; j++){
			fgets(str, 100, f); 
                }
		fclose(f);
	}
	else{
	}
	MPI_Finalize();
	return 0;
}
