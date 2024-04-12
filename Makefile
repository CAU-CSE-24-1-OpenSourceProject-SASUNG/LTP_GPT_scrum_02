CC = uvicorn

all : EXE

EXE : 
	$(CC) main:app --reload
