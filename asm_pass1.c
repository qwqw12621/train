#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "3-asm_pass1_u.c"

#define HASH_TABLE_SIZE 100

typedef struct Node {
    char* key;
    int value;
    struct Node* next;
} Node;

typedef struct {
    Node* buckets[HASH_TABLE_SIZE];
} HashMap;

Node* createNode(const char* key, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->key = strdup(key);
    newNode->value = value;
    newNode->next = NULL;
    return newNode;
}

HashMap* createHashMap() {
    HashMap* map = (HashMap*)malloc(sizeof(HashMap));
    int i;
	for (i = 0; i < HASH_TABLE_SIZE; ++i) {
        map->buckets[i] = NULL;
    }
    return map;
}

unsigned int hash(const char* key) {
    unsigned int hashValue = 0;
    while (*key) {
        hashValue = (hashValue << 5) + *key++;
    }
    return hashValue % HASH_TABLE_SIZE;
}

void put(HashMap* map, const char* key, int value) {
    unsigned int index = hash(key);
    Node* newNode = createNode(key, value);
    newNode->next = map->buckets[index];
    map->buckets[index] = newNode;
}

int get(HashMap* map, const char* key) {
    unsigned int index = hash(key);
    Node* current = map->buckets[index];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    return -1; // 如果键不存在，返回 -1
}

void printHashMap(HashMap* map) {
    int i;
	for (i = 0; i < HASH_TABLE_SIZE; ++i) {
        Node* current = map->buckets[i];
        while (current != NULL) {
            printf("%12s: 	 %06X\n", current->key, current->value);
            current = current->next;
        }
    }
}

int main(int argc, char *argv[])
{
	int			i, c, line_count, total_byte = 0, start_pos = 0, end_pos = 0;
	char		buf[LEN_SYMBOL];
	LINE		line;

	HashMap* map = createHashMap();

	if(argc < 2)
	{
		printf("Usage: %s fname.asm\n", argv[0]);
	}
	else
	{
		if(ASM_open(argv[1]) == NULL)
			printf("File not found!!\n");
		else
		{
			for(line_count = 1 ; (c = process_line(&line)) != LINE_EOF; line_count++)
			{
				if(c == LINE_ERROR)
					printf("%%06X : Error\n", total_byte);
				else if(c == LINE_COMMENT)
					continue;
					//printf("%03d : Comment line\n", line_count);
				else {
					// reserve word preprocess
					if (strcmp(line.op, "START") == 0) {
						start_pos = atoi(line.operand1);
						end_pos = atoi(line.operand1);
						total_byte = atoi(line.operand1);
						printf("%06X %12s %12s %12s %12s\n", total_byte, line.symbol, line.op, line.operand1, line.operand2);
					} else if (strcmp(line.op, "END") == 0) {
						// end_pos = atoi(line.operand1);
						// printf("%06X %12s %12s %12s %12s\n", total_byte, line.symbol, line.op, line.operand1, line.operand2);
					} else if (strcmp(line.op, "RESW") == 0) {
						if (strlen(line.symbol)) {
							put(map, line.symbol, total_byte);
						}

						printf("%06X %12s %12s %12s %12s\n", total_byte, line.symbol, line.op, line.operand1, line.operand2);
						total_byte += 3 * atoi(line.operand1);
						end_pos = total_byte;
					} else if (strcmp(line.op, "WORD") == 0) {
						if (strlen(line.symbol)) {
							put(map, line.symbol, total_byte);
						}

						printf("%06X %12s %12s %12s %12s\n", total_byte, line.symbol, line.op, line.operand1, line.operand2);
						total_byte += 3;
						end_pos = total_byte;
					} else if (strcmp(line.op, "RESB") == 0) {
						if (strlen(line.symbol)) {
							put(map, line.symbol, total_byte);
						}

						printf("%06X %12s %12s %12s %12s\n", total_byte, line.symbol, line.op, line.operand1, line.operand2);
						total_byte += atoi(line.operand1);
						end_pos = total_byte;
					} else if (strcmp(line.op, "BYTE") == 0) {
						if (strlen(line.symbol)) {
							put(map, line.symbol, total_byte);
						}
						int temp = total_byte;
						
						if (line.operand1[0] == 'C')
							total_byte += strlen(line.operand1) - 3;
						else if (line.operand1[0] == 'X') 
							if ((strlen(line.operand1) - 3) % 2 == 0) 
								total_byte += (strlen(line.operand1) - 3) / 2;
							else {
								printf("ERROR, X'' dosen't form a interger byte.\n");
								return 0;
							}

						printf("%06X %12s %12s %12s %12s\n", temp, line.symbol, line.op, line.operand1, line.operand2);
						end_pos = total_byte;
					} else {
						int out_byte = total_byte;
						char symbol[LEN_SYMBOL];
						char op[LEN_SYMBOL];
						char operand1[LEN_SYMBOL];
						char operand2[LEN_SYMBOL];
						strcpy(symbol,line.symbol);
						strcpy(op,line.op);
						strcpy(operand1,line.operand1);
						strcpy(operand2,line.operand2);

						if (strlen(line.symbol)) {
							put(map, line.symbol, total_byte);
						}

						if (line.fmt == FMT1) {
							total_byte += 1;
						} else if (line.fmt == FMT2) {
							total_byte += 2;
						} else if (line.fmt == FMT3) {
							total_byte += 3;
						} else if (line.fmt == FMT4) {
							op[0] = '+';
							strcpy(op+1,line.op);
							total_byte += 4;
						}

						end_pos = total_byte;

						if (line.addressing & ADDR_IMMEDIATE) {
							operand1[0] = '#';
							strcpy(operand1 + 1,line.operand1);
						} else if (line.addressing & ADDR_INDIRECT) {
							operand1[0] = '@';
							strcpy(operand1 + 1,line.operand1);
						}
						
						if (line.addressing & ADDR_INDEX) {
							char str[20] = ", X";
							strcat(operand1, str);
						}

						printf("%06X %12s %12s %12s %12s\n", out_byte, symbol, op, operand1, operand2);
					}
						//printf("%03d  : %12s %12s %12s,%12s (FMT=%X, ADDR=%X), code = %X\n", line_count, line.symbol, line.op, line.operand1, line.operand2, line.fmt, line.addressing, line.code);
				}
			}
			ASM_close();
		}

		printf("\n\nProgram Length = %x (hex)\n\n", end_pos - start_pos);

		printHashMap(map);
	}
}
