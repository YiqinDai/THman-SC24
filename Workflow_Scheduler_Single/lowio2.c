#include<stdio.h>
#include<mpi.h>
#include<string.h>
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
	if (rank % 4 == 0){
		char rank_str[100];
		sprintf(rank_str, "%d", rank);
		strcat(fn, rank_str);
		f = fopen( fn,"a+");
		for (int j = 0; j < 800000; j++){
			fputs("1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111", f);
		}
		fclose(f);
	}
	else if(rank % 4 == 1){
		rank -= 1;
		char rank_str[100];
                sprintf(rank_str, "%d", rank);
                strcat(fn, rank_str);
                f = fopen( fn,"a+");
		for (int j = 0; j < 900000; j++){
			fgets(str, 100, f); 
                }
		fclose(f);
	}
	else{
		sleep(80);
	}
	MPI_Finalize();
	return 0;
}
