/***********************************************************************/
/*  Program Name: 3-asm_pass1_u.c                                      */
/*  This program is the part of SIC/XE assembler Pass 1.	  		   */
/*  The program only identify the symbol, opcode and operand 		   */
/*  of a line of the asm file. The program do not build the            */
/*  SYMTAB.			                                               	   */
/*  2019.12.13                                                         */
/*  2021.03.26 Process error: format 1 & 2 instruction use + 		   */
/***********************************************************************/
#include <string.h>
#include <stdlib.h>
#include "2-optable.c"

/* Public variables and functions */
#define ADDR_SIMPLE 0x01
#define ADDR_IMMEDIATE 0x02
#define ADDR_INDIRECT 0x04
#define ADDR_INDEX 0x08

#define LINE_EOF (-1)
#define LINE_COMMENT (-2)
#define LINE_ERROR (0)
#define LINE_CORRECT (1)
#define MAX_SYMBOLS 1000


typedef struct {
    char symbol[LEN_SYMBOL];
    int value;
} Symbol;
Symbol symtab[MAX_SYMBOLS];
int symtab_len = 0;
typedef struct
{
	char symbol[LEN_SYMBOL];
	char op[LEN_SYMBOL];
	char operand1[LEN_SYMBOL];
	char operand2[LEN_SYMBOL];
	unsigned code;
	unsigned fmt;
	unsigned addressing;
} LINE;

int process_line(LINE *line);
/* return LINE_EOF, LINE_COMMENT, LINE_ERROR, LINE_CORRECT and Instruction information in *line*/

/* Private variable and function */

void init_LINE(LINE *line)
{
	line->symbol[0] = '\0';
	line->op[0] = '\0';
	line->operand1[0] = '\0';
	line->operand2[0] = '\0';
	line->code = 0x0;
	line->fmt = 0x0;
	line->addressing = ADDR_SIMPLE;
}

int process_line(LINE *line)
/* return LINE_EOF, LINE_COMMENT, LINE_ERROR, LINE_CORRECT */
{
	char buf[LEN_SYMBOL];
	int c;
	int state;
	int ret;
	Instruction *op;

	c = ASM_token(buf); /* get the first token of a line */
	if (c == EOF)
		return LINE_EOF;
	else if ((c == 1) && (buf[0] == '\n')) /* blank line */
		return LINE_COMMENT;
	else if ((c == 1) && (buf[0] == '.')) /* a comment line */
	{
		do
		{
			c = ASM_token(buf);
		} while ((c != EOF) && (buf[0] != '\n'));
		return LINE_COMMENT;
	}
	else
	{
		init_LINE(line);
		ret = LINE_ERROR;
		state = 0;
		while (state < 8)
		{
			switch (state)
			{
			case 0:
			case 1:
			case 2:
				op = is_opcode(buf);
				if ((state < 2) && (buf[0] == '+')) /* + */
				{
					line->fmt = FMT4;
					state = 2;
				}
				else if (op != NULL) /* INSTRUCTION */
				{
					strcpy(line->op, op->op);
					line->code = op->code;
					state = 3;
					if (line->fmt != FMT4)
					{
						line->fmt = op->fmt & (FMT1 | FMT2 | FMT3);
					}
					else if ((line->fmt == FMT4) && ((op->fmt & FMT4) == 0)) /* INSTRUCTION is FMT1 or FMT 2*/
					{														 /* ERROR 20210326 added */
						printf("ERROR at token %s, %s cannot use format 4 \n", buf, buf);
						ret = LINE_ERROR;
						state = 7; /* skip following tokens in the line */
					}
				}
				else if (state == 0) /* SYMBOL */
				{
					strcpy(line->symbol, buf);
					state = 1;
				}
				else /* ERROR */
				{
					printf("ERROR at token %s\n", buf);
					ret = LINE_ERROR;
					state = 7; /* skip following tokens in the line */
				}
				break;
			case 3:
				if (line->fmt == FMT1 || line->code == 0x4C) /* no operand needed */
				{
					if (c == EOF || buf[0] == '\n')
					{
						ret = LINE_CORRECT;
						state = 8;
					}
					else /* COMMENT */
					{
						ret = LINE_CORRECT;
						state = 7;
					}
				}
				else
				{
					if (c == EOF || buf[0] == '\n')
					{
						ret = LINE_ERROR;
						state = 8;
					}
					else if (buf[0] == '@' || buf[0] == '#')
					{
						line->addressing = (buf[0] == '#') ? ADDR_IMMEDIATE : ADDR_INDIRECT;
						state = 4;
					}
					else /* get a symbol */
					{
						op = is_opcode(buf);
						if (op != NULL)
						{
							printf("Operand1 cannot be a reserved word\n");
							ret = LINE_ERROR;
							state = 7; /* skip following tokens in the line */
						}
						else
						{
							strcpy(line->operand1, buf);
							state = 5;
						}
					}
				}
				break;
			case 4:
				op = is_opcode(buf);
				if (op != NULL)
				{
					printf("Operand1 cannot be a reserved word\n");
					ret = LINE_ERROR;
					state = 7; /* skip following tokens in the line */
				}
				else
				{
					strcpy(line->operand1, buf);
					state = 5;
				}
				break;
			case 5:
				if (c == EOF || buf[0] == '\n')
				{
					ret = LINE_CORRECT;
					state = 8;
				}
				else if (buf[0] == ',')
				{
					state = 6;
				}
				else /* COMMENT */
				{
					ret = LINE_CORRECT;
					state = 7; /* skip following tokens in the line */
				}
				break;
			case 6:
				if (c == EOF || buf[0] == '\n')
				{
					ret = LINE_ERROR;
					state = 8;
				}
				else /* get a symbol */
				{
					op = is_opcode(buf);
					if (op != NULL)
					{
						printf("Operand2 cannot be a reserved word\n");
						ret = LINE_ERROR;
						state = 7; /* skip following tokens in the line */
					}
					else
					{
						if (line->fmt == FMT2)
						{
							strcpy(line->operand2, buf);
							ret = LINE_CORRECT;
							state = 7;
						}
						else if ((c == 1) && (buf[0] == 'x' || buf[0] == 'X'))
						{
							line->addressing = line->addressing | ADDR_INDEX;
							ret = LINE_CORRECT;
							state = 7; /* skip following tokens in the line */
						}
						else
						{
							printf("Operand2 exists only if format 2  is used\n");
							ret = LINE_ERROR;
							state = 7; /* skip following tokens in the line */
						}
					}
				}
				break;
			case 7: /* skip tokens until '\n' || EOF */
				if (c == EOF || buf[0] == '\n')
					state = 8;
				break;
			}
			if (state < 8)
				c = ASM_token(buf); /* get the next token */
		}
		return ret;
	}
}

