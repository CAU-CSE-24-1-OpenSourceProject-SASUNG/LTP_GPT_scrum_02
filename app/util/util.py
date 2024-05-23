from app import ltp_gpt
from fastapi import HTTPException
from starlette.requests import Request


def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Authorization header must start with Bearer")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")


def get_embeddings(problem, situation, answer):
    situations = situation.split(".")  # 상황 문장별로 파싱
    problem_embedding = ltp_gpt.generate_embedding(problem)
    situation_embeddings = [ltp_gpt.generate_embedding(sentence.strip()) for sentence in situations]
    answer_embedding = ltp_gpt.generate_embedding(answer)

    return problem_embedding, situation_embeddings, answer_embedding