int main(int argc, char *argv[])
{
	int c, line_count;
	char buf[LEN_SYMBOL];
	LINE line;
	int LOCCTR = 0;
	char temp[100] = "\0";
	int start = 0;
	int n, i, x, b, p, e;
	int opcode_length;
	int current_op = 0;
	int disp;
	int base;
	char modification[100][15] = {'\0'};
	int mod_len = 0;
	if (argc < 2)
	{
		printf("Usage: %s fname.asm\n", argv[0]);
	}
	else
	{
		if (ASM_open(argv[1]) == NULL)
			printf("File not found!!\n");
		else
		{
			for (line_count = 1; (c = process_line(&line)) != LINE_EOF; line_count++)
			{
				if (c == LINE_ERROR)
					//printf("%03d : Error\n", line_count);
					continue;
				else if (c == LINE_COMMENT)
					//printf("%03d : Comment line\n", line_count);
					continue;
				else
				{
					if (strcmp(line.op, "START") == 0)
					{
						LOCCTR = strtol(line.operand1, NULL, 10);
						start = LOCCTR;
					}
					if (line.symbol[0] != '\0') 
					{
						strcpy(symtab[symtab_len].symbol, line.symbol);
						symtab[symtab_len].value = LOCCTR;
						symtab_len++;
					}
					if (strcmp(line.op, "RESW") == 0)
						LOCCTR += 3 * strtol(line.operand1, NULL, 10);
					else if (strcmp(line.op, "RESB") == 0)
						LOCCTR += strtol(line.operand1, NULL, 10);
					else if (strcmp(line.op, "BYTE") == 0)
					{
						if (line.operand1[0] == 'C')
							LOCCTR += strlen(line.operand1) - 3;
						else if (line.operand1[0] == 'X')
							LOCCTR += (strlen(line.operand1) - 3) / 2;
					}
					else if (strcmp(line.op, "WORD") == 0)
						LOCCTR += 3;
					else
						LOCCTR += line.fmt;
				}
			}
			int total = LOCCTR;
			ASM_close();
			LOCCTR = 0;
			int i;
			int current_length = 0;
			int full_length = 0;
			int total_length = 0;
			int current_address = start;
			char text_record[101] = "\0";
			char to_obc[100]= "\0";
			sprintf(text_record, "T%06X", start);
			int temp_length = 0;
			ASM_open(argv[1]);
			for (line_count = 1; (c = process_line(&line)) != LINE_EOF; line_count++)
			{
				current_address = LOCCTR;
				if (c == LINE_ERROR)
					//printf("%03d : Error\n", line_count);
					continue;
				else if (c == LINE_COMMENT)
					//printf("%03d : Comment line\n", line_count);
					continue;
				if (line_count == 1 && strcmp(line.op,"START") == 0)
				{
					LOCCTR = strtol(line.operand1, NULL, 10);
					printf("H%-6s%06X%06X\n", line.symbol, start, total - start);
					continue;
				}
				else if (strcmp(line.op, "RESW") == 0)
				{
					LOCCTR += 3 * strtol(line.operand1, NULL, 10);
					temp_length += 6 * strtol(line.operand1, NULL, 10);
					continue;
				}
				else if (strcmp(line.op, "RESB") == 0)
				{
					LOCCTR += strtol(line.operand1, NULL, 10);
					temp_length += 2 * strtol(line.operand1, NULL, 10);
					continue;
				}
				else if (strcmp(line.op, "BYTE") == 0)
				{
					if (line.operand1[0] == 'C')
					{
						LOCCTR += strlen(line.operand1) - 3;
						current_length += 2 * (strlen(line.operand1) - 3);
					}
					else if (line.operand1[0] == 'X')
					{
						LOCCTR += (strlen(line.operand1) - 3) / 2;
						current_length += (strlen(line.operand1) - 3);
					}   
				}
				else if (strcmp(line.op, "WORD") == 0)
					LOCCTR += 3;
				else
					LOCCTR += line.fmt;
				if (strcmp(line.op, "END") == 0)
				{
					break;
				}
				else if (strcmp(line.op, "BASE") == 0)
				{
					for(i = 0; i < symtab_len; i++)
					{
						if(strcmp(line.operand1, symtab[i].symbol) == 0)
						{
							base = symtab[i].value;
						}
					}
					continue;
				}
				else if (strcmp(line.op, "NOBASE") == 0)
				{
					continue;
				}
				else
				{
					n = 0, i = 0, x = 0, b = 0, p = 2, e = 0;
					char temp_ojc[100] = "\0";
					if (strcmp(line.op, "START") == 0)
					{
						LOCCTR = strtol(line.operand1, NULL, 10);
						continue;
					}
					if (strcmp(line.op, "WORD") == 0)
					{
						//save ojc code to temp_ojc
						sprintf(temp_ojc, "%06X", strtol(line.operand1, NULL, 10));
						opcode_length = 6;
					}
					if (strcmp(line.op, "BYTE") == 0)
					{
						if (line.operand1[0] == 'C')
						{
							for (i = 2; i < strlen(line.operand1) - 1; i++)
							{
								sprintf(temp_ojc, "%s%02X", temp_ojc, line.operand1[i]);
							}
							opcode_length = (strlen(line.operand1) - 3) * 2;
						}
						if (line.operand1[0] == 'X')
						{
							for (i = 2; i < strlen(line.operand1) - 1; i++)
							{
								sprintf(temp_ojc, "%s%c", temp_ojc, line.operand1[i]);
							}
							opcode_length = strlen(line.operand1) - 3;
						}
					}
					if (line.fmt == 1)
					{
						opcode_length = 2;
					}
					if (line.fmt == 2)
					{
						opcode_length = 4;
					}
					if (line.fmt == 3)
					{
						opcode_length = 6;
					}
					if (line.fmt == 4)// if fmt4,add a '+' at the start of the op code
					{
						opcode_length = 8;
						e = 1;
						p = 0;
					}
					if (line.fmt == 2)
					{
						if(strcmp(line.operand1, "A") == 0)
							n = 0;
						else if(strcmp(line.operand1, "X") == 0)
							n = 1;
						else if(strcmp(line.operand1, "L") == 0)
							n = 2;
						else if(strcmp(line.operand1, "B") == 0)
							n = 3;
						else if(strcmp(line.operand1, "S") == 0)
							n = 4;
						else if(strcmp(line.operand1, "T") == 0)
							n = 5;
						else if(strcmp(line.operand1, "F") == 0)
							n = 6;
						else if(strcmp(line.operand1, "PC") == 0)
							n = 8;
						else if(strcmp(line.operand1, "SW") == 0)
							n = 9;
						else
							n = 0;

						if(strcmp(line.operand2, "A") == 0)
							i = 0;
						else if(strcmp(line.operand2, "X") == 0)
							i = 1;
						else if(strcmp(line.operand2, "L") == 0)
							i = 2;
						else if(strcmp(line.operand2, "B") == 0)
							i = 3;
						else if(strcmp(line.operand2, "S") == 0)
							i = 4;
						else if(strcmp(line.operand2, "T") == 0)
							i = 5;
						else if(strcmp(line.operand2, "F") == 0)
							i = 6;
						else if(strcmp(line.operand2, "PC") == 0)
							i = 8;
						else if(strcmp(line.operand2, "SW") == 0)
							i = 9;
						else
							i = 0;
												
					}
					current_op = is_opcode(line.op)->code;
					if (line.fmt == 1)
					{
						current_op += 0;
					}
					else if(line.fmt == 2)
					{
						current_op += 0;
					}
					else if(line.addressing == 0x2)
					{
						current_op += 1;
					}
					else if(line.addressing == 0x4)
					{
						current_op += 2;
					}
					else
					{
						current_op += 3;
					}
					if(line.addressing == 0x9)
					{
						x = 8;
					}
					int is_op = 1;
					if (line.fmt == 3)
					{
						int save;
						for (i = 0; i < symtab_len; i++) 
						{
							if (strcmp(line.operand1, symtab[i].symbol) == 0)
							{
								disp = symtab[i].value - LOCCTR;
								if (disp < 0)
								{
									disp = ((unsigned int)disp);  // Convert disp to its 2's complement if it's negative
								}
								is_op = 0;
								save = i;
							}
						}
						if (disp < -2048 || disp > 2047)
						{
							b = 4;
							p = 0;
							disp = symtab[save].value - base;
						}
						else
						{
							b = 0;
							p = 2;
						}
					}
					if (line.fmt == 4)
					{
						for (i = 0; i < symtab_len; i++) 
						{
							if (strcmp(line.operand1, symtab[i].symbol) == 0)
							{
								disp = symtab[i].value;
								is_op = 0;
							}
						}
					}
					if ((line.fmt == 3 || line.fmt == 4) && is_op == 1)
					{
						p = 0;
						disp = strtol(line.operand1, NULL, 10);
					}
					if(line.fmt == 1)
					{
						sprintf(temp_ojc, "%02X", current_op);
					}
					else if (line.fmt == 2)
					{
						sprintf(temp_ojc, "%02X%X%X", current_op, n, i);
					}
					else if (line.fmt == 3 || line.fmt == 4)
					{
						sprintf(temp_ojc, "%02X%X", current_op, x + b + p + e);
						if (line.fmt == 3)
						{
							//只取右邊三位，不到三位補0
							sprintf(temp_ojc, "%s%03X", temp_ojc, disp & 0xFFF);
						}
						if (line.fmt == 4)
						{
							sprintf(temp_ojc, "%s%05X", temp_ojc, disp & 0xFFFFF);
						}
					}
					if(p == 0 && b == 0 && x == 0 && line.fmt == 4 && is_op == 0)
					{
						sprintf(modification[mod_len], "M%06X05", (full_length + 3) / 2);
						mod_len++;
					}
					else if(p == 0 && b == 0 && x == 0 && line.fmt == 3 && is_op == 0)
					{
						sprintf(modification[mod_len], "M%06X03", (full_length + 3) / 2);
						mod_len++;
					}
					full_length += opcode_length;
					if(total_length + opcode_length + temp_length > 60)
					{
						total_length = total_length / 2;
						sprintf(text_record, "%s%02X%s", text_record, total_length, to_obc);
						printf("%s\n", text_record);
						total_length = opcode_length;
						opcode_length = 0;
						temp_length = 0;
						sprintf(text_record, "T%06X", current_address);
						strcpy(to_obc, temp_ojc);
					}
					else
					{
						sprintf(to_obc, "%s%s", to_obc, temp_ojc);
						total_length += opcode_length;
					}
				}
			}
			if(opcode_length != 0)
			{
				total_length = total_length / 2;
				sprintf(text_record, "%s%02X%s", text_record, total_length, to_obc);
				printf("%s\n", text_record);
			}
			for(i = 0; i < mod_len; i++)
			{
				printf("%s\n", modification[i]);
			}
			printf("E%06X\n", start);
			ASM_close();
		}
	}
}
